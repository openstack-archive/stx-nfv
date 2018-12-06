#
# Copyright
#
# SPDX-License-Identifier: Apache-2.0
#
import mock
import os

from nfv_client import shell

from . import testcase  # noqa: H304


class TestNFVClientShell(testcase.NFVTestCase):

    def setUp(self):
        super(TestNFVClientShell, self).setUp()

    def tearDown(self):
        super(TestNFVClientShell, self).tearDown()

    # -- Failure cases --
    # Each failure case will :
    # - invoke _print_message (as part of exit)
    # - invoke print_usage (to indicate proper arguments)
    # - raise a SystemExit exception
    @mock.patch('argparse.ArgumentParser._print_message')
    @mock.patch('argparse.ArgumentParser.print_usage')
    def _test_shell_bad_or_empty_args(self,
                                      mock_usage=None,
                                      mock_message=None,
                                      shell_args=None):
        self.assertRaises(SystemExit, shell.process_main, shell_args)
        mock_usage.assert_called_once()
        mock_message.assert_called_once()

    # invalid arguments causes process_main to exit
    def test_shell_bad_args(self):
        shell_args = ['invalid-arg', ]
        self._test_shell_bad_or_empty_args(shell_args=shell_args)

    # empty arguments causes process_main to exit
    def test_shell_no_args(self):
        shell_args = []
        self._test_shell_bad_or_empty_args(shell_args=shell_args)

    # upgrade-strategy expects additional arguments
    def test_shell_upgrade_strategy_incomplete_args(self):
        shell_args = ['upgrade-strategy', ]
        self._test_shell_bad_or_empty_args(shell_args=shell_args)

    # patch-strategy expects additional arguments
    def test_shell_patch_strategy_incomplete_args(self):
        shell_args = ['patch-strategy', ]
        self._test_shell_bad_or_empty_args(shell_args=shell_args)

    # --- Help Cases ----
    # -h will print_help and SystemExit
    @mock.patch('argparse.ArgumentParser.print_help')
    def _test_shell_help(self, mock_help=None, shell_args=None):
        self.assertRaises(SystemExit, shell.process_main, shell_args)
        mock_help.assert_called_once()

    def test_shell_upgrade_strategy_help(self):
        shell_args = ['upgrade-strategy', '-h', ]
        self._test_shell_help(shell_args=shell_args)

    def test_shell_patch_strategy_help(self):
        shell_args = ['patch-strategy', '-h', ]
        self._test_shell_help(shell_args=shell_args)

    # -- Show commands --
    # Both patch-strategy and upgrade-strategy use the same underlying
    # sw_update class, but with different modes

    # Test the show commands are not invoked when env values missing
    @mock.patch('nfv_client.sw_update.show_strategy')
    def _test_shell_show_missing_env(self, mock_show=None, shell_args=None):
        shell.process_main(shell_args)
        mock_show.assert_not_called()

    def test_shell_upgrade_strategy_show_missing_env(self):
        shell_args = ['upgrade-strategy', 'show', ]
        self._test_shell_show_missing_env(shell_args=shell_args)

    def test_shell_patch_strategy_show_missing_env(self):
        shell_args = ['patch-strategy', 'show', ]
        self._test_shell_show_missing_env(shell_args=shell_args)

    # Test the show commands are invoked when env values detected
    @mock.patch.dict(os.environ,
                     {'OS_AUTH_URL': 'FAKE_OS_AUTH_URL',
                      'OS_PROJECT_NAME': 'FAKE_OS_PROJECT_NAME',
                      'OS_PROJECT_DOMAIN_NAME': 'FAKE_OS_PROJECT_DOMAIN_NAME',
                      'OS_USERNAME': 'FAKE_OS_USERNAME',
                      'OS_PASSWORD': 'FAKE_OS_PASSWORD',
                      'OS_USER_DOMAIN_NAME': 'FAKE_OS_USER_DOMAIN_NAME',
                      'OS_REGION_NAME': 'FAKE_OS_REGION_NAME',
                      'OS_INTERFACE': 'FAKE_OS_INTERFACE'
                     })
    @mock.patch('nfv_client.sw_update.show_strategy')
    def _test_shell_show(self, mock_show=None, shell_args=None):
        shell.process_main(shell_args)
        mock_show.assert_called_once()

    def test_shell_upgrade_strategy_show(self):
        shell_args = ['upgrade-strategy', 'show', ]
        self._test_shell_show(shell_args=shell_args)

    def test_shell_patch_strategy_show(self):
        shell_args = ['patch-strategy', 'show', ]
        self._test_shell_show(shell_args=shell_args)
