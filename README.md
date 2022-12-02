<p align="center">
    <img src="docs/images/monkeyble_logo.png">
</p>

<h3 align="center">End-to-end testing framework for Ansible</h3>

<p align="center">
<a href="https://hewlettpackard.github.io/monkeyble"><img alt="Doc" src="https://img.shields.io/badge/read-documentation-1abc9c?style=flat-square"></a>
<a href="https://makeapullrequest.com"><img alt="PR" src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square"></a>
</p>

# Monkeyble

Monkeyble is a callback plugin for Ansible that allow to execute end-to-end tests on Ansible playbooks with a 
Pythonic testing approach. 🧐

Monkeyble allows, at task level, to:

- 🐵 Check that a module has been called with expected argument values
- 🙊 Check that a module returned the expected result dictionary
- 🙈 Check the task state (changed, skipped, failed)
- 🙉 Mock a module and return a defined dictionary as result

Monkeyble is designed to be executed by a CI/CD in order to detect regressions when updating an Ansible code base. 🚀 

Complete documentation available [here](https://hewlettpackard.github.io/monkeyble)

## Hello Monkeyble

Let's consider this simple playbook
```yaml
- name: "Hello Monkeyble"
  hosts: localhost
  connection: local
  gather_facts: false
  become: false
  vars:
    who: "Monkeyble"

  tasks:
    - name: "First task"
      set_fact:
        hello_to_who: "Hello {{ who }}"

    - name: "Second task"
      debug:
        msg: "{{ hello_to_who }}"

    - when: "who != 'Monkeyble'"
      name: "Should be skipped task"
      debug:
        msg: "You said hello to somebody else"

    - name: "Push Monkeyble to a fake API"
      uri:
        url: "example.domain/monkeyble"
        method: POST
        body:
          who: "{{ who }}"
        body_format: json
```

We prepare a yaml file that contains a test scenario
```yaml
# monkeyble_scenarios.yaml
monkeyble_scenarios:
  validate_hello_monkey:
    name: "Monkeyble hello world"
    tasks_to_test:

      - task: "First task"
        test_output:
          - assert_equal:
              result_key: result.ansible_facts.hello_to_who
              expected: "Hello Monkeyble"

      - task: "Second task"
        test_input:
          - assert_equal:
              arg_name: msg
              expected: "Hello Monkeyble"

      - task: "Should be skipped task"
        should_be_skipped: true

      - task: "Push Monkeyble to a fake API"
        mock:
          config:
            monkeyble_module:
              consider_changed: true
              result_dict:
                json:
                  id: 10
                  message: "monkey added"
```

We execute the playbook like by passing 
- the dedicated ansible config that load Monkeyble (see install doc)
- the extra var file that contains our scenarios
- one extra var with the selected scenario to validate `validate_hello_monkey`

```bash
ANSIBLE_CONFIG="ansible.cfg" ansible-playbook -v  \
tests/test_playbook.yml \
-e "@tests/monkeyble_scenarios.yml" \
-e "monkeyble_scenario=validate_hello_monkey"
```

Here is the output:
```
PLAY [Hello Monkeyble] *********************************************************************************************************************************************************************************************************************************************************************************************************************************************************************
🐵 Starting Monkeyble callback
monkeyble_scenario: validate_hello_monkey
Monkeyble scenario: Monkeyble hello world

TASK [First task] **************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************
ok: [localhost] => {"ansible_facts": {"hello_to_who": "Hello Monkeyble"}, "changed": false}
🙊 Monkeyble test output passed ✔
{"task": "First task", "monkeyble_passed_test": [{"test_name": "assert_equal", "tested_value": "Hello Monkeyble", "expected": "Hello Monkeyble"}], "monkeyble_failed_test": []}

TASK [Second task] *************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************
🙈 Monkeyble test input passed ✔
{"monkeyble_passed_test": [{"test_name": "assert_equal", "tested_value": "Hello Monkeyble", "expected": "Hello Monkeyble"}], "monkeyble_failed_test": []}
ok: [localhost] => {
    "msg": "Hello Monkeyble"
}

TASK [Should be skipped task] **************************************************************************************************************************************************************************************************************************************************************************************************************************************************************
skipping: [localhost] => {}
🐵 Monkeyble - Task 'Should be skipped task' - expected 'should_be_skipped': True. actual state: True

TASK [Push Monkeyble to a fake API] ********************************************************************************************************************************************************************************************************************************************************************************************************************************************************
🙉 Monkeyble mock module - Before: 'uri' Now: 'monkeyble_module'
changed: [localhost] => {"changed": true, "json": {"id": 10, "message": "monkey added"}, "msg": "Monkeyble Mock module called. Original module: uri"}

PLAY RECAP *********************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************
localhost                  : ok=3    changed=1    unreachable=0    failed=0    skipped=1    rescued=0    ignored=0   

🐵 Monkeyble - ALL TESTS PASSED ✔ - scenario: Monkeyble hello world
```

All tests have passed. The return code on stderr is **0**.

Let's change the test to make it fail. We update the variable `who` at the beginning of the playbook.
```yaml
who: "Dog"
```

We execute the playbook the same way. The result is now the following:
```
ok: [localhost] => {"ansible_facts": {"hello_to_who": "Hello Dog"}, "changed": false}
🙊 Monkeyble failed scenario ❌: Monkeyble hello world
{"task": "First task", "monkeyble_passed_test": [], "monkeyble_failed_test": [{"test_name": "assert_equal", "tested_value": "Hello Dog", "expected": "Hello Monkeyble"}]}
```

This time the test has failed. The return code on stderr is **1**. The CI/CD It would have warned you that something has changed.

## Quick tour

### Test input

Monkeyble allows to check each instantiated argument value when the task is called:

```yml
  - task: "my_task_name"
    test_input:
      - assert_equal:
          arg_name: module_argument
          expected: "my_value"
```

Monkeyble support multiple test methods:

- assert_equal
- assert_not_equal
- assert_in
- assert_not_in
- assert_true
- assert_false
- assert_is_none
- assert_is_not_none
- assert_list_equal
- assert_dict_equal

### Test output

Monkeyble allows to check the output result dictionary of a task

```yml
  - task: "my_task_name"
    test_output:
      - assert_dict_equal:
          dict_key: "result.key.name"
          expected: 
            key1: "my_value"
            key2: "my_other_value"
```

Same methods as the `test_input` are supported.

### Test task states

Monkeyble allow to check the states of a task

```yml
  - task: "my_task_name"
    should_be_skipped: false
    should_be_changed: true
    should_fail: false
```

### Monkey patching

Monkey patching is a technique that allows you to intercept what a function would normally do, substituting its full execution with a return value of your own specification. 
In the case of Ansible, the function is actually a module and the returned value is the "result" dictionary.

Consider a scenario where you are working with public cloud API or infrastructure module. 
In the context of testing, you do not want to create a real instance of an object in the cloud like a VM or a container orchestrator.
But you still need eventually the returned dictionary so the playbook can be executed entirely.

Monkeyble allows to mock a task and return a specific value:
```yml
- task: "my_task_name"
  mock:
    config:
      monkeyble_module:
        consider_changed: true
        result_dict:
          my_key: "mock value"
```

### Cli 

Monkeyble comes with a CLI that allow to execute all tests from a single command and return a summary of test executions.
```bash
monkeyble test

Playbook   | Scenario        | Test passed
-----------+-----------------+-------------
 play1.yml | validate_test_1 | ✅
 play1.yml | validate_test_2 | ✅
 play2.yml | validate_this   | ✅
 play2.yml | validate_that   | ✅
 
 🐵 Monkeyble test result - Tests passed: 4 of 4 tests
```

## Do I need Monkeyble?

The common testing strategy when using Ansible is to deploy to a staging environment that simulates the production.
When a role or a playbook is updated, we usually run an integration test battery against staging again before pushing in production.
In case of an update of the code base, a new execution will be required on the stating environment before the production one, etc...

But when our playbooks are exposed in an [Ansible Controller/AWX](https://www.ansible.com/products/controller) (ex Tower)
or available as a service in a catalog like [Squest](https://github.com/HewlettPackard/squest), we need to be sure that we don't have any regressions 
when updating the code base, especially when modifying a role used by multiple playbooks. Manually testing each playbook would be costly. We commonly give this kind of task to a CI/CD.

Furthermore, Ansible resources are models of desired-state. Ansible modules have their own unit tests and guarantee you of their correct functioning.
As such, it's not necessary to test that services are started, packages are installed, or other such things. 
Ansible is the system that will ensure these things are declaratively true.

So finally, what do we need to test? An Ansible playbook is commonly a bunch of data manipulation before calling a module that will perform a particular action.
For example, we get data from an API endpoint, or from the result of a module, we register a variable, then use a filter transform the data like combining two dictionary, 
transforming into a list, changing the type, extract a specific value, etc... to finally call another module in a new task with the transformed data..

Given a defined list of variable defined as input we want to be sure that a particular task: 

- is well executed (the playbook could have failed before)
- is well called with the expected instantiated arguments
- produced this exact result
- has been skipped, changed or has failed

Monkeyble is a tool that can help you to enhance the quality of your Ansible code base and can be coupled 
with [official best practices](https://docs.ansible.com/ansible/latest/reference_appendices/test_strategies.html).
Placed in a CI/CD it will be in charge of validating that the legacy code is always working as expected.

## Contribute

Feel free to fill an issue containing feature request(s), or (even better) to send a Pull request, we would be happy to collaborate with you.

> If you like the project, star it ⭐, it motivates us a lot 🙂
