# This file is part of Ubuntu Continuous Integration virtual machine tools.
#
# Copyright 2015, 2016 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 3, as published by the
# Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranties of MERCHANTABILITY,
# SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import unicode_literals

import errno
import logging
import os
import subprocess
import time


from novaclient import exceptions
from novaclient import client


from ucivms import (
    errors,
    timeouts,
    vms,
)


def uci_image_name(domain, series, architecture):
    """Returns an image name.

    The images are uploaded to glance for specific needs.

    :param domain: 'cloudimg' or 'britney'.

    :param series: The ubuntu series (precise, trusty, etc).

    :param architecture: The processor architecture ('amd64', i386, etc).
    """
    if domain not in ('cloudimg', 'britney'):
        raise ValueError('Invalid image domain')
    return 'uci/{}/{}-{}.img'.format(domain, series, architecture)


def get_os_nova_client(conf, debug=False):
    os_nova_client = client.Client(
        '1.1',
        conf.get('vm.os.username'), conf.get('vm.os.password'),
        conf.get('vm.os.tenant_name'),
        conf.get('vm.os.auth_url'),
        region_name=conf.get('vm.os.region_name'),
        service_type='compute')
    return os_nova_client


class NovaServerException(errors.UciVmsError):
    pass


class NovaClient(object):
    """A nova client re-trying requests on known transient failures."""

    def __init__(self, conf, **kwargs):
        self.logger = kwargs.pop('logger')
        self.first_wait = kwargs.pop('first_wait', 30)
        self.wait_up_to = kwargs.pop('wait_up_to', 600)
        self.retries = kwargs.pop('retries', 8)
        debug = kwargs.pop('debug', False)
        # Activating debug will output the http requests issued by nova and the
        # corresponding responses (/!\ including credentials).
        if debug:
            self.logger.setLevel(logging.DEBUG)
        self.nova = get_os_nova_client(conf, debug)

    def retry(self, func, *args, **kwargs):
        no_404_retry = kwargs.pop('no_404_retry', False)
        sleeps = timeouts.ExponentialBackoff(
            self.first_wait, self.wait_up_to, self.retries)
        for attempt, sleep in enumerate(sleeps, start=1):
            try:
                if attempt > 1:
                    self.logger.info('Re-trying {} {}/{}'.format(
                        func.__name__, attempt, self.retries))
                return func(*args, **kwargs)
            except client.requests.ConnectionError:
                # Most common transient failure: the API server is unreachable
                msg = 'Connection error for {}, will sleep for {} seconds'
                self.logger.warn(msg.format(func.__name__, sleep))
            except (exceptions.OverLimit, exceptions.RateLimit):
                msg = ('Rate limit reached for {},'
                       ' will sleep for {} seconds')
                # This happens rarely but breaks badly if not caught. elmo
                # recommended a 30 seconds nap in that case.
                sleep += 30
                self.logger.exception(msg.format(func.__name__, sleep))
            except exceptions.ClientException as e:
                if no_404_retry and e.http_status == 404:
                    raise
                msg = '{} failed will sleep for {} seconds'
                self.logger.exception(msg.format(func.__name__, sleep))
            except:
                # All other exceptions are raised
                self.logger.exception('{} failed'.format(func.__name__))
                raise NovaServerException('{} failed'.format(func.__name__))
            # Take a nap before retrying
            self.logger.info('Sleeping {} seconds for {} {}/{}'.format(
                sleep, func.__name__, attempt, self.retries))
            time.sleep(sleep)
        # Raise if we didn't succeed at all
        raise NovaServerException("Failed to '{}' after {} retries".format(
            func.__name__, attempt))

    def flavors_list(self):
        return self.retry(self.nova.flavors.list)

    def images_list(self):
        return self.retry(self.nova.images.list)

    def create_server(self, name, flavor, image, user_data, nics,
                      availability_zone):
        return self.retry(self.nova.servers.create, name=name,
                          flavor=flavor, image=image, userdata=user_data,
                          nics=nics, availability_zone=availability_zone)

    def delete_server(self, server_id):
        # FIXME: 404 shouldn't be retried, if it's not there anymore, there is
        # nothing to delete. -- vila 2015-07-16
        return self.retry(self.nova.servers.delete, server_id)

    def start_server(self, instance):
        return self.retry(instance.start)

    def stop_server(self, instance):
        return self.retry(instance.stop)

    def create_floating_ip(self):
        return self.retry(self.nova.floating_ips.create)

    def delete_floating_ip(self, floating_ip):
        return self.retry(self.nova.floating_ips.delete, floating_ip)

    def add_floating_ip(self, instance, floating_ip):
        return self.retry(instance.add_floating_ip, floating_ip)

    def get_server_details(self, server_id):
        return self.retry(self.nova.servers.get, server_id,
                          no_404_retry=True)

    def get_server_console(self, server, length=None):
        return self.retry(server.get_console_output, length)


