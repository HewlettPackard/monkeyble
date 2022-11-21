# Installation

## Using the git repository

Clone the repository
```
git clone https://github.com/HewlettPackard/monkeyble
```

Create a dedicated `ansible.cfg` config file that use the "Monkeyble" callback and declare the monkeyble mock module
```ini
[defaults]
library = /path/to/monkeyble/plugins/module
module_utils = /path/to/monkeyble/plugins/module_utils
callback_plugins = /path/to/monkeyble/plugins/callback
callbacks_enabled = monkeyble_callback
jinja2_native = True
```

!!!note

    `jinja2_native` is mandatory to interpret correctly null values

That's it. Monkeyble is installed. See now the [Hello world](hello_world.md) section to learn the basics.

## Using Ansible Galaxy

Check that you have a [collection path](https://docs.ansible.com/ansible/latest/reference_appendices/config.html#collections-paths) 
declared in your ansible config (`collections_paths`). E.g:
```ini
[defaults]
collections_paths = /home/my_user/Documents
```

!!!note

    Ansible expect to find a folder named `ansible_collections` in the defined `collections_paths`

Install Monkeyble with ansible-galaxy and git repo:
```bash
ansible-galaxy collection install git+https://github.com/HewlettPackard/monkeyble
```

Install Monkeyble with ansible-galaxy:
```bash
ansible-galaxy collection install hpe.monkeyble
```

Create a dedicated `ansible.cfg` config file that use the "Monkeyble" callback and declare the monkeyble mock module
```ini
[defaults]
collections_paths = /home/my_user/Documents
library = /home/my_user/Documents/ansible_collections/hpe/monkeyble/plugins/module
module_utils = /home/my_user/Documents/ansible_collections/hpe/monkeyble/plugins/module_utils
callback_plugins = /home/my_user/Documents/ansible_collections/hpe/monkeyble/plugins/callback
callbacks_enabled = monkeyble_callback
jinja2_native = True
```
