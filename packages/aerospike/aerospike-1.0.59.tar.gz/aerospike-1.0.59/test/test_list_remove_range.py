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

class TestListRemoveRange(object):
    def setup_class(cls):
        """
        Setup method.
        """
        hostlist, user, password = TestBaseClass.get_hosts()
        config = {'hosts': hostlist}
        if user == None and password == None:
            TestListRemoveRange.client = aerospike.client(config).connect()
        else:
            TestListRemoveRange.client = aerospike.client(config).connect(user, password)

    def teardown_class(cls):
        TestListRemoveRange.client.close()

    def setup_method(self, method):
        for i in xrange(5):
            key = ('test', 'demo', i)
            rec = {'name': 'name%s' % (str(i)), 'contact_no': [i, i+1, i+2, i+3,
                i+4, i+5], 'city' : ['Pune', 'Dehli', 'Mumbai']}
            TestListRemoveRange.client.put(key, rec)
        key = ('test', 'demo', 1)
        TestListRemoveRange.client.list_append(key, "contact_no", [45, 50, 80])

    def teardown_method(self, method):
        """
        Teardown method.
        """
        for i in xrange(5):
            key = ('test', 'demo', i)
            TestListRemoveRange.client.remove(key)

    def test_list_remove_range_with_correct_paramters(self):
        """
        Invoke list_remove_range() removes elements from list with correct parameters
        """
        key = ('test', 'demo', 1)
        
        status = TestListRemoveRange.client.list_remove_range(key, "contact_no", 3, 3)
        assert status == 0L
        
        (key, meta, bins) = TestListRemoveRange.client.get(key)
        assert bins == {'city': ['Pune', 'Dehli', 'Mumbai'], 'contact_no': [1, 2, 3, [45, 50, 80]], 'name' : 'name1'}

    def test_list_remove_range_with_correct_policy(self):
        """
        Invoke list_remove_range() removes elements from list with correct policy
        """
        key = ('test', 'demo', 2)
        policy = {
            'timeout': 1000,
            'retry': aerospike.POLICY_RETRY_ONCE,
            'commit_level': aerospike.POLICY_COMMIT_LEVEL_MASTER
        }

        status = TestListRemoveRange.client.list_remove_range(key, 'contact_no', 0, 3, {}, policy)
        assert status == 0L
        
        (key, meta, bins) = TestListRemoveRange.client.get(key)
        assert bins == {'city': ['Pune', 'Dehli', 'Mumbai'], 'contact_no': [5, 6, 7], 'name' : 'name2'}

    def test_list_remove_range_with_no_parameters(self):
        """
        Invoke list_remove_range() without any mandatory parameters.
        """
        with pytest.raises(TypeError) as typeError:
            TestListRemoveRange.client.list_remove_range()
        assert "Required argument 'key' (pos 1) not found" in typeError.value

    def test_list_remove_range_with_incorrect_policy(self):
        """
        Invoke list_remove_range() with incorrect policy
        """
        key = ('test', 'demo', 1)
        policy = {
            'timeout': 0.5
        }
        try:
            TestListRemoveRange.client.list_remove_range(key, "contact_no", 0, 2, {}, policy)

        except ParamError as exception:
            assert exception.code == -2
            assert exception.msg == "timeout is invalid"

    def test_list_remove_range_with_nonexistent_key(self):
        """
        Invoke list_remove_range() with non-existent key
        """
        charSet = 'abcdefghijklmnopqrstuvwxyz1234567890'
        minLength = 5
        maxLength = 30
        length = random.randint(minLength, maxLength)
        key = ('test', 'demo', ''.join(map(lambda unused :
            random.choice(charSet), range(length)))+".com")
        try:
            TestListRemoveRange.client.list_remove_range(key, "abc", 0, 1)

        except BinIncompatibleType as exception:
            assert exception.code == 12L

    def test_list_remove_range_with_nonexistent_bin(self):
        """
        Invoke list_remove_range() with non-existent bin
        """
        key = ('test', 'demo', 1)
        charSet = 'abcdefghijklmnopqrstuvwxyz1234567890'
        minLength = 5
        maxLength = 10
        length = random.randint(minLength, maxLength)
        bin = ''.join(map(lambda unused :
            random.choice(charSet), range(length)))+".com"
        try:
            TestListRemoveRange.client.list_remove_range(key, bin, 0, 1)

        except BinIncompatibleType as exception:
            assert exception.code == 12L

    def test_list_remove_range_with_extra_parameter(self):
        """
        Invoke list_remove_range() with extra parameter.
        """
        key = ('test', 'demo', 1)
        policy = {'timeout': 1000}
        with pytest.raises(TypeError) as typeError:
            TestListRemoveRange.client.list_remove_range(key, "contact_no", 1, 1, {}, policy, "")

        assert "list_remove_range() takes at most 6 arguments (7 given)" in typeError.value

    def test_list_remove_range_policy_is_string(self):
        """
        Invoke list_remove_range() with policy is string
        """
        key = ('test', 'demo', 1)
        try:
            TestListRemoveRange.client.list_remove_range(key, "contact_no", 0, 1, {}, "")

        except ParamError as exception:
            assert exception.code == -2
            assert exception.msg == "policy must be a dict"

    def test_list_remove_range_key_is_none(self):
        """
        Invoke list_remove_range() with key is none
        """
        try:
            TestListRemoveRange.client.list_remove_range(None, "contact_no", 0, 2)

        except ParamError as exception:
            assert exception.code == -2
            assert exception.msg == "key is invalid"

    def test_list_remove_range_bin_is_none(self):
        """
        Invoke list_remove_range() with bin is none
        """
        key = ('test', 'demo', 1)
        try:
            TestListRemoveRange.client.list_remove_range(key, None, 1, 3)

        except ParamError as exception:
            assert exception.code == -2
            assert exception.msg == "Bin name should be of type string"
    
    def test_list_remove_range_with_negative_index(self):
        """
        Invoke list_remove_range() with negative index
        """
        key = ('test', 'demo', 1)
        try:
            bins = TestListRemoveRange.client.list_remove_range(key, "contact_no", -56, 5)
        except InvalidRequest as exception:
            assert exception.code == 4
    
    def test_list_remove_range_with_negative_length(self):
        """
        Invoke list_remove_range() with negative count
        """
        key = ('test', 'demo', 1)
        try:
            bins = TestListRemoveRange.client.list_remove_range(key, "contact_no", 0, -59)
        except InvalidRequest as exception:
            assert exception.code == 4

    def test_list_remove_range_meta_type_integer(self):
        """
        Invoke list_remove_range() with metadata input is of type integer
        """
        key = ('test', 'demo', 1)
        try:
            TestListRemoveRange.client.list_remove_range(key, "contact_no", 0, 2, 888)

        except ParamError as exception:
            assert exception.code == -2
            assert exception.msg == "Metadata should be of type dictionary"

    def test_list_remove_range_index_type_string(self):
        """
        Invoke list_remove_range() with index is of type string
        """
        key = ('test', 'demo', 1)

        with pytest.raises(TypeError) as typeError:
            TestListRemoveRange.client.list_remove_range(key, "contact_no", "Fifth", 2)
        assert "an integer is required" in typeError.value
