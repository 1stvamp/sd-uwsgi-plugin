"""Server Density plugin for monitoring uWSGI application server processes
(http://projects.unbit.it/uwsgi/).

Copyright 2011 Wesley Aaron Mason. All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are
permitted provided that the following conditions are met:

   1. Redistributions of source code must retain the above copyright notice, this list of
      conditions and the following disclaimer.

   2. Redistributions in binary form must reproduce the above copyright notice, this list
      of conditions and the following disclaimer in the documentation and/or other materials
      provided with the distribution.

THIS SOFTWARE IS PROVIDED BY WESLEY AARON MASON ''AS IS'' AND ANY EXPRESS OR IMPLIED
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL WESLEY AARON MASON OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those of the
authors and should not be interpreted as representing official policies, either expressed
or implied, of Wesley Aaron Mason.
"""

__author__ = "Wesley Mason <wes@1stvamp.org>"
__version__ = "1.0.1"

import subprocess

class UWSGI:
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
