# Copyright 2011 OpenStack Foundation.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from __future__ import print_function

import errno
import logging
import multiprocessing
import os
import stat
import subprocess
import sys
import tempfile

import fixtures
import mock
from oslotest import base as test_base
import six

from oslo_concurrency import processutils
from oslotest import mockpatch


PROCESS_EXECUTION_ERROR_LOGGING_TEST = """#!/bin/bash
exit 41"""

TEST_EXCEPTION_AND_MASKING_SCRIPT = """#!/bin/bash
# This is to test stdout and stderr
# and the command returned in an exception
# when a non-zero exit code is returned
echo onstdout --password='"secret"'
echo onstderr --password='"secret"' 1>&2
exit 38"""

# This byte sequence is undecodable from most encoding
UNDECODABLE_BYTES = b'[a\x80\xe9\xff]'

TRUE_UTILITY = (sys.platform.startswith('darwin') and
                '/usr/bin/true' or '/bin/true')


class UtilsTest(test_base.BaseTestCase):
    # NOTE(jkoelker) Moar tests from nova need to be ported. But they
    #                need to be mock'd out. Currently they require actually
    #                running code.
    def test_execute_unknown_kwargs(self):
        self.assertRaises(processutils.UnknownArgumentError,
                          processutils.execute,
                          hozer=True)

    @mock.patch.object(multiprocessing, 'cpu_count', return_value=8)
    def test_get_worker_count(self, mock_cpu_count):
        self.assertEqual(8, processutils.get_worker_count())

    @mock.patch.object(multiprocessing, 'cpu_count',
                       side_effect=NotImplementedError())
    def test_get_worker_count_cpu_count_not_implemented(self,
                                                        mock_cpu_count):
        self.assertEqual(1, processutils.get_worker_count())

    def test_execute_with_callback(self):
        on_execute_callback = mock.Mock()
        on_completion_callback = mock.Mock()
        processutils.execute(TRUE_UTILITY)
        self.assertEqual(0, on_execute_callback.call_count)
        self.assertEqual(0, on_completion_callback.call_count)

        processutils.execute(TRUE_UTILITY, on_execute=on_execute_callback,
                             on_completion=on_completion_callback)
        self.assertEqual(1, on_execute_callback.call_count)
        self.assertEqual(1, on_completion_callback.call_count)

    @mock.patch.object(subprocess.Popen, "communicate")
    def test_execute_with_callback_and_errors(self, mock_comm):
        on_execute_callback = mock.Mock()
        on_completion_callback = mock.Mock()

        def fake_communicate(*args):
            raise IOError("Broken pipe")

        mock_comm.side_effect = fake_communicate

        self.assertRaises(IOError,
                          processutils.execute,
                          TRUE_UTILITY,
                          on_execute=on_execute_callback,
                          on_completion=on_completion_callback)
        self.assertEqual(1, on_execute_callback.call_count)
        self.assertEqual(1, on_completion_callback.call_count)

    def test_execute_with_preexec_fn(self):
        # NOTE(dims): preexec_fn is set to a callable object, this object
        # will be called in the child process just before the child is
        # executed. So we cannot pass share variables etc, simplest is to
        # check if a specific exception is thrown which can be caught here.
        def preexec_fn():
            raise processutils.InvalidArgumentError()

        processutils.execute(TRUE_UTILITY)

        expected_exception = (processutils.InvalidArgumentError if six.PY2
                              else subprocess.SubprocessError)
        self.assertRaises(expected_exception,
                          processutils.execute,
                          TRUE_UTILITY,
                          preexec_fn=preexec_fn)


