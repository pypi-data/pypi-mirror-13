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
from __future__ import unicode_literals
import os
import unittest

from uciconfig import errors
from ucitests import assertions
from ucivms import (
    config,
    vms,
)
from ucivms.tests import fixtures


class TestVmMatcher(unittest.TestCase):

    def setUp(self):
        super(TestVmMatcher, self).setUp()
        fixtures.isolate_from_disk(self)
        self.store = config.VmStore('foo.conf')
        self.matcher = config.VmMatcher(self.store, 'test')

    def test_empty_section_always_matches(self):
        self.store._load_from_string('foo=bar')
        matching = list(self.matcher.get_sections())
        self.assertEqual(1, len(matching))

    def test_specific_before_generic(self):
        self.store._load_from_string('foo=bar\n[test]\nfoo=baz')
        matching = list(self.matcher.get_sections())
        self.assertEqual(2, len(matching))
        # First matching section is for test
        self.assertEqual(self.store, matching[0][0])
        base_section = matching[0][1]
        self.assertEqual('test', base_section.id)
        # Second matching section is the no-name one
        self.assertEqual(self.store, matching[0][0])
        no_name_section = matching[1][1]
        self.assertIs(None, no_name_section.id)


class TestVmStackOrdering(unittest.TestCase):

    def setUp(self):
        super(TestVmStackOrdering, self).setUp()
        fixtures.isolate_from_disk(self)
        self.conf = config.VmStack('foo')

    def test_default_in_empty_stack(self):
        self.assertEqual('1024', self.conf.get('vm.ram_size'))

    def test_system_overrides_internal(self):
        self.conf.system_store._load_from_string('vm.ram_size = 42')
        self.assertEqual('42', self.conf.get('vm.ram_size'))

    def test_user_overrides_system(self):
        self.conf.system_store._load_from_string('vm.ram_size = 42')
        self.conf.store._load_from_string('vm.ram_size = 84')
        self.assertEqual('84', self.conf.get('vm.ram_size'))

    def test_local_overrides_user(self):
        self.conf.system_store._load_from_string('vm.ram_size = 42')
        self.conf.store._load_from_string('vm.ram_size = 84')
        self.conf.local_store._load_from_string('vm.ram_size = 168')
        self.assertEqual('168', self.conf.get('vm.ram_size'))


class TestVmStack(unittest.TestCase):
    """Test config option values."""

    def setUp(self):
        super(TestVmStack, self).setUp()
        fixtures.isolate_from_disk(self)
        self.conf = config.VmStack('foo')
        self.conf.store._load_from_string('''
vm.release=raring
vm.cpu_model=amd64
''')

    def assertValue(self, expected_value, option):
        self.assertEqual(expected_value, self.conf.get(option))

    def test_raring_iso_url(self):
        self.assertValue('http://cdimage.ubuntu.com/daily-live/current/',
                         'vm.iso_url')

    def test_raring_iso_name(self):
        self.assertValue('raring-desktop-amd64.iso', 'vm.iso_name')

    def test_raring_cloud_image_url(self):
        self.assertValue('http://cloud-images.ubuntu.com/raring/current/',
                         'vm.cloud_image_url')

    def test_raring_cloud_image_name(self):
        self.assertValue('raring-server-cloudimg-amd64-disk1.img',
                         'vm.cloud_image_name')

    def test_apt_proxy_set(self):
        proxy = 'apt_proxy: http://example.org:4321'
        self.conf.set('vm.apt_proxy', proxy)
        self.conf.store.save_changes()
        self.assertEqual(proxy, self.conf.expand_options('{vm.apt_proxy}'))

    def test_download_cache_with_user_expansion(self):
        download_cache = '~/installers'
        self.conf.set('vm.download_cache', download_cache)
        self.conf.store.save_changes()
        self.assertValue(os.path.join(self.home_dir, 'installers'),
                         'vm.download_cache')

    def test_images_dir_with_user_expansion(self):
        images_dir = '~/images'
        self.conf.set('vm.images_dir', images_dir)
        self.conf.store.save_changes()
        self.assertValue(os.path.join(self.home_dir, 'images'),
                         'vm.images_dir')


class TestPathOption(unittest.TestCase):

    def setUp(self):
        super(TestPathOption, self).setUp()
        fixtures.isolate_from_disk(self)

    def assertConverted(self, expected, value):
        option = config.PathOption('foo', help_string='A path.')
        self.assertEqual(expected, option.convert_from_unicode(None, value))

    def test_absolute_path(self):
        self.assertConverted('/test/path', '/test/path')

    def test_home_path_with_expansion(self):
        self.assertConverted(self.home_dir, '~')

    def test_path_in_home_with_expansion(self):
        self.assertConverted(os.path.join(self.home_dir, 'test/path'),
                             '~/test/path')


