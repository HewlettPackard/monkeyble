# Copyright 2022 Hewlett Packard Enterprise Development LP
import json
import os
import sys
from builtins import super
from copy import copy

from ansible import constants as C
from ansible.errors import AnsibleUndefinedVariable
from ansible.parsing.dataloader import DataLoader
from ansible.plugins.callback import CallbackBase
from ansible.template import Templar
from ansible.utils.display import Display
from ansible.release import __version__ as ansible_version

_ANSIBLE_2_19_PLUS = tuple(int(x) for x in ansible_version.split('.')[:2]) >= (2, 19)

if _ANSIBLE_2_19_PLUS:
    from plugins.module_utils.mocked_task import MockedTask

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../..')
)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from plugins.module_utils.utils import str_to_bool, switch_test_method, get_task_config, tag_values
from plugins.module_utils.const import PASSED_TEST, FAILED_TEST
from plugins.module_utils.exceptions import MonkeybleException
from plugins.module_utils._version import __version__

global_display = Display()


class CallbackModule(CallbackBase):
    """
    Monkeyble callback will:
    - override extra vars
    - test task input (module args)
    - mock the task module
    - check if task should have been skipped
    - check if task should have been changed
    - check if task should have failed
    - test task output (result dict)
    """

    def __init__(self, *args, **kwargs):
        super(CallbackModule, self).__init__(*args, **kwargs)
        self.host_ok = {}
        self.host_unreachable = {}
        self.host_failed = {}
        self.skipped_task_list = list()
        self.changed_task_list = list()
        self.monkeyble_config = None
        self.monkeyble_scenario_description = None
        self._last_task_config = None
        self._last_task_name = None
        self._last_check_output_result = dict()
        self._last_check_input_result = dict()
        self.playbook_extra_vars = dict()
        self._last_task_ignore_errors = None
        self._current_task = None
        self.scenario_extra_vars = dict()
        self.playbook_vars = None

    @staticmethod
    def display_message_ok(msg):
        global_display.display(msg=msg, color=C.COLOR_OK)

    def v2_playbook_on_play_start(self, play):
        self.display_message_ok(msg=f"🐵 Starting Monkeyble callback {__version__}")
        vm = play.get_variable_manager()
        self.playbook_extra_vars = vm.extra_vars
        monkeyble_scenario = self.playbook_extra_vars.get("monkeyble_scenario")
        monkeyble_scenarios = self.playbook_extra_vars.get("monkeyble_scenarios")
        monkeyble_shared_tasks = self.playbook_extra_vars.get("monkeyble_shared_tasks", [])
        if monkeyble_scenario is None:
            raise MonkeybleException("'monkeyble_scenario' need to be passed as extra_vars")
        if monkeyble_scenarios is None:
            raise MonkeybleException("'monkeyble_scenarios' need to be passed as extra_vars")

        try:
            loaded_monkeyble_config = monkeyble_scenarios[monkeyble_scenario]
        except KeyError:
            raise MonkeybleException(f"The Monkeyble scenario name '{monkeyble_scenario}' "
                                     f"not found in 'monkeyble_scenarios'")

        # add shared task to the config
        loaded_monkeyble_config["monkeyble_shared_tasks"] = monkeyble_shared_tasks
        # variable placed into the monkeyble config need to be instantiated with extra vars
        templar = Templar(loader=DataLoader(), variables=self.playbook_extra_vars)
        try:
            self.monkeyble_config = templar.template(tag_values(loaded_monkeyble_config))
        except Exception as e:
            raise MonkeybleException(message=str(e),
                                     scenario_description=monkeyble_scenario)

        self.display_message_ok(f"monkeyble_scenario: {monkeyble_scenario}")
        self.monkeyble_scenario_description = monkeyble_scenario
        # keep only the config of the current scenario
        if "name" in self.monkeyble_config:
            self.monkeyble_scenario_description = self.monkeyble_config['name']
            self.display_message_ok(f"Monkeyble scenario: {self.monkeyble_scenario_description}")

        if "extra_vars" in self.monkeyble_config:
            self.scenario_extra_vars = self.monkeyble_config["extra_vars"]

        return play

    def v2_runner_on_start(self, host, task):
        self.playbook_vars = self._get_playbook_vars(host=host, task=task)

        # template the task name
        task_copy = copy(task)
        templar = Templar(loader=DataLoader(), variables=self.playbook_vars)
        templated_task_name = templar.template(tag_values(task.name))
        task_copy.name = templated_task_name
        task_copy._name = templated_task_name
        self._last_task_name = templated_task_name
        templated_task_ignore_errors = templar.template(tag_values(task.ignore_errors))
        self._last_task_ignore_errors = templated_task_ignore_errors

        # get a monkeyble config for the current task
        self._last_task_config = get_task_config(ansible_task=task_copy, monkeyble_config=self.monkeyble_config)

        if self._last_task_config is not None:
            # apply extra vars from the tested task
            task_extra_vars = self.scenario_extra_vars
            if "extra_vars" in self._last_task_config:
                task_extra_vars.update(self._last_task_config["extra_vars"])

            task = self.update_extra_var(ansible_task=task, extra_var_to_merge=task_extra_vars)

            # check input
            if "test_input" in self._last_task_config:
                self.test_input(ansible_task=task, playbook_vars=self.playbook_vars)

            if "mock" in self._last_task_config:
                if _ANSIBLE_2_19_PLUS:
                    task = self.mock_task_module(ansible_task=MockedTask.from_task(task))
                else:
                    task = self.mock_task_module(ansible_task=task)
        self._current_task = task
        return super(CallbackModule, self).v2_runner_on_start(host, task)

    def v2_playbook_on_stats(self, stats):
        if not stats.failures:
            self.display_message_ok(msg=f"🐵 Monkeyble - ALL TESTS PASSED ✔ - scenario: {self.monkeyble_scenario_description}")
        super(CallbackModule, self).v2_playbook_on_stats(stats)

    def v2_runner_on_unreachable(self, result):
        self._display.debug("Run v2_runner_on_unreachable")
        host = result._host
        self.host_unreachable[host.get_name()] = result

    def v2_runner_on_ok(self, result, *args, **kwargs):
        self._display.debug("Run v2_runner_on_ok")
        host = result._host
        self.host_ok[host.get_name()] = result
        task_name = copy(result._task.name)
        if result.is_changed():
            self.changed_task_list.append(task_name)

        self.check_if_task_should_have_been_skipped(task_has_been_actually_skipped=False)
        self.check_if_task_should_have_been_changed(task_has_been_actually_changed=result.is_changed())
        self.check_if_task_should_have_failed(task_has_actually_failed=False)
        self.test_output(result_dict=result._result)

    def v2_runner_on_failed(self, result, *args, **kwargs):
        self._display.debug("Run v2_runner_on_failed")
        host = result._host
        self.host_failed[host.get_name()] = result
        has_rescue = result._task._parent.rescue
        self.check_if_task_should_have_failed(task_has_actually_failed=True, has_rescue=has_rescue)

    def v2_runner_on_skipped(self, result, **kwargs):
        self._display.debug("Run v2_runner_on_skipped")
        self.check_if_task_should_have_been_skipped(task_has_been_actually_skipped=True)
        self.check_if_task_should_have_failed(task_has_actually_failed=False)

    def test_output(self, result_dict):

        if self._last_task_config is not None:
            if "test_output" in self._last_task_config:
                test_result = {
                    "task": self._last_task_name,
                    PASSED_TEST: [],
                    FAILED_TEST: []
                }
                for result_value_to_test in self._last_task_config["test_output"]:
                    for test_name, result_value_and_expected in result_value_to_test.items():
                        result_key = result_value_and_expected['result_key']
                        # template the result to get the real value
                        template_string = "{{  " + result_key + "  }}"
                        context = {
                            "result": result_dict
                        }
                        templar = Templar(loader=DataLoader(), variables=context)
                        try:
                            templated_value = templar.template(tag_values(template_string))
                            if templated_value == "" and test_name == "assert_is_none":
                                templated_value = None
                        except AnsibleUndefinedVariable as e:
                            raise MonkeybleException(message=str(e),
                                                     scenario_description=self.monkeyble_scenario_description)
                        try:
                            expected = result_value_and_expected['expected']
                        except KeyError:
                            expected = None  # can be none for assert_none, assert_false, assert_true, assert_false
                        returned_tuple = switch_test_method(test_name, templated_value, expected)
                        test_result[returned_tuple[0]].append(returned_tuple[1])

                self._last_check_output_result = test_result
                json_test_result = json.dumps(test_result)
                if len(test_result[FAILED_TEST]) >= 1:
                    raise MonkeybleException(message=str(json_test_result),
                                             scenario_description=self.monkeyble_scenario_description)
                self.display_message_ok(msg="🙊 Monkeyble test output passed ✔")
                self.display_message_ok(msg=str(json_test_result))

    def check_if_task_should_have_been_skipped(self, task_has_been_actually_skipped=False):
        self._display.debug("Monkeyble check_if_task_should_have_been_skipped called")
        self._compare_boolean_to_config(task_name=self._last_task_name,
                                        config_flag_name="should_be_skipped",
                                        task_config=self._last_task_config,
                                        actual_state=task_has_been_actually_skipped)

    def check_if_task_should_have_been_changed(self, task_has_been_actually_changed):
        self._display.debug("Monkeyble task_has_been_actually_changed called")

        self._compare_boolean_to_config(task_name=self._last_task_name,
                                        config_flag_name="should_be_changed",
                                        task_config=self._last_task_config,
                                        actual_state=task_has_been_actually_changed)

    def check_if_task_should_have_failed(self, task_has_actually_failed, has_rescue=False):
        self._display.debug("Monkeyble check_if_task_should_have_failed called")
        if self._last_task_config is None:
            return
        should_fail = self._last_task_config.get("should_fail", False)

        # case 1: task has not failed and was expected to fail
        if not task_has_actually_failed and should_fail:
            message = f"🐵 Monkeyble - Task '{self._last_task_name}' was expected to fail but succeeded"
            raise MonkeybleException(message=message,
                                     scenario_description=self.monkeyble_scenario_description)
        # case 2: task has failed and was explicitly expected not to fail
        if task_has_actually_failed and "should_fail" in self._last_task_config and not should_fail:
            message = f"🐵 Monkeyble - Task '{self._last_task_name}' failed and was not expected to"
            raise MonkeybleException(message=message,
                                     scenario_description=self.monkeyble_scenario_description)
        # case 3: task has failed and was expected to fail
        if task_has_actually_failed and should_fail:
            # if we reach this line, it means that the task was expected to fail.
            # We exit with code 0 to prevent a CI to fail if the task does not ignore error
            if not self._last_task_ignore_errors and not has_rescue:
                message = f"🐵 Monkeyble - Task '{self._last_task_name}' failed as expected"
                raise MonkeybleException(message=message,
                                         scenario_description=self.monkeyble_scenario_description,
                                         exit_code=0)
        # case 4: task has not failed and was not expected to fail. everything is normal
        if not task_has_actually_failed and not should_fail:
            self._display.debug(f"Monkeyble - Task '{self._last_task_name}' did not fail as expected")

    def _compare_boolean_to_config(self, task_name: str, config_flag_name: str, task_config: dict, actual_state: bool):
        if task_config is not None:
            if config_flag_name in task_config:
                config_flag_value = str_to_bool(task_config[config_flag_name])
                self._display.debug(f"config_flag_name: {config_flag_name}")
                self._display.debug(f"config_flag_value: {config_flag_value}")
                self._display.debug(f"actual_state: {actual_state}")
                message = f"🐵 Monkeyble - Task '{task_name}' - expected '{config_flag_name}': {config_flag_value}. " \
                          f"actual state: {actual_state}"
                if config_flag_value != actual_state:
                    raise MonkeybleException(message=message,
                                             scenario_description=self.monkeyble_scenario_description)
                self.display_message_ok(msg=message)
                return True
        return None

    def mock_task_module(self, ansible_task):
        new_action_name = next(iter(self._last_task_config["mock"]["config"]))
        original_module_name = ansible_task.action
        message = f"🙉 Monkeyble mock module - Before: '{original_module_name}' Now: '{new_action_name}'"
        self.display_message_ok(msg=str(message))
        ansible_task.action = new_action_name
        ansible_task.resolved_action = new_action_name
        monkeyble_action_names = [
            "monkeyble_module",
            "hpe.monkeyble.monkeyble_module",
        ]
        if new_action_name in monkeyble_action_names:
            consider_changed = self._last_task_config["mock"]["config"][new_action_name].get("consider_changed", False)
            result_dict = self._last_task_config["mock"]["config"][new_action_name].get("result_dict", {})
            ansible_task.args = {"task_name": ansible_task.name,
                                 "original_module_name": original_module_name,
                                 "consider_changed": consider_changed,
                                 "result_dict": result_dict
                                 }
        else:
            # custom module
            ansible_task.args = self._last_task_config["mock"]["config"][new_action_name]
        return ansible_task

    def update_extra_var(self, ansible_task, extra_var_to_merge=None):
        # first template our extra vars with extra vars from the playbook
        # if extra_var_to_merge is None or extra_var_to_merge == {}:
        #     return ansible_task
        templar = Templar(loader=DataLoader(), variables=self.playbook_vars)
        templated_task_extra_vars = templar.template(tag_values(extra_var_to_merge))
        # then template the module args
        templar = Templar(loader=DataLoader(), variables=templated_task_extra_vars)
        try:
            templated_module_args = templar.template(tag_values(ansible_task.args))
            ansible_task.args = templated_module_args
        except AnsibleUndefinedVariable:
            pass
        # remove keys from
        return ansible_task

    def test_input(self, ansible_task, playbook_vars: dict = None):
        playbook_vars = playbook_vars or {}
        templar = Templar(loader=DataLoader(), variables=playbook_vars)
        test_result = {PASSED_TEST: [], FAILED_TEST: []}

        def get_argument_value(module_args, arg_name):
            try:
                return module_args[arg_name]
            except KeyError:
                raise MonkeybleException(
                    message=(
                        f"arg_name '{arg_name}' not present in the list of arguments "
                        f"when executing module '{ansible_task.action}'"
                    ),
                    scenario_description=self.monkeyble_scenario_description,
                )

        def run_test(test_name, arg_name, expected, module_args):
            argument_value = get_argument_value(module_args, arg_name)
            status, result = switch_test_method(test_name, argument_value, expected)
            return status, result

        for arg_tests in self._last_task_config.get("test_input", []):
            for test_name, value_and_expected in arg_tests.items():
                expected = value_and_expected.get("expected")
                arg_name = value_and_expected["arg_name"]

                if ansible_task.loop:
                    tested_values = []
                    found_match = False

                    for loop_value in ansible_task.loop:
                        playbook_vars.update({ansible_task.loop_control.loop_var: loop_value})
                        templar = Templar(loader=DataLoader(), variables=playbook_vars)
                        module_args = templar.template(tag_values(ansible_task.args))
                        try:
                            argument_value = get_argument_value(module_args, arg_name)
                        except MonkeybleException:
                            raise  # Preserve existing behavior

                        tested_values.append(argument_value)
                        status, result = run_test(test_name, arg_name, expected, module_args)
                        if status == PASSED_TEST:
                            found_match = True
                            test_result[status].append(result)
                            break

                    if not found_match:
                        test_result[FAILED_TEST].append({
                            "test_name": test_name,
                            "tested_value": tested_values,
                            "expected": expected,
                        })
                else:
                    module_args = templar.template(ansible_task.args)
                    status, result = run_test(test_name, arg_name, expected, module_args)
                    test_result[status].append(result)

        # Save and display results
        self._last_check_input_result = test_result
        json_test_result = json.dumps(test_result)

        if test_result[FAILED_TEST]:
            raise MonkeybleException(
                message=json_test_result,
                scenario_description=self.monkeyble_scenario_description,
            )

        self.display_message_ok(msg="🙈 Monkeyble test input passed ✔")
        self.display_message_ok(msg=json_test_result)

    def _get_playbook_vars(self, host, task):
        # inventory + host vars + group vars
        playbook_vars = task.play.get_variable_manager().get_vars(host=host, task=task)
        # add play vars
        playbook_vars.update(task.play.vars)
        # add extra vars
        playbook_vars.update(self.playbook_extra_vars)
        return playbook_vars
