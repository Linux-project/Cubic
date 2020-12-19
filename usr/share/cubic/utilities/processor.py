#!/usr/bin/python3

########################################################################
#                                                                      #
# processor.py                                                         #
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

########################################################################
# References
########################################################################

# N/A

########################################################################
# Imports
########################################################################

import os
import pexpect
import re
import signal
import traceback

from utilities import logger
from utilities import model

########################################################################
# Global Variables & Constants
########################################################################

process = None

########################################################################
# Process Functions
########################################################################

# https://pexpect.readthedocs.org/en/stable/api/pexpect.html#spawn-class
# Because spwan() is a byte interface, use process.read().decode().
# Because spwanu() is a string interface, process.read().decode() is not
# necessary.

# If the child exited normally then exit_status will store the exit
# return code and signal_status will be None.
# If the child was terminated abnormally with a signal then signal_status
# will store the signal value and exit_status will be None.
#
# Process              exit_status     signal_status
# -----------------    -----------    ------------
# Running              None           None
# Exited Normally      Return Code    None
# Exited Abnormally    None           Signal Code

# Bash Process         exit_status     signal_status
# -----------------    -----------    ------------
# Running              None           None
# Exited Normally      0              None
# Exited Abnormally    1 | Error #    None


# TODO: Double check all invocations that use a command, because we
#       should check for exit status > 0 to determine error.
def execute_synchronous(command, working_directory=None):
    """
    Execute the specified command synchronously and register the
    corresponding process so it can be terminated using the
    terminate_process() function.
    """

    display_command = re.sub(r'pkexec\s*\S*commands\S{0,1}([\w-]*)"*(.*)', r'\1\2', command)
    # logger.log_label('Execute synchronously')
    # logger.log_value('Command', command)
    logger.log_value('Execute synchronously', display_command)

    result = None
    exit_status = None
    signal_status = None
    global process
    if process and process.isalive():
        logger.log_value('Warning, the process is running', process.pid)
        logger.log_value('The exit status of process %s is' % process.pid, process.exitstatus)
        logger.log_value('The signal status of process %s is' % process.pid, process.signalstatus)
    process = None
    try:
        # Using pexpect.split_command_line removes the spaces in the
        # command. This results in the error:
        # pexpect.ExceptionPexpect: The command was not found
        # or was not executable.
        # command = split_command_line(command)
        process = pexpect.spawn(command, timeout=300, cwd=working_directory, encoding='UTF-8')
        logger.log_value('The process id is', process.pid)
        result = process.read()
        result = result.strip() if result else None
        # Close the process to obtain the exit status.
        process.close()
        exit_status = process.exitstatus
        signal_status = process.signalstatus
    except pexpect.ExceptionPexpect as exception:
        # Close the process to obtain the exit status.
        if process: process.close()
        logger.log_value('Exception while executing', command)
        logger.log_value('The exception is', exception)
        logger.log_value('The tracek back is', traceback.format_exc())

    os.sync()  # Write data to disk.
    process = None

    return result, exit_status, signal_status


def execute_synchronous_unregistered(command, working_directory=None):
    """
    Execute the specified command snchronously. The process is not
    registered with this module, so it can not be terminated using the
    terminate_process() function.
    """
    display_command = re.sub(r'pkexec\s*\S*commands\S{0,1}([\w-]*)"*(.*)', r'\1\2', command)
    # logger.log_label('Execute synchronously unregistered')
    # logger.log_value('Command', command))
    logger.log_value('Execute synchronously unregistered', display_command)

    process_pid = None
    result = None
    exit_status = None
    signal_status = None
    try:
        # Using pexpect.split_command_line removes the spaces in the
        # command. This results in the error:
        # pexpect.ExceptionPexpect: The command was not found
        # or was not executable.
        # command = split_command_line(command)
        process = pexpect.spawn(command, timeout=300, cwd=working_directory, encoding='UTF-8')
        process_pid = process.pid
        logger.log_value('The unregistered process id is', process.pid)
        result = process.read()
        result = result.strip() if result else None
        # Close the process to obtain the exit status.
        process.close()
        exit_status = process.exitstatus
        signal_status = process.signalstatus
    except pexpect.ExceptionPexpect as exception:
        logger.log_value('Exception while executing', command)
        logger.log_value('The exception is', exception)
        logger.log_value('The tracek back is', traceback.format_exc())

    os.sync()  # Write data to disk.
    process = None

    return process_pid, result, exit_status, signal_status


