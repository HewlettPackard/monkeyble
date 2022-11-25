# Monkeyble CLI

The monkeyble CLI provides a convenient way to execute all your tests from a single command.

## Installation

### From Pypi

Install from pypi
```bash
pip3 install monkeyble
```

If you are using pipx, inject Monkeyble in your ansible installation
```bash
pipx inject ansible --include-apps monkeyble
```

### From sources

Run the Python setup 
```bash
python3 setup.py install
```

## Configuration file

The CLI expect to find monkeyble configuration file. The file will be searched for in the following order:

- `-c CONFIG` as a cli argument
- `MONKEYBLE_CONFIG` placed as an environment variable
- `monkeyble.yml` from the current directory

### monkeyble_test_suite

The `monkeyble_test_suite` contains a list of Monkeyble test definition.
A test definition contains information about the playbook to test with all scenario to validate.

| Name       | Required | Description                       |
|------------|----------|-----------------------------------|
| playbook   | true     | path to the playbook to test      |
| inventory  | false    | optional path to the inventory    |
| extra_vars | false    | List of path to extra var file    |
| scenarios  | true     | List of scenario name to validate |

Configuration example:

```yaml
monkeyble_test_suite:
  - playbook: "play1.yml"
    inventory: "inventory"
    extra_vars:
      - "shared_mocks.yml"
      - "play1_scenarios.yml"
    scenarios:
      - "validate_test_1"
      - "validate_test_2"
  - playbook: "play2.yml"
    inventory: "inventory"
    extra_vars:
      - "shared_mocks.yml"
      - "play2_scenarios.yml"
    scenarios:
      - "validate_this"
      - "validate_that"
```

!!! note

    As the monkeyble [scenario configuration](scenarios.md) is passed as `extra_vars` you should at least 
    have one file declared in the `extra_vars` list and one scenario name placed in `scenarios`.

## Commands

### monkeyble test

The monkeyble test command executes all the test declared in the `monkeyble_test_suite` configuration flag and provides
a test result summary.

Command:
```
ANSIBLE_CONFIG='monkeyble.cfg' monkeyble test 
```

Output example:
```
# TRUNCATED. Playbook executions output

Playbook   | Scenario        | Test passed
-----------+-----------------+-------------
 play1.yml | validate_test_1 | ✅
 play1.yml | validate_test_2 | ✅
 play2.yml | validate_this   | ✅
 play2.yml | validate_that   | ✅
 
 🐵 Monkeyble test result - Tests passed: 4 of 4 tests
```
