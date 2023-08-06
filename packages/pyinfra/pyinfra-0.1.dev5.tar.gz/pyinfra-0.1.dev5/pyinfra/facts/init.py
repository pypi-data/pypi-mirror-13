# pyinfra
# File: pyinfra/facts/init.py
# Desc: init system facts

import re

from pyinfra.api import FactBase


class SystemctlStatus(FactBase):
    '''Returns a dict of name -> status for systemd managed services.'''

    command = 'systemctl -alt service list-units'
    _regex = r'^([a-z\-]+)\.service\s+[a-z\-]+\s+[a-z]+\s+([a-z]+)'

    def process(self, output):
        services = {}

        for line in output:
            matches = re.match(self._regex, line)
            if matches:
                services[matches.group(1)] = matches.group(2) == 'running'

        return services


class ServiceStatus(FactBase):
    '''Returns a dict of name -> status for services listed by "service".'''

    command = 'service --status-all'

    _regexes = [
        # [ <status> ] <name>
        (r'^\[ ([+-\?]) \]\s+([a-zA-Z0-9\-\.]+)$', lambda matches: (
            matches.group(2),
            True if matches.group(1) == '+' else False if matches.group(1) == '-' else None
        )),
        # <name> is stopped
        (r'^([a-zA-Z0-9\.\-]+) is stopped$', lambda matches: (matches.group(1), False)),
        # <name> (pid  <pid>) is running
        (r'^([a-zA-Z0-9\.\-]+) \(pid  [0-9]+\) is running\.*$', lambda matches: (matches.group(1), True))
    ]

    def process(self, output):
        services = {}

        for line in output:
            for (regex, handler) in self._regexes:
                matches = re.match(regex, line)
                if matches:
                    name, status = handler(matches)
                    services[name] = status
                    continue

        return services


class InitdStatus(FactBase):
    '''
    Low level check for every /etc/init.d/* script. Unfortunately many of these mishehave and return
    exit status 0 while also displaying the help info/not offering status support.

    Returns a dict of name -> status.

    Expected codes found at:
        http://refspecs.linuxbase.org/LSB_3.1.0/LSB-Core-generic/LSB-Core-generic/iniscrptact.html
    '''

    command = '''
        for SERVICE in `ls /etc/init.d/`; do
            _=`cat /etc/init.d/$SERVICE | grep "### BEGIN INIT INFO"`

            if [ "$?" = "0" ]; then
                STATUS=`/etc/init.d/$SERVICE status`
                echo "$SERVICE=$?"
            fi
        done
    '''
    _regex = r'([a-zA-Z0-9]+)=([0-9]+)'

    def process(self, output):
        services = {}

        for line in output:
            matches = re.match(self._regex, line)
            if matches:
                status = int(matches.group(2))
                # Exit code 0 = OK/running
                if status == 0:
                    status = True
                # Exit codes 1-3 = DOWN/not running
                elif status < 4:
                    status = False
                # Exit codes 4+ = unknown
                else:
                    status = None

                services[matches.group(1)] = status

        return services

class RcdStatus(InitdStatus):
    '''
    As above but for BSD (/etc/rc.d) systems. Unlike Linux/init.d, BSD init scripts are
    well behaved and as such their output can be trusted.
    '''

    command = '''
        for SERVICE in `ls /etc/rc.d/`; do
            _=`cat /etc/rc.d/$SERVICE | grep "daemon="`

            if [ "$?" = "0" ]; then
                STATUS=`/etc/rc.d/$SERVICE check`
                echo "$SERVICE=$?"
            fi
        done
    '''
