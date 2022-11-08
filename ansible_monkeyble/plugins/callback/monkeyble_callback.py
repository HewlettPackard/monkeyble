import os
import sys
from copy import copy

from ansible.errors import AnsibleError, AnsibleUndefinedVariable
from ansible.parsing.dataloader import DataLoader
from ansible.plugins.callback import CallbackBase
from ansible import constants as C
from ansible.template import Templar

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../..')
)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ansible_monkeyble.plugins.strategy.utils import str_to_bool, switch_test_method, get_task_config
from ansible_monkeyble.plugins.strategy.const import PASSED_TEST, FAILED_TEST


class MonkeybleTestError(AnsibleError):
    pass


class CallbackModule(CallbackBase):
    """A sample callback plugin used for performing an action as results come in.

    If you want to collect all results into a single object for processing at
    the end of the execution, look into utilizing the ``json`` callback plugin
    or writing your own custom callback plugin.
    """

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

    def v2_playbook_on_play_start(self, play):
        vm = play.get_variable_manager()
        extra_vars = vm.extra_vars
        monkeyble_scenario = extra_vars.get("monkeyble_scenario")
        monkeyble_scenarios = extra_vars.get("monkeyble_scenarios")
        self.monkeyble_config = monkeyble_scenarios[monkeyble_scenario]

    def v2_playbook_on_task_start(self, task, is_conditional):
        self._last_task_config = get_task_config(ansible_task=task, monkeyble_config=self.monkeyble_config)
        self._last_task_name = task.name

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
                            self.exit_playbook()
                            return
                        expected = result_value_and_expected['expected']
                        returned_tuple = switch_test_method(test_name, templated_value, expected)
                        test_result[returned_tuple[0]].append(returned_tuple[1])

                self._last_check_output_result = test_result
                if len(test_result[FAILED_TEST]) >= 1:
                    self._display.display(msg=str(test_result), color=C.COLOR_ERROR)
                    self.exit_playbook()
                    return
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

        self._compare_boolean_to_config(task_name=self._last_task_name,
                                        config_flag_name="should_failed",
                                        task_config=self._last_task_config,
                                        actual_state=task_has_actually_failed)

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
                    self.exit_playbook()
                    return False
                self._display.display(msg=message, color=C.COLOR_OK)
                return True

    @staticmethod
    def exit_playbook():
        sys.exit(1)
