"""TestSuite"""

import sys
import unittest
from unittest2 import case, util


class TestSuite(unittest.TestSuite):
    """A test suite is a composite test consisting of a number of TestCases.

    For use, create an instance of TestSuite, then add test case instances.
    When all tests have been added, the suite can be passed to a test
    runner, such as TextTestRunner. It will run the individual test cases
    in the order in which they were added, aggregating the results. When
    subclassing, do not forget to call the base class constructor.
    """
    
    _previousClass = None
    
    def __init__(self, tests=()):
        self._tests = []
        self.addTests(tests)

    def __repr__(self):
        return "<%s tests=%s>" % (util.strclass(self.__class__), list(self))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return list(self) == list(other)

    def __ne__(self, other):
        return not self == other

    # Can't guarantee hash invariant, so flag as unhashable
    __hash__ = None

    def __iter__(self):
        return iter(self._tests)

    def countTestCases(self):
        cases = 0
        for test in self:
            cases += test.countTestCases()
        return cases

    def addTest(self, test):
        # sanity checks
        if not hasattr(test, '__call__'):
            raise TypeError("%r is not callable" % (test,))
        if isinstance(test, type) and issubclass(test,
                                                 (unittest.TestCase, unittest.TestSuite)):
            raise TypeError("TestCases and TestSuites must be instantiated "
                            "before passing them to addTest()")
        self._tests.append(test)

    def addTests(self, tests):
        if isinstance(tests, basestring):
            raise TypeError("tests must be an iterable of tests, not a string")
        for test in tests:
            self.addTest(test)

    def run(self, result):
        for test in self:
            if result.shouldStop:
                break
            
            if isinstance(test, unittest.TestCase):
                previousClass = self._previousClass
                currentClass = test.__class__
                if currentClass != previousClass:
                    if self._previousClass is not None:
                        self._previousClass.tearDownClass()
                    
                    try:
                        currentClass.setUpClass()
                    except:
                        test.__class__._classSetupFailed = True
                        result.addError(test, sys.exc_info())
                    else:
                        test.__class__._classSetupFailed = False
                TestSuite._previousClass = currentClass
                
                if test.__class__._classSetupFailed:
                    continue
            
            test(result)

        if self._previousClass is not None:
            self._previousClass.tearDownClass()
        return result

    def __call__(self, *args, **kwds):
        return self.run(*args, **kwds)

    def debug(self):
        """Run the tests without collecting errors in a TestResult"""
        for test in self:
            test.debug()
