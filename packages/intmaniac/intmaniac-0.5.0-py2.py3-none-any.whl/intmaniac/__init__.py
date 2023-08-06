#!/usr/bin/env python

import yaml

from intmaniac.testset import Testset
from intmaniac import tools
from intmaniac.output import init_output

import sys
from errno import *
from argparse import ArgumentParser

config = None
logger = None


def fail(errormessage):
    print("FATAL: %s" % errormessage)
    sys.exit(-10)


##############################################################################
#                                                                            #
# default configuration values for test config                               #
#                                                                            #
##############################################################################


def get_test_config_stub():
    return {'config': {}, 'meta': {}, 'environment': {}}


def get_full_config_stub():
    return {'global': get_test_config_stub(), 'testsets': {}, 'output_format': 'text'}


##############################################################################
#                                                                            #
# reading of config data                                                     #
# initialization of test set objects                                         #
#                                                                            #
##############################################################################


def get_test_set_groups(setupdata):
    """Always returns a list of list of Testsets
        :param setupdata the full yaml setup data
    """
    test_set_groups = setupdata['testsets']
    global_config = setupdata['global']
    step = 0
    rv = []
    # if it's not a list, just wrap it into one.
    if type(test_set_groups) == dict:
        test_set_groups = [test_set_groups]
    for tsgroup in test_set_groups:
        tsgroup_list = []
        rv.append(tsgroup_list)
        # this must be dict now
        for tsname in sorted(tsgroup.keys()):
            # makes for predictable order for testing ...
            tests = tsgroup[tsname]
            tsname = "%02d-%s" % (step, tsname) \
                if len(test_set_groups) > 1 \
                else tsname
            tsglobal = tools.deep_merge(
                global_config,
                tests.pop("_global", get_test_config_stub()))
            ts = Testset(global_config=tsglobal, name=tsname)
            tsgroup_list.append(ts)
            for test_name, test_config in tests.items():
                ts.add_from_config(test_name, test_config)
        step += 1
    return rv


def _get_setupdata():
    stub = get_full_config_stub()
    filedata = None
    try:
        with open(config.config_file, "r") as ifile:
            filedata = yaml.safe_load(ifile)
    except IOError as e:
        # FileNotFoundError is python3 only. yihah.
        if e.errno == ENOENT:
            fail("Could not find configuration file: %s" % config.config_file)
        else:
            fail("Unspecified IO error: %s" % str(e))
    logger.info("Read configuration file %s" % config.config_file)
    return tools.deep_merge(stub, filedata)


def _prepare_global_config(setupdata):
    global_config = setupdata['global']
    # add config file location
    global_config['meta']['_configfile'] = config.config_file
    # add env settings from command line
    if config.env:
        for tmp in config.env:
            try:
                k, v = tmp.split("=", 1)
                global_config['environment'][k] = v
            except ValueError:
                fail("Invalid environment setting: %s" % tmp)
    return global_config


def get_and_init_configuration():
    setupdata = _get_setupdata()
    _prepare_global_config(setupdata)
    init_output(setupdata['output_format'])
    return setupdata


##############################################################################
#                                                                            #
# run test sets logic                                                        #
#                                                                            #
##############################################################################


def run_test_set_groups(tsgs):
    retval = True
    dumps = []
    for testsetgroup in tsgs:
        if not retval:
            # just for nicer output
            for tso in testsetgroup:
                logger.warning("skipping %s because of failed dependency" % tso)
            continue
        # everything in here is run in parallel
        for testsetobj in testsetgroup:
            testsetobj.start()
        for testsetobj in testsetgroup:
            testsetobj.join()
            retval = testsetobj.succeeded() and retval
            dumps.append(testsetobj.dump)
            if not testsetobj.succeeded():
                logger.critical("%s failed, skipping following testsets"
                             % testsetobj)
    print("TEST PROTOCOL")
    for dump_function in dumps:
        dump_function()
    return retval


##############################################################################
#                                                                            #
# startup initialization                                                     #
#                                                                            #
##############################################################################


def prepare_environment(arguments):
    global config, logger
    parser = ArgumentParser()
    parser.add_argument("-c", "--config-file",
                        help="specify configuration file",
                        default="./intmaniac.yaml")
    parser.add_argument("-e", "--env",
                        help="dynamically add a value to the environment",
                        action="append")
    parser.add_argument("-v", "--verbose",
                        help="increase verbosity level, use multiple times",
                        default=0,
                        action="count")
    config = parser.parse_args(arguments)
    tools.init_logging(config)
    logger = tools.get_logger(__name__)


def console_entrypoint():
    prepare_environment(sys.argv[1:])
    configuration = get_and_init_configuration()
    result = run_test_set_groups(get_test_set_groups(configuration))
    if not result:
        sys.exit(1)


if __name__ == "__main__":
    console_entrypoint()
