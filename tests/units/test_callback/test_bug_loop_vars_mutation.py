import unittest
from tests.units.test_callback.base_test_callback import BaseTestMonkeybleCallback


class TestBug4PlaybookVarsMutationInLoop(BaseTestMonkeybleCallback):
    """Bug: playbook_vars.update() in loop test mutates the caller's dict.

    Location: monkeyble_callback.py:352
    """

    def setUp(self):
        super().setUp()
        self.test_callback._last_task_config = {
            "task": "test_task",
            "test_input": [
                {"assert_equal": {"arg_name": "msg", "expected": "hello world"}}
            ],
        }

    def test_playbook_vars_not_mutated_after_loop_test(self):
        """playbook_vars passed to test_input should not be modified by loop processing."""
        self.ansible_task_test.loop = ["world", "mars"]
        self.ansible_task_test.args = {"msg": "hello {{ item }}"}

        playbook_vars = {"existing_var": "keep_me"}
        original_keys = set(playbook_vars.keys())

        self.test_callback.test_input(
            self.ansible_task_test, playbook_vars=playbook_vars
        )

        self.assertEqual(
            set(playbook_vars.keys()),
            original_keys,
            f"playbook_vars was mutated by test_input loop processing. "
            f"Extra keys added: {set(playbook_vars.keys()) - original_keys}",
        )


if __name__ == "__main__":
    unittest.main()
