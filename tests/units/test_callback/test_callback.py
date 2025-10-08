from unittest.mock import patch

from ansible.errors import AnsibleUndefinedVariable

from plugins.callback.monkeyble_callback import MonkeybleException
from tests.units.test_callback.base_test_callback import BaseTestMonkeybleCallback


class TestMonkeybleCallback(BaseTestMonkeybleCallback):

    def setUp(self) -> None:
        super(TestMonkeybleCallback, self).setUp()

    @patch('sys.exit')
    def test_compare_boolean_to_config(self, mock_exit):
        task_name = "test_task"
        config_flag_name = "a_boolean_flag"

        # Test when actual value and config value are true
        task_config = {
            "task": "test_task",
            "a_boolean_flag": "true"
        }
        actual_state = True
        self.assertTrue(self.test_callback._compare_boolean_to_config(task_name, config_flag_name,
                                                                      task_config, actual_state))
        task_config = {
            "task": "test_task",
            "a_boolean_flag": True
        }
        self.assertTrue(self.test_callback._compare_boolean_to_config(task_name, config_flag_name,
                                                                      task_config, actual_state))

        # Test config is False and actual state is False
        actual_state = False
        task_config = {
            "task": "test_task",
            "a_boolean_flag": False
        }
        self.assertTrue(self.test_callback._compare_boolean_to_config(task_name, config_flag_name,
                                                                      task_config, actual_state))

        # Test config is True and actual state is False
        actual_state = False
        task_config = {
            "task": "test_task",
            "a_boolean_flag": True
        }
        with self.assertRaises(MonkeybleException):
            self.test_callback._compare_boolean_to_config(task_name, config_flag_name, task_config, actual_state)
            mock_exit.assert_called()

        # Test config is False and actual state is True
        actual_state = True
        task_config = {
            "task": "test_task",
            "a_boolean_flag": False
        }
        with self.assertRaises(MonkeybleException):
            self.test_callback._compare_boolean_to_config(task_name, config_flag_name, task_config, actual_state)
            mock_exit.assert_called()

    def test_v2_playbook_on_play_start(self):
        self.var_manager.extra_vars = {
            "my_extra_variable": "value1",
            "monkeyble_scenario": "test_scenario",
            "monkeyble_shared_tasks": [
                {"task": "shared_task_1"},
                {"task": "{{ my_extra_variable }}"},
            ],
            "monkeyble_scenarios": {
                "test_scenario": {
                    "name": "{{ my_extra_variable }}"
                }
            }
        }
        self.test_callback.v2_playbook_on_play_start(self.play)
        expected_monkeyble_config = {
            "name": "value1",
            "monkeyble_shared_tasks": [
                {"task": "shared_task_1"},
                {"task": "value1"},
            ],
        }
        self.assertDictEqual(expected_monkeyble_config, self.test_callback.monkeyble_config)

    def test_v2_runner_on_start_extra_var_overwrite_at_scenario_level(self):
        self.test_callback.playbook_extra_vars = {
            "variable_from_playbook_extra_var": "play_level_variable",
        }
        self.ansible_task_test.args = {
            "msg": "{{ variable_from_playbook_extra_var }}"
        }

        self.test_callback.monkeyble_config = {
            "name": "monkeyble_scenario",
            "tasks_to_test": [
                {
                    "task": "test_task"
                }
            ]
        }
        self.test_callback.scenario_extra_vars = {
                "variable_from_playbook_extra_var": "update_at_scenario_level",
            }

        self.test_callback.v2_runner_on_start(task=self.ansible_task_test, host=None)
        expected_args = {
            "msg": "update_at_scenario_level"
        }
        self.assertDictEqual(self.test_callback._current_task.args, expected_args)


    def test_v2_runner_on_start_extra_var_overwrite_at_task_level(self):
        self.test_callback.playbook_extra_vars = {
            "variable_from_playbook_extra_var": "play_level_variable",
        }
        self.ansible_task_test.args = {
            "msg": "{{ variable_from_playbook_extra_var }}"
        }

        self.test_callback.monkeyble_config = {
            "name": "monkeyble_scenario",
            "tasks_to_test": [
                {
                    "task": "test_task",
                    "extra_vars": {
                        "variable_from_playbook_extra_var": "update_at_task_level"
                    }
                }
            ]
        }
        self.test_callback.v2_runner_on_start(task=self.ansible_task_test, host=None)
        expected_args = {
            "msg": "update_at_task_level"
        }
        self.assertDictEqual(self.test_callback._current_task.args, expected_args)

    def test_v2_runner_on_start_extra_var_overwrite_at_task_level_over_scenario_level(self):
        self.test_callback.playbook_extra_vars = {
            "variable_from_playbook_extra_var": "play_level_variable",
        }
        self.ansible_task_test.args = {
            "msg": "{{ variable_from_playbook_extra_var }}"
        }

        self.test_callback.monkeyble_config = {
            "name": "monkeyble_scenario",
            "extra_vars": {
                "variable_from_playbook_extra_var": "update_at_scenario_level",
            },
            "tasks_to_test": [
                {
                    "task": "test_task",
                    "extra_vars": {
                        "variable_from_playbook_extra_var": "update_at_task_level"
                    }
                }
            ]
        }
        self.test_callback.v2_runner_on_start(task=self.ansible_task_test, host=None)
        expected_args = {
            "msg": "update_at_task_level"
        }
        self.assertDictEqual(self.test_callback._current_task.args, expected_args)

    @patch('sys.exit')
    def test_v2_playbook_on_play_start_fail_when_monkeyble_scenario_name_does_not_match(self, mock_exit_playbook):
        self.var_manager.extra_vars = {
            "my_extra_variable": "value1",
            "monkeyble_scenario": "test_scenario_not_found",
            "monkeyble_scenarios": {
                "test_scenario": {
                    "name": "validate"
                }
            }
        }
        with self.assertRaises(MonkeybleException):
            self.test_callback.v2_playbook_on_play_start(self.play)
            mock_exit_playbook.assert_called()

    @patch('sys.exit')
    def test_v2_playbook_on_play_start_when_no_monkeyble_scenarios(self, mock_exit_playbook):
        self.var_manager.extra_vars = {
            "my_extra_variable": "value1",
            "monkeyble_scenario": "test_scenario"
        }
        with self.assertRaises(MonkeybleException):
            self.test_callback.v2_playbook_on_play_start(self.play)
            mock_exit_playbook.assert_called()

    @patch('sys.exit')
    def test_run_fail_when_no_monkeyble_scenario(self, mock_exit_playbook):
        self.var_manager.extra_vars = {}
        with self.assertRaises(MonkeybleException):
            self.test_callback.v2_playbook_on_play_start(self.play)
            mock_exit_playbook.assert_called()

    def test_update_extra_var_hard_coded_value(self):
        self.ansible_task_test.args = {
            "var_to_change": "{{ variable_from_playbook_extra_var }}"
        }
        self.test_callback.playbook_extra_vars = {
            "variable_from_playbook_extra_var": "value"
        }
        merged_extra_var = {
            "variable_from_playbook_extra_var": "hard_coded_value"
        }
        task = self.test_callback.update_extra_var(ansible_task=self.ansible_task_test, extra_var_to_merge=merged_extra_var)
        # we expect a merge
        expected_dict = {
            "var_to_change": "hard_coded_value"
        }
        self.assertDictEqual(expected_dict, task.args)

    def test_update_extra_var_jinja_value_keep_default(self):
        self.ansible_task_test.args = {
            "msg": "{{ undefined_variable }}"
        }

        task = self.test_callback.update_extra_var(ansible_task=self.ansible_task_test, extra_var_to_merge={})
        # we expect a merge
        expected_dict = {
            "msg": "{{ undefined_variable }}"
        }
        self.assertDictEqual(expected_dict, task.args)

    def test_update_extra_var_with_jinja_value(self):
        self.ansible_task_test.args = {
            "msg": "{{ undefined_variable }}"
        }
        extra_var_to_merge = {
            "test": "{{ other_non_existing_variable }}"
        }
        with self.assertRaises(AnsibleUndefinedVariable):
            task = self.test_callback.update_extra_var(ansible_task=self.ansible_task_test, extra_var_to_merge=extra_var_to_merge)


    @patch('plugins.callback.monkeyble_callback.CallbackModule.mock_task_module')
    @patch('plugins.callback.monkeyble_callback.CallbackModule.test_input')
    @patch('plugins.callback.monkeyble_callback.CallbackModule.update_extra_var')
    def test_v2_playbook_on_task_start_when_task_does_not_match(self, mock_update_extra_var, mock_test_input, mock_mock_task_module):
        self.test_callback.monkeyble_config = {
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

        self.test_callback.v2_playbook_on_task_start(task=self.ansible_task_test, is_conditional=False)
        mock_update_extra_var.assert_not_called()
        mock_test_input.assert_not_called()
        mock_mock_task_module.assert_not_called()

    def test_v2_playbook_on_task_start_input_test_ok(self):
        self.test_callback.monkeyble_config = {
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
        self.test_callback.v2_runner_on_start(task=self.ansible_task_test, host=None)
        expected_last_check_input_result = {'monkeyble_passed_test': [
            {'test_name': 'assert_equal',
             'tested_value': 'my_message',
             'expected': 'my_message'}],
            'monkeyble_failed_test': []
        }
        self.assertDictEqual(self.test_callback._last_check_input_result, expected_last_check_input_result)

    @patch("plugins.callback.monkeyble_callback.CallbackModule._get_playbook_vars")
    def test_v2_playbook_on_task_start_input_test_ok_with_task_templated(self, mock_get_playbook_vars):
        mock_get_playbook_vars.return_value = {
            "my_extra_var": "templated_value"
        }
        self.test_callback.monkeyble_config = {
            "name": "Validate this",
            "tasks_to_test": [
                {
                    "task": "test_task templated_value",
                    "test_input": [
                        {"assert_equal": {
                            "arg_name": "msg",
                            "expected": "my_message"
                        }}
                    ]
                }
            ]
        }
        self.test_callback.v2_runner_on_start(task=self.ansible_task_test_2, host=None)
        expected_last_check_input_result = {'monkeyble_passed_test': [
            {'test_name': 'assert_equal',
             'tested_value': 'my_message',
             'expected': 'my_message'}],
            'monkeyble_failed_test': []
        }
        self.assertDictEqual(self.test_callback._last_check_input_result, expected_last_check_input_result)

    @patch('sys.exit')
    def test_v2_runner_on_start_input_test_fail(self, mock_exit_playbook):
        self.test_callback.monkeyble_config = {
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
        with self.assertRaises(MonkeybleException):
            self.test_callback.v2_runner_on_start(task=self.ansible_task_test, host=None)
            mock_exit_playbook.assert_called()
            expected_last_check_input_result = {'monkeyble_failed_test': [
                {'test_name': 'assert_equal',
                 'tested_value': 'my_message',
                 'expected': 'my_message'}],
                'monkeyble_passed_test': []
            }
            self.assertDictEqual(self.test_callback._last_check_input_result, expected_last_check_input_result)

    @patch('sys.exit')
    def test_v2_runner_on_start_fail_on_missing_var(self, mock_exit):
        self.test_callback.monkeyble_config = {
            "name": "Validate this",
            "tasks_to_test": [
            ]
        }
        self.var_manager.extra_vars = {
            "monkeyble_scenario": "test_scenario",
            "monkeyble_scenarios": {
                "test_scenario": {
                    "name": "{{ not_declared_anywhere }}"
                }
            }
        }
        with self.assertRaises(MonkeybleException):
            self.test_callback.v2_playbook_on_play_start(self.play)
            mock_exit.assert_called()
