# Copyright 2022 Hewlett Packard Enterprise Development LP
import unittest
from unittest.mock import MagicMock

from plugins.module_utils.const import PASSED_TEST, FAILED_TEST
from plugins.module_utils.utils import MonkeybleUnsupportedTest, switch_test_method, get_task_config


class TestMonkeybleUtils(unittest.TestCase):

    def test_invalid_test_name(self):
        with self.assertRaises(MonkeybleUnsupportedTest):
            switch_test_method("non_existing", "value", "other_value")

    def _do_test(self, expected_test_state, test_name, tested_value, expected):
        json_output = (expected_test_state, {
            "test_name": test_name,
            "tested_value": tested_value,
            "expected": expected
        })
        self.assertEqual(json_output, switch_test_method(test_name, tested_value, expected))

    def test_assert_equal(self):
        test_name = "assert_equal"
        tested_value = "value"

        # test OK
        expected = "value"
        expected_test_state = PASSED_TEST
        self._do_test(expected_test_state, test_name, tested_value, expected)

        # test NOK
        expected = "value_diff"
        expected_test_state = FAILED_TEST
        self._do_test(expected_test_state, test_name, tested_value, expected)

    def test_assert_not_equal(self):
        test_name = "assert_not_equal"
        tested_value = "value"

        # test OK
        expected = "value_diff"
        expected_test_state = PASSED_TEST
        self._do_test(expected_test_state, test_name, tested_value, expected)

        # test NOK
        expected = "value"
        expected_test_state = FAILED_TEST
        self._do_test(expected_test_state, test_name, tested_value, expected)

    def test_assert_in(self):
        test_name = "assert_in"

        # test OK with string
        tested_value = "val"
        expected = "value"
        expected_test_state = PASSED_TEST
        self._do_test(expected_test_state, test_name, expected, tested_value)

        # test NOK with string
        tested_value = "value"
        expected = "not_here"
        expected_test_state = FAILED_TEST
        self._do_test(expected_test_state, test_name, expected, tested_value)

        # test OK with list
        tested_value = "value"
        expected = ["value", "other_val"]
        expected_test_state = PASSED_TEST
        self._do_test(expected_test_state, test_name, expected, tested_value)

        # test NOK with list
        tested_value = "value"
        expected = ["not_here", "other_val"]
        expected_test_state = FAILED_TEST
        self._do_test(expected_test_state, test_name, expected, tested_value)

    def test_assert_not_in(self):
        # note: for this test, the first attribute (expected) is the member
        # the second attribute (tested_value) is the container
        test_name = "assert_not_in"
        tested_value = "value"

        # test OK with string
        expected = "value_and_more"
        expected_test_state = FAILED_TEST
        self._do_test(expected_test_state, test_name, expected, tested_value)

        # test OK with list
        expected = ["value", "other_val"]
        expected_test_state = FAILED_TEST
        self._do_test(expected_test_state, test_name, expected, tested_value)

        # test NOK with string
        expected = "not_here"
        expected_test_state = PASSED_TEST
        self._do_test(expected_test_state, test_name, expected, tested_value)

        # test NOK with list
        expected = ["not_here", "other_val"]
        expected_test_state = PASSED_TEST
        self._do_test(expected_test_state, test_name, expected, tested_value)

    def test_assert_true(self):
        test_name = "assert_true"
        expected = True
        # test OK
        tested_values = ["True", "true", True, 1]
        for tested_value in tested_values:
            expected_test_state = PASSED_TEST
            self._do_test(expected_test_state, test_name, tested_value, expected)

        # test NOK
        tested_values = ["False", "false", False, 0]
        for tested_value in tested_values:
            expected_test_state = FAILED_TEST
            self._do_test(expected_test_state, test_name, tested_value, expected)

    def test_assert_false(self):
        test_name = "assert_false"
        expected = False

        # test OK
        tested_values = ["True", "true", True, 1]
        for tested_value in tested_values:
            expected_test_state = FAILED_TEST
            self._do_test(expected_test_state, test_name, tested_value, expected)

        # test NOK
        tested_values = ["False", "false", False, 0]
        for tested_value in tested_values:
            expected_test_state = PASSED_TEST
            self._do_test(expected_test_state, test_name, tested_value, expected)

    def test_assert_is_none(self):
        test_name = "assert_is_none"
        expected = None

        # test OK
        tested_value = None
        expected_test_state = PASSED_TEST
        self._do_test(expected_test_state, test_name, tested_value, expected)

        # test OK
        tested_value = "value"
        expected_test_state = FAILED_TEST
        self._do_test(expected_test_state, test_name, tested_value, expected)

    def test_assert_is_not_none(self):
        test_name = "assert_is_not_none"
        expected = None

        # test OK
        tested_value = None
        expected_test_state = FAILED_TEST
        self._do_test(expected_test_state, test_name, tested_value, expected)

        # test OK
        tested_value = "value"
        expected_test_state = PASSED_TEST
        self._do_test(expected_test_state, test_name, tested_value, expected)

    def test_assert_list_equal(self):
        test_name = "assert_list_equal"
        expected = ["a", "list"]

        # test OK
        tested_value = ["a", "list"]
        expected_test_state = PASSED_TEST
        self._do_test(expected_test_state, test_name, tested_value, expected)

        # test NOK
        tested_value = ["another", "list"]
        expected_test_state = FAILED_TEST
        self._do_test(expected_test_state, test_name, tested_value, expected)

        tested_value = "a string"
        expected_test_state = FAILED_TEST
        self._do_test(expected_test_state, test_name, tested_value, expected)

    def test_assert_dict_equal(self):
        test_name = "assert_dict_equal"
        expected = {"key": "value"}

        # test OK
        tested_value = {"key": "value"}
        expected_test_state = PASSED_TEST
        self._do_test(expected_test_state, test_name, tested_value, expected)

        # test NOK
        tested_value = {"key": "other_value"}
        expected_test_state = FAILED_TEST
        self._do_test(expected_test_state, test_name, tested_value, expected)

        tested_value = "a string"
        expected_test_state = FAILED_TEST
        self._do_test(expected_test_state, test_name, tested_value, expected)

    def test_get_task_config_task_name_does_not_match(self):
        ansible_task = MagicMock()
        ansible_task.get_name.return_value = "test"
        monkeyble_config = {"name": "Validate this",
                            "tasks_to_test": [{"task": "task_name_test"}]
                            }
        result = get_task_config(ansible_task=ansible_task, monkeyble_config=monkeyble_config)
        self.assertIsNone(result)

    def test_get_task_config_task_name_match(self):
        ansible_task = MagicMock()
        ansible_task._role._role_name = None
        ansible_task.name = "task_name_test"
        monkeyble_config = {"name": "Validate this",
                            "tasks_to_test": [{"task": "task_name_test"}]
                            }
        result = get_task_config(ansible_task=ansible_task, monkeyble_config=monkeyble_config)
        expected = {"task": "task_name_test"}
        self.assertDictEqual(result, expected)

    def test_get_task_config_task_role_filter(self):
        ansible_task = MagicMock()
        ansible_task.name = "task_name_test"
        ansible_task._role._role_name = "role_name_test"
        monkeyble_config = {"name": "Validate this",
                            "tasks_to_test": [{"task": "task_name_test",
                                               "role": "role_name_test"}]
                            }

        result = get_task_config(ansible_task=ansible_task, monkeyble_config=monkeyble_config)
        expected = {"task": "task_name_test",
                    "role": "role_name_test"}
        self.assertDictEqual(result, expected)

        # test with a different role name
        ansible_task._role._role_name = "another_role_name"
        result = get_task_config(ansible_task=ansible_task, monkeyble_config=monkeyble_config)
        self.assertIsNone(result)

    def test_get_task_config_task_play_filter(self):
        ansible_task = MagicMock()
        ansible_task._role._role_name = None
        ansible_task.name = "task_name_test"
        ansible_task.play.name = "play_name_test"
        monkeyble_config = {"name": "Validate this",
                            "tasks_to_test": [{"task": "task_name_test",
                                               "play": "play_name_test"}]
                            }

        result = get_task_config(ansible_task=ansible_task, monkeyble_config=monkeyble_config)
        expected = {"task": "task_name_test",
                    "play": "play_name_test"}
        self.assertDictEqual(result, expected)

        # test with a different role name
        ansible_task.play.name = "another_play_name"
        result = get_task_config(ansible_task=ansible_task, monkeyble_config=monkeyble_config)
        self.assertIsNone(result)
