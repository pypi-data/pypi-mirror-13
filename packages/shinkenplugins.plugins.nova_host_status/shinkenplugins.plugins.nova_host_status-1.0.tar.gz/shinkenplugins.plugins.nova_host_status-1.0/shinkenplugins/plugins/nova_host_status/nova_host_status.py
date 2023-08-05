#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Copyright (C) 2014, vdnguyen <vanduc.nguyen@savoirfairelinux.com>
#               2015, Grégory Starck <g.starck@gmail.com>


from __future__ import absolute_import

from novaclient import client

from shinkenplugins.plugin import ShinkenPlugin

class CheckNovaHostStatus(ShinkenPlugin):
    NAME = 'nova_host_status'
    VERSION = '1.0'
    DESCRIPTION = 'check the current status for a nova host'
    AUTHOR = 'Flavien Peyre'
    EMAIL = 'peyre.flavien@gmail.com'


    def __init__(self):
        super(CheckNovaHostStatus, self).__init__()
        self.parser.add_argument('--auth-url', '-a', required=True, help='keystone auth url')
        self.parser.add_argument('--username', '-u',  required=True, help='keystone username')
        self.parser.add_argument('--password', '-p',  required=True, help='keystone password')
        self.parser.add_argument('--tenant-name', '-t',  required=True, help='keystone tenant name')
        self.parser.add_argument('--instance-id', '-r',  required=True, help='id of the instance to check'),


    def parse_args(self, args):
        """ Use this function to handle complex conditions """
        args = super(CheckNovaHostStatus, self).parse_args(args)
        if None in (args.auth_url, args.username, args.password, args.tenant_name, args.instance_id):
            self.parser.error('--auth-url, --username, --password, --tenant-name and --instance-id are both required')
        return args


    def run(self, args):
        """ Main Plugin function """
        nova = client.Client(2, args.username, args.password, args.tenant_name, args.auth_url)
        try:
            server = nova.servers.get(args.instance_id)
        except Exception :
            self.exit(2, 'instance id unknown')

        if server.status == 'ACTIVE':
            self.exit(0, 'instance is running')
        else:
            self.exit(2, 'instance is not running')


############################################################################

Plugin = CheckNovaHostStatus

############################################################################

def main(argv=None):
    plugin = CheckNovaHostStatus()
    plugin.execute(argv)


if __name__ == "__main__":
    main()