class NovaServer(vms.VM):

    nova_client_class = NovaClient

    def __init__(self, conf, logger=None):
        super(NovaServer, self).__init__(conf)
        if logger is None:
            # FIXME: We probably want to generalize logging -- vila 2015-08-25
            self.ensure_dir(self.config_dir_path())
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s %(levelname)s %(message)s",
                filename=os.path.join(self.config_dir_path(), 'uci-vms.log'))
            logger = logging.getLogger()
        self.logger = logger
        self.instance = None
        self.floating_ip = None
        self.nova = self.build_nova_client()
        self.test_bed_key_path = None
        self.conf.set('vm.ssh_authorized_keys',
                      self.conf.get('vm.ssh_key_path') + '.pub')
        # No need to reboot a nova instance
        self.conf.set('vm.poweroff', 'False')
        self.conf.set('vm.final_message', 'testbed setup completed.')

    # MISSINGTEST
    def state(self):
        try:
            with open(self.nova_id_path()) as f:
                nova_id = f.read().strip()
        except IOError as e:
            # python2 does not provide FileNotFoundError
            if e.errno == errno.ENOENT:
                # Unknown interface
                return 'UNKNOWN'
        try:
            self.instance = self.nova.get_server_details(nova_id)
        except exceptions.NotFound:
            return 'UNKNOWN'
        # The instance may remain in the DELETED state for some time.
        nova_states = dict(BUILD='STARTING',
                           ACTIVE='RUNNING',
                           SHUTOFF='STOPPED',
                           DELETED='UNKNOWN')
        return nova_states[self.instance.status]

    def build_nova_client(self):
        nova_client = self.nova_client_class(self.conf, logger=self.logger)
        return nova_client

    def ensure_ssh_key_is_available(self):
        self.test_bed_key_path = self.conf.get('vm.ssh_key_path')
        # FIXME: Needs to be unified for all vm classes -- vila 2015-08-26
        # From the test runner, we need an ssh key that can be used to connect
        # to the testbed. For testing purposes, we rely on self.auth_conf to
        # provide this key.
        if not os.path.exists(self.test_bed_key_path):
            base_dir = os.path.dirname(self.test_bed_key_path)
            try:
                # Try to create needed dirs
                os.makedirs(base_dir)
            except OSError as e:
                # They are already there, no worries
                if e.errno != errno.EEXIST:
                    raise
            # First time the test runner instance needs to create a test bed
            # instance, we need to create the ssh key pair.
            subprocess.call(
                ['ssh-keygen', '-t', 'rsa', '-q',
                 '-f', self.test_bed_key_path, '-N', ''])

    def find_flavor(self):
        flavors = self.conf.get('vm.os.flavors')
        existing_flavors = self.nova.flavors_list()
        for flavor in flavors:
            for existing in existing_flavors:
                if flavor == existing.name:
                    return existing
        raise NovaServerException(
            'None of [{}] can be found'.format(','.join(flavors)))

    def find_nova_image(self):
        image_name = self.conf.get('vm.image')
        existing_images = self.nova.images_list()
        for existing in existing_images:
            if image_name == existing.name:
                return existing
        raise NovaServerException(
            'Image "{}" cannot be found'.format(image_name))

    def find_nics(self):
        net_id = self.conf.get('vm.net_id')
        if net_id:
            return [{'net-id': self.conf.get('vm.net_id')}]
        return None

    # FIXME: This should save the console whether or not the setup fails
    # -- vila 2015-08-26
    def setup(self):
        flavor = self.find_flavor()
        image = self.find_nova_image()
        nics = self.find_nics()
        self.ensure_ssh_key_is_available()
        self.create_user_data()
        with open(self._user_data_path) as f:
            user_data = f.read()
        self.instance = self.nova.create_server(
            name=self.conf.get('vm.name'), flavor=flavor, image=image,
            user_data=user_data, nics=nics,
            # FIXME: We probably want at least a vm.az_name option. And get
            # that option from higher levels too -- vila 2014-10-13
            availability_zone=None)
        self.create_nova_id_file(self.instance.id)
        self.wait_for_active_instance()
