from ansible.plugins.strategy.linear import StrategyModule as LinearStrategyModule


class StrategyModule(LinearStrategyModule):
    def __init__(self, *args, **kwargs):

        print("test")
        super().__init__(*args, **kwargs)
        # super(StrategyModule, self).__init__(tqm)
        # self.debugger_active = True

    def run(self, iterator, play_context, result=0):
        print("test run")
        new_vars = {
            "my_var": "updated !!!"
        }
        play_context.vars = new_vars
        iterator._variable_manager._extra_vars = new_vars

        iterator._play.tasks[0].block[0].action = "monkeyble"
        original_module_args = iterator._play.tasks[0].block[0].args
        iterator._play.tasks[0].block[0].args = {"monkeyble_task_name": iterator._play.tasks[0].block[0].name,
                                                 "original_module_args": original_module_args}

        return super(StrategyModule, self).run(iterator, play_context)
