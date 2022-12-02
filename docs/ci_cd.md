# CI/CD usage example

This documentation is an example of usage of Monkeyble in a CI/CD.

## Create an Ansible execution environment

Create a [Ansible execution environment](https://docs.ansible.com/automation-controller/latest/html/userguide/execution_environments.html) that contains Monkeyble CLI and collections.

Example of `execution-environment.yml`:
```yaml
version: 1
dependencies:
  galaxy: requirements.yml  # place here your required Ansible role and collections
  python: requirements.txt  # place here your required python libraries
  system: bindep.txt        # place here your required system packages

ansible_config: 'ansible.cfg' 
additional_build_steps:
  prepend: |
    RUN pip3 install --upgrade pip setuptools
```

In the `requirements.txt` we should retrieve a line with the [Monkeyble cli package](https://pypi.org/project/monkeyble/). E.g:
```
monkeyble==1.2.0  # check he last version before placing it here
```

In the `requirements.yml`  we should retrieve a line with the [Monkeyble collection](https://galaxy.ansible.com/hpe/monkeyble). E.g:
```yaml
collections:
  - name: hpe.monkeyble
    version: 1.2.0  # check the last version before placing it here
```

Build the execution environment:
```bash
ansible-builder build --verbosity 3 \
--tag my_registry.example/repo/execution-environment-ansible \
--container-runtime docker
```

You can test locally the image against your repository
```bash
docker run -it --rm \
-v ${PWD}:/runner/project/ \
-v /path/to/inventory_folder:/runner/inventory/ \
-e ANSIBLE_CONFIG='monkeyble-ci.cfg' \
-w /runner/project/ \
my_registry.example/repo/execution-environment-ansible \
monkeyble test
```

## CI/CD example

### Github action

Here is a workflow example based on the built execution environment

```yaml
name: On pull request
on: [pull_request]  # set to this value when pushing in prod

jobs:
  monkeyble-tests:
    runs-on: self-hosted

    steps:
      - name: Checkout the Ansible repo
        uses: actions/checkout@v3

      - name: Run Monkeyble tests
        run: |
          docker run --rm \
          -v ${PWD}:/runner/project/ \
          -v ${PWD}/inventories:/runner/inventory/ \
          -e ANSIBLE_CONFIG='monkeyble-ci.cfg' \
          -e VAULT_GITHUB_TOKEN=$VAULT_GITHUB_TOKEN \
          -w /runner/project/ \
          my_registry.example/repo/execution-environment-ansible \
          monkeyble test
```
