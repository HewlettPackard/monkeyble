from ansible.playbook.task import Task

class MockedTask(Task):
    @property
    def resolved_action(self) -> str | None:
        return super().resolved_action()

    @resolved_action.setter
    def resolved_action(self, action):
        self._resolved_action = action

    @classmethod
    def from_task(cls, task: Task) -> 'MockedTask':
        mocked_task = task.copy()
        mocked_task.__class__ = cls

        return mocked_task
