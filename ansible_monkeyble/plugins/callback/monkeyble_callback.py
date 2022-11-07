import os
import sys
from copy import copy

from ansible.errors import AnsibleError
from ansible.parsing.dataloader import DataLoader
from ansible.plugins.callback import CallbackBase
from ansible import constants as C
from ansible.template import Templar

from ansible_monkeyble.plugins.strategy.const import PASSED_TEST, FAILED_TEST

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../..')
)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ansible_monkeyble.plugins.strategy.utils import str_to_bool, switch_test_method


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

    def v2_playbook_on_play_start(self, play):
        vm = play.get_variable_manager()
        extra_vars = vm.extra_vars
        monkeyble_scenario = extra_vars.get("monkeyble_scenario")
        monkeyble_scenarios = extra_vars.get("monkeyble_scenarios")
        print(f"Monkeyble callback init")
        self.monkeyble_config = monkeyble_scenarios[monkeyble_scenario]

    def v2_runner_on_unreachable(self, result):
        host = result._host
        self.host_unreachable[host.get_name()] = result

    def v2_runner_on_ok(self, result, *args, **kwargs):
        """Print a json representation of the result.

        Also, store the result in an instance attribute for retrieval later
        """
        host = result._host
        self.host_ok[host.get_name()] = result
        task_name = copy(result._task.name)
        if result.is_changed():
            self.changed_task_list.append(task_name)
        # check if the task should have been skipped instead of being ok
        self.check_if_task_should_have_been_skipped(ansible_task=result._task, task_has_been_actually_skipped=False)
        # check result
        self.check_output(ansible_task=result._task, result_dict=result._result)

    def v2_runner_on_failed(self, result, *args, **kwargs):
        host = result._host
        self.host_failed[host.get_name()] = result
        # print(json.dumps({host.name: result._result}, indent=4))

    def v2_runner_on_skipped(self, result, **kwargs):
        print("Run v2_runner_on_skipped")
        task_name = result._task.name
        # play_name = result._task.play.name
        # role_name = None
        # if result._task._role is not None:
        #     role_name = result._task._role._role_name
        self.skipped_task_list.append(task_name)
        self.check_if_task_should_have_been_skipped(task_has_been_actually_skipped=True, ansible_task=result._task)

    def check_if_task_should_have_been_skipped(self, ansible_task, task_has_been_actually_skipped=False):
        task_name = ansible_task.name
        play_name = ansible_task.play.name
        role_name = None
        print(f"check_if_task_should_have_been_skipped task: {task_name}")
        print(f"check_if_task_should_have_been_skipped play: {play_name}")
        print(f"check_if_task_should_have_been_skipped role: {role_name}")
        if ansible_task._role is not None:
            role_name = ansible_task._role._role_name
        for task_config in self.monkeyble_config["tasks_to_test"]:
            if task_config["task"] == task_name:
                # we've found a task name
                if "play" in task_config:
                    if task_config["play"] != play_name:
                        return None
                if "role" in task_config:
                    if role_name is None or task_config["role"] != role_name:
                        return None
                if "should_be_skipped" in task_config:
                    should_be_skipped = str_to_bool(task_config["should_be_skipped"])
                    print(f"should_be_skipped: {should_be_skipped}")
                    print(f"have been actually skipped:: {task_has_been_actually_skipped}")
                    if should_be_skipped:
                        if not task_has_been_actually_skipped:
                            message = f"The task '{task_name}' should have been skipped"
                            self._display.display(msg=message, color=C.COLOR_ERROR)
                            sys.exit(1)
                    if not should_be_skipped:
                        if task_has_been_actually_skipped:
                            message = f"The task '{task_name}' should not have been skipped"
                            self._display.display(msg=message, color=C.COLOR_ERROR)
                            sys.exit(1)

    def check_output(self, ansible_task, result_dict):
        task_name = ansible_task.name
        play_name = ansible_task.play.name
        role_name = None
        print(f"check_if_task_should_have_been_skipped task: {task_name}")
        print(f"check_if_task_should_have_been_skipped play: {play_name}")
        print(f"check_if_task_should_have_been_skipped role: {role_name}")
        if ansible_task._role is not None:
            role_name = ansible_task._role._role_name
        for task_config in self.monkeyble_config["tasks_to_test"]:
            if task_config["task"] == task_name:
                # we've found a task name
                if "play" in task_config:
                    if task_config["play"] != play_name:
                        return None
                if "role" in task_config:
                    if role_name is None or task_config["role"] != role_name:
                        return None
                if "test_output" in task_config:
                    test_result = {
                        PASSED_TEST: [],
                        FAILED_TEST: []
                    }
                    for result_value_to_test in task_config["test_output"]:
                        for test_name, result_value_and_expected in result_value_to_test.items():
                            result_value = result_value_and_expected['result_value']
                            # template the result to get the real value
                            template_string = "{{  " + result_value + "  }}"
                            context = {
                                "result": result_dict
                            }
                            templar = Templar(loader=DataLoader(), variables=context)
                            templated_value = templar.template(template_string)
                            expected = result_value_and_expected['expected']
                            returned_tuple = switch_test_method(test_name, templated_value, expected)
                            test_result[returned_tuple[0]].append(returned_tuple[1])

                    print(test_result)
                    if len(test_result[FAILED_TEST]) >= 1:
                        self._display.display(msg=str(test_result), color=C.COLOR_ERROR)
                        sys.exit(1)
                    self._display.display(msg=test_result, color=C.COLOR_OK)
                    return test_result
