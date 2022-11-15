# Test output

## Syntax

Monkeyble allow to check the returned dictionary of a task.

!!!note

    All modules doesn't return values. Check the documenttion of each module you want to test.

Monkeyble config example:

```yaml
monkeyble_scenarios:
  validate_test_1:
    name: "Monkeyble hello world"
    tasks_to_test:
      - task: "debug task"
        test_output: # list of test case method
          - assert_equal:
              result_key: result.module_output_key
              expected: "module_output_value"
          - assert_dict_equal:
              result_key: "result.module_output_key"
              expected:
                some_key: "some var"
```

A test case method expect two arguments:

- **result_key**: The string path to the key to test in the returned dict
- **expected**: The expected instantiated value of the selected 'key' in the result dict

!!! warning

     `result_key` is a raw Jinja2 expression without double curly braces like 
     a basic [Ansible "when" condition](https://docs.ansible.com/ansible/latest/user_guide/playbooks_conditionals.html#basic-conditionals-with-when)

## Test case methods

### assert_equal

```yaml
# Task example
- name: "test_output"
  set_fact:
    r2d2: "is the coolest robot ever"
```

```yaml
# Monkeyble config
- task: "test_output"
  test_output:
    - assert_equal:
        result_key: result.ansible_facts.r2d2
        expected: "is the coolest robot ever"
```

### assert_not_equal

```yaml
# Task example
- name: "test_output"
  set_fact:
    r2d2: "is the coolest robot ever"
```

```yaml
# Monkeyble config
- task: "test_output"
  test_output:
    - assert_not_equal:
        result_key: result.ansible_facts.r2d2
        expected: "is bb8"
```

### assert_in

```yaml
# Task example
- name: "test_output"
  set_fact:
    planets:
      - "tatooine"
      - "coruscant"
```

```yaml
# Monkeyble config
- task: "test_output"
  test_output:
    - assert_in:
        result_key: result.ansible_facts.planets
        expected: "tatooine"
```

### assert_not_in

```yaml
# Task example
- name: "test_output"
  set_fact:
    planets:
      - "tatooine"
      - "coruscant"
```

```yaml
# Monkeyble config
- task: "test_output"
  test_output:
    - assert_in:
        result_key: result.ansible_facts.planets
        expected: "naboo"
```

### assert_true

```yaml
# Task example
- name: "test_output"
  set_fact:
    true_bool: true
```

```yaml
# Monkeyble config
- task: "test_output"
  test_output:
    - assert_true:
        result_key: result.ansible_facts.true_bool
        expected: true
```

### assert_false

```yaml
# Task example
- name: "test_output"
  set_fact:
    false_bool: false
```

```yaml
# Monkeyble config
- task: "test_output"
  test_output:
    - assert_false:
        result_key: result.ansible_facts.false_bool
        expected: true
```

### assert_is_none

```yaml
# Task example
- name: "test_output"
  set_fact:
    null_value: null
```

```yaml
# Monkeyble config
- task: "test_output"
  test_output:
    - assert_is_none:
        result_key: result.ansible_facts.null_value
```

### assert_is_not_none

```yaml
# Task example
- name: "test_output"
  set_fact:
    saber_color: "blue"
```

```yaml
# Monkeyble config
- task: "test_output"
  test_output:
    - assert_is_not_none:
        result_key: result.ansible_facts.saber_color
```

### assert_list_equal

```yaml
# Task example
- name: "test_output"
  set_fact:
    planets:
      - "tatooine"
      - "coruscant"
```

```yaml
# Monkeyble config
- task: "test_output"
  test_output:
    - assert_list_equal:
        result_key: result.ansible_facts.planets
        expected:
          - "tatooine"
          - "coruscant"
```

### assert_dict_equal

```yaml
# Task example
- name: "test_output"
  set_fact:
    side:
      light: "yoda"
      dark: "vader"
```

```yaml
# Monkeyble config
- task: "test_output"
  test_output:
    - assert_dict_equal:
        result_key: result.ansible_facts.side
        expected:
          light: "yoda"
          dark: "vader"
```
