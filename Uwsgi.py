import subprocess

class Uwsgi:
    def __init__(self, config, logger, raw_config):
        self.config = agent_config
        self.logger = main_logger
        self.raw_config = raw_config

    def run(self):
        return_data = {'instances': 0}
        if self.config.get('UWSGI_EMPEROR_MODE', False):
            commands = {}
            found_emperor = False
            for command in [x.rstrip('\n').split(' ', 1) \
              for x in subprocess.Popen(['ps', 'h', '-eo',
                            'command', '|', 'grep', '-Fi', 'uwsgi'],
                            stdout=subprocessPIPE).communicate()[0]]:
                if command.startswith('grep '):
                    continue
                if not found_emperor and '--emperor' in command:
                    found_emperor = True
                if command not in commands:
                    commands[command] = [command]
                else:
                    commands[command].append(command)
            if not found_emperor:
                self.logger.error('uWSGI emperor mode monitoring enabled'
                        'but emperor instance not found')
                return False
            return_data['Apps'] = len(commands)
            return_data['Average instances per app'] = sum(len(v) for k,v
                    in commands.iteritems())
        else:
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
                        return_data['Instances'] += 1
            else:
                pass


        return return_data
