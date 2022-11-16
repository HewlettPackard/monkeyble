# Installation

Get the callback from Ansible galaxy:
```

```

Create a dedicated `ansible.cfg` config file that use the "Monkeyble" callback and declare the monkeyble mock module
```
[defaults]
library = ./ansible_monkeyble/plugins/library
module_utils = ./ansible_monkeyble/plugins/module_utils
callbacks_enabled = monkeyble_callback
callback_plugins = ./ansible_monkeyble/plugins/callback
jinja2_native = True
```

That's it. Monkeyble is installed. See now the [Hello world](hello_world.md) section to learn the basics.
