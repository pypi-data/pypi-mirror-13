# -*- coding: utf-8 -*-

import pytest
import sys
import cPickle as pickle
from test_base_class import TestBaseClass

aerospike = pytest.importorskip("aerospike")
try:
    from aerospike.exception import *
except:
    print "Please install aerospike python client."
    sys.exit(1)

class SomeClass(object):

    pass


class TestExists(TestBaseClass):
    def setup_class(cls):
        """
        Setup method.
        """
        hostlist, user, password = TestBaseClass.get_hosts()
        config = {'hosts': hostlist}
        if user == None and password == None:
            TestExists.client = aerospike.client(config).connect()
        else:
            TestExists.client = aerospike.client(config).connect(user, password)

    def teardown_class(cls):
        TestExists.client.close()

    def setup_method(self, method):

        self.keys = []

        for i in xrange(5):
            key = ('test', 'demo', i)
            rec = {'name': 'name%s' % (str(i)), 'age': i}
            TestExists.client.put(key, rec)
            self.keys.append(key)

        key = ('test', 'demo', 'list_key')
        self.keys.append(key)

        rec = {'names': ['John', 'Marlen', 'Steve']}

        TestExists.client.put(key, rec)

        key = ('test', 'demo', 'map_key')
        self.keys.append(key)

        rec = {'names': {'name': 'John', 'age': 24}}

        TestExists.client.put(key, rec)

        key = ('test', 'demo', 'list_map_key')
        self.keys.append(key)

        rec = {
            'names': ['John', 'Marlen', 'Steve'],
            'names_and_age': [{'name': 'John',
                               'age': 24}, {'name': 'Marlen',
                                            'age': 25}]
        }

        TestExists.client.put(key, rec)

        obj1, obj2 = SomeClass(), SomeClass()

        key = ('test', 'demo', 'objects')
        self.keys.append(key)

        rec = {'objects': [pickle.dumps(obj1), pickle.dumps(obj2)]}
        TestExists.client.put(key, rec)

        key = ('test', 'demo', 'bytes_key')
        self.keys.append(key)

        rec = {'bytes': bytearray('John', 'utf-8')}
        TestExists.client.put(key, rec)

    def teardown_method(self, method):
        """
        Teardoen method.
        """

        for key in self.keys:
            TestExists.client.remove(key)

    def test_exists_with_no_paramters(self):
        """
            Invoke self() without any mandatory parameters.
        """
        with pytest.raises(TypeError) as typeError:
            TestExists.client.exists()

        assert "Required argument 'key' (pos 1) not found" in typeError.value

    def test_exists_with_only_key(self):
        """
            Invoke exists() with a key and not policy's dict.
        """
        key = ('test', 'demo', 1)

        key, meta = TestExists.client.exists(key)

        assert meta['gen'] != None
        assert meta['ttl'] != None

    def test_exists_with_key_and_policy(self):
        """
            Invoke exists() with a key and policy.
        """
        key = ('test', 'demo', 1)
        policy = {
            'timeout': 1000,
            'replica': aerospike.POLICY_REPLICA_MASTER,
            'consistency': aerospike.POLICY_CONSISTENCY_ONE
        }

        key, meta = TestExists.client.exists(key, policy)

        assert meta['gen'] != None
        assert meta['ttl'] != None

    def test_exists_with_policy_is_string(self):
        """
            Invoke exists() with a key and policy as string.
        """
        key = ('test', 'demo', 1)
        policy = ""

        try:
            key, meta = TestExists.client.exists( key, policy )

        except ParamError as exception:
            assert exception.code == -2
            assert exception.msg == 'policy must be a dict'

    def test_exists_with_timeout_is_string(self):
        """
            Invoke exists() with a key and timeout as string.
        """
        key = ('test', 'demo', 1)
        policy = {'timeout': "1000"}

        try:
            key, meta = TestExists.client.exists( key, policy )

        except ParamError as exception:
            assert exception.code == -2
            assert exception.msg == 'timeout is invalid'

    def test_exists_for_list_type_record(self):
        """
            Invoke exists() for list typed record.
        """
        key = ('test', 'demo', 'list_key')

        key, meta = TestExists.client.exists(key)

        assert meta['gen'] != None
        assert meta['ttl'] != None

    def test_exists_for_map_type_record(self):
        """
            Invoke exists() for map type record.
        """
        key = ('test', 'demo', 'map_key')

        key, meta = TestExists.client.exists(key)

        assert meta['gen'] != None
        assert meta['ttl'] != None

    def test_exists_for_list_and_map_type_combined(self):
        """
            Invoke exists() for list and map combined record.
        """
        key = ('test', 'demo', 'list_map_key')

        key, meta = TestExists.client.exists(key)

        assert meta['gen'] != None
        assert meta['ttl'] != None

    def test_exists_with_list_of_objects(self):
        """
            Invoke exists() for list of objects.
        """
        key = ('test', 'demo', 'objects')

        key, meta = TestExists.client.exists(key)

        assert meta['gen'] != None
        assert meta['ttl'] != None

    def test_exists_with_bytearray(self):
        """
            Invoke exists() for bytarray record.
        """
        key = ('test', 'demo', 'bytes_key')

        key, meta = TestExists.client.exists(key)

        assert meta['gen'] != None
        assert meta['ttl'] != None

    def test_exists_with_typed_key(self):
        """
            Invoke exists() with a string key and not policy's dict.
        """
        key = ('test', 'demo', '1asfew923987fas3g')

        try:
            key, meta = TestExists.client.exists( key )

            """
            We are making the api backward compatible. In case of RecordNotFound an
            exception will not be raised. Instead Ok response is returned withe the
            meta as None. This might change with further releases.
            """
        except RecordNotFound as exception:
            assert True == False
            assert exception.code == 2
            assert exception.msg == 'AEROSPIKE_ERR_RECORD_NOT_FOUND'

        assert meta == None

    def test_exists_with_none_set(self):
        """
            Invoke exists() with None set in key tuple.
        """
        key = ('test', None, 2)

        try:
            key, meta = TestExists.client.exists( key )

            """
            We are making the api backward compatible. In case of RecordNotFound an
            exception will not be raised. Instead Ok response is returned withe the
            meta as None. This might change with further releases.
            """
        except RecordNotFound as exception:
            assert True == False
            assert exception.code == 2
            assert exception.msg == 'AEROSPIKE_ERR_RECORD_NOT_FOUND'

        assert meta == None

    def test_exists_with_none_namespace(self):
        """
            Invoke exists() with None namespace in key tuple.
        """
        key = (None, 'demo', 2)

        try:
            key, meta = TestExists.client.exists( key )

        except ParamError as exception:
            assert exception.code == -2
            assert exception.msg == 'namespace must be a string'

    def test_exists_with_none_pk(self):
        """
            Invoke exists() with None as primary_key part of key tuple.
        """
        key = ('test', 'demo', None)

        try:
            key, meta  = TestExists.client.exists( key )

        except ParamError as exception:
            assert exception.code == -2
            assert exception.msg == 'either key or digest is required'

    def test_exists_with_none_key(self):
        """
            Invoke exists() with None as a key.
        """
        try:
            key, meta  = TestExists.client.exists(None)

        except ParamError as exception:
            assert exception.code == -2
            assert exception.msg == "key is invalid"

    def test_exists_key_type_list(self):
        """
            Invoke exists() with key specified as a list of ns, set and key/digest.
        """
        key = ['test', 'demo', '1']

        try:
            key, meta = TestExists.client.exists(key)

        except ParamError as exception:
            assert exception.code == -2
            assert exception.msg == "key is invalid"

    def test_exists_with_non_existent_namespace(self):
        """
            Invoke exists() for non-existent namespace.
        """
        key = ('namespace', 'demo', 1)

        try:
            key, meta = TestExists.client.exists(key)

        except NamespaceNotFound as exception:
            assert exception.code == 20
            assert exception.msg == 'AEROSPIKE_ERR_NAMESPACE_NOT_FOUND'

    def test_exists_with_non_existent_set(self):
        """
            Invoke exists() for non-existent set.
        """
        key = ('test', 'set', 1)

        try:
            key, meta = TestExists.client.exists(key)

            """
            We are making the api backward compatible. In case of RecordNotFound an
            exception will not be raised. Instead Ok response is returned withe the
            meta as None. This might change with further releases.
            """
        except RecordNotFound as exception:
            assert True == False
            assert exception.code == 2
            assert exception.msg == 'AEROSPIKE_ERR_RECORD_NOT_FOUND'

        assert meta == None

    def test_exists_with_non_existent_key(self):
        """
            Invoke exists() for non-existent key.
        """
        key = ('test', 'demo', 'non-existent')
        try:
            key, meta = TestExists.client.exists( key )

            """
            We are making the api backward compatible. In case of RecordNotFound an
            exception will not be raised. Instead Ok response is returned withe the
            meta as None. This might change with further releases.
            """
        except RecordNotFound as exception:
            assert True == False
            assert exception.code == 2
            assert exception.msg == 'AEROSPIKE_ERR_RECORD_NOT_FOUND'

        assert meta == None

    def test_exists_with_only_key_without_connection(self):
        """
            Invoke exists() with a key and not policy's dict and no connection
        """
        key = ('test', 'demo', 1)
        config = {'hosts': [('127.0.0.1', 3000)]}
        client1 = aerospike.client(config)

        try:
            key, meta = client1.exists( key )

        except ClusterError as exception:
            assert exception.code == 11L
            assert exception.msg == 'No connection to aerospike cluster'
