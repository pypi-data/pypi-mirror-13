#!/usr/bin/env python

from intmaniac.testrun import Testrun
from intmaniac.tools import deep_merge
from intmaniac.output import output

from threading import Thread


class Testset(Thread):

    def __init__(self, global_config={}, *args, **kwargs):
        super(Testset, self).__init__(*args, **kwargs)
        self.tests = []
        self.name = kwargs['name'] if kwargs.get('name') else "default"
        self.global_config = global_config
        self.failed_tests = []
        self.succeeded_tests = []
        self.success = True

    def set_global_config(self, global_config):
        self.global_config = global_config

    def add_from_config(self, name, config, global_config=None):
        global_config = global_config if global_config else self.global_config
        self.tests.append(Testrun(deep_merge(global_config, config),
                                  name="%s-%s" % (self.name, name)))

    def succeeded(self):
        return self.success

    def run(self):
        for test in self.tests:
            test.start()
        for test in self.tests:
            test.join()
            if test.succeeded():
                self.succeeded_tests.append(test)
            else:
                self.failed_tests.append(test)
                self.success = False
        return self.success

    def dump(self):
        output.test_suite_open(self.name)
        for test in self.tests:
            test.dump()
        output.test_suite_done()

if __name__ == "__main__":
    print("Don't do this :)")
