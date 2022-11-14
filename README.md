<p align="center">
    <img src="docs/images/monkeyble_logo.png">
</p>

# Monkeyble

Monkeyble is a callback plugin for Ansible that allow to test a playbook with a Pythonic unit testing approach.

Monkeyble allows, at task level, to:

- Check that a module as been called with expected argument values (using Python like asserts)
- Check that a module returned the expected result dictionary
- Check the task state (changed, skipped, failed)
- Mock a module and return a defined dict as result

## Quick tour

Ansible resources are models of desired-state. Ansible modules have their own unit tests and guarantee you of their correct functioning.
As such, it's not necessary to test that services are started, packages are installed, or other such things. 
Ansible is the system that will ensure these things are declaratively true.

That being said, an Ansible playbook is commonly a bunch of data manipulation before calling a module that will perform a particular action.
For example, we call an API or a module, register a variable, then use a filter transform the data like combining two dictionary, 
transforming a dictionary into a list, change the data type, extract a specific value, etc... and finally call another module in a new task.

Given a list of variable as input we want to be sure that this last task: 

- is well called with the same instantiated arguments
- produce the same result
- has been skipped or changed

### Check input

Monkeyble allows to check each instantiated argument value when the task is called:

```yml
  - task: "my_task_name"
    test_input:
      - assert_equal:
          arg_name: module_argument
          expected: "my_value"
```
Monkeyble support following tests:

["assert_equal", "assert_not_equal", "assert_in", "assert_not_in", "assert_true", "assert_false", "assert_is_none", "assert_is_not_none", "assert_list_equal", "assert_dict_equal"]

### Check output

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

### States

Monkeyble allow to check the state of a task

```yml
  - task: "my_task_name"
    should_be_skipped: false
    should_be_changed: true
    should_failed: false
```

### Monkey patching

Monkey patching is a technique that allows you to intercept what a function would normally do, substituting its full execution with a return value of your own specification. 
In the case of Ansible, the function is actually a module and the returned value is the "result" dictionary.

Consider a scenario where you are working with public cloud API or infrastructure module. 
In the context of testing, you do not want to create a real instance of an object in the cloud like a VM or a container orchestrator.
But you still need eventually the returned dictionary so the playbook can be executed entirely.

Monkey allows to mock a task and return a specific value:
```yml
- task: "my_task_name"
  mock:
    config:
      monkeyble_module:
        consider_changed: true
        result_dict:
          my_key: "mock value"
```
