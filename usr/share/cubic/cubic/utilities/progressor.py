#!/usr/bin/python3

########################################################################
#                                                                      #
# progressor.py                                                        #
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

# https://pexpect.readthedocs.io/en/stable/
# https://stackoverflow.com/questions/41679513/python-pexpect-pxssh-getting-the-exit-status

########################################################################
# Imports
########################################################################

import ctypes
import datetime
import os
import pexpect
import re
import threading
import time
import traceback

from cubic.constants import CYAN, GREEN, RED
from cubic.constants import NORMAL
from cubic.constants import START_PERCENT, FINAL_PERCENT, SCALE_FACTOR
from cubic.utilities import logger
from cubic.utilities import processor

########################################################################
# Global Variables & Constants
########################################################################

# Pattern to match percent in the output. The format is "###.##%".
PERCENT_PATTERN = re.compile(r'[0-9]{1,3}(\.[0-9]{2}){0,1}%')

# Number of steps in the progress at 0%.
START_POSITION = int(START_PERCENT * SCALE_FACTOR)  # steps

# Number of steps in the progress at 100%.
FINAL_POSITION = int(FINAL_PERCENT * SCALE_FACTOR)  # steps

# Exist status 0 indicates the process completed successfully.
OK = 0

is_debug = False

########################################################################
# Classes
########################################################################


class InterruptException(Exception):
    """
    Exception used by the interrupt_navigation_thread() function to
    interrupt a running navigation thread.
    """

    def __str__(self):
        """
        The string representation of this exception used for display
        purposes.

        Returns:
            (str): 'Interrupt Exception'
        """

        return 'Interrupt Exception'


class ProgressTracker(threading.Thread):

    def __init__(self, progress_callback):

        self.progress_callback = progress_callback
        self.unblock_event = threading.Event()
        self.target_position = START_POSITION
        self.time = time.time()
        self.delay = -1

        threading.Thread.__init__(self, daemon=True)

    def block(self, is_block):

        if is_block:
            # Block.
            # Reset the internal flag to false. Subsequently, threads
            # calling wait() will block until set() is called to set the
            # internal flag to true again.
            self.unblock_event.clear()
        else:
            # Unblock.
            # Set the internal flag to true. All threads waiting for it
            # to become true are awakened. Threads that call wait() once
            # the flag is true will not block at all.
            self.unblock_event.set()

    def is_blocked(self):

        return not self.unblock_event.is_set()

    def wait(self):
        """
        Wait until unblocked.
        """

        self.unblock_event.wait()

    def update(self, percent):
        """
        Update the target position and the delay, and unblock the run()
        function if the new target position is greater than the previous
        target position.
        """

        previous_target_position = self.target_position
        target_position = percent * SCALE_FACTOR
        if target_position > previous_target_position:
            if is_debug: print(CYAN + '▹ Progress: {:6.2f} %'.format(percent) + NORMAL)
            previous_time = self.time
            self.time = time.time()
            delta_time = self.time - previous_time
            delta_target_position = target_position - previous_target_position
            self.delay = delta_time / delta_target_position
            self.target_position = target_position
            self.block(False)  # Unblock.

    def run(self):
        """
        Increment the position and notify the client using the supplied
        callback function. Block whenever the (current) position reaches
        the target position.
        """

        logger.log_value('The progress tracker', 'Started')
        logger.log_value('The progress tracker id is', self.ident)
        position = START_POSITION
        try:
            while position < FINAL_POSITION:
                # Block when the current position reaches the target position.
                self.block(position >= self.target_position)
                self.progress_callback(position / SCALE_FACTOR)
                if is_debug: self.print_values(position, self.target_position, self.delay, self.is_blocked())
                self.wait()  # Wait until unblocked.
                position += 1
                time.sleep(self.delay)

            self.progress_callback(position / SCALE_FACTOR)
            if is_debug: self.print_values(position, self.target_position, self.delay, self.is_blocked())

        except InterruptException as exception:
            logger.log_value('Interrupted the progress tracker', exception)
            # logger.log_value('The tracek back is', traceback.format_exc())
            # return exception

        except Exception as exception:
            logger.log_value('Error while running the progress tracker', exception)
            # logger.log_value('The tracek back is', traceback.format_exc())
            # return exception

        logger.log_value('The progress tracker', 'Stopped')

    def stop(self):

        logger.log_value('Stop the progress tracker with id', self.ident)
        ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(self.ident), ctypes.py_object(InterruptException))
        self.block(False)
        # Do not join this thread because it may block the application.
        # self.join()

    def print_values(self, position, target_position, delay, is_blocked):

        # https://docs.python.org/3.8/library/string.html

        print(
            '| Position: {:6.2f} % | '
            'Target: {:6.2f} % | '
            'Delay: {:8.5f} | '
            '{:>9} |'.format(
                position / SCALE_FACTOR,
                target_position / SCALE_FACTOR,
                delay,
                RED + 'Blocked  ' + NORMAL if is_blocked else GREEN + 'Unblocked' + NORMAL))
        if is_blocked: print('=' * 71)