def execute_asynchronous(command, working_directory=None):
    """
    Execute the specified command asynchronously and register the
    corresponding process so it can be terminated. The calling
    application must read the output stream until the end of file (EOF)
    is reached, using expect(), expect_exact(), expect_list(), read(),
    readline(), or read_nonblocking(). The application must explicitly
    close the connection with the process to obtain the exit status:
        process.close()
        exit_status = process.exitstatus
        signal_status = process.signalstatus
    """

    display_command = re.sub(r'pkexec\s*\S*commands\S{0,1}([\w-]*)"*(.*)', r'\1\2', command)
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
        # pexpect.ExceptionPexpect: The command was not found
        # or was not executable.
        # command = split_command_line(command)
        process = pexpect.spawn(command, timeout=300, cwd=working_directory, encoding='UTF-8')
        logger.log_value('The process id is', process.pid)
    except pexpect.ExceptionPexpect as exception:
        logger.log_value('Exception while executing', command)
        logger.log_value('The exception is', exception)
        logger.log_value('The tracek back is', traceback.format_exc())

    return process


########################################################################
# Process Functions
########################################################################


def terminate_process():
    """
    Terminate the process registered with this module.
    """

    _terminate_root_process()


def _terminate_user_process():

    # Store a reference to the global process, in case the execute_synchronous()
    # function completes and sets the current process to None before it is
    # terminated.
    global process
    current_process = process
    if current_process and current_process.isalive():
        logger.log_value('Terminate process', current_process.pid)
        try:
            current_process.kill(signal.SIGTERM)
            # Get the exit status and signal status of the process that was killed.
            logger.log_value('The exit status of process %s is' % current_process.pid, current_process.exitstatus)
            logger.log_value('The signal status of process %s is' % current_process.pid, current_process.signalstatus)
            # Set the global process to None.
            process = None
        except PermissionError as exception:
            logger.log_value('The exception is', exception)
            logger.log_value('The tracek back is', traceback.format_exc())
        except Exception as exception:
            logger.log_value('The exception is', exception)
            logger.log_value('The tracek back is', traceback.format_exc())


def _terminate_root_process():

    # Store a reference to the global process, in case the execute_synchronous()
    # function completes and sets the current process to None before it is
    # terminated.
    global process
    current_process = process
    if current_process and current_process.isalive():
        logger.log_value('Terminate process', current_process.pid)
        try:
            program = os.path.join(model.application.directory, 'commands', 'stop-process')
            command = 'pkexec "%s" "%s"' % (program, current_process.pid)
            # Get the exit status and signal status of the terminator process.
            terminator_pid, result, exit_status, signal_status = execute_synchronous_unregistered(command, model.application.directory)
            # Set the global process to None.
            process = None
            # logger.log_value('The result is', result)
            logger.log_value('The exit status of terminator process %s is' % terminator_pid, exit_status)
            logger.log_value('The signal status of terminator process %s is' % terminator_pid, signal_status)
            # Get the exit status and signal status of the process that was killed.
            logger.log_value('The exit status of process %s is' % current_process.pid, current_process.exitstatus)
            logger.log_value('The signal status of process %s is' % current_process.pid, current_process.signalstatus)
        except Exception as exception:
            logger.log_value('The exception is', exception)
            logger.log_value('The tracek back is', traceback.format_exc())
