#!/usr/bin/python3

########################################################################
#                                                                      #
# process_utilities.py                                                 #
#                                                                      #
# Copyright (C) 2020 PJ Singh <psingh.cubic@gmail.com>                 #
#                                                                      #
########################################################################

########################################################################
#                                                                      #
# This file is part of Cubic - Custom Ubuntu ISO Creator.              #
#                                                                      #
# Cubic is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by #
# the Free Software Foundation, either version 3 of the License, or    #
# (at your option) any later version.                                  #
#                                                                      #
# Cubic is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of       #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the         #
# GNU General Public License for more details.                         #
#                                                                      #
# You should have received a copy of the GNU General Public License    #
# along with Cubic. If not, see <http://www.gnu.org/licenses/>.        #
#                                                                      #
########################################################################

from utilities import logger
from utilities import model

import os
from pexpect import spawn, ExceptionPexpect
from re import sub
from signal import SIGTERM
import sys
import traceback
from time import sleep

########################################################################
# Globals & Constants
########################################################################

process = None

########################################################################
# Process Functions
########################################################################

# https://pexpect.readthedocs.org/en/stable/api/pexpect.html#spawn-class
# Because spwan() is a byte interface, use process.read().decode().
# Because spwanu() is a string interface, process.read().decode() is not
# necessary.

# If the child exited normally then exitstatus will store the exit
# return code and signalstatus will be None.
# If the child was terminated abnormally with a signal then signalstatus
# will store the signal value and exitstatus will be None.
#
# Process              exitstatus     signalstatus
# -----------------    -----------    ------------
# Running              None           None
# Exited Normally      Return Code    None
# Exited Abnormally    None           Signal Code

# Bash Process         exitstatus     signalstatus
# -----------------    -----------    ------------
# Running              None           None
# Exited Normally      0              None
# Exited Abnormally    1 | Error #    None

# TODO: Double check all invocations that use a command, because we
#       should check for exit status > 0 to determine error.


def execute_synchronous(command, working_directory=None):

    display_command = sub(r'pkexec\s*\S*commands\S{0,1}([\w-]*)"*(.*)', r'\1\2', command)
    # logger.log_label('Execute synchronously')
    # logger.log_value('Command', command)
    logger.log_value('Execute synchronously', display_command)

    result = None
    exitstatus = None
    signalstatus = None
    global process
    if process and process.isalive():
        logger.log_value('Warning, the process is running', process.pid)
        logger.log_value('The exit status of process %s is' % process.pid, process.exitstatus)
        logger.log_value('The signal status of process %s is' % process.pid, process.signalstatus)
    process = None
    try:
        # Using pexpect.split_command_line removes the spaces in the
        # command. This results in the error:
        # pexpect.exceptions.ExceptionPexpect: The command was not found
        # or was not executable.
        # command = split_command_line(command)
        # For Pexpect Pexpect 3.x
        # process = spawnu(command, timeout=300, cwd=working_directory)
        # For Pexpect 4.0
        process = spawn(command, timeout=300, cwd=working_directory, encoding='UTF-8')
        logger.log_value('The process id is', process.pid)
        result = process.read()
        result = result.strip() if result else None
        exitstatus = process.exitstatus
        signalstatus = process.signalstatus
    except ExceptionPexpect as exception:
        logger.log_value('Exception while executing', command)
        logger.log_value('The exception is', exception)
        logger.log_value('The tracekback is', traceback.format_exc())

    # Calling flush() seems to prevent the process from becoming a zombie.
    sys.stdout.flush()
    process = None

    return result, exitstatus, signalstatus


