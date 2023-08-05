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

import os
import unittest

from ucitests import features
from ucivms import (
    config,
    errors,
)
from ucivms.tests import (
    features as vms_features,
    fixtures as vms_fixtures,
)
from ucivms.vms import lxd


class TestUciImageName(unittest.TestCase):

    def test_valid_cloud_image(self):
        self.assertEqual(
            'uci/cloudimg/trusty-amd64',
            lxd.uci_image_name('cloudimg', 'trusty', 'amd64'))


@features.requires(vms_features.lxd_client_feature)
class TestInit(unittest.TestCase):

    def setUp(self):
        super(TestInit, self).setUp()
        # FIXME: The following will be needed by all lxd tests
        # -- vila 2015-12-21
        # lxc requires a cert and key for the client and automagically generate
        # them on first need.
        lxd_conf_dir = os.path.expanduser('~/.config/lxc')
        vms_fixtures.isolate_from_disk(self)
        os.environ['LXD_CONF'] = lxd_conf_dir
        # To isolate tests from each other, created vms needs a unique name. To
        # keep those names legal and still user-readable we use the class name
        # and the test method name. The process id is added so that the same
        # test suite can be run on the same host in several processes.
        self.vm_name = '{}-{}-{}'.format(self.__class__.__name__,
                                         self._testMethodName, os.getpid())
        # lxc wants a valid hostname, '_' are clearly forbidden
        self.vm_name = self.vm_name.replace('_', '-')
        config_dir = os.path.join(self.uniq_dir, 'config')
        # Create a shared config
        conf = config.VmStack(None)
        conf.store._load_from_string('''
vm.config_dir={config_dir}
[{vm_name}]
vm.name = {vm_name}
vm.class = lxd
'''.format(config_dir=config_dir, vm_name=self.vm_name))
        conf.store.save()
        conf.store.unload()
        self.addCleanup(conf.store.save_changes)

    def get_image_id(self, series, arch):
        return lxd.uci_image_name('cloudimg', series, arch)

    def test_unknown_image(self):
        vm = lxd.Lxd(config.VmStack(self.vm_name))
        image_id = self.get_image_id('Idontexist', 'amd64')
        vm.conf.set('vm.image', image_id)
        with self.assertRaises(errors.CommandError) as cm:
            vm.init()
        err_msg = "error: can't get info for image '{}': not found\n"
        self.assertEqual(err_msg.format(image_id),
                         cm.exception.err)

    def test_known_image(self):
        vm = lxd.Lxd(config.VmStack(self.vm_name))
        image_id = self.get_image_id('xenial', 'amd64')
        vm.conf.set('vm.image', image_id)
        self.addCleanup(vm.teardown)
        ret, out, err = vm.init()
        self.assertEqual(0, ret)
        self.assertEqual('Creating {} done.\n'.format(vm.conf.get('vm.name')),
                         out)
        self.assertEqual('', err)


class TestInfo(unittest.TestCase):

    def test_unknown(self):
        info = lxd.lxd_info('idontexist', '')
        self.assertEqual('UNKNOWN', info['state'])

    def test_running(self):
        info = lxd.lxd_info('foo', '''
Name: foo
Status: Running
Init: 8114
Processcount: 20
Ips:
  eth0:	IPV4	10.0.3.130	vethKJJF5J
  lo:	IPV4	127.0.0.1
  lo:	IPV6	::1
  lxcbr0:	IPV4	10.0.4.1
''')
        self.assertEqual('RUNNING', info['state'])
        self.assertEqual('8114', info['pid'])
        self.assertEqual('10.0.3.130', info['ip'])

    def test_stopped(self):
        info = lxd.lxd_info('foo', '''
Name: foo
Status: Stopped
''')
        self.assertEqual({'state': 'STOPPED'}, info)

    def test_no_ips(self):
        # Before ips are set
        info = lxd.lxd_info('foo', '''
Name: foo
Status: Running
Ips:
(none)
''')
        self.assertEqual({'state': 'RUNNING'}, info)
        self.assertFalse('ip' in info)


@features.requires(vms_features.lxd_client_feature)
class TestSetup(unittest.TestCase):

    def setUp(self):
        super(TestSetup, self).setUp()
        # FIXME: The following will be needed by all lxd tests
        # -- vila 2015-12-21
        # lxc requires a cert and key for the client and automagically generate
        # them on first need.
        lxd_conf_dir = os.path.expanduser('~/.config/lxc')
        vms_fixtures.isolate_from_disk(self)
        os.environ['LXD_CONF'] = lxd_conf_dir
        # To isolate tests from each other, created vms needs a unique name. To
        # keep those names legal and still user-readable we use the class name
        # and the test method name. The process id is added so that the same
        # test suite can be run on the same host in several processes.
        self.vm_name = '{}-{}-{}'.format(self.__class__.__name__,
                                         self._testMethodName, os.getpid())
        # lxc wants a valid hostname, '_' are clearly forbidden
        self.vm_name = self.vm_name.replace('_', '-')
        config_dir = os.path.join(self.uniq_dir, 'config')
        # Create a shared config
        conf = config.VmStack(None)
        conf.store._load_from_string('''
vm.ssh_opts=-oUserKnownHostsFile=/dev/null,-oStrictHostKeyChecking=no
# FIXME: A bit too specific for a test ;-D -- vila 2015-12-22
vm.ssh_authorized_keys = /home/vila/.ssh/keys/vila@launchpad.pub
lxd.network=eth0,nic,nictype=bridged,parent=br0,name=eth0
vm.config_dir={config_dir}
[{vm_name}]
vm.name = {vm_name}
vm.class = lxd
'''.format(config_dir=config_dir, vm_name=self.vm_name))
        conf.store.save()
        conf.store.unload()
        self.addCleanup(conf.store.save_changes)

    def get_image_id(self, series, arch):
        return lxd.uci_image_name('cloudimg', series, arch)

    def test_usable(self):
        vm = lxd.Lxd(config.VmStack(self.vm_name))
        image_id = self.get_image_id('xenial', 'amd64')
        vm.conf.set('vm.image', image_id)
        self.addCleanup(vm.teardown)
        vm.setup()
        # We should be able to ssh with the right user
        ret, out, err = vm.shell_captured('whoami')
        self.assertEqual(0, ret)
        self.assertEqual('ubuntu\n', out)
