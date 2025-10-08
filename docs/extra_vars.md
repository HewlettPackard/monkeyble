# Extra vars

The `extra_vars` flag will override default variables when executing a task. 
This allows to change variable in the context of a scenario to validate a playbook behavior.

Extra vars can be set at **scenario** or **task** level.

Extra vars set at task level take precedence over extra vars set at scenario level.

```yaml
monkeyble_scenarios:
  validate_test_1:
    name: "Monkeyble hello world"
    extra_vars:
      new_var_key: "new_value_at_scenario_level"     
      override_existing_key: "other value"  
    tasks_to_test:
      - task: "debug task"    
        extra_vars:
          new_var_key: "new_value_at_task_level"     
          override_other_var: "other value" 
```

## Scenario extra vars

```yaml
monkeyble_scenarios:
  validate_test_1:
    name: "Monkeyble hello world"
    extra_vars:
      new_var_key: "new_value_at_scenario_level"     
      override_existing_key: "other value"  
    tasks_to_test:
      - task: "debug task"               
```


## Task extra vars

```yaml
monkeyble_scenarios:
  validate_test_1:
    name: "Monkeyble hello world"
    tasks_to_test:
      - task: "debug task"    
        extra_vars:
          new_var_key: "new_value"     
          override_existing_key: "other value"     
```


### Example

```yaml
# playbook.yml
- name: "Hello Monkeyble"
  hosts: localhost
  connection: local
  gather_facts: false
  become: false
  vars:
    play_level_var: "default play var"
  tasks:
    - name: "Print play var non updated"
      debug:
        msg: "{{ play_level_var }}"

    - name: "Print play var updated at scenario level"
      debug:
        msg: "{{ play_level_var }}"

    - name: "Print play var updated at task level"
      debug:
        msg: "{{ play_level_var }}"
```

```yaml
# monkeyble.yml
monkeyble_scenarios:
  validate_test_1:
    name: "Monkeyble hello world"
    extra_vars:
      my_var: "updated_at_scenario"
    tasks_to_test:
      - task: "Print play var updated at scenario level"
        test_input:
          - assert_equal:
              arg_name: msg
              expected: "scenario level var"

      - task: "Print play var updated at task level"
        extra_vars:
          play_level_var: "task level"
        test_input:
          - assert_equal:
              arg_name: msg
              expected: "task level"
```


When executed, the second task use the overwritten variable value instead of the default one set at playbook level:
```
PLAY [Hello Monkeyble] *********************************************************************************************************************************************************************************************************************************
🐵 Starting Monkeyble callback 1.5.0b
monkeyble_scenario: validate_hello_monkey
Monkeyble scenario: Monkeyble hello world

TASK [Print play var non updated] **********************************************************************************************************************************************************************************************************************
ok: [localhost] => {
    "msg": "default play var"
}

TASK [Print play var updated at scenario level] ********************************************************************************************************************************************************************************************************
🙈 Monkeyble test input passed ✔
{"monkeyble_passed_test": [{"test_name": "assert_equal", "tested_value": "scenario level var", "expected": "scenario level var"}], "monkeyble_failed_test": []}
ok: [localhost] => {
    "msg": "scenario level var"
}

TASK [Print play var updated at task level] ************************************************************************************************************************************************************************************************************
🙈 Monkeyble test input passed ✔
{"monkeyble_passed_test": [{"test_name": "assert_equal", "tested_value": "task level", "expected": "task level"}], "monkeyble_failed_test": []}
ok: [localhost] => {
    "msg": "task level"
}

PLAY RECAP *********************************************************************************************************************************************************************************************************************************************
localhost                  : ok=3    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   

🐵 Monkeyble - ALL TESTS PASSED ✔ - scenario: Monkeyble hello world
```
