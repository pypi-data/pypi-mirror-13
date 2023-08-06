#!/usr/bin/env python

import sys


output = None


class OutputException(Exception):
    pass


class GenericOutput:
    str_test_suite_open = "### TEST SUITE: {name}"
    str_test_suite_done = "### /TEST SUITE: {name}"
    str_test_open = "## TEST: {name}"
    str_test_fail = "TEST FAILURE:\nTYPE: {type}\nMESSAGE: {message}\nDETAILS:\n{details}\n"
    str_test_stdout = "TEST STDOUT:\n{text}"
    str_test_stderr = "TEST STDERR:\n{text}"
    str_test_done = "## /TEST {name}"
    str_block_open = "**** BLOCK {name}"
    str_block_done = "**** /BLOCK {name}"

    def __init__(self):
        self.open_tests = []
        self.open_test_suits = []
        self.open_blocks = []

    # generic grouping of output

    def block_open(self, s):
        self.dump(self.str_block_open.format(name=s))
        self.open_blocks.append(s)

    def block_done(self):
        self.dump(self.str_block_done.format(name=self.open_blocks.pop()))

    # test suites

    def test_suite_open(self, s):
        self.dump(self.str_test_suite_open.format(name=s))
        self.open_test_suits.append(s)

    def test_suite_done(self):
        self.dump(self.str_test_suite_done.format(name=self.open_test_suits.pop()))

    # test_open, ONE of the middle methods, then test_done

    def test_open(self, s):
        self.dump(self.str_test_open.format(name=s))
        self.open_tests.append(s)

    def test_stdout(self, s):
        self.dump(self.str_test_stdout.format(text=s))

    def test_stderr(self, s):
        self.dump(self.str_test_stderr.format(text=s))

    def test_failed(self, type="GenericFailure", message="No reason available", details="No details available"):
        self.dump(self.str_test_fail.format(name=self.open_tests[-1],
                                            type=type,
                                            message=message,
                                            details=details))

    def test_done(self):
        self.dump(self.str_test_done.format(name=self.open_tests.pop()))

    # generic print

    @staticmethod
    def dump(*args):
        sys.stdout.write(*args)
        sys.stdout.write("\n")


class TeamcityOutput(GenericOutput):
    str_test_suite_open = "##teamcity[testSuiteStarted name='{name}']"
    str_test_suite_done = "##teamcity[testSuiteFinished name='{name}']"
    str_test_open = "##teamcity[testStarted name='{name}']"
    str_test_fail = "##teamcity[testFailed name='{name}' type='{type}' message='{message}' details='{details}']"
    str_test_stdout = "##teamcity[testStdOut name='{name}' out='{text}' ]"
    str_test_stderr = "##teamcity[testStdErr name='{name}' out='{text}' ]"
    str_test_done = "##teamcity[testFinished name='{name}']"
    str_block_open = "##teamcity[blockOpened name='{name}']"
    str_block_done = "##teamcity[blockClosed name='{name}']"


def init_output(otype):
    global output
    if otype == "teamcity":
        output = TeamcityOutput()
    elif otype == "text":
        pass    # is set by default anyway :)
    else:
        raise OutputException("Unknown Output type: %s" % otype)


# this might be bad style, but it's necessary.
output = GenericOutput()


if __name__ == "__main__":
    print("Don't do this :)")
