# Copyright 2022 Hewlett Packard Enterprise Development LP
from unittest.mock import patch

from plugins.callback.monkeyble_callback import MonkeybleException
from tests.units.test_callback.base_test_callback import BaseTestMonkeybleCallback


class TestMonkeybleCallbackOutput(BaseTestMonkeybleCallback):

    def setUp(self) -> None:
        super(TestMonkeybleCallbackOutput, self).setUp()

    def test_check_output_test_ok(self):
        task_result = {
            "key1": "value1"
        }
        expected = {'task': 'test_task', 'monkeyble_passed_test': [{'test_name': 'assert_equal',
                                                                    'tested_value': 'value1',
                                                                    'expected': 'value1'}],
                    'monkeyble_failed_test': []}

        self.test_callback.test_output(task_result)
        self.assertDictEqual(self.test_callback._last_check_output_result, expected)

    def test_check_output_test_ok_null_value(self):
        task_result = {
            "key1": None,
        }
        self.test_callback._last_task_name = "test_ok_null_value"
        self.test_callback._last_task_config = {
            "task": "test_ok_null_value",
            "test_output": [
                {
                    "assert_is_none": {
                        "result_key": "result.key1",
                    }
                },
            ]
        }
        expected = {'task': 'test_ok_null_value', 'monkeyble_passed_test': [{'test_name': 'assert_is_none',
                                                                             'tested_value': None,
                                                                             'expected': None}],
                    'monkeyble_failed_test': []}

        self.test_callback.test_output(task_result)
        self.assertDictEqual(self.test_callback._last_check_output_result, expected)

    def test_check_output_test_ok_empty_value(self):
        task_result = {
            "key2": ""
        }
        self.test_callback._last_task_config = {
            "task": "test_task",
            "test_output": [
                {
                    "assert_equal": {
                        "result_key": "result.key2",
                        "expected": ""
                    }
                }
            ]
        }
        expected = {'task': 'test_task', 'monkeyble_passed_test': [{'test_name': 'assert_equal',
                                                                    'tested_value': '',
                                                                    'expected': ''}
                                                                   ],
                    'monkeyble_failed_test': []}

        self.test_callback.test_output(task_result)
        self.assertDictEqual(self.test_callback._last_check_output_result, expected)

    @patch('sys.exit')
    def test_check_output_test_fail(self, mock_exit):
        task_result = {
            "key1": "value2"
        }
        with self.assertRaises(MonkeybleException):
            self.test_callback.test_output(task_result)
            mock_exit.assert_called()

    @patch('sys.exit')
    def test_check_output_invalid_key_path(self, mock_exit):
        # test with an invalid key path
        self.test_callback._last_task_config = {
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
        with self.assertRaises(MonkeybleException):
            self.test_callback.test_output(task_result)
            mock_exit.assert_called()
