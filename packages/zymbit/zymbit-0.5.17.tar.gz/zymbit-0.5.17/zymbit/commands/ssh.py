import logging
import os

from zymbit.commands import Command

from zymbit.util import ZymbitApi

TUNNEL_HOST = 'tunnel.zymbit.com'


class SSHCommand(Command):
    command_name = 'ssh'
    devices_endpoint = '/zymbots'

    @property
    def logger(self):
        return logging.getLogger(__name__)

    @classmethod
    def setup_parser(cls, parser):
        command_parser = super(SSHCommand, cls).setup_parser(parser)

        command_parser.add_argument('-u', '--user', default='zymbit', help='the user to login as')
        command_parser.add_argument('hostname')

        return command_parser

    def run(self):
        api = ZymbitApi()

        # get devices
        response = api.request('get', self.devices_endpoint)

        device_info = None

        devices_data = response.json()
        for item in devices_data['results']:
            if self.args.hostname.lower() == item['hostname'].lower():
                device_info = item
                break
        else:
            print 'hostname={} not found'.format(self.args.hostname)

        ssh_port = str(device_info['ssh_port'])

        command = ['ssh', '-p', ssh_port, '-l', self.args.user, TUNNEL_HOST]

        self.logger.debug(command)

        os.execvp(command[0], command)
