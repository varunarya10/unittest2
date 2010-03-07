from __future__ import with_statement

import os
import sys
import warnings

from StringIO import StringIO

if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

import unittest2
from unittest2.test.support import OldTestResult, catch_warnings


class TestWith(unittest2.TestCase):
    """Tests that use the with statement live in this
    module so that all other tests can be run with Python 2.4.
    """

    def testAssertRaisesExcValue(self):
        class ExceptionMock(Exception):
            pass

        def Stub(foo):
            raise ExceptionMock(foo)
        v = "particular value"

        ctx = self.assertRaises(ExceptionMock)
        with ctx:
            Stub(v)
        e = ctx.exception
        self.assertIsInstance(e, ExceptionMock)
        self.assertEqual(e.args[0], v)

    
    def test_assertRaises(self):
        def _raise(e):
            raise e
        self.assertRaises(KeyError, _raise, KeyError)
        self.assertRaises(KeyError, _raise, KeyError("key"))
        try:
            self.assertRaises(KeyError, lambda: None)
        except self.failureException, e:
            self.assertIn("KeyError not raised", e.args)
        else:
            self.fail("assertRaises() didn't fail")
        try:
            self.assertRaises(KeyError, _raise, ValueError)
        except ValueError:
            pass
        else:
            self.fail("assertRaises() didn't let exception pass through")
        with self.assertRaises(KeyError) as cm:
            try:
                raise KeyError
            except Exception, e:
                raise
        self.assertIs(cm.exception, e)

        with self.assertRaises(KeyError):
            raise KeyError("key")
        try:
            with self.assertRaises(KeyError):
                pass
        except self.failureException, e:
            self.assertIn("KeyError not raised", e.args)
        else:
            self.fail("assertRaises() didn't fail")
        try:
            with self.assertRaises(KeyError):
                raise ValueError
        except ValueError:
            pass
        else:
            self.fail("assertRaises() didn't let exception pass through")

    def test_assert_dict_unicode_error(self):
        with catch_warnings(record=True):
            # This causes a UnicodeWarning due to its craziness
            one = ''.join(chr(i) for i in range(255))
            # this used to cause a UnicodeDecodeError constructing the failure msg
            with self.assertRaises(self.failureException):
                self.assertDictContainsSubset({'foo': one}, {'foo': u'\uFFFD'})

    def test_formatMessage_unicode_error(self):
        with catch_warnings(record=True):
            # This causes a UnicodeWarning due to its craziness
            one = ''.join(chr(i) for i in range(255))
            # this used to cause a UnicodeDecodeError constructing msg
            self._formatMessage(one, u'\uFFFD')
                
    def assertOldResultWarning(self, test, failures):
        with catch_warnings(record=True) as log:
            result = OldTestResult()
            test.run(result)
            self.assertEqual(len(result.failures), failures)
            warning, = log
            self.assertIs(warning.category, DeprecationWarning)

    def test_old_testresult(self):
        class Test(unittest2.TestCase):
            def testSkip(self):
                self.skipTest('foobar')
            @unittest2.expectedFailure
            def testExpectedFail(self):
                raise TypeError
            @unittest2.expectedFailure
            def testUnexpectedSuccess(self):
                pass
        
        for test_name, should_pass in (('testSkip', True), 
                                       ('testExpectedFail', True), 
                                       ('testUnexpectedSuccess', False)):
            test = Test(test_name)
            self.assertOldResultWarning(test, int(not should_pass))
        
    def test_old_testresult_setup(self):
        class Test(unittest2.TestCase):
            def setUp(self):
                self.skipTest('no reason')
            def testFoo(self):
                pass
        self.assertOldResultWarning(Test('testFoo'), 0)
        
    def test_old_testresult_class(self):
        class Test(unittest2.TestCase):
            def testFoo(self):
                pass
        Test = unittest2.skip('no reason')(Test)
        self.assertOldResultWarning(Test('testFoo'), 0)
    

if __name__ == '__main__':
    unittest2.main()