########################################################################
# Process Function
########################################################################

# https://pexpect.readthedocs.io/en/stable/api/pexpect.html#spawn-class
# If you wish to get the exit status of the child you must call the
# close() method. The exit or signal status of the child will be stored
# in self.exitstatus or self.signalstatus. If the child exited normally
# then exit_status will store the exit return code and signal_status will
# be None. If the child was terminated abnormally with a signal then
# signal_status will store the signal value and exit_status will be None.

# When using rsync, note that the percentages can fluctuate, sometimes
# reverting to a lower value than previously reported.


def process_command(command, progress_tracker, working_directory=None):
    """
    Execute the command while updating the progress tracker with percent
    complete information from the running process.
    """

    current_time = datetime.datetime.now()
    formatted_time = '{:%H:%M:%S.%f}'.format(current_time)
    logger.log_value('The process started at', formatted_time)

    try:
        process = processor.execute_asynchronous(command, working_directory)
        done = False
        while not done:
            try:
                process.expect(PERCENT_PATTERN)
            except pexpect.EOF as exception:
                # Close the process to obtain the exit status.
                process.close()
                done = (process.exitstatus is OK)
                if not done: raise exception
            else:
                percent = float((process.after)[:-1])
                progress_tracker.update(percent)

    except Exception as exception:
        current_time = datetime.datetime.now()
        progress_tracker.stop()
        process.close()
        logger.log_value('Error', 'An exception occurred.')
        formatted_time = '{:%H:%M:%S.%f}'.format(current_time)
        logger.log_value('The process stopped at', formatted_time)
        logger.log_value('The exit status, signal status is', '%s, %s' % (process.exitstatus, process.signalstatus))
        logger.log_value('The exception is', exception)
        logger.log_value('The tracek back is', traceback.format_exc())
        message = process.before.strip().replace('\r\n', '\n')
        logger.log_value('The message is', message)
        if is_debug: print_message_and_exception(message, exception)
        return exception, message

    else:
        os.sync()  # Write data to disk.
        # Only wait after an EOF, otherwise the process will block.
        process.wait()
        current_time = datetime.datetime.now()
        if percent < FINAL_PERCENT:
            logger.log_value('Adjust the final percent', 'from {:.2f}% to {:.2f}%'.format(percent, FINAL_PERCENT))
            progress_tracker.update(FINAL_PERCENT)
        progress_tracker.join()
        formatted_time = '{:%H:%M:%S.%f}'.format(current_time)
        logger.log_value('The process finished at', formatted_time)
        logger.log_value('The exit status, signal status is', '%s, %s' % (process.exitstatus, process.signalstatus))
        message = process.before.strip().replace('\r\n', '\n')
        logger.log_value('The message is', message)
        if is_debug: print_message_and_exception(message)
        return None, message


def print_message_and_exception(message, exception='No exception'):

    print()
    print('-' * 80)
    print('MESSAGE:\n')
    print(message)
    print('-' * 80)
    print('EXCEPTION:\n')
    print(exception)
    print('-' * 80)
    print()


########################################################################
# Show Progress Function
########################################################################


def show_progress(command, progress_callback, working_directory=None):

    # Start the thread to track the progress of the process.
    progress_tracker = ProgressTracker(progress_callback)
    progress_tracker.start()

    # Start the process which should be tracked.
    exception, message = process_command(command, progress_tracker, working_directory)

    return exception, message
