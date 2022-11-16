# Copyright 2022 Hewlett Packard Enterprise Development LP
from unittest.mock import patch

from plugins.callback.monkeyble_callback import MonkeybleException
from tests.units.test_callback.base_test_callback import BaseTestMonkeybleCallback


class TestMonkeybleCallbackInput(BaseTestMonkeybleCallback):

    def setUp(self) -> None:
        super(TestMonkeybleCallbackInput, self).setUp()

        self.test_input_list = [{
            "assert_equal": {
                "arg_name": "msg",
                "expected": "value1"
            }
        }]
        self.test_callback._last_task_config["test_input"] = self.test_input_list

    def test_check_input_ok(self):
        self.ansible_task_test.args = {
            "msg": "value1"
        }

        expected = {'monkeyble_passed_test': [{'test_name': 'assert_equal',
                                               'tested_value': 'value1',
                                               'expected': 'value1'}],
                    'monkeyble_failed_test': []}
        self.test_callback.test_input(self.ansible_task_test)
        self.assertDictEqual(self.test_callback._last_check_input_result, expected)

    @patch('sys.exit')
    def test_check_input_fail(self, mock_exit):
        # test fail test
        self.ansible_task_test.args = {
            "msg": "another_value"
        }
        expected = {'monkeyble_passed_test': [],
                    'monkeyble_failed_test': [{'test_name': 'assert_equal',
                                               'tested_value': 'another_value',
                                               'expected': 'value1'}]}
        with self.assertRaises(MonkeybleException):
            self.test_callback.test_input(self.ansible_task_test)
            self.assertDictEqual(self.test_callback._last_check_input_result, expected)
            mock_exit.assert_called()