class TestPackageListOption(unittest.TestCase):

    def setUp(self):
        super(TestPackageListOption, self).setUp()
        fixtures.isolate_from_disk(self)

    def assertConverted(self, expected, value):
        option = config.PackageListOption('foo', help_string='A package list.')
        self.assertEqual(expected, option.convert_from_unicode(None, value))

    def test_empty(self):
        self.assertConverted(None, None)

    def test_regular_packages(self):
        self.assertConverted(['a', 'b'], 'a,b')

    def test_existing_file(self):
        with open('packages', 'w') as f:
            f.write('a\nb\n')
        self.assertConverted(['a', 'b'], '@packages')

    def test_non_existing_file(self):
        with self.assertRaises(errors.OptionValueError) as cm:
            self.assertConverted(None, '@I-dont-exist')
        self.assertEqual('foo', cm.exception.name)


class TestVmClass(unittest.TestCase):

    def setUp(self):
        super(TestVmClass, self).setUp()
        fixtures.isolate_from_disk(self)

    def test_class_mandatory(self):
        conf = config.VmStack('I-dont-exist')
        with self.assertRaises(errors.OptionMandatoryValueError):
            conf.get('vm.class')

    def test_lxc(self):
        conf = config.VmStack('I-dont-exist')
        conf.store._load_from_string('''vm.class=lxc''')
        self.assertIs(vms.Lxc, conf.get('vm.class'))

    def test_ephemeral_lxc(self):
        conf = config.VmStack('I-dont-exist')
        conf.store._load_from_string('''vm.class=ephemeral-lxc''')
        self.assertIs(vms.EphemeralLxc, conf.get('vm.class'))

    def test_kvm(self):
        conf = config.VmStack('I-dont-exist')
        conf.store._load_from_string('''vm.class=kvm''')
        self.assertIs(vms.Kvm, conf.get('vm.class'))

    def test_bogus(self):
        conf = config.VmStack('I-dont-exist')
        conf.store._load_from_string('''vm.class=bogus''')
        with self.assertRaises(errors.OptionMandatoryValueError):
            conf.get('vm.class')


class TestStartingNameMatcher(unittest.TestCase):

    def setUp(self):
        super(TestStartingNameMatcher, self).setUp()
        fixtures.isolate_from_disk(self)
        # Any simple store is good enough
        self.store = config.VmStore('foo.conf')

    def assertSectionIDs(self, expected, name, content):
        self.store._load_from_string(content)
        matcher = config.StartingNameMatcher(self.store, name)
        sections = list(matcher.get_sections())
        assertions.assertLength(self, len(expected), sections)
        self.assertEqual(expected, [section.id for _, section in sections])
        return sections

    def test_none_with_sections(self):
        self.assertSectionIDs([], None, '''\
[foo]
[bar]
''')

    def test_empty(self):
        self.assertSectionIDs([], 'whatever', '')

    def test_matching_paths(self):
        self.assertSectionIDs(['foo-bar', 'foo'],
                              'foo-bar-baz', '''\
[foo]
[foo-bar]
''')

    def test_no_name_section_included_when_present(self):
        # Note that other tests will cover the case where the no-name section
        # is empty and as such, not included.
        self.assertSectionIDs(['foo-bar', 'foo', None],
                              'foo-bar-baz', '''\
option = defined so the no-name section exists
[foo]
[foo-bar]
''')

    def test_order_reversed(self):
        self.assertSectionIDs(['foo-bar', 'foo'], 'foo-bar-baz', '''\
[foo]
[foo-bar]
''')

    def test_unrelated_section_excluded(self):
        self.assertSectionIDs(['foo-bar', 'foo'], 'foo-bar-baz', '''\
[foo]
[foo-qux]
[foo-bar]
''')

    def test_respect_order(self):
        self.assertSectionIDs(['foo', 'foo-b', 'foo-bar-baz'],
                              'foo-bar-baz', '''\
[foo-bar-baz]
[foo-qux]
[foo-b]
[foo]
''')


class TestVmName(unittest.TestCase):

    def setUp(self):
        super(TestVmName, self).setUp()
        fixtures.isolate_from_disk(self)
        self.config_dir = os.path.join(self.uniq_dir, 'config')

    def save_config(self, content):
        user_config_path = os.path.join(self.uniq_dir, 'home',
                                        config.config_file_basename())
        with open(user_config_path, 'w')as f:
            f.write(content)

    def test_name_starts_with_section_name(self):
        self.save_config('''\
[foo]
vm.class = lxc
''')
        conf = config.VmStack('foo1')
        conf.cmdline_store.from_cmdline(['vm.name=foo1'])
        self.assertEqual('foo1', conf.get('vm.name'))
        self.assertIs(vms.Lxc, conf.get('vm.class'))
