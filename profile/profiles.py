#!/usr/bin/python
# -*- coding: utf-8 -*-


import boto
import boto.ec2
import os
from os.path import expanduser
import logging


HOME = expanduser('~')
FILE = '.aws/config'
AWS = '/.aws/'
RELATIVE_PATH = HOME + AWS + FILE
PATH_FILE = os.path.join(expanduser('~'), '.aws/config')
LOG = logging.getLogger('AWSToolProfile.' + __name__)

class Profiles(object):

    def __init__(self, options):
        self.profile = 'profile ' + options.profile
        self.region = options.region
        self.output = options.output
        self.file_name = options.file_name
        self.list_of_instances = []
        self.headers = ''
        self.vpc = False

        if options.verbose:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)
        LOG.debug('Starting the Tool')

        boto.config.load_from_path(PATH_FILE)
        items = boto.config._sections.__getitem__(self.profile)
        LOG.debug('Getting the key and secret for the profile')
        for (key, value) in items.iteritems():
            if 'aws_access_key_id' in key:
                self.key = value
            if 'aws_secret_access_key' in key:
                self.secret = value

    def connection(self):
        """Making a connection with AWS API"""
        conn = boto.ec2.connect_to_region(self.region, aws_access_key_id=self.key, aws_secret_access_key=self.secret)
        return conn

