# Setup a dev environment

Requirements: ansible > 2.11

Clone the project:
```bash
git clone https://github.com/HewlettPackard/monkeyble
```

## Dev with Ansible CLI

Update the test ansible playbook in `tests/test_playbook.yml`

Update the monkeyble config in `tests/monkeyble.yml`

Run the playbook using the provided `ansible.cfg` that point to the local repository:
```bash
ANSIBLE_CONFIG="ansible.cfg" ansible-playbook  tests/test_playbook.yml -e "@tests/monkeyble.yml" -e "monkeyble_scenario=validate_test_1"
```

## Dev with Python

To use the python debugger you can execute the python script `tests/local_play.py` which is based on the Ansible Python API.
```bash
python3 tests/local_play.py
```
