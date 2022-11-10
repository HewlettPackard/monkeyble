import unittest
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
