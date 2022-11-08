import unittest
from unittest.mock import MagicMock

from ansible_monkeyble.plugins.strategy.monkeyble_linear import StrategyModule as MonkeybleStrategyModule, \
    MonkeybleTestFailed


class TestMonkeybleStrategy(unittest.TestCase):

    def setUp(self) -> None:
        tqm = MagicMock()
        self.test_strategy = MonkeybleStrategyModule(tqm)

        self.ansible_task_test = MagicMock()
        self.ansible_task_test.name = "test_task"
        self.ansible_task_test.action = "debug"
        self.ansible_task_test.args = {
            "msg": "my_message"
        }

    def test_check_input_ok(self):

        test_input_list = [{
            "assert_equal": {
                "arg_name": "msg",
                "expected": "value1"
            }
        }]
        ansible_task_args = {
            "msg": "value1"
        }

        expected = {'monkeyble_passed_test': [{'test_name': 'assert_equal',
                                               'tested_value': 'value1',
                                               'expected': 'value1'}],
                    'monkeyble_failed_test': []}
        self.test_strategy.check_input(test_input_list, ansible_task_args)
        self.assertDictEqual(self.test_strategy._last_check_input_result, expected)

        # test fail test
        ansible_task_args = {
            "msg": "another_value"
        }
        expected = {'monkeyble_passed_test': [],
                    'monkeyble_failed_test': [{'test_name': 'assert_equal',
                                               'tested_value': 'another_value',
                                               'expected': 'value1'}]}
        with self.assertRaises(MonkeybleTestFailed):
            self.test_strategy.check_input(test_input_list, ansible_task_args)
            self.assertDictEqual(self.test_strategy._last_check_input_result, expected)

    def test_mock_task_module(self):
        mock_config_test = {
            "config": {
                "monkeyble_module": {
                    "consider_changed": True,
                    "result_dict": {
                        "msg": "output_value"
                    }
                }
            }
        }

        update_ansible_task = self.test_strategy.mock_task_module(mock_config_test, self.ansible_task_test)
        self.assertEqual("test_task", update_ansible_task.name)
        self.assertEqual("debug", update_ansible_task.args["original_module_name"])
        self.assertTrue(update_ansible_task.args["consider_changed"])
        expected_result_dict = {
            "msg": "output_value"
        }
        self.assertDictEqual(expected_result_dict, update_ansible_task.args["result_dict"])
        expected_original_module_args = {
            "msg": "my_message"
        }
        self.assertDictEqual(expected_original_module_args, update_ansible_task.args["original_module_args"])

    def test_mock_task_module_default_config(self):
        mock_config_test = {
            "config": {
                "monkeyble_module": {}
            }
        }
        update_ansible_task = self.test_strategy.mock_task_module(mock_config_test, self.ansible_task_test)
        self.assertEqual("test_task", update_ansible_task.name)
        self.assertEqual("debug", update_ansible_task.args["original_module_name"])
        self.assertFalse(update_ansible_task.args["consider_changed"])
        expected_result_dict = {}
        self.assertDictEqual(expected_result_dict, update_ansible_task.args["result_dict"])
        expected_original_module_args = {
            "msg": "my_message"
        }
        self.assertDictEqual(expected_original_module_args, update_ansible_task.args["original_module_args"])
