import unittest
from unittest import mock
from unittest.mock import patch

from ansible_monkeyble.plugins.callback.monkeyble_callback import CallbackModule as MonkeybleCallbackModule


class TestMonkeybleCallback(unittest.TestCase):

    def test__compare_boolean_to_config(self):
        test_callback = MonkeybleCallbackModule()
        task_name = "test_task"
        config_flag_name = "a_boolean_flag"

        # Test when actual value and config value are true
        task_config = {
            "task": "test_task",
            "a_boolean_flag": "true"
        }
        actual_state = True
        self.assertTrue(test_callback._compare_boolean_to_config(task_name, config_flag_name,
                                                                 task_config, actual_state))
        task_config = {
            "task": "test_task",
            "a_boolean_flag": True
        }
        self.assertTrue(test_callback._compare_boolean_to_config(task_name, config_flag_name,
                                                                 task_config, actual_state))

        # Test config is False and actual state is False
        actual_state = False
        task_config = {
            "task": "test_task",
            "a_boolean_flag": False
        }
        self.assertTrue(test_callback._compare_boolean_to_config(task_name, config_flag_name,
                                                                 task_config, actual_state))

        # Test config is True and actual state is False
        actual_state = False
        task_config = {
            "task": "test_task",
            "a_boolean_flag": True
        }
        with mock.patch('ansible_monkeyble.plugins.callback.monkeyble_callback.CallbackModule.exit_playbook') as mock_exit_playbook:
            test_callback._compare_boolean_to_config(task_name, config_flag_name, task_config, actual_state)
            mock_exit_playbook.assert_called()

        # Test config is False and actual state is True
        actual_state = True
        task_config = {
            "task": "test_task",
            "a_boolean_flag": False
        }
        with mock.patch('ansible_monkeyble.plugins.callback.monkeyble_callback.CallbackModule.exit_playbook') as mock_exit_playbook:
            test_callback._compare_boolean_to_config(task_name, config_flag_name, task_config, actual_state)
            mock_exit_playbook.assert_called()

    def _get_testing_callback(self):
        test_callback = MonkeybleCallbackModule()
        test_callback._last_task_name = "test_task"
        test_callback._last_task_config = {
            "task": "test_task",
            "test_output": [
                {"assert_equal": {
                    "result_key": "result.key1",
                    "expected": "value1"
                }}
            ]
        }
        return test_callback

    def test_check_output_test_ok(self):
        test_callback = self._get_testing_callback()
        task_result = {
            "key1": "value1"
        }
        expected = {'task': 'test_task', 'monkeyble_passed_test': [{'test_name': 'assert_equal',
                                                                    'tested_value': 'value1',
                                                                    'expected': 'value1'}],
                    'monkeyble_failed_test': []}

        test_callback.check_output(task_result)
        self.assertDictEqual(test_callback._last_check_output_result, expected)

    def test_check_output_test_fail(self):
        test_callback = self._get_testing_callback()
        task_result = {
            "key1": "value2"
        }
        with mock.patch('ansible_monkeyble.plugins.callback.monkeyble_callback.CallbackModule.exit_playbook') as mock_exit_playbook:
            test_callback.check_output(task_result)
            mock_exit_playbook.assert_called()

    def test_check_output_invalid_key_path(self):
        test_callback = self._get_testing_callback()
        # test with an invalid key path
        test_callback._last_task_config = {
            "task": "test_task",
            "test_output": [
                {"assert_equal": {
                    "result_key": "result.does_not_exist",
                    "expected": "value1"
                }}
            ]
        }
        task_result = {
            "key1": "value2"
        }
        with mock.patch('ansible_monkeyble.plugins.callback.monkeyble_callback.CallbackModule.exit_playbook') as mock_exit_playbook:
            test_callback.check_output(task_result)
            mock_exit_playbook.assert_called()

    @patch('ansible_monkeyble.plugins.callback.monkeyble_callback.CallbackModule.exit_playbook')
    def test_check_if_task_should_have_failed_continue_on_error_errors(self, mock_exit_playbook):
        test_callback = self._get_testing_callback()
        test_callback._last_task_config = {
            "task": "test_task",
            "should_failed": True
        }
        test_callback._last_task_ignore_errors = True
        test_callback.check_if_task_should_have_failed(task_has_actually_failed=True)
        mock_exit_playbook.assert_not_called()

    @patch('ansible_monkeyble.plugins.callback.monkeyble_callback.CallbackModule.exit_playbook')
    def test_check_if_task_should_have_failed_exit_zero_when_not_ignoring_errors(self, mock_exit_playbook):
        test_callback = self._get_testing_callback()
        test_callback._last_task_config = {
            "task": "test_task",
            "should_failed": True
        }
        test_callback._last_task_ignore_errors = False
        test_callback.check_if_task_should_have_failed(task_has_actually_failed=True)
        mock_exit_playbook.assert_called()
