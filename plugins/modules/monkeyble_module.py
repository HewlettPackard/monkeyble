# Copyright 2022 Hewlett Packard Enterprise Development LP
from ansible.module_utils.basic import AnsibleModule


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = {
        'task_name': dict(type='str', required=True),
        'original_module_name': dict(type='str', required=True),
        'consider_changed': dict(type='bool', required=False, default=False),
        'result_dict': dict(type='dict', required=False),
    }

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )
    module.log(msg='Monkeyble mock module started')

    # CHANGED
    result = {
        'changed': module.params['consider_changed'],
        'msg': f"Monkeyble Mock module called. Original module: {module.params['original_module_name']}"
    }

    # RESULT DICT
    if module.params['result_dict']:
        result.update(module.params['result_dict'])

    # Prevent AnsibleModule._return_formatted() from calling add_path_info().
    # That method checks if a file at 'dest' or 'path' exists on the local filesystem
    # and overwrites uid, gid, owner, group, mode, size, state with real values.
    # This silently corrupts mock results when the target file happens to exist.
    module.add_path_info = lambda kwargs: kwargs

    module.exit_json(**result)


def main():
    # local testing
    # set_module_args({
    #     'task_name': 'test',
    #     'original_module_name': "copy"
    #
    # })
    run_module()


if __name__ == '__main__':
    main()
