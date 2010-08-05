from unittest2 import Plugin

help_text = "display a progress indicator of tests (verbose only)"
class CountTests(Plugin):

    configSection = 'count'
    commandLineSwitch = (None, 'count', help_text)

    def __init__(self):
        self.totalTests = 0
        self.current = 0
        self.failed = set()
        self.error = set()
        self.passed = set()
        self.skipped = set()
        self.unexpectedSuccess = set()
        self.expectedFailure = set()
        self.other = set()
        self.seen = {}

        self.enhanced = self.config.as_bool('enhanced', False)

    def startTestRun(self, event):
        try:
            self.totalTests = event.suite.countTestCases()
        except AttributeError:
            # workaround a unittest2 test that checks you can pass a function
            # to a TestRunner - which is dumb but should work for backwards
            # compatibility reasons
            self.totalTests = 1
    
    def startTest(self, event):
        self.current += 1
        if not self.enhanced:
            msg = '[%s/%s]  ' % (self.current, self.totalTests)
        else:
            msg = self.getMsg()
        event.message(msg, "verbose")

    def stopTest(self, event):
        test = event.test
        test_id = test.id()
        if test_id in self.seen:
            self.seen[test_id].remove(test_id)
            del self.seen[test_id]
        
        the_set = getattr(self, event.outcome, self.other)
        the_set.add(test_id)
        self.seen[test_id] = the_set

    def getMsg(self):
        values = []
        frag = '%s%s'
        for letter, attr in [('s', 'skipped'), ('f', 'failed'), ('e', 'error'),
                             ('u', 'unexpectedSuccess'), ('o', 'other'),
                             ('x', 'expectedFailure'), ('p', 'passed')]:
            number = len(getattr(self, attr))
            if not number and attr != 'passed':
                continue
            values.append(frag % (number, letter))
        msg = '[%s/%s] ' % ('/'.join(values), self.totalTests)
        return msg
