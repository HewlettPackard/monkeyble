import os
import sys
import unittest

from ansible.errors import AnsibleError, AnsibleAssertionError
from ansible.plugins.strategy.linear import StrategyModule as LinearStrategyModule
from ansible.template import Templar
from ansible.utils.display import Display

from ansible_monkeyble.plugins.strategy.const import PASSED_TEST, FAILED_TEST
from ansible_monkeyble.plugins.strategy.utils import str_to_bool, switch_test_method

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../..')
)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


display = Display()


class MonkeybleTestFailed(AnsibleError):
    pass


class MonkeybleConfigError(AnsibleError):
    pass


def get_task_config(play_name=None, role_name=None, task_name=None, monkeyble_config=None):
    """
    Check if the 'task_name' is present in the config.
    Return the config mapped in 'mocks' if:
    - the config exist
    - if the role is the right one
    - if the play is the right one
    """
    for task_config in monkeyble_config["tasks_to_test"]:
        if task_config["task"] == task_name:
            # we've found a task name. Check play and role filter
            if "play" in task_config:
                if task_config["play"] != play_name:
                    return None
            if "role" in task_config:
                if role_name is None or task_config["role"] != role_name:
                    return None
            return task_config
    return None


class StrategyModule(LinearStrategyModule):
    def __init__(self, tqm):
        super(StrategyModule, self).__init__(tqm)
        self.monkeyble_config = None

    def run(self, iterator, play_context, result=0):
        display.debug("Execute Monkeyble strategy")

        # check if a scenario has been given
        monkeyble_scenario = iterator._variable_manager._extra_vars.get("monkeyble_scenario")
        monkeyble_scenarios = iterator._variable_manager._extra_vars.get("monkeyble_scenarios")
        if monkeyble_scenario is None:
            raise AnsibleAssertionError("'monkeyble_scenario' need to be passed as extra_vars")
        if monkeyble_scenarios is None:
            raise AnsibleAssertionError("'monkeyble_scenarios' need to be passed as extra_vars")

        # template Monkeyble config
        try:
            self.monkeyble_config = monkeyble_scenarios[monkeyble_scenario]
        except KeyError:
            raise AnsibleAssertionError(f"The Monkeyble scenario name'{monkeyble_scenario}' "
                                        f"not found in 'monkeyble_scenarios'")
        print(f"Monkeyble selected scenario: {monkeyble_scenario}")
        # template the scenario with extra vars
        templar = Templar(loader=self._loader, variables=iterator._variable_manager._extra_vars)
        self.monkeyble_config = templar.template(self.monkeyble_config)
        print(self.monkeyble_config)

        # # apply extra vars from task config
        # if "extra_vars" in self.monkeyble_config:
        #     iterator._variable_manager._extra_vars.update(self.monkeyble_config["extra_vars"])

        # call default Ansible Linear Strategy
        return super(StrategyModule, self).run(iterator, play_context)

    def mock_task_module(self, mock_config, ansible_task):
        new_action_name = next(iter(mock_config["config"]))
        original_module_name = ansible_task.action
        print(f"Monkeyble mock module - Before: '{original_module_name}' Now: '{new_action_name}'")
        ansible_task.action = new_action_name
        if new_action_name == "monkeyble_module":
            original_module_args = ansible_task.args
            ansible_task.args = {"task_name": ansible_task.name,
                                 "original_module_name": original_module_name,
                                 "original_module_args": original_module_args,
                                 "consider_changed": mock_config.get("changed", False),
                                 "result_dict": mock_config.get("result_dict", {})
                                 }
            ansible_task.args.update(mock_config["config"][new_action_name])
        # TODO test with custom module
        return ansible_task

    def _queue_task(self, host, task, task_vars, play_context):
        display.debug("Monkeyble strategy _queue_task called")
        print("Monkeyble strategy _queue_task called")

        task_name = task.name
        play_name = task.play.name
        role_name = None
        if task._role is not None:
            role_name = task._role._role_name
        print(f"Play name: {play_name}")
        print(f"Role name: {role_name}")
        print(f"Task name: {task_name}")

        # update task if
        task_config = get_task_config(play_name=play_name,
                                      task_name=task_name,
                                      role_name=role_name,
                                      monkeyble_config=self.monkeyble_config)

        if task_config is not None:
            # TODO apply extra vars

            # get all vars
            templar = Templar(loader=self._loader, variables=task_vars)
            templated_module_args = templar.template(task.args)

            # check input
            if "test_input" in task_config:
                self.check_input(task_config["test_input"], ansible_task_args=templated_module_args)

            if "mock" in task_config:
                task = self.mock_task_module(task_config["mock"], ansible_task=task)

        super(StrategyModule, self)._queue_task(host, task, task_vars, play_context)

    @staticmethod
    def check_input(test_input_list, ansible_task_args):
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
                expected = value_and_expected['expected']
                returned_tuple = switch_test_method(test_name, argument_value, expected)
                test_result[returned_tuple[0]].append(returned_tuple[1])

        print(test_result)
        if len(test_result[FAILED_TEST]) >= 1:
            raise MonkeybleTestFailed(message=str(test_result))
        return test_result
