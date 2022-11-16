# Installation

## Using Ansible Galaxy

Check that you have a [collection path](https://docs.ansible.com/ansible/latest/reference_appendices/config.html#collections-paths) declared in your ansible config (`collections_paths`). E.g:
```ini
[defaults]
collections_paths = /home/my_user/Documents
```

Get the callback from Ansible galaxy:
```
ansible-galaxy collection install hpe.monkeyble
```

Create a dedicated `ansible.cfg` config file that use the "Monkeyble" callback and declare the monkeyble mock module
```ini
[defaults]
collections_paths = /home/my_user/Documents
library = /home/my_user/Documents/ansible_collections/hpe/monkeyble/plugins/library
module_utils = /home/my_user/Documents/ansible_collections/hpe/monkeyble/plugins/module_utils
callbacks_enabled = monkeyble_callback
callback_plugins = /home/my_user/Documents/ansible_collections/hpe/monkeyble/plugins/callback
jinja2_native = True
```

## Using the git repository

Clone the repository
```
git clone https://github.com/HewlettPackard/monkeyble
```

Create a dedicated `ansible.cfg` config file that use the "Monkeyble" callback and declare the monkeyble mock module
```ini
[defaults]
library = ./monkeyble/plugins/library
module_utils = ./monkeyble/plugins/module_utils
callbacks_enabled = monkeyble_callback
callback_plugins = ./monkeyble/plugins/callback
jinja2_native = True
```

!!!note

    `jinja2_native` is mandatory to interpret correctly some values

That's it. Monkeyble is installed. See now the [Hello world](hello_world.md) section to learn the basics.