class ProcessExecutionErrorTest(test_base.BaseTestCase):

    def test_defaults(self):
        err = processutils.ProcessExecutionError()
        self.assertTrue('None\n' in six.text_type(err))
        self.assertTrue('code: -\n' in six.text_type(err))

    def test_with_description(self):
        description = 'The Narwhal Bacons at Midnight'
        err = processutils.ProcessExecutionError(description=description)
        self.assertTrue(description in six.text_type(err))

    def test_with_exit_code(self):
        exit_code = 0
        err = processutils.ProcessExecutionError(exit_code=exit_code)
        self.assertTrue(str(exit_code) in six.text_type(err))

    def test_with_cmd(self):
        cmd = 'telinit'
        err = processutils.ProcessExecutionError(cmd=cmd)
        self.assertTrue(cmd in six.text_type(err))

    def test_with_stdout(self):
        stdout = """
        Lo, praise of the prowess of people-kings
        of spear-armed Danes, in days long sped,
        we have heard, and what honot the athelings won!
        Oft Scyld the Scefing from squadroned foes,
        from many a tribe, the mead-bench tore,
        awing the earls. Since erse he lay
        friendless, a foundling, fate repaid him:
        for he waxed under welkin, in wealth he trove,
        till before him the folk, both far and near,
        who house by the whale-path, heard his mandate,
        gabe him gits: a good king he!
        To him an heir was afterward born,
        a son in his halls, whom heaven sent
        to favor the fol, feeling their woe
        that erst they had lacked an earl for leader
        so long a while; the Lord endowed him,
        the Wielder of Wonder, with world's renown.
        """.strip()
        err = processutils.ProcessExecutionError(stdout=stdout)
        print(six.text_type(err))
        self.assertTrue('people-kings' in six.text_type(err))

    def test_with_stderr(self):
        stderr = 'Cottonian library'
        err = processutils.ProcessExecutionError(stderr=stderr)
        self.assertTrue(stderr in six.text_type(err))

    def test_retry_on_failure(self):
        fd, tmpfilename = tempfile.mkstemp()
        _, tmpfilename2 = tempfile.mkstemp()
        try:
            fp = os.fdopen(fd, 'w+')
            fp.write('''#!/bin/sh
# If stdin fails to get passed during one of the runs, make a note.
if ! grep -q foo
then
    echo 'failure' > "$1"
fi
# If stdin has failed to get passed during this or a previous run, exit early.
if grep failure "$1"
then
    exit 1
fi
runs="$(cat $1)"
if [ -z "$runs" ]
then
    runs=0
fi
runs=$(($runs + 1))
echo $runs > "$1"
exit 1
''')
            fp.close()
            os.chmod(tmpfilename, 0o755)
            self.assertRaises(processutils.ProcessExecutionError,
                              processutils.execute,
                              tmpfilename, tmpfilename2, attempts=10,
                              process_input=b'foo',
                              delay_on_retry=False)
            fp = open(tmpfilename2, 'r')
            runs = fp.read()
            fp.close()
            self.assertNotEqual(runs.strip(), 'failure', 'stdin did not '
                                                         'always get passed '
                                                         'correctly')
            runs = int(runs.strip())
            self.assertEqual(runs, 10, 'Ran %d times instead of 10.' % (runs,))
        finally:
            os.unlink(tmpfilename)
            os.unlink(tmpfilename2)

    def test_unknown_kwargs_raises_error(self):
        self.assertRaises(processutils.UnknownArgumentError,
                          processutils.execute,
                          '/usr/bin/env', 'true',
                          this_is_not_a_valid_kwarg=True)

    def test_check_exit_code_boolean(self):
        processutils.execute('/usr/bin/env', 'false', check_exit_code=False)
        self.assertRaises(processutils.ProcessExecutionError,
                          processutils.execute,
                          '/usr/bin/env', 'false', check_exit_code=True)

    def test_check_cwd(self):
        tmpdir = tempfile.mkdtemp()
        out, err = processutils.execute('/usr/bin/env',
                                        'sh', '-c', 'pwd',
                                        cwd=tmpdir)
        self.assertIn(tmpdir, out)

    def test_check_exit_code_list(self):
        processutils.execute('/usr/bin/env', 'sh', '-c', 'exit 101',
                             check_exit_code=(101, 102))
        processutils.execute('/usr/bin/env', 'sh', '-c', 'exit 102',
                             check_exit_code=(101, 102))
        self.assertRaises(processutils.ProcessExecutionError,
                          processutils.execute,
                          '/usr/bin/env', 'sh', '-c', 'exit 103',
                          check_exit_code=(101, 102))
        self.assertRaises(processutils.ProcessExecutionError,
                          processutils.execute,
                          '/usr/bin/env', 'sh', '-c', 'exit 0',
                          check_exit_code=(101, 102))

    def test_no_retry_on_success(self):
        fd, tmpfilename = tempfile.mkstemp()
        _, tmpfilename2 = tempfile.mkstemp()
        try:
            fp = os.fdopen(fd, 'w+')
            fp.write("""#!/bin/sh
# If we've already run, bail out.
grep -q foo "$1" && exit 1
# Mark that we've run before.
echo foo > "$1"
# Check that stdin gets passed correctly.
grep foo
""")
            fp.close()
            os.chmod(tmpfilename, 0o755)
            processutils.execute(tmpfilename,
                                 tmpfilename2,
                                 process_input=b'foo',
                                 attempts=2)
        finally:
            os.unlink(tmpfilename)
            os.unlink(tmpfilename2)

    # This test and the one below ensures that when communicate raises
    # an OSError, we do the right thing(s)
    def test_exception_on_communicate_error(self):
        mock = self.useFixture(mockpatch.Patch(
            'subprocess.Popen.communicate',
            side_effect=OSError(errno.EAGAIN, 'fake-test')))

        self.assertRaises(OSError,
                          processutils.execute,
                          '/usr/bin/env',
                          'false',
                          check_exit_code=False)

        self.assertEqual(1, mock.mock.call_count)

    def test_retry_on_communicate_error(self):
        mock = self.useFixture(mockpatch.Patch(
            'subprocess.Popen.communicate',
            side_effect=OSError(errno.EAGAIN, 'fake-test')))

        self.assertRaises(OSError,
                          processutils.execute,
                          '/usr/bin/env',
                          'false',
                          check_exit_code=False,
                          attempts=5)

        self.assertEqual(5, mock.mock.call_count)

    def _test_and_check_logging_communicate_errors(self, log_errors=None,
                                                   attempts=None):
        mock = self.useFixture(mockpatch.Patch(
            'subprocess.Popen.communicate',
            side_effect=OSError(errno.EAGAIN, 'fake-test')))

        fixture = self.useFixture(fixtures.FakeLogger(level=logging.DEBUG))
        kwargs = {}

        if log_errors:
            kwargs.update({"log_errors": log_errors})

        if attempts:
            kwargs.update({"attempts": attempts})

        self.assertRaises(OSError,
                          processutils.execute,
                          '/usr/bin/env',
                          'false',
                          **kwargs)

        self.assertEqual(attempts if attempts else 1, mock.mock.call_count)
        self.assertIn('Got an OSError', fixture.output)
        self.assertIn('errno: %d' % errno.EAGAIN, fixture.output)
        self.assertIn("'/usr/bin/env false'", fixture.output)

    def test_logging_on_communicate_error_1(self):
        self._test_and_check_logging_communicate_errors(
            log_errors=processutils.LOG_FINAL_ERROR,
            attempts=None)

    def test_logging_on_communicate_error_2(self):
        self._test_and_check_logging_communicate_errors(
            log_errors=processutils.LOG_FINAL_ERROR,
            attempts=1)

    def test_logging_on_communicate_error_3(self):
        self._test_and_check_logging_communicate_errors(
            log_errors=processutils.LOG_FINAL_ERROR,
            attempts=5)

    def test_logging_on_communicate_error_4(self):
        self._test_and_check_logging_communicate_errors(
            log_errors=processutils.LOG_ALL_ERRORS,
            attempts=None)

    def test_logging_on_communicate_error_5(self):
        self._test_and_check_logging_communicate_errors(
            log_errors=processutils.LOG_ALL_ERRORS,
            attempts=1)

    def test_logging_on_communicate_error_6(self):
        self._test_and_check_logging_communicate_errors(
            log_errors=processutils.LOG_ALL_ERRORS,
            attempts=5)

    def test_with_env_variables(self):
        env_vars = {'SUPER_UNIQUE_VAR': 'The answer is 42'}

        out, err = processutils.execute('/usr/bin/env', env_variables=env_vars)
        self.assertIsInstance(out, str)
        self.assertIsInstance(err, str)

        self.assertIn('SUPER_UNIQUE_VAR=The answer is 42', out)

    def test_binary(self):
        env_vars = {'SUPER_UNIQUE_VAR': 'The answer is 42'}

        out, err = processutils.execute('/usr/bin/env',
                                        env_variables=env_vars,
                                        binary=True)
        self.assertIsInstance(out, bytes)
        self.assertIsInstance(err, bytes)

        self.assertIn(b'SUPER_UNIQUE_VAR=The answer is 42', out)

    def test_exception_and_masking(self):
        tmpfilename = self.create_tempfiles(
            [["test_exceptions_and_masking",
              TEST_EXCEPTION_AND_MASKING_SCRIPT]], ext='bash')[0]

        os.chmod(tmpfilename, (stat.S_IRWXU |
                               stat.S_IRGRP |
                               stat.S_IXGRP |
                               stat.S_IROTH |
                               stat.S_IXOTH))

        err = self.assertRaises(processutils.ProcessExecutionError,
                                processutils.execute,
                                tmpfilename, 'password="secret"',
                                'something')

        self.assertEqual(38, err.exit_code)
        self.assertIsInstance(err.stdout, six.text_type)
        self.assertIsInstance(err.stderr, six.text_type)
        self.assertIn('onstdout --password="***"', err.stdout)
        self.assertIn('onstderr --password="***"', err.stderr)
        self.assertEqual(err.cmd, ' '.join([tmpfilename,
                                            'password="***"',
                                            'something']))
        self.assertNotIn('secret', str(err))

    def execute_undecodable_bytes(self, out_bytes, err_bytes,
                                  exitcode=0, binary=False):
        if six.PY3:
            code = ';'.join(('import sys',
                             'sys.stdout.buffer.write(%a)' % out_bytes,
                             'sys.stdout.flush()',
                             'sys.stderr.buffer.write(%a)' % err_bytes,
                             'sys.stderr.flush()',
                             'sys.exit(%s)' % exitcode))
        else:
            code = ';'.join(('import sys',
                             'sys.stdout.write(%r)' % out_bytes,
                             'sys.stdout.flush()',
                             'sys.stderr.write(%r)' % err_bytes,
                             'sys.stderr.flush()',
                             'sys.exit(%s)' % exitcode))

        return processutils.execute(sys.executable, '-c', code, binary=binary)

    def check_undecodable_bytes(self, binary):
        out_bytes = b'out: ' + UNDECODABLE_BYTES
        err_bytes = b'err: ' + UNDECODABLE_BYTES
        out, err = self.execute_undecodable_bytes(out_bytes, err_bytes,
                                                  binary=binary)
        if six.PY3 and not binary:
            self.assertEqual(out, os.fsdecode(out_bytes))
            self.assertEqual(err, os.fsdecode(err_bytes))
        else:
            self.assertEqual(out, out_bytes)
            self.assertEqual(err, err_bytes)

    def test_undecodable_bytes(self):
        self.check_undecodable_bytes(False)

    def test_binary_undecodable_bytes(self):
        self.check_undecodable_bytes(True)

    def check_undecodable_bytes_error(self, binary):
        out_bytes = b'out: password="secret1" ' + UNDECODABLE_BYTES
        err_bytes = b'err: password="secret2" ' + UNDECODABLE_BYTES
        exc = self.assertRaises(processutils.ProcessExecutionError,
                                self.execute_undecodable_bytes,
                                out_bytes, err_bytes, exitcode=1,
                                binary=binary)

        out = exc.stdout
        err = exc.stderr
        out_bytes = b'out: password="***" ' + UNDECODABLE_BYTES
        err_bytes = b'err: password="***" ' + UNDECODABLE_BYTES
        if six.PY3:
            # On Python 3, stdout and stderr attributes of
            # ProcessExecutionError must always be Unicode
            self.assertEqual(out, os.fsdecode(out_bytes))
            self.assertEqual(err, os.fsdecode(err_bytes))
        else:
            # On Python 2, stdout and stderr attributes of
            # ProcessExecutionError must always be bytes
            self.assertEqual(out, out_bytes)
            self.assertEqual(err, err_bytes)

    def test_undecodable_bytes_error(self):
        self.check_undecodable_bytes_error(False)

    def test_binary_undecodable_bytes_error(self):
        self.check_undecodable_bytes_error(True)


