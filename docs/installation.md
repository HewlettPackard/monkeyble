# Installation

## Using the git repository

Clone the repository
```
git clone https://github.com/HewlettPackard/monkeyble
```

Create a dedicated `ansible.cfg` config file that use the "Monkeyble" callback and declare the monkeyble mock module
```ini
[defaults]
library = /path/to/monkeyble/plugins/library
module_utils = /path/to/monkeyble/plugins/module_utils
callback_plugins = /path/to/monkeyble/plugins/callback
callbacks_enabled = monkeyble_callback
jinja2_native = True
```

!!!note

    `jinja2_native` is mandatory to interpret correctly null values

That's it. Monkeyble is installed. See now the [Hello world](hello_world.md) section to learn the basics.

## Using Ansible Galaxy

!!!info
    
    Coming soon
