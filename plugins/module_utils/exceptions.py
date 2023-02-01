# Copyright 2022 Hewlett Packard Enterprise Development LP
import sys

from ansible.utils.display import Display
from ansible import constants as C

global_display = Display()


class MonkeybleException(Exception):
    def __init__(self, message, scenario_description=None, exit_code=1):
        super().__init__(message)
        global_display.display(msg=f"❌ MONKEYBLE ERROR ❌", color=C.COLOR_ERROR)
        if scenario_description is not None:
            global_display.display(msg=f"🙊 Failed scenario: {scenario_description}", color=C.COLOR_ERROR)
        global_display.display(msg=message, color=C.COLOR_ERROR)
        sys.exit(exit_code)
