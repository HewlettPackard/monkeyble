
class ScenarioResult(object):
    def __init__(self, scenario, result=None):
        self.scenario = scenario
        self.result = result


class MonkeybleResult(object):
    def __init__(self, playbook, scenario_results=list):
        self.playbook = playbook
        self.scenario_results = scenario_results
