import os
import sys

from ansible.errors import AnsibleError, AnsibleAssertionError
from ansible.plugins.strategy.linear import StrategyModule as LinearStrategyModule
from ansible.template import Templar
from ansible.utils.display import Display
from ansible import constants as C

from ansible_monkeyble.plugins.strategy.const import PASSED_TEST, FAILED_TEST
from ansible_monkeyble.plugins.strategy.utils import switch_test_method, get_task_config

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


class StrategyModule(LinearStrategyModule):
    def __init__(self, tqm):
        super(StrategyModule, self).__init__(tqm)
        self.monkeyble_config = None
        self._last_check_input_result = dict()

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
        display.display(f"Monkeyble selected scenario: {monkeyble_scenario}", color=C.COLOR_OK)

        # template the scenario with extra vars
        templar = Templar(loader=self._loader, variables=iterator._variable_manager._extra_vars)
        self.monkeyble_config = templar.template(self.monkeyble_config)

        if "name" in self.monkeyble_config:
            display.display(f"Monkeyble: {self.monkeyble_config['name']}", color=C.COLOR_OK)

        # call default Ansible Linear Strategy
        return super(StrategyModule, self).run(iterator, play_context)

    def _queue_task(self, host, task, task_vars, play_context):
        display.debug("Monkeyble strategy _queue_task called")

        # get the Monkeyble task config if exist
        task_config = get_task_config(ansible_task=task, monkeyble_config=self.monkeyble_config)

        if task_config is not None:
            # apply extra vars from the tested task
            if "extra_vars" in task_config:
                task_vars.update(task_config["extra_vars"])

            # get all vars
            templar = Templar(loader=self._loader, variables=task_vars)
            templated_module_args = templar.template(task.args)

            # check input
            if "test_input" in task_config:
                result = self.check_input(task_config["test_input"], ansible_task_args=templated_module_args)
                if len(result[FAILED_TEST]) >= 1:
                    self._display.display(msg=str(result), color=C.COLOR_ERROR)
                    raise MonkeybleTestFailed(message=str(result))
                self._display.display(msg=str(result), color=C.COLOR_CHANGED)

            if "mock" in task_config:
                task = self.mock_task_module(task_config["mock"], ansible_task=task)

        super(StrategyModule, self)._queue_task(host, task, task_vars, play_context)

    def mock_task_module(self, mock_config, ansible_task):
        new_action_name = next(iter(mock_config["config"]))
        original_module_name = ansible_task.action
        msg = f"Monkeyble mock module - Before: '{original_module_name}' Now: '{new_action_name}'"
        self._display.display(msg=str(msg), color=C.COLOR_CHANGED)
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
