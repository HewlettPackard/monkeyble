#!/usr/bin/env python

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible import context
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.inventory.manager import InventoryManager
from ansible.module_utils.common.collections import ImmutableDict
from ansible.parsing.dataloader import DataLoader
from ansible.playbook.play import Play
from ansible.vars.manager import VariableManager

# Create a callback plugin so we can capture the output
from ansible_monkeyble.plugins.callback.monkeyble_callback import CallbackModule as MonkeybleCallback


def main():
    host_list = ['localhost']
    # since the API is constructed for CLI it expects certain options to always be set in the context object
    context.CLIARGS = ImmutableDict(connection='local', module_path=['/to/mymodules', '/usr/share/ansible'], forks=10,
                                    become=None, become_method=None, become_user=None, check=False, diff=False,
                                    verbosity=0)
    # required for
    # https://github.com/ansible/ansible/blob/devel/lib/ansible/inventory/manager.py#L204
    sources = ','.join(host_list)
    if len(host_list) == 1:
        sources += ','

    # initialize needed objects
    loader = DataLoader()  # Takes care of finding and reading yaml, json and ini files
    passwords = dict(vault_pass='secret')

    # Instantiate our ResultsCollectorJSONCallback for handling results as they come in.
    # Ansible expects this to be one of its main display outlets
    results_callback = MonkeybleCallback()

    # create inventory, use path to host config file as source or hosts in a comma separated string
    inventory = InventoryManager(loader=loader, sources=sources)

    # variable manager takes care of merging all the different sources to give you a unified view of variables
    # available in each context
    extra_vars = {
        "test_input_config_1": [
            {
                "assert_equal": {
                    "arg_name": "msg",
                    "expected": "general kenobi"
                }
            }
        ],
        "replace_debug_mock": {
            "monkeyble_module": {
                "consider_changed": False,
                "result_dict": {
                    "msg": "output_value"
                }
            }
        },
        "monkeyble_scenario": "validate_test_1",
        "monkeyble_scenarios": {
            "validate_test_1": {
                "name": "Validate that bla bla",
                # "tasks_to_test": [
                #     {
                #         "task": "test_name2",
                #         "should_be_changed": True,
                #         "should_be_skipped": False,
                #         "should_failed": False,
                #         "test_input": "{{ test_input_config_1 }}",
                #         "mock": {"config": "{{ replace_debug_mock }}"}
                #     }
                # ]
                "tasks_to_test": [
                    {
                        "task": "test_name3",
                        "test_output": [
                            {
                                "assert_dict_equal": {
                                    "result_value": "result.ansible_facts",
                                    "expected": {
                                        "new_var": "new_valdd"
                                    }
                                }
                            }
                        ]
                    }
                ]
            }
        }
    }
    variable_manager = VariableManager(loader=loader, inventory=inventory)
    variable_manager._extra_vars = extra_vars

    # instantiate task queue manager, which takes care of forking and setting up all objects to
    # iterate over host list and tasks
    # IMPORTANT: This also adds library dirs paths to the module loader
    # IMPORTANT: and so it must be initialized before calling `Play.load()`.
    tqm = TaskQueueManager(
        inventory=inventory,
        variable_manager=variable_manager,
        loader=loader,
        passwords=passwords,
        stdout_callback=results_callback,
    )

    # create data structure that represents our play, including tasks,
    # this is basically what our YAML loader does internally.
    play_source = dict(
        name="Ansible Play",
        hosts=host_list,
        gather_facts='no',
        vars={
            "my_var": "general kenobi"
        },
        tasks=[
            # dict(action=dict(module='shell', args='ls'), register='shell_out'),
            # dict(name="test_name2", action=dict(module='debug', args=dict(msg='{{ my_var }}')), when="my_var == 'to_be_updated'"),
            # dict(name="test_name2", action=dict(module='debug', args=dict(msg='{{ my_var }}'))),
            # dict(name="test_name3", action=dict(module='find', args=dict(path='/tmp'))),
            dict(name="test_name3", action=dict(module='set_fact', args=dict(new_var='new_val'))),
            # dict(name="test_name1", action=dict(module='debug', args=dict(msg='{{ my_var }}'))),
            # dict(action=dict(module='debug', args=dict(msg='{{shell_out.stdout}}'))),
            # dict(action=dict(module='command', args=dict(cmd='/usr/bin/uptime'))),
        ]
    )

    # Create play object, playbook objects use .load instead of init or new methods,
    # this will also automatically create the task objects from the info provided in play_source
    play = Play().load(play_source, variable_manager=variable_manager, loader=loader)

    # Actually run it
    try:
        result = tqm.run(play)  # most interesting data for a play is actually sent to the callback's methods
    finally:
        # we always need to cleanup child procs and the structures we use to communicate with them
        tqm.cleanup()
        if loader:
            loader.cleanup_all_tmp_files()

    # Remove ansible tmpdir
    # shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)

    print("UP ***********")
    for host, result in results_callback.host_ok.items():
        print('{0} >>> {1}'.format(host, result._result))

    print("FAILED *******")
    for host, result in results_callback.host_failed.items():
        print('{0} >>> {1}'.format(host, result._result))

    print("DOWN *********")
    for host, result in results_callback.host_unreachable.items():
        print('{0} >>> {1}'.format(host, result._result))

    # print("SKIPPED *********")
    # for host, result in results_callback.host_skipped.items():
    #     print(result._result)
    print(f"changed: {results_callback.changed_task_list}")
    print(f"skipped: {results_callback.skipped_task_list}")

if __name__ == '__main__':
    main()
