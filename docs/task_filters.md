# Task filters

Task filters allow to only test a particular task when the task name is placed into a defined role or play name.

## Syntax

```yaml
monkeyble_scenarios:
  validate_test_1:
    name: "Monkeyble hello world"
    tasks_to_test:
      - task: "debug task"
        role: "role_name" # the test will be executed if the role matches
        play: "play_name" # the test will be executed if the play matches
        should_be_changed: true
        test_input:
          # config 
        test_output:
          # config
```
## Example

```yaml
# playbook.yml
- name: "play1"
  hosts: localhost
  connection: local
  gather_facts: false
  become: false
  tasks:
    - name: "debug task"
      debug:
        msg: "Hello Monkeyble"

- name: "play2"
  hosts: localhost
  connection: local
  gather_facts: false
  become: false
  tasks:
    - name: "debug task"
      debug:
        msg: "Hello Monkeyble"
```

```yaml
# monkeyble.yml
monkeyble_scenarios:
  validate_test_1:
    name: "Validate task is tested only in play1"
    tasks_to_test:
      - task: "debug task"
        play: play1
        test_input:
          - assert_equal:
              arg_name: msg
              expected: "Hello Monkeyble"
```

When executed, the task "debug task" is only tested when executed from the play named "play1"
```
PLAY [play1] *******************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************
Starting Monkeyble callback
monkeyble_scenario: validate_test_1
Monkeyble scenario: Validate task is tested only in play1

TASK [debug task] **************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************
{'monkeyble_passed_test': [{'test_name': 'assert_equal', 'tested_value': 'Hello Monkeyble', 'expected': 'Hello Monkeyble'}], 'monkeyble_failed_test': []}
ok: [localhost] => {
    "msg": "Hello Monkeyble"
}

PLAY [play2] *******************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************
Starting Monkeyble callback
monkeyble_scenario: validate_test_1
Monkeyble scenario: Monkeyble hello world

TASK [debug task] **************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************
ok: [localhost] => {
    "msg": "Hello Monkeyble"
}

PLAY RECAP *********************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************
localhost                  : ok=2    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0 
```