# FIXME: We want a vm.create_floating_ip option ? -- vila 2015-08-24
#        if unit_config.is_hpcloud(self.conf.get('os.auth_url')):
#            self.floating_ip = self.nova.create_floating_ip()
#            self.nova.add_floating_ip(self.instance, self.floating_ip)
        self.wait_for_ip()
        self.wait_for_cloud_init()
        self.ensure_ssh_works()
        # FIXME: inherited from uci-engine, revisit -- vila 2016-01-18
        ppas = self.conf.get('vm.ppas')
        if ppas:
            cmd = ['sudo', 'add-apt-repository']
            if self.conf.get('vm.release') > 'precise':
                cmd.append('--enable-source')
            for ppa in ppas:
                self.ssh(*(cmd + [ppa]))
        # Now we can apt-get update (doing it earlier would lead to the wrong
        # source package to be installed).
        self.safe_apt_get_update()

    def apt_get_update(self):
        return self.ssh('sudo', 'apt-get', 'update')

    def safe_apt_get_update(self):
        for timeout in self.conf.get('vm.apt_get.update.timeouts'):
            proc, out, err = self.apt_get_update()
            if proc.returncode == 0:
                # We're done
                return
            else:
                msg = ('apt-get update failed, wait {}s\n'
                       'stdout:\n{}\n'
                       'stderr:\n{}\n')
                self.logger.info(msg.format(timeout, out, err))
                time.sleep(float(timeout))
        raise NovaServerException('apt-get update never succeeded')

    def update_instance(self, nova_id=None):
        if nova_id is None:
            nova_id = self.instance.id
        try:
            # Always query nova to get updated data about the instance
            self.instance = self.nova.get_server_details(nova_id)
            return True
        except:
            # But catch exceptions if something goes wrong. Higher levels will
            # deal with the instance not replying.
            return False

    def wait_for_active_instance(self):
        timeout_limit = time.time() + self.conf.get('vm.nova.boot_timeout')
        while (time.time() < timeout_limit and
               self.instance.status not in ('ACTIVE', 'ERROR')):
            time.sleep(5)
            self.update_instance()
        if self.instance.status != 'ACTIVE':
            msg = 'Instance {} never came up (last status: {})'.format(
                self.instance.id, self.instance.status)
            raise NovaServerException(msg)

    def nova_id_path(self):
        return os.path.join(self.config_dir_path(), 'nova_id')

    def create_nova_id_file(self, nova_id):
        nova_id_path = self.nova_id_path()
        self.ensure_dir(self.config_dir_path())
        with open(nova_id_path, 'w') as f:
            f.write(nova_id + '\n')

    # FIXME: ~Duplicated with lxc, refactor to extract discover_ip() which is
    # the part where the ip is acquired with different means depending on the
    # vm provider. -- vila 2015-10-25
    def wait_for_ip(self):
        timeout_limit = time.time() + self.conf.get('vm.nova.set_ip_timeout')
        while time.time() < timeout_limit:
            if not self.update_instance():
                time.sleep(5)
                continue
            networks = self.instance.networks.values()
            if networks:
                # The network name is arbitrary, can vary for different clouds
                # but there should be only one network so we get the first one
                # and avoid the need for a config option for the network name.
                # We take the last IP address so it's either the only one or
                # the floating one. In both cases that gives us a reachable IP.
                self.ip = networks[0][-1]
                self.logger.info('Got IP {} for {}'.format(
                    self.ip, self.instance.id))
                # FIXME: Why not get it from the console ? -- vila 2015-08-26
                # MISSINGTEST
                self.create_iface_file('eth0', self.ip, 'unknown', 'unknown')
                return
            else:
                self.logger.info(
                    'IP not yet available for {}'.format(self.instance.id))
            time.sleep(5)
        msg = 'Instance {} never provided an IP'.format(self.instance.id)
        raise NovaServerException(msg)

    def get_cloud_init_console(self, length=None):
        return self.nova.get_server_console(self.instance, length)

    # FIXME: ~Duplicated with lxc, refactor to extract discovering cloud-init
    # completion (success/failure may be refined later if at least ssh access
    # is provided. In this case, the cloud-init log files can be
    # acquired/analyzed more precisely. This will require refactoring
    # setup(). -- vila 2015-10-25
    def wait_for_cloud_init(self):
        timeout_limit = (time.time() +
                         self.conf.get('vm.nova.cloud_init_timeout'))
        final_message = self.conf.get('vm.final_message')
        while time.time() < timeout_limit:
            # A relatively cheap way to catch cloud-init completion is to watch
            # the console for the specific message we specified in user-data).
            # FIXME: or at least check that we don't miss when we sleep a
            # significant time between two calls (like on canonistack where we
            # can sleep for minute(s) -- vila 2015-07-17
            console = self.get_cloud_init_console(10)
            if final_message in console:
                # We're good to go
                self.logger.info(
                    'cloud-init completed for {}'.format(self.instance.id))
                return
            time.sleep(5)
        raise NovaServerException(
            'Instance {} never completed cloud-init'.format(self.instance.id))

    def ensure_ssh_works(self):
        proc, out, err = self.ssh('whoami')
        if proc.returncode:
            msg = ('testbed {} IP {} cannot be reached with ssh, retcode: {}\n'
                   'stdout:\n{}\n'
                   'stderr:\n{}\n')
            self.logger.info(msg.format(self.instance.id, self.ip,
                                        proc.returncode, out, err))
            raise NovaServerException('No ssh access to {}, IP: {}'.format(
                self.instance.id, self.ip))

    # MISSINGTEST
    def start(self):
        self.nova.start_server(self.instance)

    # MISSINGTEST
    def stop(self):
        self.nova.stop_server(self.instance)

    def teardown(self):
        if self.instance is not None:
            self.logger.info('Deleting instance {}'.format(self.instance.id))
            self.nova.delete_server(self.instance.id)
            self.instance = None
            os.remove(self.nova_id_path())
        if self.floating_ip is not None:
            self.nova.delete_floating_ip(self.floating_ip)
            self.floating_ip = None
        # FIXME: Now we can remove the testbed key from known_hosts (see
        # ssh()). -- vila 2014-01-30

    # FIXME: Should be unified with 'shell' and 'shell_captured'
    # -- vila 2015-08-26
    def ssh(self, command, *args, **kwargs):
        """Run a command in the testbed via ssh.

        :param args: The command and its positional arguments as a list.

        FIXME: Unused ?!? -- vila 2015-10-25
        :param kwargs: The named arguments for the command.

        The stdout and stderr outputs are captured and returned to the caller.
        """
        user = 'ubuntu'
        host = self.ip
        cmd = ['ssh',
               # FIXME: It would be better to ssh-keygen -f
               # "~/.ssh/known_hosts" -R self.ip once we're done with the test
               # bed to avoid polluting ssh commands stdout, but that will do
               # for now (that's what juju is doing after all ;)
               # -- vila 2014-01-29
               '-oStrictHostKeyChecking=no',
               '-i', self.test_bed_key_path,
               '{}@{}'.format(user, host)]
        if command is not None:
            cmd += [command]
        if args:
            cmd += args
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        out, err = proc.communicate()
        return proc, out, err

    # FIXME: Should be provided by the base class -- vila 2015-08-26
    def scp(self, local_path, remote_path):
        cmd = ['scp',
               # FIXME: It would be better to ssh-keygen -f
               # "~/.ssh/known_hosts" -R self.ip once we're done with the test
               # bed to avoid polluting ssh commands stdout, but that will do
               # for now (that's what juju is doing after all ;)
               # -- vila 2014-01-29
               '-oStrictHostKeyChecking=no',
               '-i', self.test_bed_key_path,
               local_path, remote_path]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        out, err = proc.communicate()
        return proc, out, err

    def get_remote_content(self, path):
        proc, content, err = self.ssh('cat', path)
        if proc.returncode:
            # We didn't get a proper content, report it instead
            content = ("{} couldn't be copied from testbed {}:\n"
                       "error: {}\n".format(path, self.ip, err))
        return content
