from unittest.mock import patch

from ansible_monkeyble.plugins.callback.monkeyble_callback import MonkeybleException
from tests.units.test_callback.base_test_callback import BaseTestMonkeybleCallback


class TestMonkeybleCallback(BaseTestMonkeybleCallback):

    def setUp(self) -> None:
        super(TestMonkeybleCallback, self).setUp()

    @patch('sys.exit')
    def test_compare_boolean_to_config(self, mock_exit):
        task_name = "test_task"
        config_flag_name = "a_boolean_flag"

        # Test when actual value and config value are true
        task_config = {
            "task": "test_task",
            "a_boolean_flag": "true"
        }
        actual_state = True
        self.assertTrue(self.test_callback._compare_boolean_to_config(task_name, config_flag_name,
                                                                      task_config, actual_state))
        task_config = {
            "task": "test_task",
            "a_boolean_flag": True
        }
        self.assertTrue(self.test_callback._compare_boolean_to_config(task_name, config_flag_name,
                                                                      task_config, actual_state))

        # Test config is False and actual state is False
        actual_state = False
        task_config = {
            "task": "test_task",
            "a_boolean_flag": False
        }
        self.assertTrue(self.test_callback._compare_boolean_to_config(task_name, config_flag_name,
                                                                      task_config, actual_state))

        # Test config is True and actual state is False
        actual_state = False
        task_config = {
            "task": "test_task",
            "a_boolean_flag": True
        }
        with self.assertRaises(MonkeybleException):
            self.test_callback._compare_boolean_to_config(task_name, config_flag_name, task_config, actual_state)
            mock_exit.assert_called()

        # Test config is False and actual state is True
        actual_state = True
        task_config = {
            "task": "test_task",
            "a_boolean_flag": False
        }
        with self.assertRaises(MonkeybleException):
            self.test_callback._compare_boolean_to_config(task_name, config_flag_name, task_config, actual_state)
            mock_exit.assert_called()
