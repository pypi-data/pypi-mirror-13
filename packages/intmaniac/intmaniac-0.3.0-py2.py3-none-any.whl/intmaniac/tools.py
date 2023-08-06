#!/usr/bin/env python

import subprocess as sp
from sys import version_info as vinf

python_version = 10 * vinf[0] + vinf[1]


class DummyCompletedProcess:
    """Poor man's Pyton 2.7 CompletedProcess replacement"""

    def __init__(self, returncode, cmd, output=None):
        # mimic constructor and behavior of CalledProcessError
        self.cmd = cmd
        self.returncode = returncode
        self.output = output

    def __str__(self):
        return "<DummyCompletedProcess: %s (%d)" % \
               (" ".join(self.cmd), self.returncode)


def deep_merge(d0, d1):
    d = {}
    for k, v in d1.items():
        if type(v) == dict and k in d0 and type(d0[k]) == dict:
                d[k] = deep_merge(d0[k], v)
        else:
            d[k] = v
    for k, v in d0.items():
        if k not in d1:
            d[k] = v
    return d


def run_command(command):
    """takes an array as "command", which is executed. Mimics python 3
    behavior, in the way that it returns a CalledProcessError on execution
    failure. The object WILL HAVE the python 3 .stdout and .stderr
    properties, always.
    :param command an array to execute as one command
    """
    try:
        if python_version >= 35:
            # python 3.5 implementation, which rules
            rv = sp.run(
                command,
                check=True,
                stdout=sp.PIPE, stderr=sp.STDOUT,
                universal_newlines=True,
            )
            rv.cmd = rv.args
        else:
            # the others, which kinda suck.
            p = sp.Popen(command, stdout=sp.PIPE, stderr=sp.STDOUT)
            stdout, _ = p.communicate()
            # mimic check=True behavior from python3
            cls = DummyCompletedProcess \
                if p.returncode == 0 \
                else sp.CalledProcessError
            rv = cls(p.returncode, command, stdout)
            # deviate from python standard. make all have .args
            # and make all have .stdout and .stderr like python 3.5
            rv.args = rv.cmd
            rv.stdout = rv.output
            rv.stderr = None
            if type(rv) == sp.CalledProcessError:
                raise rv
    except OSError as err:
        # python 2 & 3, make this behave consistently
        # has .returncode, command and output properties and constructor
        # parameters, but we also need stdout
        rv = sp.CalledProcessError(-7, command, "Exception: " + str(err))
        rv.args = rv.cmd
        rv.stdout = rv.output
        rv.stderr = None
        raise rv
    return rv


if __name__ == "__main__":
    print("Don't do this :)")