class ProcessExecutionErrorLoggingTest(test_base.BaseTestCase):
    def setUp(self):
        super(ProcessExecutionErrorLoggingTest, self).setUp()
        self.tmpfilename = self.create_tempfiles(
            [["process_execution_error_logging_test",
              PROCESS_EXECUTION_ERROR_LOGGING_TEST]],
            ext='bash')[0]

        os.chmod(self.tmpfilename, (stat.S_IRWXU | stat.S_IRGRP |
                                    stat.S_IXGRP | stat.S_IROTH |
                                    stat.S_IXOTH))

    def _test_and_check(self, log_errors=None, attempts=None):
        fixture = self.useFixture(fixtures.FakeLogger(level=logging.DEBUG))
        kwargs = {}

        if log_errors:
            kwargs.update({"log_errors": log_errors})

        if attempts:
            kwargs.update({"attempts": attempts})

        err = self.assertRaises(processutils.ProcessExecutionError,
                                processutils.execute,
                                self.tmpfilename,
                                **kwargs)

        self.assertEqual(41, err.exit_code)
        self.assertIn(self.tmpfilename, fixture.output)

    def test_with_invalid_log_errors(self):
        self.assertRaises(processutils.InvalidArgumentError,
                          processutils.execute,
                          self.tmpfilename,
                          log_errors='invalid')

    def test_with_log_errors_NONE(self):
        self._test_and_check(log_errors=None, attempts=None)

    def test_with_log_errors_final(self):
        self._test_and_check(log_errors=processutils.LOG_FINAL_ERROR,
                             attempts=None)

    def test_with_log_errors_all(self):
        self._test_and_check(log_errors=processutils.LOG_ALL_ERRORS,
                             attempts=None)

    def test_multiattempt_with_log_errors_NONE(self):
        self._test_and_check(log_errors=None, attempts=3)

    def test_multiattempt_with_log_errors_final(self):
        self._test_and_check(log_errors=processutils.LOG_FINAL_ERROR,
                             attempts=3)

    def test_multiattempt_with_log_errors_all(self):
        self._test_and_check(log_errors=processutils.LOG_ALL_ERRORS,
                             attempts=3)


