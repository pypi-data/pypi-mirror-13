# (c) Copyright 2015 Hewlett Packard Enterprise Development LP
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

import mock
import paramiko
import unittest

import test_HPELeftHandClient_base
from hpelefthandclient import exceptions
from hpelefthandclient import ssh

# Python 3+ override
try:
    basestring
except NameError:
    basestring = str

user = "u"
password = "p"
ip = "10.10.22.241"
api_url = "http://10.10.22.241:8008/api/v1"


class HPELeftHandClientMockSSHTestCase(test_HPELeftHandClient_base
                                       .HPELeftHandClientBaseTestCase):

    def mock_paramiko(self, known_hosts_file, missing_key_policy):
        """Verify that these params get into paramiko."""

        mock_lhk = mock.Mock()
        mock_lshk = mock.Mock()
        mock_smhkp = mock.Mock()
        mock_smhkp.side_effect = Exception("Let's end this here")

        with mock.patch('paramiko.client.SSHClient.load_system_host_keys',
                        mock_lshk, create=True):
            with mock.patch('paramiko.client.SSHClient.load_host_keys',
                            mock_lhk, create=True):
                with mock.patch('paramiko.client.SSHClient.'
                                'set_missing_host_key_policy',
                                mock_smhkp, create=True):
                    try:
                        self.cl.setSSHOptions(
                            ip, user, password,
                            known_hosts_file=known_hosts_file,
                            missing_key_policy=missing_key_policy)
                    except paramiko.SSHException as e:
                        if 'Invalid missing_key_policy' in str(e):
                            raise e
                    except Exception:
                        pass

                    if known_hosts_file is None:
                        mock_lhk.assert_not_called()
                        mock_lshk.assert_called_with()
                    else:
                        mock_lhk.assert_called_with(known_hosts_file)
                        mock_lshk.assert_not_called()

                    actual = mock_smhkp.call_args[0][0].__class__.__name__
                    if missing_key_policy is None:
                        # If missing, it should be called with our
                        # default which is an AutoAddPolicy
                        expected = paramiko.AutoAddPolicy().__class__.__name__
                    elif isinstance(missing_key_policy, basestring):
                        expected = missing_key_policy
                    else:
                        expected = missing_key_policy.__class__.__name__
                    self.assertEqual(actual, expected)

    def do_mock_create_ssh(self, known_hosts_file, missing_key_policy):
        """Verify that params are getting forwarded to _create_ssh()."""

        mock_ssh = mock.Mock()
        path = 'hpelefthandclient.ssh.HPELeftHandSSHClient._create_ssh'
        with mock.patch(path, mock_ssh, create=True):

            self.cl.setSSHOptions(ip, user, password,
                                  known_hosts_file=known_hosts_file,
                                  missing_key_policy=missing_key_policy)

            mock_ssh.assert_called_with(missing_key_policy=missing_key_policy,
                                        known_hosts_file=known_hosts_file)

        # Create a mocked ssh object for the client so that it can be
        # "closed" during a logout.
        self.cl.ssh = mock.MagicMock()

    @mock.patch('hpelefthandclient.ssh.HPELeftHandSSHClient')
    def do_mock_ssh(self, known_hosts_file, missing_key_policy,
                    mock_ssh_client):
        """Verify that params are getting forwarded to HPELeftHandSSHClient."""

        self.cl.setSSHOptions(ip, user, password,
                              known_hosts_file=known_hosts_file,
                              missing_key_policy=missing_key_policy)

        mock_ssh_client.assert_called_with(
            ip, user, password, 16022, None, None,
            missing_key_policy=missing_key_policy,
            known_hosts_file=known_hosts_file)

    def base(self, known_hosts_file, missing_key_policy):
        self.printHeader("%s : known_hosts_file=%s missing_key_policy=%s" %
                         (unittest.TestCase.id(self),
                          known_hosts_file, missing_key_policy))
        self.do_mock_ssh(known_hosts_file, missing_key_policy)
        self.do_mock_create_ssh(known_hosts_file, missing_key_policy)
        self.mock_paramiko(known_hosts_file, missing_key_policy)
        self.printFooter(unittest.TestCase.id(self))

    def test_auto_add_policy(self):
        known_hosts_file = "test_bogus_known_hosts_file"
        missing_key_policy = "AutoAddPolicy"
        self.base(known_hosts_file, missing_key_policy)

    def test_warning_policy(self):
        known_hosts_file = "test_bogus_known_hosts_file"
        missing_key_policy = "WarningPolicy"
        self.base(known_hosts_file, missing_key_policy)

    def test_reject_policy(self):
        known_hosts_file = "test_bogus_known_hosts_file"
        missing_key_policy = "RejectPolicy"
        self.base(known_hosts_file, missing_key_policy)

    def test_known_hosts_file_is_none(self):
        known_hosts_file = None
        missing_key_policy = paramiko.RejectPolicy()
        self.base(known_hosts_file, missing_key_policy)

    def test_both_settings_are_none(self):
        known_hosts_file = None
        missing_key_policy = None
        self.base(known_hosts_file, missing_key_policy)

    def test_bogus_missing_key_policy(self):
        known_hosts_file = None
        missing_key_policy = "bogus"
        self.assertRaises(paramiko.SSHException,
                          self.base,
                          known_hosts_file,
                          missing_key_policy)

    def test_create_ssh_except(self):
        """Make sure that SSH exceptions are not quietly eaten."""

        self.cl.setSSHOptions(ip,
                              user,
                              password,
                              known_hosts_file=None,
                              missing_key_policy=paramiko.AutoAddPolicy)

        self.cl.ssh.ssh = mock.Mock()
        self.cl.ssh.ssh.invoke_shell.side_effect = Exception('boom')

        cmd = ['fake']
        self.assertRaises(exceptions.SSHException, self.cl.ssh._run_ssh, cmd)

        self.cl.ssh.ssh.assert_has_calls(
            [
                mock.call.get_transport(),
                mock.call.get_transport().is_alive(),
                mock.call.invoke_shell(),
                mock.call.get_transport(),
                mock.call.get_transport().is_alive(),
            ]
        )

    def test_was_command_successful_true(self):
        cmd_out = ['',
                   'HP StoreVirtual LeftHand OS Command Line Interface',
                   '(C) Copyright 2007-2013',
                   '',
                   'RESPONSE',
                   ' result         0']
        ssh_client = ssh.HPELeftHandSSHClient('foo', 'bar', 'biz')
        out = ssh_client.was_command_successful(cmd_out)
        self.assertTrue(out)

    def test_was_command_successful_false(self):
        # Create our fake SSH client
        ssh_client = ssh.HPELeftHandSSHClient('foo', 'bar', 'biz')

        # Test invalid command output
        cmd_out = ['invalid']
        self.assertRaises(exceptions.SSHException,
                          ssh_client.was_command_successful,
                          cmd_out)

        # Test valid command output, but command failed
        cmd_out = ['',
                   'HP StoreVirtual LeftHand OS Command Line Interface',
                   '(C) Copyright 2007-2013',
                   '',
                   'RESPONSE',
                   ' result         8080878378']
        self.assertRaises(exceptions.SSHException,
                          ssh_client.was_command_successful,
                          cmd_out)
