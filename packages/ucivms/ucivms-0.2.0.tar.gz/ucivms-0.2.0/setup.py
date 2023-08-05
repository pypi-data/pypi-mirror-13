#!/usr/bin/env python3

# This file is part of the Ubuntu Continuous Integration virtual machine tools
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


import setuptools
import sys


import ucivms


def get_scripts():
    if sys.version_info < (3,):
        return ['uci-vms2']
    else:
        return ['uci-vms']


setuptools.setup(
    name='ucivms',
    version='.'.join(str(c) for c in ucivms.__version__[0:3]),
    description=('Ubuntu Continuous Integration virtual machine tools.'),
    author='Vincent Ladeuil',
    author_email='vila+qa@canonical.com',
    url='https://launchpad.net/uci-vms',
    license='GPLv3',
    install_requires=['uciconfig'],
    packages=['ucivms', 'ucivms.tests', 'ucivms.vms'],
    scripts=get_scripts(),
)