def execute_synchronous_unregistered(command, working_directory=None):

    display_command = sub(r'pkexec\s*\S*commands\S{0,1}([\w-]*)"*(.*)', r'\1\2', command)
    # logger.log_label('Execute synchronously unregistered')
    # logger.log_value('Command', command))
    logger.log_value('Execute synchronously unregistered', display_command)

    process_pid = None
    result = None
    exitstatus = None
    signalstatus = None
    try:
        # Using pexpect.split_command_line removes the spaces in the
        # command. This results in the error:
        # pexpect.exceptions.ExceptionPexpect: The command was not found
        # or was not executable.
        # command = split_command_line(command)
        # For Pexpect Pexpect 3.x
        # process = spawnu(command, timeout=300, cwd=working_directory)
        # For Pexpect 4.0
        process = spawn(command, timeout=300, cwd=working_directory, encoding='UTF-8')
        process_pid = process.pid
        logger.log_value('The unregistered process id is', process.pid)
        result = process.read()
        result = result.strip() if result else None
        exitstatus = process.exitstatus
        signalstatus = process.signalstatus
    except ExceptionPexpect as exception:
        logger.log_value('Exception while executing', command)
        logger.log_value('The exception is', exception)
        logger.log_value('The tracekback is', traceback.format_exc())

    # Calling flush() seems to prevent the process from becoming a zombie.
    sys.stdout.flush()
    process = None

    return process_pid, result, exitstatus, signalstatus


def execute_asynchronous(command, working_directory=None):

    display_command = sub(r'pkexec\s*\S*commands\S{0,1}([\w-]*)"*(.*)', r'\1\2', command)
    # logger.log_label('Execute asynchronously')
    # logger.log_value('Command', command)
    logger.log_value('Execute asynchronously', display_command)

    global process
    if process and process.isalive():
        logger.log_value('Warning, the process is running', process.pid)
        logger.log_value('The exit status of process %s is' % process.pid, process.exitstatus)
        logger.log_value('The signal status of process %s is' % process.pid, process.signalstatus)
    process = None
    try:
        # Using pexpect.split_command_line removes the spaces in the
        # command. This results in the error:
        # pexpect.exceptions.ExceptionPexpect: The command was not found
        # or was not executable.
        # command = split_command_line(command)
        # For Pexpect Pexpect 3.x
        # process = spawnu(command, timeout=300, cwd=working_directory)
        # For Pexpect 4.0
        process = spawn(command, timeout=300, cwd=working_directory, encoding='UTF-8')
        logger.log_value('The process id is', process.pid)
    except ExceptionPexpect as exception:
        logger.log_value('Exception while executing', command)
        logger.log_value('The exception is', exception)
        logger.log_value('The tracekback is', traceback.format_exc())

    # Calling flush() seems to prevent the process from becoming a zombie.
    sys.stdout.flush()

    return process


########################################################################
# Terminate Process Functions
########################################################################


def terminate_process():

    _terminate_root_process()


def _terminate_user_process():

    global process

    logger.log_value('Terminate process', process.pid)

    try:
        process.kill(SIGTERM)
    except PermissionError as exception:
        logger.log_value('The exception is', exception)
        logger.log_value('The tracekback is', traceback.format_exc())
    except Exception as exception:
        logger.log_value('The exception is', exception)
        logger.log_value('The tracekback is', traceback.format_exc())
    # This returns the exit status and signal status of the running
    # process that was killed.
    logger.log_value('The exit status of process %s is' % process.pid, process.exitstatus)
    logger.log_value('The signal status of process %s is' % process.pid, process.signalstatus)

    # Calling flush() seems to prevent the process from becoming a zombie.
    sys.stdout.flush()
    process = None


def _terminate_root_process():

    exitstatus = None
    signalstatus = None
    global process
    if process and process.isalive():
        logger.log_value('Terminate process', process.pid)
        program = os.path.join(model.application.directory, 'commands', 'terminate-process')
        command = 'pkexec "%s" "%s"' % (program, process.pid)
        terminate_process_pid, result, exitstatus, signalstatus = execute_synchronous_unregistered(command, model.application.directory)
        # sleep(0.50)
        # This returns the exit status and signal status of the process
        # that killed the running process.
        # logger.log_value('The result is', result)
        logger.log_value('The exit status of terminate process %s is' % terminate_process_pid, exitstatus)
        logger.log_value('The signal status of terminate process %s is' % terminate_process_pid, signalstatus)
        logger.log_value('The exit status of process %s is' % process.pid, process.exitstatus)
        logger.log_value('The signal status of process %s is' % process.pid, process.signalstatus)

    # Calling flush() seems to prevent the process from becoming a zombie.
    sys.stdout.flush()
    process = None
