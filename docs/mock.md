# Mock

Mock modules are simulated modules that mimic the behaviour of real module in controlled ways.
Mock can be used to test the behavior of a playbook without actually perform some operations like creating resource 
in a cloud or in IT infrastructure.
The mock module can return values so the tested playbook can register new variable from its output like if it was the real module.

## Syntax

Monkeyble config example:
```yaml
monkeyble_scenarios:
  validate_test_1:
    name: "Monkeyble hello world"
    tasks_to_test:
      - task: "debug task"
        mock:
          config:
            # <new module>
```

## The monkeyble mock module

Monkeyble comes with a mock module that return a configured dict.

Considering this task from a role or a playbook. We create a VM in a VMware hypervisor.
```yaml
- name: "Create a virtual machine on given ESXi hostname"
  community.vmware.vmware_guest:
    hostname: "{{ vcenter_hostname }}"
    username: "{{ vcenter_username }}"
    password: "{{ vcenter_password }}"
    folder: /DC1/vm/
    name: test_vm_0001
    state: present
    guest_id: centos64Guest
    esxi_hostname: "{{ esxi_hostname }}"
    disk:
    - size_gb: 10
      type: thin
      datastore: datastore1
    hardware:
      memory_mb: 512
      num_cpus: 4
      scsi: paravirtual
    networks:
    - name: VM Network
  delegate_to: localhost
  register: deploy_vm

# the next task in the playbook actually need a value from 
# the output of previous task
- name: Get the mac address from the VM creation
  set_fact:
    mac_address: "{{ deploy_vm.instance.hw_eth0.macaddress }}"

- name: "Print the generated mac"
  debug:
    var: mac_address
```

We don't need to test the module itself because the provider guaranty it is working and does what it is supposed to do.
We also don't want to actually create a VM in our infrastructure each time we run our test from the CI/CD.

For that case, we can mock the module by replacing it with the Monkeyble mock module:
```yaml
- task: "Create a virtual machine on given ESXi hostname"
  mock:
    config:
      monkeyble_module:
        consider_changed: true
        result_dict:
          instance: 
            hw_eth0:
              macaddress: "01:02:b1:03:04:9d"
```

When the playbook is executed, the module of the task is replaced by the mock
```
PLAY [Testing play] ************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************
Starting Monkeyble callback
monkeyble_scenario: validate_test_1
Monkeyble scenario: Monkeyble hello world

TASK [Create a virtual machine on given ESXi hostname] *************************************************************************************************************************************************************************************************************************************************************************************************************************************
Monkeyble mock module - Before: 'community.vmware.vmware_guest' Now: 'monkeyble_module'
changed: [localhost]

TASK [Get the mac address from the VM creation] ********************************************************************************************************************************************************************************************************************************************************************************************************************************************
ok: [localhost]

TASK [Print the generated mac] *************************************************************************************************************************************************************************************************************************************************************************************************************************************************************
ok: [localhost] => {
    "mac_address": "01:02:b1:03:04:9d"
}

PLAY RECAP *********************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************
localhost                  : ok=3    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```
