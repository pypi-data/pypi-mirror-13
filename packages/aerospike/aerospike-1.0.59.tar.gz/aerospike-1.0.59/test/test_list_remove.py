# -*- coding: utf-8 -*-
import pytest
import time
import sys
import random
import cPickle as pickle
from test_base_class import TestBaseClass

aerospike = pytest.importorskip("aerospike")
try:
    from aerospike.exception import *
except:
    print "Please install aerospike python client."
    sys.exit(1)

class TestListRemove(object):
    def setup_class(cls):
        """
        Setup method.
        """
        hostlist, user, password = TestBaseClass.get_hosts()
        config = {'hosts': hostlist}
        if user == None and password == None:
            TestListRemove.client = aerospike.client(config).connect()
        else:
            TestListRemove.client = aerospike.client(config).connect(user, password)

    def teardown_class(cls):
        TestListRemove.client.close()

    def setup_method(self, method):
        for i in xrange(5):
            key = ('test', 'demo', i)
            rec = {'name': 'name%s' % (str(i)), 'contact_no': [i, i+1], 'city' : ['Pune', 'Dehli']}
            TestListRemove.client.put(key, rec)
        key = ('test', 'demo', 2)
        TestListRemove.client.list_append(key, "contact_no", [45, 50, 80])

    def teardown_method(self, method):
        """
        Teardown method.
        """
        #time.sleep(1)
        for i in xrange(5):
            key = ('test', 'demo', i)
            TestListRemove.client.remove(key)

    def test_list_remove_with_correct_paramters(self):
        """
        Invoke list_remove() pop string with correct parameters
        """
        key = ('test', 'demo', 1)
        
        status = TestListRemove.client.list_remove(key, "contact_no", 0)
        assert status == 0L

        (key, meta, bins) = TestListRemove.client.get(key)
        assert bins == {'city': ['Pune', 'Dehli'], 'contact_no': [2], 'name' : 'name1'}

    def test_list_remove_with_correct_policy(self):
        """
        Invoke list_remove() remove list with correct policy
        """
        key = ('test', 'demo', 2)
        policy = {
            'timeout': 1000,
            'retry': aerospike.POLICY_RETRY_ONCE,
            'commit_level': aerospike.POLICY_COMMIT_LEVEL_MASTER
        }

        status = TestListRemove.client.list_remove(key, 'contact_no', 2, {}, policy)
        assert status == 0L

        (key, meta, bins) = TestListRemove.client.get(key)
        assert bins == {'city': ['Pune', 'Dehli'], 'contact_no': [2, 3], 'name' : 'name2'}

    def test_list_remove_with_no_parameters(self):
        """
        Invoke list_remove() without any mandatory parameters.
        """
        with pytest.raises(TypeError) as typeError:
            TestListRemove.client.list_remove()
        assert "Required argument 'key' (pos 1) not found" in typeError.value

    def test_list_remove_with_incorrect_policy(self):
        """
        Invoke list_remove() with incorrect policy
        """
        key = ('test', 'demo', 1)
        policy = {
            'timeout': 0.5
        }
        try:
            TestListRemove.client.list_remove(key, "contact_no", 0, {}, policy)

        except ParamError as exception:
            assert exception.code == -2
            assert exception.msg == "timeout is invalid"

    def test_list_remove_with_nonexistent_key(self):
        """
        Invoke list_remove() with non-existent key
        """
        charSet = 'abcdefghijklmnopqrstuvwxyz1234567890'
        minLength = 5
        maxLength = 30
        length = random.randint(minLength, maxLength)
        key = ('test', 'demo', ''.join(map(lambda unused :
            random.choice(charSet), range(length)))+".com")
        try:
            TestListRemove.client.list_remove(key, "contact_no", 0)

        except BinIncompatibleType as exception:
            assert exception.code == 12L

    def test_list_remove_with_nonexistent_bin(self):
        """
        Invoke list_remove() with non-existent bin
        """
        key = ('test', 'demo', 1)
        charSet = 'abcdefghijklmnopqrstuvwxyz1234567890'
        minLength = 5
        maxLength = 10
        length = random.randint(minLength, maxLength)
        bin = ''.join(map(lambda unused :
            random.choice(charSet), range(length)))+".com"
        try:
            TestListRemove.client.list_remove(key, bin, 585)

        except BinIncompatibleType as exception:
            assert exception.code == 12L

    def test_list_remove_with_extra_parameter(self):
        """
        Invoke list_remove() with extra parameter.
        """
        key = ('test', 'demo', 1)
        policy = {'timeout': 1000}
        with pytest.raises(TypeError) as typeError:
            TestListRemove.client.list_remove(key, "contact_no", 1, {}, policy, "")

        assert "list_remove() takes at most 5 arguments (6 given)" in typeError.value

    def test_list_remove_policy_is_string(self):
        """
        Invoke list_remove() with policy is string
        """
        key = ('test', 'demo', 1)
        try:
            TestListRemove.client.list_remove(key, "contact_no", 1, {}, "")

        except ParamError as exception:
            assert exception.code == -2
            assert exception.msg == "policy must be a dict"

    def test_list_remove_key_is_none(self):
        """
        Invoke list_remove() with key is none
        """
        try:
            TestListRemove.client.list_remove(None, "contact_no", 0)

        except ParamError as exception:
            assert exception.code == -2
            assert exception.msg == "key is invalid"

    def test_list_remove_bin_is_none(self):
        """
        Invoke list_remove() with bin is none
        """
        key = ('test', 'demo', 1)
        try:
            TestListRemove.client.list_remove(key, None, 1)

        except ParamError as exception:
            assert exception.code == -2
            assert exception.msg == "Bin name should be of type string"
    
    def test_list_remove_with_negative_index(self):
        """
        Invoke list_remove() with negative index
        """
        key = ('test', 'demo', 1)
        try:
            bins = TestListRemove.client.list_remove(key, "contact_no", -56)
        except InvalidRequest as exception:
            assert exception.code == 4

    def test_list_remove_meta_type_integer(self):
        """
        Invoke list_remove() with metadata input is of type integer
        """
        key = ('test', 'demo', 1)
        try:
            TestListRemove.client.list_remove(key, "contact_no", 1, 888)

        except ParamError as exception:
            assert exception.code == -2
            assert exception.msg == "Metadata should be of type dictionary"

    def test_list_remove_index_type_string(self):
        """
        Invoke list_remove() with index is of type string
        """
        key = ('test', 'demo', 1)

        with pytest.raises(TypeError) as typeError:
            TestListRemove.client.list_remove(key, "contact_no", "Fifth")
        assert "an integer is required" in typeError.value
