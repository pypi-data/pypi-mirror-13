# -*- coding: utf-8 -*-

import pytest
import sys
import json
import cPickle as pickle
from test_base_class import TestBaseClass

aerospike = pytest.importorskip("aerospike")
try:
    from aerospike.exception import *
except:
    print "Please install aerospike python client."
    sys.exit(1)

class TestConnect(TestBaseClass):
    def setup_class(cls):
        hostlist, user, password = TestBaseClass.get_hosts()
        config = {'hosts': hostlist}
        TestConnect.config = config

    def test_version(self):
        """
            Check for aerospike vrsion
        """
        assert aerospike.__version__ != None

    def test_connect_positive(self):
        """
            Invoke connect() with positive parameters.
        """
        config = {'hosts': TestConnect.hostlist}
        if TestConnect.user == None and TestConnect.password == None:
            self.client = aerospike.client(config).connect()
        else:
            self.client = aerospike.client(config).connect(
                TestConnect.user, TestConnect.password)

        assert self.client != None
        assert self.client.is_connected() == True
        self.client.close()

    def test_connect_positive_with_policy(self):
        """
            Invoke connect() with positive parameters and policy.
        """
        config = {
            'hosts': TestConnect.hostlist,
            'policies': {'timeout': 10000}
        }
        if TestConnect.user == None and TestConnect.password == None:
            self.client = aerospike.client(config).connect()
        else:
            self.client = aerospike.client(config).connect(
                TestConnect.user, TestConnect.password)

        assert self.client.is_connected() == True
        assert self.client.is_connected() == True
        self.client.close()

    def test_connect_positive_with_multiple_hosts(self):
        """
            Invoke connect() with multiple hosts.
        """
        config = {'hosts': TestConnect.hostlist}
        if TestConnect.user == None and TestConnect.password == None:
            self.client = aerospike.client(config).connect()
        else:
            self.client = aerospike.client(config).connect(
                TestConnect.user, TestConnect.password)

        assert self.client != None
        self.client.close()

    def test_connect_positive_unicode_hosts(self):
        """
            Invoke connect() with unicode hosts.
        """
        uni = json.dumps(TestConnect.hostlist[0])
        hostlist = json.loads(uni)
        config = {'hosts': [(hostlist[0], hostlist[1])],
                'policies': {'use_batch_direct': True}
                }
        if TestConnect.user == None and TestConnect.password == None:
            self.client = aerospike.client(config).connect()
        else:
            self.client = aerospike.client(config).connect(
                TestConnect.user, TestConnect.password)

        assert self.client != None
        assert self.client.is_connected() == True
        self.client.close()

    def test_connect_config_not_dict(self):
        """
            Invoke connect with config as Integer (non-dict)
        """
        config = 1
        try:
            self.client = aerospike.client(config).connect()
        except ParamError as exception:
            assert exception.code == -2
            assert exception.msg == "Parameters are incorrect"
    
    def test_connect_config_empty_dict(self):
        """
            Invoke connect() with config as empty dict.
        """
        config = {
                }
        try:
            self.client = aerospike.client(config).connect()

        except ParamError as exception:
            assert exception.code == -2L
            assert exception.msg == 'No hosts provided'

    def test_connect_missing_hosts_key(self):
        """
            Invoke connect() with host key missing in config dict.
        """
        config = {
                '': [('127.0.0.1', 3000)]
                }
        try:
            self.client = aerospike.client(config).connect()

        except ParamError as exception:
            assert exception.code == -2L
            assert exception.msg == 'No hosts provided'

    def test_connect_missing_address(self):
        """
            Invoke connect() with missing address in config dict.
        """
        config = {
                'hosts': [3000]
                }
        try:
            self.client = aerospike.client(config).connect()

        except ParamError as exception:
            assert exception.code == -2L

    def test_connect_missing_port(self):
        """
            Invoke connect() with missing port in config dict.
        """
        config = {
                'hosts': [('127.0.0.1')]
                }
        self.client = aerospike.client(config)
        try:
            self.client.connect()
            self.client.close()
        except ClientError as exception:
            assert exception.code == -1
            assert self.client.is_connected() != True

    def test_connect_incorrect_port(self):
        """
            Invoke connect() with incorrect port in config dict.
        """
        config = {
                'hosts': [('127.0.0.1', 2000)]
                }
        try:
            self.client = aerospike.client(config).connect()

        except ClientError as exception:
            assert exception.code == -1
            assert exception.msg == 'Failed to seed cluster'

    def test_connect_port_is_string(self):
        """
            Invoke connect() with port as string in config dict.
        """
        config = {
                'hosts': [('127.0.0.1', '3000')]
                }
        try:
            self.client = aerospike.client(config).connect()

        except ClientError as exception:
            assert exception.code == -1
            assert exception.msg == 'Failed to seed cluster'

    def test_connect_positive_shm_key(self):
        """
            Invoke connect() with shm_key specified
        """
        config = {'hosts': TestConnect.hostlist,
                'shm': {'shm_key': 3}
                }
        if TestConnect.user == None and TestConnect.password == None:
            self.client = aerospike.client(config).connect()
        else:
            self.client = aerospike.client(config).connect(
                TestConnect.user, TestConnect.password)

        assert self.client != None
        assert self.client.is_connected() == True
        assert self.client.shm_key() == 3
        self.client.close()

    def test_connect_positive_shm_key_default(self):
        """
            Invoke connect() with shm enabled but shm_key not specified
        """
        config = {'hosts': TestConnect.hostlist,
                'shm': {'shm_max_nodes': 5}
                }
        if TestConnect.user == None and TestConnect.password == None:
            self.client = aerospike.client(config).connect()
        else:
            self.client = aerospike.client(config).connect(
                TestConnect.user, TestConnect.password)

        assert self.client != None
        assert self.client.is_connected() == True
        assert self.client.shm_key() == 2768240640
        self.client.close()

    def test_connect_positive_shm_not_enabled(self):
        """
            Invoke connect() with shm not anabled
        """
        config = {'hosts': TestConnect.hostlist,
                }
        if TestConnect.user == None and TestConnect.password == None:
            self.client = aerospike.client(config).connect()
        else:
            self.client = aerospike.client(config).connect(
                TestConnect.user, TestConnect.password)

        assert self.client != None
        assert self.client.is_connected() == True
        assert self.client.shm_key() == None
        self.client.close()
