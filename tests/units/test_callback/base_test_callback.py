# Copyright 2022 Hewlett Packard Enterprise Development LP
import unittest
from unittest.mock import MagicMock

from ansible_monkeyble.plugins.callback.monkeyble_callback import CallbackModule as MonkeybleCallbackModule


class BaseTestMonkeybleCallback(unittest.TestCase):

    def setUp(self) -> None:
        self.test_callback = MonkeybleCallbackModule()
        self.test_callback._last_task_name = "test_task"
        self.test_callback._last_task_config = {
            "task": "test_task",
            "test_output": [
                {
                    "assert_equal": {
                        "result_key": "result.key1",
                        "expected": "value1"
                    }
                }
            ]
        }

        self.play = MagicMock()
        self.var_manager = MagicMock()
        self.play.get_variable_manager.return_value = self.var_manager

        self.ansible_task_test = MagicMock()
        self.ansible_task_test.name = "test_task"
        self.ansible_task_test.get_name.return_value = "test_task"
        self.ansible_task_test.action = "debug"
        self.ansible_task_test.args = {
            "msg": "my_message"
        }
