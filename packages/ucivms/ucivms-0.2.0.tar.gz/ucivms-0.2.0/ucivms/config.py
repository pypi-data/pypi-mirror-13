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
from __future__ import unicode_literals
import errno
import os

from uciconfig import (
    options,
    registries,
    stacks,
    stores,
)


class StartingNameMatcher(stacks.SectionMatcher):
    """A sub name section matcher.

    This selects sections starting with a given name respecting the Store
    order.
    """

    def __init__(self, store, name):
        super(StartingNameMatcher, self).__init__(store)
        self.name = name

    def get_sections(self):
        """Get all sections starting with ``name`` in the store.

        The most generic sections are described first in the store, then more
        specific ones can be provided for reduced scopes.

        The returned sections are therefore returned in the reversed order so
        the most specific ones can be found first.
        """
        store = self.store
        # Later sections are more specific, they should be returned first
        for _, section in reversed(list(store.get_sections())):
            if section.id is None:
                # The no-name section is always included if present
                yield store, section
                continue
            if self.name is None:
                # If no name has been defined, no section can match
                continue
            section_name = section.id
            if self.name.startswith(section_name):
                yield store, section


VmMatcher = StartingNameMatcher
VmStore = stores.FileStore
VmCmdLineStore = stores.CommandLineStore


def system_config_dir():
    return '/etc'


def config_file_basename():
    return 'uci-vms.conf'


class VmStack(stacks.Stack):
    """Per-directory options."""

    def __init__(self, name):
        """Make a new stack for a given vm.

        :param name: The name of a virtual machine.

        The options are searched in following files each one providing a
        ``name`` specific section and defaults in the no-name section.

        The directory local file:
        * the ``name`` section in ./uci-vms.conf,
        * the no-name section in ./uci-vms.conf
        The user file:
        * the ``name`` section in ~/uci-vms.conf,
        * the no-name section in ~/uci-vms.conf
        The system-wide file:
        * the ``name`` section in /etc/uci-vms.conf,
        * the no-name section in /etc/uci-vms.conf
        """
        self.cmdline_store = VmCmdLineStore()
        lpath = os.path.abspath(config_file_basename())
        self.local_store = self.get_shared_store(VmStore(lpath))
        section_getters = [self.cmdline_store.get_sections,
                           VmMatcher(self.local_store, name).get_sections]
        upath = os.path.join(os.environ['HOME'], config_file_basename())
        if upath != lpath:
            # Only add user store if we're not running from HOME
            user_store = self.get_shared_store(VmStore(upath))
            section_getters.append(VmMatcher(user_store, name).get_sections)
        else:
            user_store = self.local_store
        spath = os.path.join(system_config_dir(), config_file_basename())
        self.system_store = self.get_shared_store(VmStore(spath))
        section_getters.append(VmMatcher(self.system_store, name).get_sections)
        super(VmStack, self).__init__(
            section_getters, user_store, mutable_section_id=name)

    # FIXME: This should be a DictOption -- vila 2016-01-05
    def get_nova_creds(self):
        """Get nova credentials from a config.

        This defines the set of options needed to authenticate against nova in
        a single place.

        :raises: uciconfig.errors.OptionMandatoryValueError if one of the
            options is not set.
        """
        creds = {}
        for k in ('username', 'password', 'tenant_name',
                  'auth_url', 'region_name'):
            opt_name = 'vm.os.{}'.format(k)
            creds[opt_name] = self.get(opt_name)
        return creds


def path_from_unicode(path_string):
    return os.path.expanduser(path_string)


class PathOption(options.Option):

    def __init__(self, *args, **kwargs):
        """A path option definition.

        This possibly expands the user home directory.
        """
        super(PathOption, self).__init__(
            *args, from_unicode=path_from_unicode, **kwargs)


class PackageListOption(options.ListOption):
    """A package list option definition.

    This possibly expands '@filename' replacing it with the file content.
    """

    def __init__(self, *args, **kwargs):
        # Foce invalid values to be an error (and forbids overriding it) to
        # catch invalid file names
        super(PackageListOption, self).__init__(
            *args, invalid='error', **kwargs)

    def from_unicode(self, string):
        values = super(PackageListOption, self).from_unicode(string)
        if not values:
            return values
        converted = []
        for v in values:
            if v.startswith('@'):
                try:
                    # FIXME: A bit more care should be taken about interpreting
                    # relative paths: are they relative to the config file ?
                    # Also, the current implementation swallow the ValueError
                    # raised below, turning it into an OptionValueError
                    # instead, losing the precision if multiple files are
                    # involved -- vila 2015-06-18
                    with open(v[1:]) as f:
                        for package in f:
                            converted.append(package.strip())
                except IOError as e:
                    # python2 does not provide FileNotFoundError
                    if e.errno == errno.ENOENT:
                        raise ValueError('{} does not exist'.format(v[1:]))
                    else:
                        raise
            else:
                converted.append(v)
        return converted


