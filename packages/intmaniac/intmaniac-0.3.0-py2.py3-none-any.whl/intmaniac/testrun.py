#!/usr/bin/env python

from intmaniac.tools import deep_merge, run_command
from intmaniac.output import output

import copy
import threading
import shutil
import logging as log
import subprocess as sp
import os
from os.path import basename, join, isabs, realpath, dirname
from re import sub as resub


default_commandline_start = ["docker-compose", "run"]
default_commandline_end = []

default_config = {
    'environment': {},
    'meta': {
        # no default values, must be set in config:
        'test_container': None,
        # default values, always used
        'docker_compose_template': 'docker-compose.yml.tmpl',
        'test_shell': '/bin/bash',
        'run_timeout': 0,
        'test_service': 'test-service',
        # optional values
        'docker_compose_params': [],
        'test_commands': None,
        'test_report_files': None,
    },
}


class Testrun(threading.Thread):
    """Actually invokes docker-compose with the information given in the
    configuration, and evaluates the results.
    """

    def __init__(self, test_definition, *args, **kwargs):
        super(Testrun, self).__init__(*args, **kwargs)
        self.log = log.getLogger("t-%s" % self.name)
        self.log.debug("Instantiated")
        test_definition = deep_merge(default_config, test_definition)
        # quick shortcuts
        self.test_env = test_definition['environment']
        self.test_meta = test_definition['meta']
        # okay.
        # let's keep all file references relative to the configuration
        # file. easy to remember.
        configfilepath = realpath(dirname(self.test_meta.get('_configfile',
                                                             './dummy')))
        # self.TEMPLATE / .TEMPLATE_NAME
        tmp = self.test_meta['docker_compose_template']
        if not isabs(tmp):
            tmp = realpath(join(configfilepath, tmp))
        self.template = tmp
        self.template_name = basename(self.template)
        # self.BASEDIR
        tmp = self.test_meta.get('test_basedir', configfilepath)
        if not isabs(tmp):
            tmp = realpath(join(configfilepath, tmp))
        self.base_dir = tmp
        # self.SANITIZED_NAME, .TEST_DIR
        self.sanitized_name = resub("[^a-zA-Z0-9_]", "-", self.name)
        self.test_dir = join(self.base_dir, self.sanitized_name)
        # extend SELF.TEST_ENV with TEST_DIR
        self.test_env['test_dir'] = self.test_dir
        #### create SELF.COMMANDLINE
        self.commandline = copy.copy(default_commandline_start)
        for param in self.test_meta['docker_compose_params']:
            self.commandline.append(param)
        for key, val in self.test_env.items():
            self.commandline.append("-e")
            self.commandline.append("%s=%s" % (key, val))
        self.commandline.append("--rm")
        self.commandline.extend(copy.copy(default_commandline_end))
        self.commandline.append(self.test_meta['test_service'])
        # sanitize SELF.TEST_META['test_commands']
        if type(self.test_meta['test_commands']) == str:
            self.test_meta['test_commands'] = [self.test_meta['test_commands']]
        # create SELF.SUCCESS, .RESULT, .EXCEPTION, .REASON
        self.success = True
        self.results = []
        self.exception = None
        self.reason = None
        # some debug output
        self.log.info("base commandline '%s'" % " ".join(self.commandline))
        self.log.debug("test directory '%s'" % self.test_dir)
        self.log.debug("template path '%s'" % self.template)
        for key, val in self.test_env.items():
            self.log.debug("env %s=%s" % (key, val))

    def __str__(self):
        return "<runner.Test '%s'>" % self.name

    def __repr__(self):
        return self.__str__()

    def init_environment(self):
        self.log.debug("creating test directory %s" % self.test_dir)
        shutil.rmtree(self.test_dir, ignore_errors=True)
        os.makedirs(self.test_dir)
        os.chdir(self.test_dir)
        # TODO - catch & error handling if template cannot be found.
        with open(self.template, "r") as ifile:
            tpl = ifile.read()
        for key, val in self.test_env.items():
            tpl = tpl.replace("%%%%%s%%%%" % key.upper(), val)
        # TODO (maybe) - catch and error handling if new tmpl cannot be written
        with open(os.path.join(self.test_dir,
                               "docker-compose.yml"), "w") as ofile:
            ofile.write(tpl)

    def run_test_command(self, command=None, use_base_command=True):
        """:param command the command to execute as array"""
        if not command:
            command = self.commandline
        else:
            command = self.commandline + command
        rv = run_command(command)
        self.results.append(rv)

    def cleanup(self):
        cleanup = True
        for cmd in ("docker-compose kill", "docker-compose rm"):
            try:
                self.log.debug("cleanup command: %s" % cmd)
                rv = run_command(cmd.split(" "))
            except sp.CalledProcessError as e:
                rv = e
                cleanup = False
            if not rv.returncode == 0:
                self.log.warning("cleanup command '%s' failed. code %d, output: %s"
                                 % (" ".join(rv.args),
                                    rv.returncode,
                                    str(rv.stdout)))
        if not cleanup:
            self.log.error("cleanup failed")

    def run(self):
        try:
            self.init_environment()
            if len(self.test_meta['test_commands']) > 0:
                for cmd in self.test_meta['test_commands']:
                    cmd = cmd.split(" ") if type(cmd) == str else cmd
                    self.log.info("command '%s'" % " ".join(cmd))
                    self.run_test_command(cmd)
            else:
                self.run_test_command()
        except IOError as e:
            self.exception = e
            self.success = False
            self.reason = "Exception"
            # for now we re-raise to get the stacktrace on the console.
            raise e
        except sp.CalledProcessError as e:
            # we don't re-raise here, that's just the exit from the command
            # loop above
            self.log.info("command FAILED.")
            self.log.debug("command output: %s" % e.stdout.strip())
            self.results.append(e)
            self.success = False
            self.reason = "Failed command"
        finally:
            self.cleanup()
        self.log.warning("test successful" if self.success else "test FAILED")
        return self.success

    def succeeded(self):
        return self.success

    def dump(self):
        output.test_open(self.name)
        if not self.success:
            output.test_failed(type=self.reason,
                               message=str(self.exception)
                               if self.exception
                               else "Test output following",
                               details="No details available")
        output.test_stdout("\n".join([r.stdout for r in self.results]))
        output.test_done()

if __name__ == "__main__":
    print("Don't do this :)")
