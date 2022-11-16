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
            "should_failed": True
        }
        self.test_callback._last_task_ignore_errors = True
        self.test_callback.check_if_task_should_have_failed(task_has_actually_failed=True)
        mock_exit_playbook.assert_not_called()

    @patch('sys.exit')
    def test_check_if_task_should_have_failed_exit_zero_when_not_ignoring_errors(self, mock_exit_playbook):
        self.test_callback._last_task_config = {
            "task": "test_task",
            "should_failed": True
        }
        self.test_callback._last_task_ignore_errors = False
        with self.assertRaises(MonkeybleException):
            self.test_callback.check_if_task_should_have_failed(task_has_actually_failed=True)
            mock_exit_playbook.assert_called()
