import unittest

from ansible_monkeyble.plugins.strategy.const import PASSED_TEST, FAILED_TEST
from ansible_monkeyble.plugins.strategy.monkeyble_linear import MonkeybleUnsupportedTest, switch_test_method


class TestMonkeybleModule(unittest.TestCase):

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
        tested_value = "value"

        # test OK with string
        expected = "value_and_more"
        expected_test_state = PASSED_TEST
        self._do_test(expected_test_state, test_name, tested_value, expected)

        # test OK with list
        expected = ["value", "other_val"]
        expected_test_state = PASSED_TEST
        self._do_test(expected_test_state, test_name, tested_value, expected)

        # test NOK with string
        expected = "not_here"
        expected_test_state = FAILED_TEST
        self._do_test(expected_test_state, test_name, tested_value, expected)

        # test NOK with list
        expected = ["not_here", "other_val"]
        expected_test_state = FAILED_TEST
        self._do_test(expected_test_state, test_name, tested_value, expected)

    def test_assert_not_in(self):
        test_name = "assert_not_in"
        tested_value = "value"

        # test OK with string
        expected = "value_and_more"
        expected_test_state = FAILED_TEST
        self._do_test(expected_test_state, test_name, tested_value, expected)

        # test OK with list
        expected = ["value", "other_val"]
        expected_test_state = FAILED_TEST
        self._do_test(expected_test_state, test_name, tested_value, expected)

        # test NOK with string
        expected = "not_here"
        expected_test_state = PASSED_TEST
        self._do_test(expected_test_state, test_name, tested_value, expected)

        # test NOK with list
        expected = ["not_here", "other_val"]
        expected_test_state = PASSED_TEST
        self._do_test(expected_test_state, test_name, tested_value, expected)

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
