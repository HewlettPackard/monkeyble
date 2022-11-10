# Copyright 2022 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import unittest
from unittest import mock
from unittest.mock import MagicMock, patch

from ansible.errors import AnsibleAssertionError

from ansible_monkeyble.plugins.strategy.monkeyble_linear import StrategyModule as MonkeybleStrategyModule, \
    MonkeybleTestFailed


class TestMonkeybleStrategy(unittest.TestCase):

    def setUp(self) -> None:
        tqm = MagicMock()
        self.test_strategy = MonkeybleStrategyModule(tqm)

        self.ansible_task_test = MagicMock()
        self.ansible_task_test.name = "test_task"
        self.ansible_task_test.get_name.return_value = "test_task"
        self.ansible_task_test.action = "debug"
        self.ansible_task_test.args = {
            "msg": "my_message"
        }

        self.test_input_list = [{
            "assert_equal": {
                "arg_name": "msg",
                "expected": "value1"
            }
        }]

        # test queue
        self.host = MagicMock()
        self.play_context = MagicMock()
        self.task_vars = {
            "default_var_key": "default_var_value"
        }

        # test run
        self.iterator = MagicMock()
        self.play_context = MagicMock()





    @patch('ansible.plugins.strategy.StrategyBase._queue_task')
    def test_queue_task_task_not_match(self, mock_ansible_queue_task):
        self.test_strategy.monkeyble_config = {
            "name": "Validate this",
            "tasks_to_test": [
                {
                    "task": "test_task_not_found",
                    "extra_vars": {
                        "default_var_key": "overriden_value"
                    }
                }
            ]
        }
        self.test_strategy._queue_task(self.host, self.ansible_task_test, self.task_vars, self.play_context)
        # the ansible mother class is called without any change
        mock_ansible_queue_task.assert_called_with(self.host, self.ansible_task_test,
                                                   self.task_vars, self.play_context)

    @patch('ansible.plugins.strategy.StrategyBase._queue_task')
    def test_queue_task_task_match_task_override_extra_vars(self, mock_ansible_queue_task):
        self.test_strategy.monkeyble_config = {
            "name": "Validate this",
            "tasks_to_test": [
                {
                    "task": "test_task",
                    "extra_vars": {
                        "default_var_key": "overriden_value"
                    }
                }
            ]
        }
        self.test_strategy._queue_task(self.host, self.ansible_task_test, self.task_vars, self.play_context)
        # the ansible mother class is called with change on extra vars
        expected_task_var = {
            "default_var_key": "overriden_value"
        }
        mock_ansible_queue_task.assert_called_with(self.host, self.ansible_task_test,
                                                   expected_task_var, self.play_context)

    @patch('ansible.plugins.strategy.StrategyBase._queue_task')
    def test_queue_task_task_match_task_test_ok(self, mock_ansible_queue_task):
        self.test_strategy.monkeyble_config = {
            "name": "Validate this",
            "tasks_to_test": [
                {
                    "task": "test_task",
                    "test_input": [
                        {"assert_equal": {
                            "arg_name": "msg",
                            "expected": "my_message"
                        }}
                    ]
                }
            ]
        }
        self.test_strategy._queue_task(self.host, self.ansible_task_test, self.task_vars, self.play_context)
        mock_ansible_queue_task.assert_called_with(self.host, self.ansible_task_test,
                                                   self.task_vars, self.play_context)
        expected_last_check_input_result = {'monkeyble_passed_test': [
            {'test_name': 'assert_equal',
             'tested_value': 'my_message',
             'expected': 'my_message'}],
            'monkeyble_failed_test': []
        }
        self.assertDictEqual(self.test_strategy._last_check_input_result, expected_last_check_input_result)

    @patch('ansible.plugins.strategy.StrategyBase._queue_task')
    def test_queue_task_task_match_task_test_fail(self, mock_ansible_queue_task):
        self.test_strategy.monkeyble_config = {
            "name": "Validate this",
            "tasks_to_test": [
                {
                    "task": "test_task",
                    "test_input": [
                        {"assert_equal": {
                            "arg_name": "msg",
                            "expected": "different_value"
                        }}
                    ]
                }
            ]
        }
        with self.assertRaises(MonkeybleTestFailed):
            self.test_strategy._queue_task(self.host, self.ansible_task_test, self.task_vars, self.play_context)
            mock_ansible_queue_task.assert_not_called()
            expected_last_check_input_result = {'monkeyble_failed_test': [
                {'test_name': 'assert_equal',
                 'tested_value': 'my_message',
                 'expected': 'my_message'}],
                'monkeyble_passed_test': []
            }
            self.assertDictEqual(self.test_strategy._last_check_input_result, expected_last_check_input_result)

    @patch('ansible_monkeyble.plugins.strategy.monkeyble_linear.StrategyModule.mock_task_module')
    @patch('ansible.plugins.strategy.StrategyBase._queue_task')
    def test_queue_task_task_match_task_mock_task(self, mock_ansible_queue_task, mock_mock_task_module):
        self.test_strategy.monkeyble_config = {
            "name": "Validate this",
            "tasks_to_test": [
                {
                    "task": "test_task",
                    "mock": {
                        "config": {
                            "monkeyble_module": {
                                "consider_changed": False,
                                "result_dict": {
                                    "msg": "output_value"
                                }
                            }
                        }
                    }
                }
            ]
        }
        self.test_strategy._queue_task(self.host, self.ansible_task_test, self.task_vars, self.play_context)
        mock_ansible_queue_task.assert_called()
        expected_config = {
            "config": {"monkeyble_module": {"consider_changed": False, "result_dict": {
                "msg": "output_value"}}}}
        mock_mock_task_module.assert_called_with(expected_config, ansible_task=self.ansible_task_test)

    @patch('ansible.plugins.strategy.linear.StrategyModule.run')
    def test_run_fail_when_no_monkeyble_scenario(self, mock_run):
        self.iterator._variable_manager._extra_vars = {}
        with self.assertRaises(AnsibleAssertionError):
            self.test_strategy.run(self.iterator, self.play_context)
        mock_run.assert_not_called()

    @patch('ansible.plugins.strategy.linear.StrategyModule.run')
    def test_run_fail_when_no_monkeyble_scenarios(self, mock_run):
        self.iterator._variable_manager._extra_vars = {
            "monkeyble_scenario": "test_scenario"
        }
        with self.assertRaises(AnsibleAssertionError):
            self.test_strategy.run(self.iterator, self.play_context)
        mock_run.assert_not_called()

    @patch('ansible.plugins.strategy.linear.StrategyModule.run')
    def test_run_fail_when_monkeyble_scenario_name_does_not_match(self, mock_run):
        self.iterator._variable_manager._extra_vars = {
            "monkeyble_scenario": "test_scenario_not_found",
            "monkeyble_scenarios": {
                "test_scenario": {
                    "name": "Validate"
                }
            }
        }
        with self.assertRaises(AnsibleAssertionError):
            self.test_strategy.run(self.iterator, self.play_context)
            mock_run.assert_not_called()

    @patch('ansible.plugins.strategy.linear.StrategyModule.run')
    def test_run_template_monkeyble_config(self, mock_run):
        self.iterator._variable_manager._extra_vars = {
            "my_extra_variable": "value1",
            "monkeyble_scenario": "test_scenario",
            "monkeyble_scenarios": {
                "test_scenario": {
                    "name": "{{ my_extra_variable }}"
                }
            }
        }
        self.test_strategy.run(self.iterator, self.play_context)
        mock_run.assert_called()
        expected_monkeyble_config = {
            "name": "value1"
        }
        self.assertDictEqual(expected_monkeyble_config, self.test_strategy.monkeyble_config)
