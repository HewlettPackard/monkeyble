# Copyright 2022 Hewlett Packard Enterprise Development LP
from unittest.mock import patch

from plugins.callback.monkeyble_callback import MonkeybleException
from tests.units.test_callback.base_test_callback import BaseTestMonkeybleCallback


class TestMonkeybleCallbackState(BaseTestMonkeybleCallback):

    def setUp(self) -> None:
        super(TestMonkeybleCallbackState, self).setUp()

    @patch('sys.exit')
    def test_check_if_task_should_have_failed_continue_on_error_errors(self, mock_exit_playbook):
        self.test_callback._last_task_config = {
            "task": "test_task",
            "should_fail": True
        }
        self.test_callback._last_task_ignore_errors = True
        self.test_callback.check_if_task_should_have_failed(task_has_actually_failed=True)
        mock_exit_playbook.assert_not_called()

    @patch('sys.exit')
    def test_check_if_task_should_have_failed_exit_zero_when_not_ignoring_errors(self, mock_exit_playbook):
        self.test_callback._last_task_config = {
            "task": "test_task",
            "should_fail": True
        }
        self.test_callback._last_task_ignore_errors = False
        with self.assertRaises(MonkeybleException):
            self.test_callback.check_if_task_should_have_failed(task_has_actually_failed=True)
            mock_exit_playbook.assert_called()

    @patch('sys.exit')
    def test_check_if_task_should_have_failed_continue_on_rescue(self, mock_exit_playbook):
        self.test_callback._last_task_config = {
            "task": "test_task",
            "should_fail": True
        }
        self.test_callback.check_if_task_should_have_failed(task_has_actually_failed=True, has_rescue=True)
        mock_exit_playbook.assert_not_called()

    @patch('sys.exit')
    def test_check_if_task_should_not_have_failed(self, mock_exit_playbook):
        self.test_callback._last_task_config = {
            "task": "test_task",
            "should_fail": False
        }
        self.test_callback.check_if_task_should_have_failed(task_has_actually_failed=False)
        mock_exit_playbook.assert_not_called()

    @patch('sys.exit')
    def test_check_if_task_should_have_failed_but_succeeded(self, mock_exit_playbook):
        self.test_callback._last_task_config = {
            "task": "test_task",
            "should_fail": True
        }
        with self.assertRaises(MonkeybleException):
            self.test_callback.check_if_task_should_have_failed(task_has_actually_failed=False)

    @patch('sys.exit')
    def test_check_if_task_should_not_have_failed_but_did(self, mock_exit_playbook):
        self.test_callback._last_task_config = {
            "task": "test_task",
            "should_fail": False
        }
        with self.assertRaises(MonkeybleException):
            self.test_callback.check_if_task_should_have_failed(task_has_actually_failed=True)

    @patch('sys.exit')
    def test_check_if_task_failed_without_should_fail_configured(self, mock_exit_playbook):
        """When should_fail is not in config at all, a failing task should not raise"""
        self.test_callback._last_task_config = {
            "task": "test_task"
        }
        self.test_callback.check_if_task_should_have_failed(task_has_actually_failed=True)
        mock_exit_playbook.assert_not_called()
