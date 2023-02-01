# Scenarios

A scenario is like a real-world  use cases of the playbook under test. Scenarios are generally derived from user stories.

## Syntax

The monkeyble configuration is given to the playbook to be tested as an **extra var**.
The best approach consist into creating a dedicated var file like `monkeyble.yml` that contains the set of variable used
by the playbook to test as well as the Monkeyble configuration placed in the `monkeyble_scenarios` variable.

E.g:
```yaml
# monkeyble.yml
# playbook variables
my_var: "value"
my_other_var: "other value"

# monkeyble config
monkeyble_scenarios:
  scenario1:
    name: "Validate that we can create a VM"
    # config
  scenario2:
    name: "Validate that the playbook stop when wrong DNS name is given"
    # config
  scenario3:
    name: "Validate that the selected network is prod when 'prod' flag is true"
    # config
```

## Scenario

Scenario configuration:

- **name**: The scenario description
- **[Test input](test_input.md)**: Test instantiated arguments of a task module 
- **[Test output](test_output.md)**: Test the result dictionary of an executed task
- **[Test state](states.md)**: Check the state of the task (changed, skipped, failed)
- **[Mock](mock.md)**: Mock the executed module of a task 
- **[Task filter](task_filters.md)**: Filter tested tasks by role or playbook name 
- **[Task extra vars](extra_vars.md)**: Override the default extra variable set a playbook level

Execute a playbook to test against a scenario:

```bash
ANSIBLE_CONFIG="ansible.cfg" ansible-playbook playbook.yml \
-e "@<path_to_extra_var>" \
-e "monkeyble_scenario=<scenario_name>"
```

E.G:
```bash
ANSIBLE_CONFIG="ansible.cfg" ansible-playbook playbook.yml \
-e "@monkeyble.yml" \
-e "monkeyble_scenario=validate_test_1"
```

## Re-using test code

### Using Jinja in extra vars

As the configuration is passed as an extra var, usage of jinja template is available to reuse some part of your configuration

E.g:
```yaml
test_input_config:
  - assert_equal:
      arg_name: msg
      expected: "general kenobi"
      
monkeyble_scenarios:
  scenario_1:
    name: "Check the general name"
    tasks_to_test:
      - task: "a task"
        test_input: "{{ test_input_config }}"
  scenario_2:
    name: "Check the general name"
    tasks_to_test:
      - task: "another task"
        test_input: "{{ test_input_config }}"
```

Configuration can be placed in multiple files to be resued by multiple Monkeyble config

```yaml
# shared_tests.yml
a_shared_test:
  - assert_equal:
      arg_name: msg
      expected: "Hello Monkeyble"
```

```yaml
# monkeyble.yml
monkeyble_scenarios:
  validate_test_1:
    name: "Check the general name"
    tasks_to_test:
      - task: "debug task"
        test_input: "{{ a_shared_test }}"
```

Then call the playbook by passing all extra vars:

```bash
ANSIBLE_CONFIG="ansible.cfg" ansible-playbook playbook.yml \
-e "@shared_tests.yml" \
-e "@monkeyble.yml" \
-e "monkeyble_scenario=validate_test_1"
```

### Using 'monkeyble_shared_tasks'

The 'monkeyble_shared_tasks' is a variable that can be used to place test configuration that will always be available in every executed scenario.

As an example. We have a role, which is used in a lot of playbook, that call Hashicorp Vault server to get a token from a Github token. Here is the ansible code of the task:

```yaml
- name: Get a vault token from github token
  uri:
    url: "{{ vault_address }}/v1/auth/github/login"
    method: POST
    headers:
      Content-Type: application/json
    body_format: json
    body:
      token: "{{ vault_github_token }}"
  register: get_vault_token
```

The mock configuration of this particular task can be placed in the `monkeyble_shared_tasks` variable and passed as extra var, so it's always available 
without having to declare it in the `tasks_to_test` list of each scenario.
```yaml
monkeyble_shared_tasks:
  - task: "Get a vault token from github token"
    mock:
      config:
        monkeyble_module:
          consider_changed: true
          result_dict:
            json:
              auth:
                client_token: fake_token
```


## Ansible native test components

The following Ansible components may be placed into playbooks and roles to prevent from failure:

- [check_mode](https://docs.ansible.com/ansible/latest/user_guide/playbooks_checkmode.html)
- [assert](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/assert_module.html)
- [fail](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/fail_module.html)
