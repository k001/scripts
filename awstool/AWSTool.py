#!/usr/bin/python
# -*- coding: utf-8 -*-


from profile import profiles
import argparse
import boto.ec2
import logging
import sys

LOG = logging.getLogger('AWSToolProfile.' + __name__)

SECURITY_GROUPS = []
str_deleted = []

class AWSTool(object):

    def __init__(self, options):
        self.connection = profiles.Profiles(options).connection()
        self.check = options.check
        self.delete = options.delete

        if options.verbose:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)
        LOG.debug('Starting the Tool')

    def get_all_securitygroups(self):
        filter_to_used = {'ip-permission.cidr': '0.0.0.0/0'}
        if self.check is True:
            reservations = self.connection.get_all_security_groups(filters=filter_to_used)
        else:
            reservations = self.connection.get_all_security_groups()
        LOG.info("I'm working please be patient...")
        for reservation in reservations:
            self.get_instances_of_securitygroups(reservation)
        print "ID\t\tNAME\t\t\t"
        for seg in SECURITY_GROUPS:
            string_print = ''
            for key, value in seg.items():
                if key is not 'VPC':
                    string_print += "%s\t%s\t" % (key, value)
                else:
                    string_print += "%s" % (value)
                print string_print
        print str_deleted

    def delete_securitygroup(self, idSec=None, nameSec=None):
        try:
            deleted = boto.ec2.securitygroup.SecurityGroup(self.connection, id=idSec, name=nameSec).delete()
            str_del = "Name: %s \tDeleted: %s" % (nameSec, deleted)
            LOG.info(str_del)
        except boto.exception.EC2ResponseError, e:
            error = "Can delete: %s, error: %s" % (idSec, e)
            LOG.error(error)


    def get_instances_of_securitygroups(self, securitygroup):
        security_groups = boto.ec2.securitygroup.SecurityGroup(self.connection, id=securitygroup.id)
        instances = security_groups.instances()
        if not instances:
            if self.delete:
                self.delete_securitygroup(idSec=securitygroup.id, nameSec=securitygroup.name)
            if securitygroup.vpc_id is None:
                vpc = None
            else:
                vpc = securitygroup.vpc_id
            SECURITY_GROUPS.append({securitygroup.id:securitygroup.name, 'VPC':vpc})

def run(options):
    """Principal method to run"""

    if not options.profile:
        print options.print_help()
        return 0
    else:
        tool = AWSTool(options)
        tool.get_all_securitygroups()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-p',
        '--profile',
        dest='profile',
        required=True,
        action='store',
        default='zzlivepush',
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
                        help='To check Security Groups with 0.0.0.0/0 to any port')
    parser.add_argument('-d', '--delete', action='store_true',
                        dest='delete',
                        help='Delete Security Group, only if this empty')

    options = parser.parse_args()
    run(options)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        raise
    finally:
        print "\n"
        print 'At least I hope you thank me, if I went to help, at least! %s' % sys.argv[0]


