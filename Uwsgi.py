"""Server Density plugin for monitoring uWSGI application server processes
(http://projects.unbit.it/uwsgi/).
"""
__author__ = "Wesley Mason <wes@1stvamp.org>"
__version__ = "1.0.0"

import subprocess

class Uwsgi:
    def __init__(self, config, logger, raw_config):
        self.config = config
        self.logger = logger
        self.raw_config = raw_config

    def run(self):
        return_data = {'Instances': 0}
        if self.config.get('UWSGI_EMPEROR_MODE', False):
            # uWSGI is running in Emperor mode, so attempt monitor each app's
            # process and check for the presence of the emperor process.
            commands = {}
            found_emperor = False
            for command in [x.rstrip('\n').split(' ', 1) \
              for x in subprocess.Popen('ps h -eo command | grep '
                            '-Fi uwsgi', stdout=subprocess.PIPE, shell=True
                            ).communicate()[0]]:
                if command.startswith('grep '):
                    continue
                if not found_emperor and '--emperor' in command:
                    found_emperor = True
                if command not in commands:
                    commands[command] = [command]
                else:
                    commands[command].append(command)
                return_data['Instances'] += 1
            if not found_emperor:
                self.logger.error('uWSGI emperor mode monitoring enabled '
                        'but emperor instance not found')
                return False
            return_data['Apps'] = len(commands)
            return_data['Average instances per app'] = sum(len(v) for k,v
                    in commands.iteritems())
        else:
            # If we know the address and port uwsgi is running on
            # try to ping it
            addresses = self.config.get('UWSGI_ADDRESSES', False)
            if addresses:
                addresses = addresses.split('\n')
                return_data['Instances down'] = 0
                for address in addresses:
                    code = subprocess.call(
                        ["/usr/bin/env uwsgi", "--ping", address.strip()],
                        shell=True
                    )
                    if code != 0:
                        return_data['Instances down'] += 1
                    else:
                        return_data['Instances'] += 1
            else:
                # No specific TCP/IP addresses to monitor and not running in
                # Emperor mode, so just check for running processes
                return_data['Instances'] = int(subprocess.Popen('ps h -eo command'
                            '| grep -Fi uwsgi | grep -Fv grep | wc -l',
                            stdout=subprocess.PIPE,
                            shell=True).communicate()[0].strip())

        return_data['Total memory (MB)'] = subprocess.Popen('ps aux | awk '
                                            "'/uwsgi/{total+=$4}END{print "
                                            "total}'", stdout=subprocess.PIPE,
                                            shell=True).communicate()[0].strip()

        return return_data
