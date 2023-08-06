#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# 

import mock
import unittest
from pyrcmd import SSH


class TestSSH(unittest.TestCase):
    def setUp(self):
        self.hostname = 'fake.marreta.org'
        self.username = 'foo'
        self.password = 'G1v3_M3_a_B33r'
        self.command = 'whoami'

    # test SSH()
    def test_ssh(self):
        SSH(self.hostname, self.username, self.password, timeout=30)
        self.assertRaises(Exception, SSH.__init__, "")

    # test the SSH.execute()
    @mock.patch('pyrcmd.SSH')
    @mock.patch('pyrcmd.SSH.execute')
    def test_ssh_execute(self, mock_ssh, mock_ssh_execute):
        mock_ssh.return_value = '<SSH object at 0x1024641d0>'
        mock_ssh_execute.return_value = {'return_code': 0, 'stderr': '',
                                         'stdout': self.username + '\n'}
        remote_server = SSH(self.hostname, self.username, self.password)
        remote_server.execute(self.command)
        self.assertEqual(
            mock_ssh_execute.return_value,
            {'return_code': 0, 'stderr': '', 'stdout': '{0}\n'
                .format(self.username)}
        )

    # testing exceptions
    #

    # exception DNSLookupFailure
    @mock.patch('pyrcmd.SSH')
    @mock.patch('pyrcmd.SSH.execute')
    def test_ssh_execute_dnsLookupfailure(self, mock_ssh, mock_ssh_execute):
        mock_ssh.return_value = '<SSH object at 0x1024641d0>'
        mock_ssh_execute.return_exception = "ValueError('DSNLookupFailure)"
        instance = SSH(self.hostname, self.username, self.password, timeout=30)
        self.assertRaises(Exception, instance.execute(self.command))

    # exception AuthFailure
    @mock.patch('pyrcmd.SSH')
    @mock.patch('pyrcmd.SSH.execute')
    def test_ssh_execute_authfailure(self, mock_ssh, mock_ssh_execute):
        mock_ssh.return_value = '<SSH object at 0x1024641d0>'
        mock_ssh_execute.return_exception = "ValueError('AuthFailure)"
        instance = SSH(self.hostname, self.username, self.password, timeout=30)
        self.assertRaises(Exception, instance.execute(self.command))

    # exception BadHostKey
    @mock.patch('pyrcmd.SSH')
    @mock.patch('pyrcmd.SSH.execute')
    def test_ssh_execute_badhostkey(self, mock_ssh, mock_ssh_execute):
        mock_ssh.return_value = '<SSH object at 0x1024641d0>'
        mock_ssh_execute.return_exception = "ValueError('BadHostKey)"
        instance = SSH(self.hostname, self.username, self.password, timeout=30)
        self.assertRaises(Exception, instance.execute(self.command))

    # exception SshProtocol
    @mock.patch('pyrcmd.SSH')
    @mock.patch('pyrcmd.SSH.execute')
    def test_ssh_execute_sshprotocol(self, mock_ssh, mock_ssh_execute):
        mock_ssh.return_value = '<SSH object at 0x1024641d0>'
        mock_ssh_execute.return_exception = "ValueError('SshProtocol)"
        instance = SSH(self.hostname, self.username, self.password, timeout=30)
        self.assertRaises(Exception, instance.execute(self.command))

    # exception TimeOut
    @mock.patch('pyrcmd.SSH')
    @mock.patch('pyrcmd.SSH.execute')
    def test_ssh_execute_timeout(self, mock_ssh, mock_ssh_execute):
        mock_ssh.return_value = '<SSH object at 0x1024641d0>'
        mock_ssh_execute.return_exception = "ValueError('TimeOut)"
        instance = SSH(self.hostname, self.username, self.password, timeout=30)
        self.assertRaises(Exception, instance.execute(self.command))


if __name__ == '__main__':
    unittest.main()