def register(option):
    options.option_registry.register(option)

register(options.Option('vm', default=None,
                        help_string='''\
The name space defining a virtual machine.

This option is a place holder to document the options that defines a virtual
machine and the options defining the infrastructure used to manage them all.

For qemu based vms, the definition of a vm is stored in an xml file under
'/etc/libvirt/qemu/{vm.name}.xml'. This is under the libvirt package control
and is out of scope for uci-vms.

There are 3 other significant files used for a given vm:

- a disk image mounted at '/' from '/dev/sda1':
  '{vm.images_dir}/{vm.name}.qcow2'

- a iso image available from '/dev/sdb' labeled 'cidata':
  {vm.images_dir}/{vm.name}.seed which contains the cloud-init data used to
  configure/install/update the vm.

- a console: {vm.images_dir}/{vm.name}.console which can be 'tail -f'ed from
  the host.

The data used to create the seed above are stored in a vm specific
configuration directory for easier debug and reference:
- {vm.config_dir}/user-data
- {vm.config_dir}/meta-data
- {vm.config_dir}/ecdsa
- {vm.config_dir}/ecdsa.pub
'''))

# The directory where we store vm files related to their configuration with
# cloud-init (user-data, meta-data, ssh keys).
register(PathOption('vm.vms_dir', default='~/.config/uci-vms',
                    help_string='''\
Where vm related config files are stored.

This includes user-data and meta-data for cloud-init and ssh server keys.

This directory must exist.

Each vm get a specific directory (automatically created) there based on its
name.
'''))
# The base directories where vms are stored for kvm
register(PathOption('vm.images_dir', default='/var/lib/libvirt/images',
                    help_string='''Where vm disk images are stored.''',))
register(options.Option('vm.qemu_etc_dir', default='/etc/libvirt/qemu',
                        help_string='''\
Where libvirt (qemu) stores the vms config files.'''))

# The base directories where vms are stored for lxc
register(PathOption('vm.lxcs_dir', default='/var/lib/lxc',
                    help_string='''Where lxc definitions are stored.'''))
# Isos and images download handling
register(options.Option('vm.iso_url',
                        default='''\
http://cdimage.ubuntu.com/daily-live/current/''',
                        help_string='''Where an iso can be downloaded from.'''
                        ))
register(options.Option('vm.iso_name',
                        default='{vm.release}-desktop-{vm.cpu_model}.iso',
                        help_string='''The name of the iso.'''))
register(options.Option('vm.cloud_image_url',
                        default='''\
http://cloud-images.ubuntu.com/{vm.release}/current/''',
                        help_string='''\
Where a cloud image can be downloaded from.'''))
register(options.Option('vm.cloud_image_name',
                        default='''\
{vm.release}-server-cloudimg-{vm.cpu_model}-disk1.img''',
                        help_string='''The name of the cloud image.'''))
register(PathOption('vm.download_cache', default='{vm.images_dir}',
                    help_string='''Where downloads end up.'''))


# The VM classes are registered where/when needed
vm_class_registry = registries.Registry()


register(options.RegistryOption('vm.class', registry=vm_class_registry,
                                default=options.MANDATORY,
                                help_string='''\
The virtual machine technology to use.'''))
# The ubiquitous vm name
register(options.Option('vm.name', default=None, invalid='error',
                        help_string='''\
The vm name, used as a prefix for related files.'''))
# The second most important bit to define a vm: which ubuntu release ?
register(options.Option('vm.release', default=None, invalid='error',
                        help_string='''The ubuntu release name.'''))
# The third important piece to define a vm: where to store files like the
# console, the user-data and meta-data files, the ssh server keys, etc.
register(PathOption('vm.config_dir', default='{vm.vms_dir}/{vm.name}',
                    invalid='error',
                    help_string='''\
The directory where files specific to a vm are stored.

This includes the user-data and meta-data files used at install time (for
reference and easier debug) as well as the optional ssh server keys.

By default this is {vm.vms_dir}/{vm.name}. You can put it somewhere else by
redefining it as long as it ends up being unique for the vm.

{vm.vms_dir}/{vm.release}/{vm.name} may better suit your taste for example.
'''))
# The options defining the vm physical characteristics
register(options.Option('vm.ram_size', default='1024',
                        help_string='''The ram size in megabytes.'''))
