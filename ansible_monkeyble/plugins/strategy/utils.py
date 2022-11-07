import unittest

from ansible.errors import AnsibleError
from ansible_monkeyble.plugins.strategy.const import *


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
        raise MonkeybleUnsupportedTest(message=f"Test name '{test_name}' is not supported")
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
            test_case.assertIn(tested_value, expected)
        if test_name == "assert_not_in":
            test_case.assertNotIn(tested_value, expected)
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
        print(f"{test_name} failed. tested_value: {tested_value}. expected: {expected}")
        return FAILED_TEST, json_output
