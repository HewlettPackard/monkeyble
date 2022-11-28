# Setup a dev environment

Clone the project:
```bash
git clone https://github.com/HewlettPackard/monkeyble
```

## Install dependencies

Initializing and installing python libraries with Poetry
```
poetry install
```

A new virtual environment is created in `/home/user/.cache/pypoetry/virtualenvs/monkeyble-yk3Ua9-4-py3.10`.
You can configure your IDE to use the python binary `/home/user/.cache/pypoetry/virtualenvs/monkeyble-yk3Ua9-4-py3.10/bin/python3.10`.

## Dev the callback

### Dev with Ansible CLI

Update the test ansible playbook in `tests/test_playbook.yml`

Update the monkeyble config in `tests/monkeyble.yml`

Run the playbook using the provided `ansible.cfg` that point to the local repository:
```bash
ANSIBLE_CONFIG="ansible.cfg" ansible-playbook  tests/test_playbook.yml -e "@tests/monkeyble.yml" -e "monkeyble_scenario=validate_test_1"
```

### Dev with Python

To use the python debugger you can execute the python script `tests/local_play.py` which is based on the Ansible Python API.
```bash
python3 tests/local_play.py
```

## Dev the CLI

Execute the `cli/monkeyble_cli.py` script with an action parameter like `test`.

To execute unit tests:
```
poetry shell
python3 -m unittest discover
```
