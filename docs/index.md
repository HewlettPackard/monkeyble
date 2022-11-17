# Monkeyble

<p align="center">
    <img src="images/monkeyble_logo.png">
</p>

Welcome to the Monkeyble documentation! 👋

Monkeyble is a callback plugin for Ansible that allow to execute end-to-end tests on Ansible playbooks with a 
Pythonic testing approach. 🐍

Monkeyble allows, at task level, to:

- 🐵 Check that a module has been called with expected argument values
- 🙊 Check that a module returned the expected result dictionary
- 🙈 Check the task state (changed, skipped, failed)
- 🙉 Mock a module and return a defined dictionary as result

Monkeyble is designed to be executed by a CI/CD in order to detect regressions when updating an Ansible code base. 🚀  
