from monkeyble.cli.const import *


class Colors:
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    END = '\033[0m'


class Utils(object):
    @classmethod
    def print_success(cls, message):
        print(f"{Colors.GREEN}{message}{Colors.END}")

    @classmethod
    def print_danger(cls, message):
        print(f"{Colors.RED}{message}{Colors.END}")

    @classmethod
    def print_warning(cls, message):
        print(f"{Colors.WARNING}{message}{Colors.END}")

    @classmethod
    def print_info(cls, message):
        print(f"{Colors.BLUE}{message}{Colors.END}")

    @classmethod
    def get_icon_result(cls, result_code):
        if result_code == TEST_PASSED:
            return "✅"
        return "❌"
