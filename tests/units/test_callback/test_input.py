from unittest.mock import patch

from ansible_monkeyble.plugins.callback.monkeyble_callback import MonkeybleException
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

    def test_check_input_ok(self):
        ansible_task_args = {
            "msg": "value1"
        }

        expected = {'monkeyble_passed_test': [{'test_name': 'assert_equal',
                                               'tested_value': 'value1',
                                               'expected': 'value1'}],
                    'monkeyble_failed_test': []}
        self.test_callback._check_input(self.test_input_list, ansible_task_args)
        self.assertDictEqual(self.test_callback._last_check_input_result, expected)

    def test_check_input_fail(self):
        # test fail test
        ansible_task_args = {
            "msg": "another_value"
        }
        expected = {'monkeyble_passed_test': [],
                    'monkeyble_failed_test': [{'test_name': 'assert_equal',
                                               'tested_value': 'another_value',
                                               'expected': 'value1'}]}

        self.test_callback._check_input(self.test_input_list, ansible_task_args)
        self.assertDictEqual(self.test_callback._last_check_input_result, expected)