register(options.Option('vm.disk_size', default='8G',
                        help_string='''The disk image size in bytes.

Optional suffixes "k" or "K" (kilobyte, 1024) "M" (megabyte, 1024k) "G"
(gigabyte, 1024M) and T (terabyte, 1024G) are supported.
'''))
register(options.Option('vm.cpus', default='1', help_string='''\
The number of cpus.'''))
register(options.Option('vm.cpu_model', default=None, invalid='error',
                        help_string='''The number of cpus.'''))
register(options.ListOption('vm.network', default='{{vm.class}.network}',
                            help_string='''\
The network setup.

The default value depends on the vm class used.
'''))

register(options.ListOption('kvm.network', default='network=default',
                            help_string='''\
The --network parameter for virt-install.

This can be specialized for each machine but the default should work in most
setups. Watch for your DHCP server exhausting its address space if you create a
lot of vms with random MAC addresses.
'''))
register(options.ListOption('lxd.network', default=None,
                            help_string='''\
The parameters for the 'lxc config device add command'.
'''))


register(options.Option('vm.meta_data', default='''\
instance-id: {vm.name}
local-hostname: {vm.name}
''',
                        invalid='error',
                        help_string='''\
The meta data for cloud-init to put in the seed.'''))

register(options.ListOption(
    'vm.ssh_opts',
    default=None,
    help_string='''\
A list of ssh options to be used when connecting to the vm via ssh.'''))

# host user related options
register(options.Option('vm.bind_home', default=False,
                        from_unicode=options.bool_from_store,
                        help_string='''\
Whether or not the user home dir should be mounted inside the vm.

The {vm.user} home directory is mounted.

This is implemented for lxc only.
'''))
register(options.Option('vm.user',
                        default_from_env=['USER'],
                        help_string='''The user for {vm.bind_home}.'''))

# Some bits that may added to user-data but are optional

register(PackageListOption('vm.packages', default=None,
                           help_string='''\
A list of package names to be installed.

If the package name starts with '@', it is interpreted as a file name
and its content, one package by line, is inserted in the list.
'''))
register(options.Option('vm.apt_proxy', default=None, invalid='error',
                        help_string='''\
A local proxy for apt to avoid repeated .deb downloads.

Example:

  vm.apt_proxy = http://192.168.0.42:3142
'''))
register(options.ListOption('vm.apt_sources', default=None,
                            help_string='''\
A list of apt sources entries to be added to the default ones.

Cloud-init already setup /etc/apt/sources.list with appropriate entries. Only
additional entries need to be specified here.
'''))
register(options.ListOption('vm.ssh_authorized_keys', default=None,
                            help_string='''\
A list of paths to public ssh keys to be authorized for the default user.'''))
register(options.ListOption('vm.ssh_keys', default=None,
                            help_string='''A list of paths to server ssh keys.

Both public and private keys can be provided. Accepted ssh key types are rsa,
dsa and ecdsa. The file names should match <type>.*[.pub].
'''))
register(options.Option('vm.update', default=False,
                        from_unicode=options.bool_from_store,
                        help_string='''Whether or not the vm should be updated.

Both apt-get update and apt-get upgrade are called if this option is set.
'''))
register(options.Option('vm.poweroff', default=True,
                        from_unicode=options.bool_from_store,
                        help_string='''\
Whether or not the vm should stop at the end of the installation.'''))
register(options.Option('vm.password', default='ubuntu', invalid='error',
                        help_string='''The ubuntu user password.'''))
register(options.Option('vm.launchpad_id',
                        help_string='''\
The launchpad login used for launchpad ssh access from the guest.'''))
# The scripts that are executed before powering off
register(PathOption('vm.root_script', default=None,
                    help_string='''\
The path to a script executed as root before powering off.

This script is executed before {vm.ubuntu_script}.
'''))
register(PathOption('vm.ubuntu_script', default=None,
                    help_string='''\
The path to a script executed as ubuntu before powering off.

This script is excuted after {vm.root_script}.
'''))
register(options.ListOption('vm.uploaded_scripts', default=None,
                            help_string='''\
A list of scripts to be uploaded to the guest.

Scripts can use config options from their vm, they will be expanded before
upload. All scripts are uploaded into {vm.uploaded_scripts.guest_dir} under
their base name.
'''))
register(options.Option('vm.uploaded_scripts.guest_dir',
                        default='~ubuntu/bin',
                        help_string='''\
Where {vm.uploaded_scripts} are uploaded on the guest.'''))
register(options.Option('vm.final_message',
                        default=None,
                        help_string='''\
The cloud-init final message, a release-specific message is used if
none is provided to address compatibility with Ubuntu precise.'''))

