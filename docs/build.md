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

The build package need to be present
```
pip3 install build
```

Build the CLI:
```
python -m build
```

This command creates a file in `dist/`


Publish to test env Pypi:
```
python3 -m twine upload --repository testpypi -u sispheor -p $PYPI_PASSWORD dist/*
```

Publish to prod env Pypi:
```
python3 -m twine upload --repository pypi dist/*
```

Test installing with pipx
```
pipx inject ansible --index-url https://test.pypi.org/simple/ --include-apps monkeyble
```
