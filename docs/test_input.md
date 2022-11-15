# Test input

## Syntax

Monkeyble allow to check instantiated arguments of a task.

Monkeyble config example:

```yaml
monkeyble_scenarios:
  validate_test_1:
    name: "Monkeyble hello world"
    tasks_to_test:
      - task: "debug task"
        test_input: # list of test case method
          - assert_equal:
              arg_name: msg
              expected: "Hello Monkeyble"
          - assert_not_equal:
              arg_name: msg
              expected: "Goodbye Monkeyble"
```

A test case method expect two arguments:

- **arg_name**: The name of the module argument where monkeyble will check the instantiated value
- **expected**: The expected instantiated value passed to the task when executed


## Test case methods

### assert_equal

```yaml
# Task example
- name: "test_assert_equal"
  debug:
    msg: "general kenobi"
```

```yaml
# Monkeyble config
  - task: "test_assert_equal"
    test_input:
      - assert_equal:
          arg_name: msg
          expected: "general kenobi"
```

### assert_not_equal

```yaml
# Task example
- name: "test_assert_equal"
  debug:
    msg: "general kenobi"
```

```yaml
# Monkeyble config
- task: "test_assert_equal"
  test_input:
    - assert_not_equal:
        arg_name: msg
        expected: "general organa"
```

### assert_in

```yaml
# Task example
- name: "test_assert_in_with_list"
  find:
    path: "/tmp"
    excludes : 
      - "luke"
      - "obi-wan"
      - 
- name: "test_assert_in_with_string"
  debug:
    msg: "anakin"
```

```yaml
# Monkeyble config
- task: "test_assert_in_with_list"
  test_input:
    - assert_in:
        arg_name: excludes
        expected: "luke"

- task: "test_assert_in_with_string"
  test_input:
    - assert_in:
        arg_name: msg
        expected: "kin"
```

### assert_not_in

```yaml
# Task example
- name: "test_assert_in_with_list"
  find:
    path: "/tmp"
    excludes : 
      - "luke"
      - "obi-wan"
      - 
- name: "test_assert_in_with_string"
  debug:
    msg: "anakin"
```

```yaml
# Monkeyble config
- task: "test_assert_in_with_list"
  test_input:
    - assert_not_in:
        arg_name: excludes
        expected: "palpatine"

- task: "test_assert_in_with_string"
  test_input:
    - assert_not_in:
        arg_name: msg
        expected: "not_there"
```

### assert_true

```yaml
# Task example
- name: "test_assert_true"
  find:
    path: "/tmp"
    hidden: true
```

```yaml
# Monkeyble config
- task: "test_assert_true"
  test_input:
    - assert_true:
        arg_name: hidden
```

### assert_false

```yaml
# Task example
- name: "test_assert_true"
  find:
    path: "/tmp"
    hidden: false
```

```yaml
# Monkeyble config
- task: "test_assert_false"
  test_input:
    - assert_false:
        arg_name: hidden
```

### assert_is_none

```yaml
# Task example
- name: "assert_is_none"
  debug:
    msg: null
```

```yaml
# Monkeyble config
- task: "assert_is_none"
  test_input:
    - assert_is_none:
        arg_name: msg
```

### assert_is_not_none

```yaml
# Task example
- name: "test_is_not_none"
  debug:
    msg: "There's always a bigger fish"
```

```yaml
# Monkeyble config
- task: "test_is_not_none"
  test_input:
    - assert_is_not_none:
        arg_name: msg
```

### assert_list_equal

```yaml
# Task example
- name: "test_list_equal"
  find:
    path: "/tmp"
    excludes:
      - "tatooine"
      - "naboo"
```

```yaml
# Monkeyble config
- task: "test_list_equal"
  test_input:
    - assert_list_equal:
        arg_name: excludes
        expected:
          - "tatooine"
          - "naboo"
```

### assert_dict_equal

```yaml
# Task example
- name: "test_dict_equal"
  uri:
    url: "https://www.hpe.com"
    headers:
      key1: value1
      key2: value2
```

```yaml
# Monkeyble config
- task: "test_dict_equal"
  test_input:
    - assert_dict_equal:
      arg_name: headers
      expected:
        key1: value1
        key2: value2
```