def fake_execute(*cmd, **kwargs):
    return 'stdout', 'stderr'


def fake_execute_raises(*cmd, **kwargs):
    raise processutils.ProcessExecutionError(exit_code=42,
                                             stdout='stdout',
                                             stderr='stderr',
                                             cmd=['this', 'is', 'a',
                                                  'command'])


class TryCmdTestCase(test_base.BaseTestCase):
    def test_keep_warnings(self):
        self.useFixture(fixtures.MonkeyPatch(
            'oslo_concurrency.processutils.execute', fake_execute))
        o, e = processutils.trycmd('this is a command'.split(' '))
        self.assertNotEqual('', o)
        self.assertNotEqual('', e)

    def test_keep_warnings_from_raise(self):
        self.useFixture(fixtures.MonkeyPatch(
            'oslo_concurrency.processutils.execute', fake_execute_raises))
        o, e = processutils.trycmd('this is a command'.split(' '),
                                   discard_warnings=True)
        self.assertIsNotNone(o)
        self.assertNotEqual('', e)

    def test_discard_warnings(self):
        self.useFixture(fixtures.MonkeyPatch(
            'oslo_concurrency.processutils.execute', fake_execute))
        o, e = processutils.trycmd('this is a command'.split(' '),
                                   discard_warnings=True)
        self.assertIsNotNone(o)
        self.assertEqual('', e)


