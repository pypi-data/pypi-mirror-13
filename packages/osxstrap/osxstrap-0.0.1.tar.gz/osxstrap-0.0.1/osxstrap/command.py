# -*- coding: utf-8 -*-

"""osxstrap.command: Runs commands on the local system."""

import sys

import os

import subprocess

import output

class _AttributeString(str):
    """
    Simple string subclass to allow arbitrary attribute access.
    From https://github.com/fabric/fabric/blob/master/fabric/operations.py.
    """
    @property
    def stdout(self):
        return str(self)


def run(command, capture=False, shell=None):
    """
    Run a command on the local system.

    Based on https://github.com/fabric/fabric/blob/master/fabric/operations.py.
    """
    print("running local command: %s" % (command))
    # Tie in to global output controls as best we can; our capture argument
    # takes precedence over the output settings.
    dev_null = None
    if capture:
        out_stream = subprocess.PIPE
        err_stream = subprocess.PIPE
    else:
        dev_null = open(os.devnull, 'w+')
        # Non-captured, hidden streams are discarded.
        out_stream = None
        err_stream = None
    try:
        cmd_arg = [command]
        p = subprocess.Popen(cmd_arg, shell=True, stdout=out_stream,
                             stderr=err_stream, executable=shell)
        (stdout, stderr) = p.communicate()
    finally:
        if dev_null is not None:
            dev_null.close()
    # Handle error condition (deal with stdout being None, too)
    out = _AttributeString(stdout.strip() if stdout else "")
    err = _AttributeString(stderr.strip() if stderr else "")
    out.command = command
    out.real_command = command
    out.failed = False
    out.return_code = p.returncode
    out.stderr = err
    if p.returncode not in [0]:
        out.failed = True
        msg = "local command encountered an error (return code %s) while executing '%s'" % (p.returncode, command)
        output.abort(msg)
    out.succeeded = not out.failed
    # If we were capturing, this will be a string; otherwise it will be None.
    return out