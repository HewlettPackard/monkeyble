from ansible.playbook.task import Task

class MockedTask(Task):
    """Task subclass that allows setting resolved_action, needed for Ansible 2.19+."""

    @property
    def resolved_action(self) -> str | None:
        return super().resolved_action()

    @resolved_action.setter
    def resolved_action(self, action):
        self._resolved_action = action
