# -*- coding: utf-8 -*-
import pytest
import time
import sys
import cPickle as pickle
from test_base_class import TestBaseClass

aerospike = pytest.importorskip("aerospike")
try:
    from aerospike.exception import *
except:
    print "Please install aerospike python client."
    sys.exit(1)

class TestAppend(object):
    def setup_class(cls):
        """
        Setup method.
        """
        hostlist, user, password = TestBaseClass.get_hosts()
        config = {'hosts': hostlist}
        if user == None and password == None:
            TestAppend.client = aerospike.client(config).connect()
        else:
            TestAppend.client = aerospike.client(config).connect(user, password)

    def teardown_class(cls):
        TestAppend.client.close()

    def setup_method(self, method):
        for i in xrange(5):
            key = ('test', 'demo', i)
            rec = {'name': 'name%s' % (str(i)), 'age': i}
            TestAppend.client.put(key, rec)
        key = ('test', 'demo', 'bytearray_key')
        TestAppend.client.put(key, {"bytearray_bin": bytearray("asd;as[d'as;d",
            "utf-8")})

    def teardown_method(self, method):
        """
        Teardoen method.
        """
        #time.sleep(1)
        for i in xrange(5):
            key = ('test', 'demo', i)
            TestAppend.client.remove(key)
        key = ('test', 'demo', 'bytearray_key')
        TestAppend.client.remove(key)

    def test_append_with_no_parameters(self):
        """
        Invoke append() without any mandatory parameters.
        """
        with pytest.raises(TypeError) as typeError:
            TestAppend.client.append()
        assert "Required argument 'key' (pos 1) not found" in typeError.value

    def test_append_with_correct_paramters(self):
        """
        Invoke append() with correct parameters
        """
        key = ('test', 'demo', 1)
        TestAppend.client.append(key, "name", "str")

        (key, meta, bins) = TestAppend.client.get(key)

        assert bins == {'age': 1, 'name': 'name1str'}

    def test_append_with_correct_policy(self):
        """
        Invoke append() with correct policy
        """
        key = ('test', 'demo', 1)
        policy = {
            'timeout': 1000,
            'retry': aerospike.POLICY_RETRY_ONCE,
            'commit_level': aerospike.POLICY_COMMIT_LEVEL_MASTER
        }
        TestAppend.client.append(key, "name", "str", {}, policy)

        (key, meta, bins) = TestAppend.client.get(key)

        assert bins == {'age': 1, 'name': 'name1str'}

    def test_append_with_policy_key_send(self):
        """
        Invoke append() with policy key send
        """
        key = ('test', 'demo', 1)
        policy = {
            'timeout': 1000,
            'key': aerospike.POLICY_KEY_SEND,
            'retry': aerospike.POLICY_RETRY_ONCE,
            'commit_level': aerospike.POLICY_COMMIT_LEVEL_ALL
        }
        TestAppend.client.append(key, "name", "str", {}, policy)

        (key, meta, bins) = TestAppend.client.get(key)

        assert bins == {'age': 1, 'name': 'name1str'}
        assert key == ('test', 'demo', None, bytearray(
            b'\xb7\xf4\xb88\x89\xe2\xdag\xdeh>\x1d\xf6\x91\x9a\x1e\xac\xc4F\xc8')
                      )

    def test_append_with_policy_key_digest(self):
        """
        Invoke append() with policy key digest
        """
        key = ('test', 'demo', None, bytearray("asd;as[d'as;djk;uyfl",
                                               "utf-8"))
        rec = {'name': 'name%s' % (str(1)), 'age': 1, 'nolist': [1, 2, 3]}
        TestAppend.client.put(key, rec)

        policy = {
            'timeout': 1000,
            'key': aerospike.POLICY_KEY_DIGEST,
            'retry': aerospike.POLICY_RETRY_NONE
        }
        TestAppend.client.append(key, "name", "str", {}, policy)

        (key, meta, bins) = TestAppend.client.get(key)

        assert bins == {'age': 1, 'name': 'name1str', 'nolist': [1, 2, 3]}
        assert key == ('test', 'demo', None,
                       bytearray(b"asd;as[d\'as;djk;uyfl"))

        TestAppend.client.remove(key)

    def test_append_with_policy_key_gen_EQ_ignore(self):
        """
        Invoke append() with gen eq positive ignore
        """
        key = ('test', 'demo', 1)
        policy = {
            'timeout': 1000,
            'key': aerospike.POLICY_KEY_SEND,
            'retry': aerospike.POLICY_RETRY_ONCE,
            'gen': aerospike.POLICY_GEN_IGNORE
        }

        meta = {'gen': 10, 'ttl': 1200}
        TestAppend.client.append(key, "name", "str", meta, policy)

        (key, meta, bins) = TestAppend.client.get(key)

        assert bins == {'age': 1, 'name': 'name1str'}
        assert key == ('test', 'demo', None, bytearray(
            b'\xb7\xf4\xb88\x89\xe2\xdag\xdeh>\x1d\xf6\x91\x9a\x1e\xac\xc4F\xc8')
                      )

    def test_append_with_policy_key_gen_EQ_positive(self):
        """
        Invoke append() with gen eq positive
        """
        key = ('test', 'demo', 1)
        policy = {
            'timeout': 1000,
            'key': aerospike.POLICY_KEY_SEND,
            'retry': aerospike.POLICY_RETRY_ONCE,
            'gen': aerospike.POLICY_GEN_EQ
        }
        (key, meta) = TestAppend.client.exists(key)

        gen = meta['gen']

        meta = {'gen': gen, 'ttl': 1200}
        TestAppend.client.append(key, "name", "str", meta, policy)

        (key, meta, bins) = TestAppend.client.get(key)

        assert bins == {'age': 1, 'name': 'name1str'}
        assert key == ('test', 'demo', None, bytearray(
            b'\xb7\xf4\xb88\x89\xe2\xdag\xdeh>\x1d\xf6\x91\x9a\x1e\xac\xc4F\xc8')
                      )

    def test_append_with_policy_key_gen_GT_lesser(self):
        """
        Invoke append() with gen GT lesser
        """
        key = ('test', 'demo', 1)
        policy = {
            'timeout': 1000,
            'key': aerospike.POLICY_KEY_SEND,
            'retry': aerospike.POLICY_RETRY_ONCE,
            'gen': aerospike.POLICY_GEN_GT
        }
        (key, meta) = TestAppend.client.exists(key)

        gen = meta['gen']

        meta = {
            'gen': gen,
            'ttl': 1200
        }
        try:
            TestAppend.client.append(key, "name", "str", meta, policy)

        except RecordGenerationError as exception:
            assert exception.code == 3
            assert exception.msg == "AEROSPIKE_ERR_RECORD_GENERATION"
            assert exception.bin == "name"

        (key , meta, bins) = TestAppend.client.get(key)

        assert bins == {'age': 1, 'name': 'name1'}
        assert key == ('test', 'demo', None, bytearray(
            b'\xb7\xf4\xb88\x89\xe2\xdag\xdeh>\x1d\xf6\x91\x9a\x1e\xac\xc4F\xc8')
                      )

    def test_append_with_policy_key_gen_GT_positive(self):
        """
        Invoke append() with gen GT positive
        """
        key = ('test', 'demo', 1)
        policy = {
            'timeout': 1000,
            'key': aerospike.POLICY_KEY_SEND,
            'retry': aerospike.POLICY_RETRY_ONCE,
            'gen': aerospike.POLICY_GEN_GT
        }
        (key, meta) = TestAppend.client.exists(key)

        gen = meta['gen']

        meta = {'gen': gen + 2, 'ttl': 1200}
        TestAppend.client.append(key, "name", "str", meta, policy)

        (key, meta, bins) = TestAppend.client.get(key)

        assert bins == {'age': 1, 'name': 'name1str'}
        assert key == ('test', 'demo', None, bytearray(
            b'\xb7\xf4\xb88\x89\xe2\xdag\xdeh>\x1d\xf6\x91\x9a\x1e\xac\xc4F\xc8')
                      )

    def test_append_with_policy_key_gen_EQ_not_equal(self):
        """
        Invoke append() with policy key EQ not equal
        """
        key = ('test', 'demo', 1)
        policy = {
            'timeout': 1000,
            'key': aerospike.POLICY_KEY_SEND,
            'retry': aerospike.POLICY_RETRY_ONCE,
            'gen': aerospike.POLICY_GEN_EQ
        }
        (key, meta) = TestAppend.client.exists(key)
        gen = meta['gen']

        meta = {
            'gen': gen + 5,
            'ttl': 1200
        }
        try:
            TestAppend.client.append(key, "name", "str", meta, policy)

        except RecordGenerationError as exception:
            assert exception.code == 3
            assert exception.msg == "AEROSPIKE_ERR_RECORD_GENERATION"
            assert exception.bin == "name"

        (key , meta, bins) = TestAppend.client.get(key)

        assert bins == {'age': 1, 'name': 'name1'}
        assert key == ('test', 'demo', None, bytearray(
            b'\xb7\xf4\xb88\x89\xe2\xdag\xdeh>\x1d\xf6\x91\x9a\x1e\xac\xc4F\xc8')
                      )

    def test_append_with_incorrect_policy(self):
        """
        Invoke append() with incorrect policy
        """
        key = ('test', 'demo', 1)
        policy = {
            'timeout': 0.5
        }
        try:
            TestAppend.client.append(key, "name", "str", {}, policy)

        except ParamError as exception:
            assert exception.code == -2
            assert exception.msg == "timeout is invalid"

    def test_append_with_nonexistent_key(self):
        """
        Invoke append() with non-existent key
        """
        key = ('test', 'demo', 1000)
        status = TestAppend.client.append(key, "name", "str")

        assert status == 0L
        TestAppend.client.remove(key)

    def test_append_with_nonexistent_bin(self):
        """
        Invoke append() with non-existent bin
        """
        key = ('test', 'demo', 1)
        status = TestAppend.client.append(key, "name1", "str")

        assert status == 0L

    def test_append_value_not_string(self):
        """
        Invoke append() not a string
        """
        key = ('test', 'demo', 1)
        try:
            TestAppend.client.append(key, "name", 2)

        except ParamError as exception:
            assert exception.code == -2
            assert exception.msg == "Cannot concatenate 'str' and 'non-str' objects"

    def test_append_with_extra_parameter(self):
        """
        Invoke append() with extra parameter.
        """
        key = ('test', 'demo', 1)
        policy = {'timeout': 1000}
        with pytest.raises(TypeError) as typeError:
            TestAppend.client.append(key, "name", "str", {}, policy, "")

        assert "append() takes at most 5 arguments (6 given)" in typeError.value

    def test_append_policy_is_string(self):
        """
        Invoke append() with policy is string
        """
        key = ('test', 'demo', 1)
        try:
            TestAppend.client.append(key, "name", "pqr", {}, "")

        except ParamError as exception:
            assert exception.code == -2
            assert exception.msg == "policy must be a dict"

    def test_append_key_is_none(self):
        """
        Invoke append() with key is none
        """
        try:
            TestAppend.client.append(None, "name", "str")

        except ParamError as exception:
            assert exception.code == -2
            assert exception.msg == "key is invalid"

    def test_append_bin_is_none(self):
        """
        Invoke append() with bin is none
        """
        key = ('test', 'demo', 1)
        try:
            TestAppend.client.append(key, None, "str")

        except ParamError as exception:
            assert exception.code == -2
            assert exception.msg == "Bin name should be of type string"
    
    def test_append_unicode_value(self):
        """
        Invoke append() with unicode string
        """
        key = ('test', 'demo', 1)
        res = TestAppend.client.append(key, "name", u"address")

        key, meta, bins = TestAppend.client.get(key)
        assert bins['name'] == 'name1address'

    def test_append_unicode_bin_name(self):
        """
        Invoke append() with unicode string
        """
        key = ('test', 'demo', 1)
        res = TestAppend.client.append(key, u"add", u"address")

        key, meta, bins = TestAppend.client.get(key)
        assert bins['add'] == 'address'

    def test_append_with_correct_paramters_without_connection(self):
        """
        Invoke append() with correct parameters without connection
        """
        config = {'hosts': [('127.0.0.1', 3000)]}
        client1 = aerospike.client(config)
        key = ('test', 'demo', 1)

        try:
            client1.append(key, "name", "str")

        except ClusterError as exception:
            assert exception.code == 11L
            assert exception.msg == 'No connection to aerospike cluster'

    def test_append_with_bytearray(self):
        """
        Invoke append() with bytearray value
        """
        key = ('test', 'demo', 'bytearray_key')
        TestAppend.client.append(key, "bytearray_bin", bytearray("abc"))

        (key, meta, bins) = TestAppend.client.get(key)

        assert bins == {'bytearray_bin': "asd;as[d'as;dabc"}

    def test_append_with_bytearray_new_key(self):
        """
        Invoke append() with bytearray value with a new record(non-existing)
        """
        key = ('test', 'demo', 'bytearray_new')
        TestAppend.client.append(key, "bytearray_bin", bytearray("asd;as[d'as;d", "utf-8"))

        (key, meta, bins) = TestAppend.client.get(key)

        assert bins == {'bytearray_bin': "asd;as[d'as;d"}

        TestAppend.client.remove(key)
