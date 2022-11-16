from ansible.module_utils.basic import AnsibleModule


def run_module():
    module_args = {
        'my_arg': dict(type='str', required=True),
    }

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )
    module.log(msg='My module started')

    # CHANGED
    result = {
        'changed': True,
    }
    print("my module executed")
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
