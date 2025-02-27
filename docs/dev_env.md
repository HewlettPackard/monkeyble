# Setup a dev environment

## Python env

Clone the project:
```bash
git clone https://github.com/HewlettPackard/monkeyble
```

Pre-requisites: [pyenv](https://github.com/pyenv/pyenv)

```bash
cd monkeyble
pyenv install 3.12.8
pyenv virtualenv 3.12.8 monkeyble
pyenv local monkeyble
pip3 install poetry
```

## Install dependencies

Initializing and installing python libraries with Poetry
```
poetry install --with dev
```

A new virtual environment is created in `$PYENV_ROOT/versions/monkeyble`.
You can configure your IDE to use the python binary `$PYENV_ROOT/versions/monkeyble/bin/python3`.

## Dev the callback

### Dev with Ansible CLI

Update the test ansible playbook in `tests/test_playbook.yml`

Update the monkeyble config in `tests/monkeyble.yml`

Run the playbook using the provided `ansible.cfg` that point to the local repository:
```bash
ANSIBLE_CONFIG="ansible.cfg" ansible-playbook  tests/test_playbook.yml -e "@tests/monkeyble.yml" -e "monkeyble_scenario=validate_test_1"
```

To run Ansible unit test
```
cd tests/ansible_test
./run_ansible_tests.sh
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
