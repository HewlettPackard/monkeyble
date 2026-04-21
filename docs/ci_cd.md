# CI/CD usage example

This documentation is an example of usage of Monkeyble in a CI/CD.

## Official Execution Environment

An official prebuilt [Ansible Execution Environment](https://docs.ansible.com/automation-controller/latest/html/userguide/execution_environments.html) is available on Quay.io. It ships with the Monkeyble CLI, the `hpe.monkeyble` collection, and the callback plugin already enabled in `ansible.cfg`.

```
quay.io/hewlettpackardenterprise/monkeyble:latest
```

A version-pinned tag is also available for each release (e.g. `quay.io/hewlettpackardenterprise/monkeyble:1.6.0`).

You can pull and use it directly:
```bash
docker pull quay.io/hewlettpackardenterprise/monkeyble:latest
```

Test locally against your Ansible repository:
```bash
docker run -it --rm \
-v ${PWD}:/runner/project/ \
-v /path/to/inventory_folder:/runner/inventory/ \
-w /runner/project/ \
quay.io/hewlettpackardenterprise/monkeyble:latest \
monkeyble test
```

## Build your own Execution Environment

If you need a custom image with additional collections or Python dependencies, you can build your own EE.

Example of `execution-environment.yml`:
```yaml
version: 3

images:
  base_image:
    name: quay.io/hewlettpackardenterprise/monkeyble:latest

dependencies:
  galaxy: requirements.yml  # place here your additional Ansible roles and collections
  python: requirements.txt  # place here your additional Python libraries
```

Build the execution environment:
```bash
ansible-builder build --verbosity 3 \
--tag my_registry.example/repo/my-custom-ee
```

Test locally:
```bash
docker run -it --rm \
-v ${PWD}:/runner/project/ \
-v /path/to/inventory_folder:/runner/inventory/ \
-w /runner/project/ \
my_registry.example/repo/my-custom-ee \
monkeyble test
```

## CI/CD example

### Github action

Here is a workflow example using the official Monkeyble execution environment:

```yaml
name: On pull request
on: [pull_request]

jobs:
  monkeyble-tests:
    runs-on: self-hosted

    steps:
      - name: Checkout the Ansible repo
        uses: actions/checkout@v4

      - name: Run Monkeyble tests
        run: |
          docker run --rm \
          -v ${PWD}:/runner/project/ \
          -v ${PWD}/inventories:/runner/inventory/ \
          -e VAULT_GITHUB_TOKEN=$VAULT_GITHUB_TOKEN \
          -w /runner/project/ \
          quay.io/hewlettpackardenterprise/monkeyble:latest \
          monkeyble test
```
