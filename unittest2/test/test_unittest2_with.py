from __future__ import with_statement

import os
import sys
import warnings

if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

import unittest2


classDict = dict(unittest2.TestResult.__dict__)
for m in 'addSkip', 'addExpectedFailure', 'addUnexpectedSuccess':
    del classDict[m]
OldResult = type('OldResult', (object,), classDict)


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

    def test_old_test_result(self):
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
            with catch_warnings(record=True) as log:
                result = OldResult()
                test = Test(test_name)
                test.run(result)
                self.assertEqual(len(result.failures), int(not should_pass))
                warning, = log
                self.assertIs(warning.category, DeprecationWarning)

# copied from Python 2.6
try:
    from warnings import catch_warnings
except ImportError:
    class catch_warnings(object):
        def __init__(self, record=False, module=None):
            self._record = record
            self._module = sys.modules['warnings'] if module is None else module
            self._entered = False
    
        def __repr__(self):
            args = []
            if self._record:
                args.append("record=True")
            if self._module is not sys.modules['warnings']:
                args.append("module=%r" % self._module)
            name = type(self).__name__
            return "%s(%s)" % (name, ", ".join(args))
    
        def __enter__(self):
            if self._entered:
                raise RuntimeError("Cannot enter %r twice" % self)
            self._entered = True
            self._filters = self._module.filters
            self._module.filters = self._filters[:]
            self._showwarning = self._module.showwarning
            if self._record:
                log = []
                self._module.showwarning = lambda *args, **kw: None
                return log
            else:
                return None
    
        def __exit__(self, *exc_info):
            if not self._entered:
                raise RuntimeError("Cannot exit %r without entering first" % self)
            self._module.filters = self._filters
            self._module.showwarning = self._showwarning

if __name__ == '__main__':
    unittest2.main()
