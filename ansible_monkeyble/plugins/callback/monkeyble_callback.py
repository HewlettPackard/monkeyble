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

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../..')
)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ansible_monkeyble.plugins.module_utils.utils import str_to_bool, switch_test_method, get_task_config
from ansible_monkeyble.plugins.module_utils.const import PASSED_TEST, FAILED_TEST

global_display = Display()


class MonkeybleException(Exception):
    def __init__(self, message, exit_code=1):
        super().__init__(message)
        global_display.display(msg=message, color=C.COLOR_ERROR)
        sys.exit(exit_code)


class CallbackModule(CallbackBase):

    def __init__(self, *args, **kwargs):
        super(CallbackModule, self).__init__(*args, **kwargs)
        self.host_ok = {}
        self.host_unreachable = {}
        self.host_failed = {}
        self.skipped_task_list = list()
        self.changed_task_list = list()
        self.monkeyble_config = None
        self._last_task_config = None
        self._last_task_name = None
        self._last_check_output_result = dict()
        self._last_check_input_result = dict()
        self.extra_vars = None
        self._last_task_ignore_errors = None

    def v2_playbook_on_play_start(self, play):
        global_display.display(msg="Starting Monkeyble callback", color=C.COLOR_OK)
        vm = play.get_variable_manager()
        self.extra_vars = vm.extra_vars
        monkeyble_scenario = self.extra_vars.get("monkeyble_scenario")
        monkeyble_scenarios = self.extra_vars.get("monkeyble_scenarios")
        if monkeyble_scenario is None:
            raise MonkeybleException("'monkeyble_scenario' need to be passed as extra_vars")
        if monkeyble_scenarios is None:
            raise MonkeybleException("'monkeyble_scenarios' need to be passed as extra_vars")

        try:
            loaded_monkeyble_config = monkeyble_scenarios[monkeyble_scenario]
        except KeyError:
            raise MonkeybleException(f"The Monkeyble scenario name'{monkeyble_scenario}' "
                                     f"not found in 'monkeyble_scenarios'")

        # variable placed into the monkeyble config need to be instantiated with extra vars
        templar = Templar(loader=DataLoader(), variables=self.extra_vars)
        self.monkeyble_config = templar.template(loaded_monkeyble_config)

        global_display.display(f"monkeyble_scenario: {monkeyble_scenario}", color=C.COLOR_OK)

        # keep only the config of the current scenario
        if "name" in self.monkeyble_config:
            global_display.display(f"Monkeyble scenario: {self.monkeyble_config['name']}", color=C.COLOR_OK)

        return play

    def v2_playbook_on_stats(self, stats):
        # if we reach this line, all test have passed successfully
        global_display.display(msg="Monkeyble - ALL TESTS PASSED", color=C.COLOR_OK)
        super(CallbackModule, self).v2_playbook_on_stats(stats)

    def v2_playbook_on_task_start(self, task, is_conditional):
        self._last_task_config = get_task_config(ansible_task=task, monkeyble_config=self.monkeyble_config)
        self._last_task_name = task.name
        self._last_task_ignore_errors = task.ignore_errors

        if self._last_task_config is not None:
            # apply extra vars from the tested task
            if "extra_vars" in self._last_task_config:
                # first template our extra vars with extra vars from the playbook
                templar = Templar(loader=DataLoader(), variables=self.extra_vars)
                templated_task_extra_vars = templar.template(self._last_task_config["extra_vars"])
                # then template the module args
                templar = Templar(loader=DataLoader(), variables=templated_task_extra_vars)
                templated_module_args = templar.template(task.args)
                task.args = templated_module_args

            # check input
            if "test_input" in self._last_task_config:
                task_vars = task.play.vars
                task_vars.update(self.extra_vars)
                templar = Templar(loader=DataLoader(), variables=task_vars)
                templated_module_args = templar.template(task.args)
                result = self.check_input(self._last_task_config["test_input"], ansible_task_args=templated_module_args)
                if len(result[FAILED_TEST]) >= 1:
                    # self._display.display(msg=str(result), color=C.COLOR_ERROR)
                    raise MonkeybleException(message=str(result))
                self._display.display(msg=str(result), color=C.COLOR_CHANGED)

            if "mock" in self._last_task_config:
                task = self.mock_task_module(self._last_task_config["mock"], ansible_task=task)

        return super(CallbackModule, self).v2_playbook_on_task_start(task, is_conditional)

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
        self.check_output(result_dict=result._result)

    def v2_runner_on_failed(self, result, *args, **kwargs):
        self._display.debug("Run v2_runner_on_failed")
        host = result._host
        self.host_failed[host.get_name()] = result
        self.check_if_task_should_have_failed(task_has_actually_failed=True)

    def v2_runner_on_skipped(self, result, **kwargs):
        self._display.debug("Run v2_runner_on_skipped")
        self.check_if_task_should_have_been_skipped(task_has_been_actually_skipped=True)

    def check_output(self, result_dict):

        if self._last_task_config is not None:
            if "test_output" in self._last_task_config:
                test_result = {
                    "task": self._last_task_name,
                    PASSED_TEST: [],
                    FAILED_TEST: []
                }
                for result_value_to_test in self._last_task_config["test_output"]:
                    for test_name, result_value_and_expected in result_value_to_test.items():
                        result_value = result_value_and_expected['result_key']
                        # template the result to get the real value
                        template_string = "{{  " + result_value + "  }}"
                        context = {
                            "result": result_dict
                        }
                        templar = Templar(loader=DataLoader(), variables=context)
                        try:
                            templated_value = templar.template(template_string)
                        except AnsibleUndefinedVariable as e:
                            self._display.display(msg=str(e), color=C.COLOR_ERROR)
                            raise MonkeybleException(message=str(e))
                        expected = result_value_and_expected['expected']
                        returned_tuple = switch_test_method(test_name, templated_value, expected)
                        test_result[returned_tuple[0]].append(returned_tuple[1])

                self._last_check_output_result = test_result
                if len(test_result[FAILED_TEST]) >= 1:
                    raise MonkeybleException(message=str(test_result))
                self._display.display(msg=str(test_result), color=C.COLOR_OK)

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

    def check_if_task_should_have_failed(self, task_has_actually_failed):
        self._display.debug("Monkeyble check_if_task_should_have_failed called")

        result = self._compare_boolean_to_config(task_name=self._last_task_name,
                                                 config_flag_name="should_failed",
                                                 task_config=self._last_task_config,
                                                 actual_state=task_has_actually_failed)
        if result is not None and result:
            # if we reach this line, it means that the task was expected to fail.
            # We exit with code 0 to prevent a CI to fail if the task does not ignore error
            if not self._last_task_ignore_errors:
                message = f"Task '{self._last_task_name}' failed as expected"
                raise MonkeybleException(message=message, exit_code=0)

    def _compare_boolean_to_config(self, task_name: str, config_flag_name: str, task_config: dict, actual_state: bool):
        if task_config is not None:
            if config_flag_name in task_config:
                config_flag_value = str_to_bool(task_config[config_flag_name])
                self._display.debug(f"config_flag_name: {config_flag_name}")
                self._display.debug(f"config_flag_value: {config_flag_value}")
                self._display.debug(f"actual_state: {actual_state}")
                message = f"Task '{task_name}' - expected '{config_flag_name}': {config_flag_value}. " \
                          f"actual state: {actual_state}"
                if config_flag_value != actual_state:
                    self._display.display(msg=message, color=C.COLOR_ERROR)
                    raise MonkeybleException(message=message)
                self._display.display(msg=message, color=C.COLOR_OK)
                return True
        return None

    def check_input(self, test_input_list, ansible_task_args):
        """
        Test all args and raise an error if one of the test has failed
        """
        test_result = {
            PASSED_TEST: [],
            FAILED_TEST: []
        }
        for arg_to_test in test_input_list:
            for test_name, value_and_expected in arg_to_test.items():
                argument_value = ansible_task_args[value_and_expected['arg_name']]
                try:
                    expected = value_and_expected['expected']
                except KeyError:
                    expected = None
                returned_tuple = switch_test_method(test_name, argument_value, expected)
                test_result[returned_tuple[0]].append(returned_tuple[1])
        self._last_check_input_result = test_result
        return test_result

    @staticmethod
    def mock_task_module(mock_config, ansible_task):
        new_action_name = next(iter(mock_config["config"]))
        original_module_name = ansible_task.action
        message = f"Monkeyble mock module - Before: '{original_module_name}' Now: '{new_action_name}'"
        global_display.display(msg=str(message), color=C.COLOR_CHANGED)
        ansible_task.action = new_action_name
        if new_action_name == "monkeyble_module":
            original_module_args = ansible_task.args
            ansible_task.args = {"task_name": ansible_task.name,
                                 "original_module_name": original_module_name,
                                 "original_module_args": original_module_args,
                                 "consider_changed": mock_config["config"]["monkeyble_module"].get("consider_changed",
                                                                                                   False),
                                 "result_dict": mock_config["config"]["monkeyble_module"].get("result_dict", {})
                                 }
            # ansible_task.args.update(mock_config["config"]["monkeyble_module"])
        # TODO test with custom module
        return ansible_task