# timeouts: some operations may fail transiently, they have to be retried
# FIXME: two kinds of timeouts seem appropriate: a simple list to sleep times,
# a tuple defining an exponential backoff. -- vila 2015-06-25
register(options.ListOption('vm.lxc.set_ip_timeouts', default='0, 120, 10',
                            help_string='''\
A timeouts tuple to use when waiting for lxc to set an IP.

(first, up_to, retries):
- first: seconds to wait after the first attempt
- up_to: seconds after which to give up
- retries: how many attempts after the first try
'''))
register(options.ListOption('vm.lxc.ssh_setup_timeouts', default='0, 120, 10',
                            help_string='''\
A timeouts tuple to use when waiting for lxc to setup ssh.

(first, up_to, retries):
- first: seconds to wait after the first attempt
- up_to: seconds after which to give up
- retries: how many attempts after the first try
'''))
register(options.ListOption('vm.lxd.set_ip_timeouts', default='0, 120, 10',
                            help_string='''\
A timeouts tuple to use when waiting for lxd to set an IP.

(first, up_to, retries):
- first: seconds to wait after the first attempt
- up_to: seconds after which to give up
- retries: how many attempts after the first try
'''))
register(options.ListOption('vm.lxd.ssh_setup_timeouts', default='0, 120, 10',
                            help_string='''\
A timeouts tuple to use when waiting for lxd to setup ssh.

(first, up_to, retries):
- first: seconds to wait after the first attempt
- up_to: seconds after which to give up
- retries: how many attempts after the first try
'''))

# nova options
register(options.Option('vm.os.username', default_from_env=['OS_USERNAME'],
                        default=options.MANDATORY,
                        help_string='''The Open Stack user name.

This is generally set via OS_USERNAME, sourced from a novarc file
(~/.novarc, ~/.canonistack/novarc).
'''))
register(options.Option('vm.os.password', default_from_env=['OS_PASSWORD'],
                        default=options.MANDATORY,
                        help_string='''The Open Stack password.

This is generally set via OS_PASSWORD, sourced from a novarc file
(~/.novarc, ~/.canonistack/novarc).
'''))
register(options.Option('vm.os.region_name',
                        default_from_env=['OS_REGION_NAME'],
                        default=options.MANDATORY,
                        help_string='''The Open Stack region name.

This is generally set via OS_REGION_NAME, sourced from a novarc file
(~/.novarc, ~/.canonistack/novarc).
'''))
register(options.Option('vm.os.tenant_name',
                        default_from_env=['OS_TENANT_NAME'],
                        default=options.MANDATORY,
                        help_string='''The Open Stack tenant name.

This is generally set via OS_TENANT_NAME, sourced from a novarc file
(~/.novarc, ~/.canonistack/novarc).
'''))
register(options.Option('vm.os.auth_url', default_from_env=['OS_AUTH_URL'],
                        default=options.MANDATORY,
                        help_string='''The Open Stack keystone url.

This is generally set via OS_AUTH_URL, sourced from a novarc file
(~/.novarc, ~/.canonistack/novarc).
'''))
register(options.ListOption('vm.os.flavors', default=None,
                            help_string='''\
A list of flavors for all supported clouds.

The first known one is used.
'''))
register(options.Option('vm.image', default=options.MANDATORY,
                        help_string='''The glance image to boot from.'''))
register(options.Option('vm.net_id', default=None,
                        help_string='''The network id for the vm.'''))
register(PathOption('vm.ssh_key_path', default='~/.ssh/id_rsa',
                    help_string='''The ssh key for the vm.'''))
register(options.ListOption('vm.apt_get.update.timeouts',
                            default='15.0, 90.0, 240.0',
                            help_string='''apt-get update timeouts in seconds.

When apt-get update fails on hash sum mismatches, retry after the specified
timeouts. More values mean more retries.
'''))
# FIXME: According to the help string this can (and should) be fixed
# -- vila 2015-07-20
register(options.ListOption('vm.ppas',
                            default=None,
                            help_string='''PPAs to be added to the vm.

This works around cloud-init not activating the deb-src line and not providing
a way to do so. This is intended to be fixed in uci-vms so vm.apt_sources can
be used again.
'''))
register(options.Option('vm.nova.boot_timeout', default='600',
                        from_unicode=options.float_from_store,
                        help_string='''\
Max time to boot a nova instance (in seconds).'''))
register(options.Option('vm.nova.set_ip_timeout', default='300',
                        from_unicode=options.float_from_store,
                        help_string='''\
Max time for a nova instance to get an IP (in seconds).'''))
# FIXME: 600 is a more realistic value but canonistack can be really slow and
# 3600 has been observed. There should be a better way to declare default
# values on a per cloud basis -- vila 2015-12-21
register(options.Option('vm.nova.cloud_init_timeout', default='3600',
                        from_unicode=options.float_from_store,
                        help_string='''\
Max time for cloud-init to finish (in seconds).'''))
