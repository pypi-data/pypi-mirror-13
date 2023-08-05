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
import sys
import unittest

from ucitests import fixtures
from ucivms import (
    errors,
    subprocesses,
)


class TestRun(unittest.TestCase):

    def setUp(self):
        super(TestRun, self).setUp()
        fixtures.set_uniq_cwd(self)

    def test_success(self):
        ret, out, err = subprocesses.run(['echo', '-n', 'Hello'])
        self.assertEqual(0, ret)
        self.assertEqual('Hello', out)
        self.assertEqual('', err)

    def test_with_input(self):
        ret, out, err = subprocesses.run(['cat', '-'], 'bar\n')
        self.assertEqual(0, ret)
        self.assertEqual('bar\n', out)
        self.assertEqual('', err)

    def test_failure(self):
        with self.assertRaises(errors.CommandError) as cm:
            subprocesses.run(['ls', 'I-dont-exist'])
        self.assertEqual(2, cm.exception.retcode)
        self.assertEqual('', cm.exception.out)
        self.assertEqual(
            'ls: cannot access I-dont-exist: No such file or directory\n',
            cm.exception.err)

    def test_error(self):
        # python2 doesn't have FileNotFoundError
        with self.assertRaises(OSError) as cm:
            subprocesses.run(['I-dont-exist'])
        self.assertEqual(errno.ENOENT, cm.exception.errno)
        if sys.version_info[0] < 3:
            self.assertEqual("No such file or directory",
                             cm.exception.strerror)
        else:
            self.assertEqual("No such file or directory: 'I-dont-exist'",
                             cm.exception.strerror)


class TestPipe(unittest.TestCase):

    def setUp(self):
        super(TestPipe, self).setUp()
        fixtures.set_uniq_cwd(self)

    def test_success(self):
        proc = subprocesses.pipe(['echo', '-n', 'Hello'])
        self.assertEqual('Hello', proc.stdout.read().decode('utf8'))

    def test_failure(self):
        proc = subprocesses.pipe(['ls', 'I-dont-exist'])
        self.assertEqual(
            'ls: cannot access I-dont-exist: No such file or directory\n',
            proc.stdout.read().decode())
        # We get the above in stdout because stderr is redirected there
        self.assertIs(None, proc.stderr)

    def test_error(self):
        # python2 doesn't have FileNotFoundError
        with self.assertRaises(OSError) as cm:
            subprocesses.pipe(['I-dont-exist'])
        self.assertEqual(errno.ENOENT, cm.exception.errno)
        if sys.version_info[0] < 3:
            self.assertEqual("No such file or directory",
                             cm.exception.strerror)
        else:
            self.assertEqual("No such file or directory: 'I-dont-exist'",
                             cm.exception.strerror)


# MISSINGTESTS:
# test_ssh_no_args (hard, interactive session)
# test_ssh_simple_command
# test_ssh_cant_connect (wrong host, unknown host, missing key, wrong user)
