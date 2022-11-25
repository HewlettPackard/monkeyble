import argparse
import logging
import os
import subprocess
import sys
import pathlib
import yaml
from tabulate import tabulate

from monkeyble.cli.const import MONKEYBLE_DEFAULT_CONFIG_PATH, TEST_PASSED, TEST_FAILED, MONKEYBLE, \
    MONKEYBLE_DEFAULT_ANSIBLE_CMD
from monkeyble.cli.exceptions import MonkeybleCLIException
from monkeyble.cli.models import MonkeybleResult, ScenarioResult
from monkeyble.cli.utils import Utils

logger = logging.getLogger(MONKEYBLE)

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

# actions available
ACTION_LIST = ["test"]


def run_ansible(ansible_cmd, playbook, inventory, extra_vars, scenario):
    ansible_cmd = ansible_cmd.split()
    cmd = list()
    cmd.extend(ansible_cmd)
    cmd.append(playbook)
    if inventory is not None:
        cmd.append("-i")
        cmd.append(inventory)
    if extra_vars is not None:
        for extra_var_path in extra_vars:
            cmd.append("-e")
            cmd.append(f"@{extra_var_path}")
    cmd.append("-e")
    cmd.append(f"monkeyble_scenario={scenario}")
    Utils.print_info(f"Monkeyble - exec: '{cmd}'")

    pipes = subprocess.Popen(cmd,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
    for line in iter(pipes.stdout.readline, b''):
        print(f"{line.rstrip().decode('utf-8')}")
    pipes.wait()
    if pipes.returncode == 0:
        return TEST_PASSED
    else:
        return TEST_FAILED


def run_monkeyble_test(monkeyble_config):
    ansible_cmd = MONKEYBLE_DEFAULT_ANSIBLE_CMD
    if "monkeyble_test_suite" not in monkeyble_config:
        raise MonkeybleCLIException(message="No 'monkeyble_test_suite' variable defined")
    list_result = list()
    for test_config in monkeyble_config["monkeyble_test_suite"]:
        Utils.print_info(f"Monkeyble - ansible cmd: {ansible_cmd}")
        playbook = test_config.get("playbook", None)
        new_result = MonkeybleResult(playbook)
        if playbook is None:
            raise MonkeybleCLIException(message="Missing 'playbook' key in a test")
        inventory = test_config.get("inventory", None)
        extra_vars = test_config.get("extra_vars", None)
        scenarios = test_config.get("scenarios", None)
        if scenarios is None:
            raise MonkeybleCLIException(message=f"No scenarios for playbook {playbook}")
        # print the current path
        Utils.print_info(f"Monkeyble - current path: {pathlib.Path().resolve()}")
        list_scenario_result = list()
        for scenario in scenarios:
            scenario_result = ScenarioResult(scenario)
            scenario_result.result = run_ansible(ansible_cmd, playbook, inventory, extra_vars, scenario)
            list_scenario_result.append(scenario_result)
        new_result.scenario_results = list_scenario_result
        list_result.append(new_result)
    return list_result


def print_result_table(monkeyble_results):
    headers = ["Playbook", "Scenario", "Test passed"]
    table = list()

    for monkeyble_result in monkeyble_results:
        for scenario_result in monkeyble_result.scenario_results:
            row = [monkeyble_result.playbook, scenario_result.scenario, Utils.get_icon_result(scenario_result.result)]
            table.append(row)
    print("")
    print(tabulate(table, headers=headers, tablefmt="presto"))


def do_exit(test_results):
    """
    Exit with code 1 if at least one test has failed
    """
    total_test = 0
    total_passed = 0
    at_least_one_test_failed = False
    for result in test_results:
        for scenario_result in result.scenario_results:
            total_test += 1
            if scenario_result.result == TEST_PASSED:
                total_passed += 1
            else:
                at_least_one_test_failed = True
    print("")
    test_result_message = f"Tests passed: {total_passed} of {total_test} tests"
    if at_least_one_test_failed:
        Utils.print_danger(f"🙊 Monkeyble test result - {test_result_message}")
        sys.exit(1)
    else:
        Utils.print_success(f"🐵 Monkeyble test result - {test_result_message}")
        sys.exit(0)


def load_monkeyble_config(arg_config_path):
    """
    Load the yaml monkeyble config file.
    Precedence:
    - default local monkeyble.yml
    - env var MONKEYBLE_CONFIG
    - cli args 'config'
    """
    # set a default config
    config_path = MONKEYBLE_DEFAULT_CONFIG_PATH
    # load from env if exist
    env_config = os.getenv("MONKEYBLE_CONFIG", default=None)
    if env_config is not None:
        config_path = env_config
    # load from cli args
    if arg_config_path is not None:
        config_path = arg_config_path
    logger.debug(f"Try to open file {config_path}")
    with open(config_path, "r") as stream:
        try:
            monkeyble_config = yaml.full_load(stream)
        except yaml.YAMLError as exc:
            Utils.print_danger(exc)
            sys.exit(1)
    Utils.print_info(f"Monkeyble - config path: {config_path}")
    return monkeyble_config


def parse_args(args):
    """
    Parsing function
    :param args: arguments passed from the command line
    :return: return parser
    """
    # create arguments
    parser = argparse.ArgumentParser(description=MONKEYBLE)
    parser.add_argument("action", help="[test]")
    parser.add_argument("-c", "--config",
                        help="Path to the monkeyble config")

    # parse arguments from script parameters
    return parser.parse_args(args)


def main():
    try:
        parser = parse_args(sys.argv[1:])  # script name removed from args
    except SystemExit:
        sys.exit(1)
    logger.debug("monkeyble args: %s" % parser)

    if parser.action not in ACTION_LIST:
        Utils.print_warning("%s is not a recognised action\n" % parser.action)
        sys.exit(1)

    config = load_monkeyble_config(parser.config)

    if parser.action == "test":
        test_results = run_monkeyble_test(config)
        print_result_table(test_results)
        do_exit(test_results)


if __name__ == '__main__':
    main()
