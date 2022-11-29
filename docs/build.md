# Build

## Ansible collection

Build the collection
```
ansible-galaxy collection build
```

Push to Galaxy:
```
ansible-galaxy collection publish <built_tarball>
```

E.g:
```
ansible-galaxy collection publish hpe-monkeyble-1.0.3.tar.gz
```

## Python package

Build the CLI:
```
poetry build
```

This command creates a file in `dist/`

Configure poetry

```
# dev
poetry config repositories.test-pypi https://test.pypi.org/legacy/
poetry config pypi-token.test-pypi $TEST_PYPI_TOKEN

# prod
poetry config pypi-token.pypi $PYPI_TOKEN
```

Publish to test env Pypi:
```
poetry publish --repository test-pypi
```

Publish to prod env Pypi:
```
poetry publish
```

Test installing with pipx
```
pipx inject ansible --index-url https://test.pypi.org/simple/ --include-apps monkeyble
```
