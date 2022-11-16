# Copyright 2022 Hewlett Packard Enterprise Development LP
from unittest.mock import MagicMock

from tests.units.test_callback.base_test_callback import BaseTestMonkeybleCallback


class TestMonkeybleCallbackMock(BaseTestMonkeybleCallback):

    def setUp(self) -> None:
        super(TestMonkeybleCallbackMock, self).setUp()

        self.ansible_task_test = MagicMock()
        self.ansible_task_test.name = "test_task"
        self.ansible_task_test.get_name.return_value = "test_task"
        self.ansible_task_test.action = "debug"
        self.ansible_task_test.args = {
            "msg": "my_message"
        }

    def test_mock_task_module(self):
        mock_config_test = {
            "monkeyble_module": {
                "consider_changed": True,
                "result_dict": {
                    "msg": "output_value"
                }
            }
        }
        self.test_callback._last_task_config["mock"] = dict()
        self.test_callback._last_task_config["mock"]["config"] = mock_config_test

        update_ansible_task = self.test_callback.mock_task_module(self.ansible_task_test)
        self.assertEqual("test_task", update_ansible_task.name)
        self.assertEqual("debug", update_ansible_task.args["original_module_name"])
        self.assertTrue(update_ansible_task.args["consider_changed"])
        expected_result_dict = {
            "msg": "output_value"
        }
        self.assertDictEqual(expected_result_dict, update_ansible_task.args["result_dict"])
        expected_original_module_args = {
            "msg": "my_message"
        }
        self.assertDictEqual(expected_original_module_args, update_ansible_task.args["original_module_args"])

    def test_mock_task_module_default_config(self):
        mock_config_test = {
            "monkeyble_module": {}
        }
        self.test_callback._last_task_config["mock"] = dict()
        self.test_callback._last_task_config["mock"]["config"] = mock_config_test
        update_ansible_task = self.test_callback.mock_task_module(self.ansible_task_test)
        self.assertEqual("test_task", update_ansible_task.name)
        self.assertEqual("debug", update_ansible_task.args["original_module_name"])
        self.assertFalse(update_ansible_task.args["consider_changed"])
        expected_result_dict = {}
        self.assertDictEqual(expected_result_dict, update_ansible_task.args["result_dict"])
        expected_original_module_args = {
            "msg": "my_message"
        }
        self.assertDictEqual(expected_original_module_args, update_ansible_task.args["original_module_args"])
