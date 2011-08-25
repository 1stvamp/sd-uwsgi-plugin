class Uwsgi:
    def __init__(self, agent_config, main_logger, raw_config):
        self.agent_config = agent_config
        self.main_logger = main_logger
        self.raw_config = raw_config

    def run(self):
        return {}
