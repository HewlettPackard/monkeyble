# Hello Monkeyble

For the example, consider this playbook
```yaml
- name: "Testing play"
  hosts: localhost
  connection: local
  gather_facts: false
  become: false

  tasks:
    - name: "debug task"
      debug:
        msg: "Hello Monkeyble"
```

You need an extra var file that will contain all your Monkeyble scenarios. For example `monkeyble.yml`.
```yaml
monkeyble_scenarios:
  validate_test_1:
    name: "Monkeyble hello world"
    tasks_to_test:
      - task: "debug task"
        test_input:   
          - assert_equal:
              arg_name: msg
              expected: "Hello Monkeyble"
```

Then, call your playbook by passing the Ansible configuration, the extra var file that contains all your scenarios and the selected scenario to validate.
```bash
ANSIBLE_CONFIG="ansible.cfg" ansible-playbook \
playbook.yml \
-e "@monkeyble.yml" \
-e "monkeyble_scenario=validate_test_1"
```

Here is the output:

```
PLAY [play1] *******************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************
🐵 Starting Monkeyble callback
monkeyble_scenario: validate_test_1
Monkeyble scenario: Monkeyble hello world

TASK [debug task] **************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************
🙈 Monkeyble test input passed ✔
{"monkeyble_passed_test": [{"test_name": "assert_equal", "tested_value": "Hello Monkeyble", "expected": "Hello Monkeyble"}], "monkeyble_failed_test": []}
ok: [localhost] => {
    "msg": "Hello Monkeyble"
}

PLAY RECAP *********************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************
localhost                  : ok=1    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   

🐵 Monkeyble - ALL TESTS PASSED ✔ - scenario: Monkeyble hello world
```

The debug module has been well called with the expected argument value. The test passed. The return code on stderr is `0`.

Let's change the test to make it fail. We update the executed task and change the `msg` argument of the `debug` module.

```yaml
- name: "debug task"
  debug:
    msg: "Goodbye Monkeyble"
```

We execute the playbook the same way. The result is now the following:
```
PLAY [play1] *******************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************
🐵 Starting Monkeyble callback
monkeyble_scenario: validate_test_1
Monkeyble scenario: Monkeyble hello world

TASK [debug task] **************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************
🙊 Monkeyble failed scenario ❌: Monkeyble hello world
{"monkeyble_passed_test": [], "monkeyble_failed_test": [{"test_name": "assert_equal", "tested_value": "Goodbye Monkeyble", "expected": "Hello Monkeyble"}]}
```

This time the test has failed. The return code on stderr is `1`.
