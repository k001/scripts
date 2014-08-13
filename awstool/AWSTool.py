#!/usr/bin/python
# -*- coding: utf-8 -*-


from profile import profiles
import argparse
import boto.ec2
import logging

LOG = logging.getLogger('AWSToolProfile')

SECURITY_GROUPS = []
SECURITY_GROUPS_EMPTY = []
str_deleted = []

class AWSTool(object):

    def __init__(self, options):
        LOG.info("Working in progress...")
        self.connection = profiles.Profiles(options).connection()
        self.check = options.check
        self.delete = options.delete
        self.port = options.port
        self.instances = options.instances
        self.security_group = options.security_id
        self.filter = options.filter
        self.all_instances = []
        self.open_network = options.open_network
        self.save = options.save

        if options.verbose:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)
        LOG.debug('Starting the Tool')

    def _get_all_instances(self, instances):
        instances_list = []
        for instance in instances:
            instances_list.append(instance.id)
        return instances_list

    def _get_all_ports(self, ip_permissions):
        ports = []
        for port in ip_permissions:
            for Iprange in port.grants:
                if str(Iprange.cidr_ip) == '0.0.0.0/0':
                    ports.append(port.from_port)
        return ports

    def _get_instances_by_security_group_id(self, reservation):
        if reservation.vpc_id is not None:
            instances = self.connection.get_only_instances(
                filters={'instance.group-id':reservation.id, 'instance-state-name':'running'})
        else:
            instances = self.connection.get_only_instances(
                filters={'group-id':reservation.id, 'instance-state-name':'running'})
        security_group_info = {}
        security_group_info['id'] = reservation.id
        security_group_info['name'] = reservation.name
        security_group_info['vpc'] = reservation.vpc_id
        security_group_info['instances'] = len(self._get_all_instances(instances))
        try:
            security_group_info['ports'] = "\"%s\"" % (" ".join(self._get_all_ports(reservation.rules)))
        except TypeError:
            security_group_info['ports'] = ""
        self.all_instances.append(security_group_info)

    def _get_all_security_groups(self, filters_sg=None):
        if filters_sg:
            reservation = self.connection.get_all_security_groups(filters=filters_sg)
        else:
            reservation = self.connection.get_all_security_groups()
        return reservation

    def get_all_security_groups_empty(self):
        LOG.debug("Getting all Security Groups Empty, I mean without Instances...")
        filter_to_used = {'ip-permission.cidr': '0.0.0.0/0'}

        if self.open_network:
            reservations = self._get_all_security_groups(filter_to_used)
        else:
            reservations = self._get_all_security_groups()

        for reservation in reservations:
            self._get_instances_by_security_group_id(reservation)
        # All this I don't like, I think it can be better code, TODO someday
        headers = "{:<10}, {:<10}, {:<10}, {:<10}, {:<10}\n".format('Id', 'Name', 'VPC', 'Instances #', 'Ports')
        body = ''
        for instance in self.all_instances:
            body += "{:<10}, {:<10}, {:<10}, {:<10}, {:<10}\n".format(
                instance['id'], instance['name'], instance['vpc'], instance['instances'], instance['ports'])

        if body != "":
            print headers
            print body

        if self.save:
            fd = open(LOG.name+'.csv', 'w')
            fd.write(headers)
            fd.writelines(body)
            fd.close()

    def delete_securitygroup(self, idSec=None, nameSec=None):
        try:
            deleted = boto.ec2.securitygroup.SecurityGroup(self.connection, id=idSec, name=nameSec).delete()
            str_del = "Name: %s \tDeleted: %s" % (nameSec, deleted)
            LOG.info(str_del)
        except boto.exception.EC2ResponseError, e:
            data = e
            print data
            #print dir(data)
            #root = objectify.fromstring(data).Errors.Error.Message
            #error = "Can delete: %s, error: %s" % (idSec, root)
            #LOG.error(error)

    def get_security_group_by_id(self):
        self._get_instances_by_security_group_id(self.security_group)

    def get_all_instances_by_security_group(self):
        if self.security_group.startswith('sg-'):
            filter_to_use = {'group-id': self.security_group}
        else:
            filter_to_use = {'group-name': self.security_group}
        reservations = self._get_all_security_groups(filter_to_use)
        return reservations

def run(options):
    '''Principal method to run'''

    if not options.profile:
        print options.print_help()
        return 0
    else:
        tool = AWSTool(options)
        if options.security_id:
            tool.get_security_group_by_id()
        elif options.check:
            tool.get_all_security_groups_empty()
        elif options.instances:
            LOG.info("Returning all Instances")
            tool.get_all_instances_by_security_group()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-p',
        '--profile',
        dest='profile',
        required=True,
        action='store',
        help='Required for add the properprofile from the config file from $HOME/\
            .aws path'
        )

    parser.add_argument(
        '-r',
        '--region',
        dest='region',
        action='store',
        default='us-east-1',
        help='Required for region for AWS,default region us-east-1'
        )
    parser.add_argument(
        '-o',
        '--out',
        dest='output',
        action='store',
        choices=['xml', 'json', 'csv', 'console'],
        default='console',
        help='Output format'
        )
    parser.add_argument('-n', '--name', dest='file_name', action='store'
                        , help='Name of output file')
    parser.add_argument('-v', '--verbose', dest='verbose',
                        action='store_true', help='Enable debug verbose')
    parser.add_argument('--version', action='version',
                        version='%(prog)s 1.0')
    parser.add_argument('-c', '--check', action='store_true',
                        dest='check',
                        help='Get all Security Groups Empty')
    parser.add_argument('-d', '--delete', action='store_true',
                        dest='delete',
                        help='Delete Security Group, only if this empty')
    parser.add_argument('-i', '--instances', action='store_true',
                        dest='instances',
                        help='Get the number of instances running')
    parser.add_argument('--network', action='store_true',
                        dest='open_network',
                        help='Checking the open world 0.0.0.0/0 issue')
    parser.add_argument('-s', '--security_id', action='store',
                        dest='security_id',
                        help='Return all Instances by Security Group Id')
    parser.add_argument('--save', action='store_true',
                        dest='save',
                        help='Save output into a file csv format')
    parser.add_argument('--port', action='store',
                        dest='port', default='22',
                        help='Define the port to check')
    parser.add_argument('--filter', action='store',
                        dest='filter',
                        help='Define filter to use')
    options = parser.parse_args()
    run(options)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        raise
