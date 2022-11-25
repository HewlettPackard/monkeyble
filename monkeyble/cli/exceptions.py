# Copyright 2022 Hewlett Packard Enterprise Development LP
import sys

from ansible.utils.display import Display
from ansible import constants as C
from monkeyble.cli.utils import Utils

global_display = Display()


class MonkeybleCLIException(Exception):
    def __init__(self, message, exit_code=1):
        super().__init__(message)
        Utils.print_danger(message)
        sys.exit(exit_code)
