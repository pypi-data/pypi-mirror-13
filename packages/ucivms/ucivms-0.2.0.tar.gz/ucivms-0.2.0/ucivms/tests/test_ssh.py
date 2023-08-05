# This file is part of Ubuntu Continuous Integration virtual machine tools.
#
# Copyright 2014, 2015 Canonical Ltd.
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

import os
import unittest

from ucitests import (
    features,
    scenarii,
)

from ucivms import (
    config,
    ssh,
    vms,
)
from ucivms.tests import (
    features as vms_features,
    fixtures as vms_fixtures,
)


load_tests = scenarii.load_tests_with_scenarios


class TestInfoFromPath(unittest.TestCase):

    scenarios = scenarii.multiply_scenarios(
        # key
        ([('rsa', dict(algo='rsa', key_name='rsa')),
          ('dsa', dict(algo='dsa', key_name='dsa')),
          ('ecdsa', dict(algo='ecdsa', key_name='ecdsa')),
          ('unknown', dict(algo=None, key_name='foo'))]),
        # visibility
        ([('private', dict(visible='private', suffix='')),
          ('public', dict(visible='public', suffix='.pub'))]))

    def assertInfoFromPath(self, expected, key_path):
        self.assertEqual(expected, ssh.infos_from_path(key_path))

    def test_key(self):
        self.assertInfoFromPath((self.algo, self.visible),
                                './{}{}'.format(self.key_name, self.suffix))


@features.requires(vms_features.ssh_feature)
class TestKeyGen(unittest.TestCase):

    scenarios = [('rsa', dict(algo='rsa', prefix='ssh-rsa ',
                              upper_type='RSA')),
                 ('dsa', dict(algo='dsa', prefix='ssh-dss ',
                              upper_type='DSA')),
                 ('ecdsa', dict(algo='ecdsa', prefix='ecdsa-sha2-nistp256 ',
                                upper_type='EC'))]

    def setUp(self):
        super(TestKeyGen, self).setUp()
        vms_fixtures.isolate_from_disk(self)

    def keygen(self, ssh_type, upper_type):
        private_path = os.path.join(self.uniq_dir, ssh_type)
        ssh.keygen(private_path, 'uci-vms@test')
        self.assertTrue(os.path.exists(private_path))
        public_path = private_path + '.pub'
        self.assertTrue(os.path.exists(public_path))
        with open(public_path) as f:
            public = f.read()
        with open(private_path) as f:
            private = f.read()
        self.assertTrue(
            private.startswith('-----BEGIN %s PRIVATE KEY-----\n'
                               % (upper_type,)))
        self.assertTrue(
            private.endswith('-----END %s PRIVATE KEY-----\n' % (upper_type,)))
        self.assertTrue(public.endswith(' uci-vms@test\n'))
        return private, public

    def test_key(self):
        private, public = self.keygen(self.algo, self.upper_type)
        self.assertTrue(public.startswith(self.prefix))


@features.requires(vms_features.use_sudo_for_tests_feature)
class TestSsh(unittest.TestCase):

    def setUp(self):
        super(TestSsh, self).setUp()
        vms_features.requires_existing_vm(self, 'uci-vms-tests-lxc')
        vms_fixtures.isolate_from_disk(self)
        # To isolate tests from each other, created vms needs a unique name. To
        # keep those names legal and still user-readable we use the class name
        # and the test method name
        self.vm_name = '{}-{}-{}'.format(self.__class__.__name__,
                                         self._testMethodName, os.getpid())
        config_dir = os.path.join(self.uniq_dir, 'config')
        # Create a shared config
        conf = config.VmStack(None)
        conf.store._load_from_string('''
vm.ssh_opts=-oUserKnownHostsFile=/dev/null,-oStrictHostKeyChecking=no
vm.config_dir={config_dir}
[uci-vms-tests-lxc]
# /!\ Should match the one defined by the user
vm.name = uci-vms-tests-lxc
vm.class = lxc
vm.release = trusty
[{vm_name}]
vm.name = {vm_name}
vm.class = ephemeral-lxc
vm.backing = uci-vms-tests-lxc
vm.release = trusty
'''.format(config_dir=config_dir, vm_name=self.vm_name))
        conf.store.save()
        conf.store.unload()

    def test_simple_command(self):
        vm = vms.EphemeralLxc(config.VmStack(self.vm_name))
        self.addCleanup(vm.stop)
        vm.start()
        ret, out, err = vm.shell_captured('whoami')
        self.assertEqual(0, ret)
        self.assertEqual('ubuntu\n', out)

# test_ssh_no_args (hard, interactive session)
# test_ssh_cant_connect (wrong host, unknown host, missing key, wrong user)
