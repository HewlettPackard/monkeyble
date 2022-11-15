# Extra vars

The `extra_vars` flag will override default variables when executing a task. 
This allows to change variable in the context of a scenario to validate a playbook behavior.

## Syntax

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

## Example

```yaml
# playbook.yml
- name: "play1"
  hosts: localhost
  connection: local
  gather_facts: false
  become: false
  vars:
    my_var: "Hello Monkeyble"
  tasks:
    - name: "task1"
      debug:
        msg: "{{ my_var }}"

    - name: "task2"
      debug:
        msg: "{{ my_var }}"
```

```yaml
# monkeyble.yml
monkeyble_scenarios:
  validate_test_1:
    name: "Monkeyble hello world"
    tasks_to_test:
      - task: "task2"
        extra_vars:
          my_var: "new value"
```

When executed, the second task use the overriden variable value instead of the default one set at playbook level:
```
PLAY [play1] *******************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************
Starting Monkeyble callback
monkeyble_scenario: validate_test_1
Monkeyble scenario: Monkeyble hello world

TASK [task1] *******************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************
ok: [localhost] => {
    "msg": "Hello Monkeyble"
}

TASK [task2] *******************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************
ok: [localhost] => {
    "msg": "new value"
}

PLAY RECAP *********************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************
localhost                  : ok=2    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```
