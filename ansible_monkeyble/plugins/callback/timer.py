from datetime import datetime

from ansible.plugins.callback import CallbackBase


class CallbackModule(CallbackBase):
    """
    This callback module tells you how long your plays ran for.
    """
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'aggregate'
    CALLBACK_NAME = 'namespace.collection_name.monkeyble_callback'

    # only needed if you ship it and don't want to enable by default
    CALLBACK_NEEDS_ENABLED = True

    def __init__(self):
        print("Init timer callback called")
        # make sure the expected objects are present, calling the base's __init__
        super(CallbackModule, self).__init__()

        # start the timer when the plugin is loaded, the first play should start a few milliseconds after.
        self.start_time = datetime.now()

    def _days_hours_minutes_seconds(self, runtime):
        ''' internal helper method for this callback '''
        minutes = (runtime.seconds // 60) % 60
        r_seconds = runtime.seconds - (minutes * 60)
        retuned = runtime.days, runtime.seconds // 3600, minutes, r_seconds
        return retuned

    # this is only event we care about for display, when the play shows its summary stats; the rest are ignored by the base class
    def v2_playbook_on_stats(self, stats):
        print("v2_playbook_on_stats called")
        end_time = datetime.now()
        runtime = end_time - self.start_time

        # Shows the usage of a config option declared in the DOCUMENTATION variable. Ansible will have set it when it loads the plugin.
        # Also note the use of the display object to print to screen. This is available to all callbacks, and you should use this over printing yourself
        # self._display.display(self._plugin_options['format_string'] % (self._days_hours_minutes_seconds(runtime)))
        days_hours_minutes_seconds = self._days_hours_minutes_seconds(runtime)
        # print(self._plugin_options['format_string'])
        format_string = "Playbook run took %s days, %s hours, %s minutes, %s seconds"
        # self._display.display(self._plugin_options['format_string'] % (days_hours_minutes_seconds))
        self._display.display(format_string % days_hours_minutes_seconds)
