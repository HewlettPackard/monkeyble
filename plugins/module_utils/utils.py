# Copyright 2022 Hewlett Packard Enterprise Development LP
import unittest

from ansible.errors import AnsibleError
from ansible.playbook.task import Task

from plugins.module_utils.const import *
from plugins.module_utils.exceptions import MonkeybleException


class MonkeybleUnsupportedTest(AnsibleError):
    pass


def str_to_bool(s):
    if isinstance(s, bool):  # do not convert if already a boolean
        return s
    else:
        if s == 'True' \
                or s == 'true' \
                or s == '1' \
                or s == 1 \
                or s == True:
            return True
        elif s == 'False' \
                or s == 'false' \
                or s == '0' \
                or s == 0 \
                or s == False:
            return False
    return False


def switch_test_method(test_name, tested_value, expected=None):
    if test_name not in SUPPORTED_TEST:
        raise MonkeybleUnsupportedTest(message=f"Test name '{test_name}' is not supported. "
                                               f"Supported tests: {SUPPORTED_TEST}")
    json_output = {
        "test_name": test_name,
        "tested_value": tested_value,
        "expected": expected
    }
    if test_name == "assert_true":
        json_output.update({"expected": True})
    if test_name == "assert_false":
        json_output.update({"expected": False})
    test_case = unittest.case.TestCase()
    try:
        if test_name == "assert_equal":
            test_case.assertEqual(tested_value, expected)
        if test_name == "assert_not_equal":
            test_case.assertNotEqual(tested_value, expected)
        if test_name == "assert_in":
            # assertIn(member, container)
            test_case.assertIn(expected, tested_value)
        if test_name == "assert_not_in":
            # assertNotIn(member, container)
            test_case.assertNotIn(expected, tested_value)
        if test_name == "assert_true":
            test_case.assertTrue(str_to_bool(tested_value))
        if test_name == "assert_false":
            test_case.assertFalse(str_to_bool(tested_value))
        if test_name == "assert_is_none":
            test_case.assertIsNone(tested_value)
        if test_name == "assert_is_not_none":
            test_case.assertIsNotNone(tested_value)
        if test_name == "assert_list_equal":
            test_case.assertListEqual(tested_value, expected)
        if test_name == "assert_dict_equal":
            test_case.assertDictEqual(tested_value, expected)
        return PASSED_TEST, json_output
    except AssertionError:
        return FAILED_TEST, json_output


def get_task_config(ansible_task: Task, monkeyble_config: dict):
    """
    Check if the task name is present in the Monkey config of the current strategy
    Return the config if:
    - the config exist
    - if the role filter is ok
    - if the play filter is ok
    :ansible_task: AnsibleTask object
    :ty
    """
    task_name = ansible_task.name
    play_name = ansible_task.play.name
    role_name = None
    # print(f"get_task_config task: {task_name}")
    # print(f"get_task_config play: {play_name}")
    if ansible_task._role is not None:
        role_name = ansible_task._role._role_name
    # print(f"get_task_config role: {role_name}")
    if "tasks_to_test" in monkeyble_config:
        # we add global task at the end the list of task
        if "monkeyble_shared_tasks" in monkeyble_config:
            monkeyble_config["tasks_to_test"].extend(monkeyble_config["monkeyble_shared_tasks"])
        for task_config in monkeyble_config["tasks_to_test"]:
            if "task" not in task_config:
                raise MonkeybleException(message=str("Monkeyble error: Task name need to be set"))
            name_to_test = task_config["task"]
            if name_to_test == task_name:
                # we've found a task name
                if "play" in task_config:
                    if task_config["play"] != play_name:
                        return None
                if "role" in task_config:
                    if role_name is None or task_config["role"] != role_name:
                        return None
                return task_config
    return None
