import io
import os
import unittest
from unittest import mock
from unittest.mock import patch, mock_open, call

from monkeyble.cli.const import TEST_PASSED, TEST_FAILED, MONKEYBLE_DEFAULT_ANSIBLE_CMD
from monkeyble.cli.exceptions import MonkeybleCLIException

from monkeyble.cli.models import MonkeybleResult, ScenarioResult

from monkeyble.cli.monkeyble_cli import load_monkeyble_config, do_exit, run_monkeyble_test, run_ansible


class TestMonkeybleModule(unittest.TestCase):

    def test_load_monkeyble_config_default_config(self):
        with patch("builtins.open", mock_open(read_data="data")) as mock_open_file:
            load_monkeyble_config(None)
        mock_open_file.assert_called_with("monkeyble.yml", 'r')

    @mock.patch.dict(os.environ, {"MONKEYBLE_CONFIG": "monkeyble_from_env.yml"})
    def test_load_monkeyble_config_from_env(self):
        with patch("builtins.open", mock_open(read_data="data")) as mock_open_file:
            load_monkeyble_config(None)
        mock_open_file.assert_called_with("monkeyble_from_env.yml", 'r')

    def test_load_monkeyble_config_from_args(self):
        with patch("builtins.open", mock_open(read_data="data")) as mock_open_file:
            load_monkeyble_config("/path/to/monkeyble.yml")
        mock_open_file.assert_called_with("/path/to/monkeyble.yml", 'r')

    @patch("monkeyble.cli.monkeyble_cli.MONKEYBLE_DEFAULT_CONFIG_PATH", "test_config/monkeyble.yml")
    def test_load_monkeyble_config(self):
        data = load_monkeyble_config(None)
        expected = {'monkeyble_test_suite': [{'playbook': 'test_playbook.yml',
                                              'inventory': 'inventory',
                                              'extra_vars': ['mocks.yml', 'monkeyble_scenarios.yml'],
                                              'scenarios': ['validate_test_1', 'validate_test_2']}]}

        self.assertDictEqual(data, expected)

    @patch('sys.exit')
    def test_do_exit_all_test_passed(self, mock_exit):
        scenario_result1 = ScenarioResult(scenario="scenario1", result=TEST_PASSED)
        scenario_result2 = ScenarioResult(scenario="scenario2", result=TEST_PASSED)
        monkeyble_result = MonkeybleResult(playbook="playbook", scenario_results=[scenario_result1, scenario_result2])

        do_exit([monkeyble_result])
        mock_exit.assert_called_with(0)

    @patch('sys.exit')
    def test_do_exit_all_test_failed(self, mock_exit):
        scenario_result1 = ScenarioResult(scenario="scenario1", result=TEST_PASSED)
        scenario_result2 = ScenarioResult(scenario="scenario2", result=TEST_FAILED)
        monkeyble_result = MonkeybleResult(playbook="playbook", scenario_results=[scenario_result1, scenario_result2])

        do_exit([monkeyble_result])
        mock_exit.assert_called_with(1)

    @patch('sys.exit')
    def test_run_monkeyble_test_no_tests_defined(self, mock_exit):
        monkeyble_config = dict()
        with self.assertRaises(MonkeybleCLIException):
            run_monkeyble_test(monkeyble_config)
            mock_exit.assert_called_with(1)

    @patch('sys.exit')
    def test_run_monkeyble_test_no_playbook_defined(self, mock_exit):
        monkeyble_config = {
            "monkeyble_test_suite": [
                {"inventory": "test"}
            ]
        }
        with self.assertRaises(MonkeybleCLIException):
            run_monkeyble_test(monkeyble_config)
            mock_exit.assert_called_with(1)

    @patch('sys.exit')
    def test_run_monkeyble_test_no_scenario_defined(self, mock_exit):
        monkeyble_config = {
            "monkeyble_test_suite": [
                {"playbook": "playbook.yml"}
            ]
        }
        with self.assertRaises(MonkeybleCLIException):
            run_monkeyble_test(monkeyble_config)
            mock_exit.assert_called_with(1)

    def test_run_monkeyble_test_run_ansible_called(self):
        monkeyble_config = {
            "monkeyble_test_suite": [
                {
                    "playbook": "playbook.yml",
                    "inventory": "my_inventory",
                    "extra_vars": ["extra_vars1.yml", "extra_vars2.yml"],
                    "scenarios": ["scenario1", "scenario2"]
                }
            ]
        }

        with mock.patch("monkeyble.cli.monkeyble_cli.run_ansible") as mock_run_ansible:
            run_monkeyble_test(monkeyble_config)
            self.assertEqual(mock_run_ansible.call_count, 2)
            call_1 = call(MONKEYBLE_DEFAULT_ANSIBLE_CMD,
                          "playbook.yml",
                          "my_inventory",
                          ["extra_vars1.yml", "extra_vars2.yml"],
                          "scenario1")
            call_2 = call(MONKEYBLE_DEFAULT_ANSIBLE_CMD,
                          "playbook.yml",
                          "my_inventory",
                          ["extra_vars1.yml", "extra_vars2.yml"],
                          "scenario2")
            mock_run_ansible.assert_has_calls([call_1, call_2])

    @patch("subprocess.Popen")
    def test_run_ansible(self, mock_subproc_popen):
        mock_subproc_popen.return_value.stdout = io.BytesIO(b"playbook output")

        run_ansible(MONKEYBLE_DEFAULT_ANSIBLE_CMD,
                    "playbook.yml",
                    "my_inventory",
                    ["extra_vars1.yml", "extra_vars2.yml"],
                    "scenario1")
        self.assertTrue(mock_subproc_popen.called)

        expected_call = call(['ansible-playbook', 'playbook.yml', '-i', 'my_inventory',
                              '-e', '@extra_vars1.yml', '-e', '@extra_vars2.yml',
                              '-e', 'monkeyble_scenario=scenario1'], stdout=-1, stderr=-2)
        mock_subproc_popen.assert_has_calls([expected_call])