class FakeSshChannel(object):
    def __init__(self, rc):
        self.rc = rc

    def recv_exit_status(self):
        return self.rc


class FakeSshStream(six.BytesIO):
    def setup_channel(self, rc):
        self.channel = FakeSshChannel(rc)


class FakeSshConnection(object):
    def __init__(self, rc, out=b'stdout', err=b'stderr'):
        self.rc = rc
        self.out = out
        self.err = err

    def exec_command(self, cmd):
        stdout = FakeSshStream(self.out)
        stdout.setup_channel(self.rc)
        return (six.BytesIO(),
                stdout,
                six.BytesIO(self.err))


class SshExecuteTestCase(test_base.BaseTestCase):
    def test_invalid_addl_env(self):
        self.assertRaises(processutils.InvalidArgumentError,
                          processutils.ssh_execute,
                          None, 'ls', addl_env='important')

    def test_invalid_process_input(self):
        self.assertRaises(processutils.InvalidArgumentError,
                          processutils.ssh_execute,
                          None, 'ls', process_input='important')

    def test_works(self):
        out, err = processutils.ssh_execute(FakeSshConnection(0), 'ls')
        self.assertEqual('stdout', out)
        self.assertEqual('stderr', err)
        self.assertIsInstance(out, six.text_type)
        self.assertIsInstance(err, six.text_type)

    def test_binary(self):
        o, e = processutils.ssh_execute(FakeSshConnection(0), 'ls',
                                        binary=True)
        self.assertEqual(b'stdout', o)
        self.assertEqual(b'stderr', e)
        self.assertIsInstance(o, bytes)
        self.assertIsInstance(e, bytes)

    def check_undecodable_bytes(self, binary):
        out_bytes = b'out: ' + UNDECODABLE_BYTES
        err_bytes = b'err: ' + UNDECODABLE_BYTES
        conn = FakeSshConnection(0, out=out_bytes, err=err_bytes)

        out, err = processutils.ssh_execute(conn, 'ls', binary=binary)
        if six.PY3 and not binary:
            self.assertEqual(out, os.fsdecode(out_bytes))
            self.assertEqual(err, os.fsdecode(err_bytes))
        else:
            self.assertEqual(out, out_bytes)
            self.assertEqual(err, err_bytes)

    def test_undecodable_bytes(self):
        self.check_undecodable_bytes(False)

    def test_binary_undecodable_bytes(self):
        self.check_undecodable_bytes(True)

    def check_undecodable_bytes_error(self, binary):
        out_bytes = b'out: password="secret1" ' + UNDECODABLE_BYTES
        err_bytes = b'err: password="secret2" ' + UNDECODABLE_BYTES
        conn = FakeSshConnection(1, out=out_bytes, err=err_bytes)

        out_bytes = b'out: password="***" ' + UNDECODABLE_BYTES
        err_bytes = b'err: password="***" ' + UNDECODABLE_BYTES

        exc = self.assertRaises(processutils.ProcessExecutionError,
                                processutils.ssh_execute,
                                conn, 'ls',
                                binary=binary, check_exit_code=True)

        out = exc.stdout
        err = exc.stderr
        if six.PY3:
            # On Python 3, stdout and stderr attributes of
            # ProcessExecutionError must always be Unicode
            self.assertEqual(out, os.fsdecode(out_bytes))
            self.assertEqual(err, os.fsdecode(err_bytes))
        else:
            # On Python 2, stdout and stderr attributes of
            # ProcessExecutionError must always be bytes
            self.assertEqual(out, out_bytes)
            self.assertEqual(err, err_bytes)

    def test_undecodable_bytes_error(self):
        self.check_undecodable_bytes_error(False)

    def test_binary_undecodable_bytes_error(self):
        self.check_undecodable_bytes_error(True)

    def test_fails(self):
        self.assertRaises(processutils.ProcessExecutionError,
                          processutils.ssh_execute, FakeSshConnection(1), 'ls')

    def _test_compromising_ssh(self, rc, check):
        fixture = self.useFixture(fixtures.FakeLogger(level=logging.DEBUG))
        fake_stdin = six.BytesIO()

        fake_stdout = mock.Mock()
        fake_stdout.channel.recv_exit_status.return_value = rc
        fake_stdout.read.return_value = b'password="secret"'

        fake_stderr = six.BytesIO(b'password="foobar"')

        command = 'ls --password="bar"'

        connection = mock.Mock()
        connection.exec_command.return_value = (fake_stdin, fake_stdout,
                                                fake_stderr)

        if check and rc != -1 and rc != 0:
            err = self.assertRaises(processutils.ProcessExecutionError,
                                    processutils.ssh_execute,
                                    connection, command,
                                    check_exit_code=check)

            self.assertEqual(rc, err.exit_code)
            self.assertEqual(err.stdout, 'password="***"')
            self.assertEqual(err.stderr, 'password="***"')
            self.assertEqual(err.cmd, 'ls --password="***"')
            self.assertNotIn('secret', str(err))
            self.assertNotIn('foobar', str(err))
        else:
            o, e = processutils.ssh_execute(connection, command,
                                            check_exit_code=check)
            self.assertEqual('password="***"', o)
            self.assertEqual('password="***"', e)
            self.assertIn('password="***"', fixture.output)
            self.assertNotIn('bar', fixture.output)

    def test_compromising_ssh1(self):
        self._test_compromising_ssh(rc=-1, check=True)

    def test_compromising_ssh2(self):
        self._test_compromising_ssh(rc=0, check=True)

    def test_compromising_ssh3(self):
        self._test_compromising_ssh(rc=1, check=True)

    def test_compromising_ssh4(self):
        self._test_compromising_ssh(rc=1, check=False)

    def test_compromising_ssh5(self):
        self._test_compromising_ssh(rc=0, check=False)

    def test_compromising_ssh6(self):
        self._test_compromising_ssh(rc=-1, check=False)
