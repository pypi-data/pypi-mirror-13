# This file is part of Ubuntu Continuous Integration virtual machine tools.
#
# Copyright 2016 Canonical Ltd.
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

import logging
import os
import time

from ucivms import (
    errors,
    subprocesses,
    timeouts,
    vms,
)


# FIXME: Too much duplication from nova here... -- vila 2015-12-22
def uci_image_name(domain, series, architecture):
    """Returns an image name.

    Images can be exported to lxd for specific needs.

    :param domain: 'cloudimg' for example.

    :param series: The ubuntu series (trusty, xenial, etc).

    :param architecture: The processor architecture ('amd64', 'i386', etc).
    """
    return 'uci/{}/{}-{}'.format(domain, series, architecture)


def lxd_info(vm_name, source=None):
    info = dict(state='UNKNOWN')
    if source is None:
        info_cmd = ['lxc', 'info', vm_name]
        try:
            _, source, err = subprocesses.run(info_cmd)
        except errors.CommandError as e:
            if e.err == 'error: not found\n':
                return info
            else:
                raise
    scanning_ips = False
    for l in source.splitlines():
        if scanning_ips:
            if l == '(none)':
                # interfaces are not setup yet
                continue
            details = l.split('\t')
            try:
                ifce, proto, ip = details[0:3]
            except ValueError:
                raise ValueError('Unexpected IP line: {}'.format(l))
                # FIXME: Assume eth0 until we can do better -- vila 2015-12-22
            if 'eth0' in ifce and proto == 'IPV4':
                info['ip'] = ip
        elif l.startswith('Status:'):
            _, s = l.split()
            info['state'] = s.upper()
        elif l.startswith('Init:'):
            _, pid = l.split()
            info['pid'] = pid
        elif l.startswith('Ips:'):
            scanning_ips = True
    return info


class Lxd(vms.VM):

    def __init__(self, conf, logger=None):
        super(Lxd, self).__init__(conf)
        if logger is None:
            # FIXME: Duplicated from nova.py -- vila 2015-12-21
            self.ensure_dir(self.config_dir_path())
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s %(levelname)s %(message)s",
                filename=os.path.join(self.config_dir_path(), 'uci-vms.log'))
            logger = logging.getLogger()
        self.logger = logger

    def state(self):
        # man lxc(7) defines the possible states as: STOPPED, STARTING,
        # RUNNING, ABORTING, STOPPING. We add UNKNOWN.
        info = lxd_info(self.conf.get('vm.name'))
        return info['state']

    def init(self):
        init_cmd = ['lxc', 'init', self.conf.get('vm.image'),
                    self.conf.get('vm.name')]
        return subprocesses.run(init_cmd)

    def set_cloud_init_config(self):
        self.create_user_data()
        config_cmd = ['lxc', 'config', 'set', self.conf.get('vm.name'),
                      'user.user-data', '-']
        return subprocesses.run(config_cmd, cmd_input=self.ci_user_data.dump())

    def setup(self):
        _, out, err = self.init()
        # FIXME: Log out & err ? -- vila 2015-12-22
        _, out, err = self.set_cloud_init_config()
        network = self.conf.get('vm.network')
        if network:
            dev_add_cmd = (['lxc', 'config', 'device', 'add',
                            self.conf.get('vm.name')] + network)
            # FIXME: Log out & err ? -- vila 2016-01-05
            _, out, err = subprocesses.run(dev_add_cmd)
        return self.start()

    # MISSINGTEST
    # FIXME: duplicated from Lxc -- vila 2015-12-22
    def wait_for_ip(self):
        ip = None
        first, up_to, retries = self.conf.get('vm.lxd.set_ip_timeouts')
        first = float(first)
        up_to = float(up_to)
        retries = int(retries)
        exc = None
        for sleep in timeouts.ExponentialBackoff(first, up_to, retries):
            try:
                info = lxd_info(self.conf.get('vm.name'))
                if info['state'] != 'RUNNING' or 'ip' not in info:
                    raise errors.UciVmsError(
                        'Lxd {} has not provided an IP yet: {}'.format(
                            self.conf.get('vm.name'), info))
                ip = info['ip']
                # FIXME: Assume eth0 until we can do better -- vila 2015-12-22
                self.create_iface_file('eth0', ip, 'unknown', 'unknown')
                # Success, clear the exception
                exc = None
                break
            except (errors.CommandError, errors.UciVmsError) as e:
                exc = e
                # FIXME: logging + metric  -- vila 2015-06-25
                pass
            time.sleep(sleep)
        if exc is not None:
            # Re-raise the last seen exception
            raise exc
        if ip is None:
            raise errors.UciVmsError('Lxd {} never provided an IP'.format(
                self.conf.get('vm.name')))

    # MISSINGTEST
    # FIXME: duplicated from Lxc -- vila 2015-12-22
    def wait_for_ssh(self):
        first, up_to, retries = self.conf.get('vm.lxd.ssh_setup_timeouts')
        first = float(first)
        up_to = float(up_to)
        retries = int(retries)
        exc = None
        for attempt, sleep in enumerate(timeouts.ExponentialBackoff(
                first, up_to, retries), start=1):
            try:
                ret, out, err = self.shell_captured('whoami')
                # Success, clear the exception
                exc = None
                break
            # FIXME: There may be better feedback to provide here if (for
            # example, the IP is lost abruptly or the vm is killed for reasons)
            # -- vila 2015-10-24
            except errors.CommandError as e:
                exc = e
                # FIXME: logging + metric  -- vila 2015-06-25
                pass
            time.sleep(sleep)
        if exc is not None:
            # Re-raise the last seen exception
            raise exc

    def start(self):
        start_cmd = ['lxc', 'start', self.conf.get('vm.name')]
        _, out, err = subprocesses.run(start_cmd)
        self.wait_for_ip()
        self.wait_for_ssh()

    def stop(self):
        stop_cmd = ['lxc', 'stop', self.conf.get('vm.name')]
        return subprocesses.run(stop_cmd)

    def teardown(self):
        return subprocesses.run(
            ['lxc', 'delete', self.conf.get('vm.name')])

# MISSINGTEST: Experiment and run tests in qemu where lxd is not installed

# MISSINGTEST: for stop(), teardown()
# MISSINGTEST: for download() which NIY

# Strip down the cloud-init dependency to the bare minimum so it's easier to
# ensure it didn't break. Turn the stripped features into ssh/lxc exec
# commands.

# /etc/cloud/cloud.cfg is the defaut config for cloud-init

# /etc/cloud/cloud.cfg.d/90_dpkg.cfg may be worth overriding to avoid searching
# for clouds we don't use
