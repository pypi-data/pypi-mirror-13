# This file is part of Ubuntu Continuous Integration virtual machine tools.
#
# Copyright 2014, 2015, 2016 Canonical Ltd.
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

import errno
import os
import subprocess
import sys

try:
    if sys.version_info < (3,):
        # novaclient doesn't support python3 (yet)
        from ucivms.vms import nova
        with_nova = True
    else:
        with_nova = False
except ImportError:
    with_nova = False

from uciconfig import errors
from ucitests import features
from ucivms import config


qemu_img_feature = features.ExecutableFeature('qemu-img')
lxd_client_feature = features.ExecutableFeature('lxc')


class _UseSudoForTestsFeature(features.Feature):
    """User has sudo access.

    There is no direct way to test for sudo access other than trying to use
    it. This is not something we can do in automated tests as it requires user
    input.

    Whatever trick is used to guess whether or not the user *can* sudo won't
    tell us if she agrees to run the sudo tests. Instead, this should rely on
    an opt-in mechanism so each user decides whether or not she wants to run
    the tests.
    """

    def _probe(self):
        # I.e. if you want to run the tests that requires sudo issue:
        # $ touch ~/.uci-vms.use_sudo_for_tests
        # if you don't, issue:
        # $ rm -f ~/.uci-vms.use_sudo_for_tests
        path = os.path.expanduser('~/.uci-vms.use_sudo_for_tests')
        return os.path.exists(path)

    def feature_name(self):
        return 'sudo access'


use_sudo_for_tests_feature = _UseSudoForTestsFeature()


class _SshFeature(features.ExecutableFeature):

    def __init__(self):
        super(_SshFeature, self).__init__('ssh')
        self.version = None

    def _probe(self):
        exists = super(_SshFeature, self)._probe()
        if exists:
            try:
                proc = subprocess.Popen(['ssh', '-V'],
                                        stderr=subprocess.PIPE,
                                        stdout=subprocess.PIPE)
                out, err = proc.communicate()
            except OSError as e:
                if e.errno == errno.ENOENT:
                    # broken install
                    return False
                else:
                    raise
            self.version = err.decode()
        return exists

    def requires_ecdsa(self, test):
        ecdsa_support = 'OpenSSH_5.9p1-5ubuntu.1.1'
        if self.version < ecdsa_support:
            test.skipTest('ecdsa requires ssh >= %s, you have %s'
                          % (ecdsa_support, self.version,))


ssh_feature = _SshFeature()


def requires_existing_vm(test, vm_name):
    """Skip a test if a known reference vm is not provided locally.

    :note: This may be revisited later when it becomes easier to create vms for
       test purposes.

    :note: This should be called early during setUp so the user configuration
        is still available (i.e. the test has not yet been isolated from disk).

    :param test: The TestCase requiring the vm.

    :param vm_name: The vm name in the config.
    """
    user_conf = config.VmStack(vm_name)
    if user_conf.get('vm.name') != vm_name:
        test.skipTest('{} does not exist'.format(vm_name))


class NovaCompute(features.Feature):

    def _probe(self):
        if not with_nova:
            # novaclient doesn't support python3 (yet)
            return False
        client = self.get_client()
        if client is None:
            return False
        try:
            # can transiently fail with requests.exceptions.ConnectionError
            # (converted from MaxRetryError).
            client.authenticate()
        except nova.exceptions.ClientException:
            return False
        return True

    def get_client(self):
        test_vm_conf = config.VmStack('uci-vms-tests-nova')
        try:
            return nova.get_os_nova_client(test_vm_conf)
        except errors.OptionMandatoryValueError:
            return None


# The single instance shared by all tests
nova_compute = NovaCompute()


class NovaCredentials(features.Feature):

    def __init__(self):
        super(NovaCredentials, self).__init__()

    def _probe(self):
        if not with_nova:
            # novaclient doesn't support python3 (yet)
            return False
        try:
            config.VmStack('uci-vms-tests-nova').get_nova_creds()
        except errors.OptionMandatoryValueError:
            return False
        return True

    def feature_name(self):
        return 'Valid nova credentials'


# The single instance shared by all tests
nova_creds = NovaCredentials()
