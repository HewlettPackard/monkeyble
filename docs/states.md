# States

Monkeyble allows to check the state of an executed task

## Syntax

Monkeyble config example:

```yaml
monkeyble_scenarios:
  validate_test_1:
    name: "Monkeyble hello world"
    tasks_to_test:
      - task: "debug task"
        should_be_changed: true
        should_be_skipped: false
        should_fail: false
```

## States

### should_be_changed

```yaml
# Task example
- name: "should_be_changed_false"
  debug:
    msg: "Obi-Wan Kenobi is a Jedi"

- name: "should_be_changed_true"
  command: ls
```

```yaml
# Monkeyble config
- task: "should_be_changed_false"
  should_be_changed: false
- task: "should_be_changed_true"
  should_be_changed: true
```

### should_be_skipped

```yaml
# Task example
- when: "side == 'dark'"
  name: "should_be_skipped"
  debug:
    msg: "going to the dark side"
```

```yaml
# Monkeyble config
- task: "should_be_skipped"
  should_be_skipped: true
```

### should_fail

```yaml
# Task example
- name: "should_fail"
  fail:
    msg: "save Palpatine"
```

```yaml
# Monkeyble config
- task: "should_fail"
  should_fail: true
```

!!!warning

    The normal return code when a task fail in an Ansible is **1**.
    When a task is declared as `should_fail` in a Monkeyble and actually fail then the return code
     is **O** instead to prevent a CI/CD from concidering the test as a failure.
