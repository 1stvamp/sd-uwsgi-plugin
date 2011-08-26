import subprocess

class Uwsgi:
    def __init__(self, config, logger, raw_config):
        self.config = agent_config
        self.logger = main_logger
        self.raw_config = raw_config

    def run(self):
        return_data = {}
        if self.config.get('UWSGI_EMPEROR_MODE', False):
            pass
        else:
            return_data['Instances up'] = 0
            return_data['Instances down'] = 0
            # If we know the address and port uwsgi is running on
            # try to ping it
            addresses = self.config.get('UWSGI_ADDRESSES', False)
            if addresses:
                for address in addresses:
                    code = subprocess.call(
                        ["/usr/bin/env uwsgi", "--ping", address],
                        shell=True
                    )
                    if code != 0:
                        return_data['Instances down'] += 1
                    else:
                        return_data['Instances up'] += 1
            else:
                pass
        return return_data
