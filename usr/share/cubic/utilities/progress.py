#!/usr/bin/python3

########################################################################
#                                                                      #
# progress_2.py                                                        #
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

from constants import ZOOM, PERCENT_START, PERCENT_STOP, PROGRESS_START, PROGRESS_STOP, SLOW_INTERVAL, FAST_INTERVAL

from utilities.processor import execute_asynchronous
from utilities import logger

from datetime import datetime
from pexpect import TIMEOUT, EOF
import re
from threading import Event, Lock, Thread
from time import sleep, time
import traceback

########################################################################
# Globals & Constants
########################################################################

debug = False

########################################################################
# Classes
########################################################################


class ProcessingError(Exception):

    def __init__(self, message, exitstatus, signalstatus):

        super().__init__(message)

        self.exitstatus = exitstatus
        self.signalstatus = signalstatus


class ProgressEvent(Event):

    def __init__(self):

        super().__init__()

        self.actual_progress = PROGRESS_START
        self.actual_time = time()
        self.actual_period = 0
        self.target_progress = PROGRESS_START
        self.target_period = SLOW_INTERVAL
        self.target_limit = PROGRESS_STOP
        self.process_error = None

    def notify_block(self):

        # Note: clear() causes threads to block.
        self.clear()

    def notify_unblock(self):
        # Note: set() causes threads to unblock.
        self.set()

    def update(self, actual_percent, *, process_error=None):

        actual_progress = actual_percent * ZOOM

        # Wait to update the process error while it is being read, or
        # block other threads from reading the process error while it is
        # being updated.
        with Lock():
            self.process_error = process_error

        current_time = time()

        if actual_progress > self.actual_progress:

            # Compute the actual progress period.
            actual_delta = actual_progress - self.actual_progress
            time_delta = current_time - self.actual_time
            self.actual_period = time_delta / actual_delta

            # Compute the target progress period.
            actual_remaining = PROGRESS_STOP - actual_progress
            target_remaining = PROGRESS_STOP - self.target_progress
            time_remaining = self.actual_period * actual_remaining
            if target_remaining:
                computed_period = time_remaining / target_remaining
                self.target_period = max(computed_period, FAST_INTERVAL)
            else:
                self.target_period = FAST_INTERVAL

        elif actual_progress == PROGRESS_START:
            self.target_period = SLOW_INTERVAL
        elif actual_progress == PROGRESS_STOP:
            self.target_period = FAST_INTERVAL
        else:
            # Use the previously computed progress target period.
            # This part of the if-else block is typically only reached
            # when the process terminates due to an exception, or when
            # update() is invoked using the same process progress.
            pass

        # Compute the progress target limit. The progress target limit
        # should be within 10% of the remaining actual progress.
        self.target_limit = actual_progress + int((PROGRESS_STOP - actual_progress) / 10.0)

        # Save the new values.
        self.actual_progress = actual_progress
        self.actual_time = current_time

        # Notify clients to unblock, if already blocked.
        self.notify_unblock()

        block = not self.is_set()
        self.print_values(
            self.actual_progress,
            self.target_progress,
            self.target_limit,
            self.actual_period,
            self.target_period,
            not block and not process_error,
            block and not process_error,
            self.process_error,
            flag='*')

    def pause(self, target_progress):

        self.target_progress = target_progress

        # Wait to read the process error while it is being updated, or
        # block other threads from updating the process error while it
        # is being read.
        with Lock():
            process_error = self.process_error

        block = (self.target_progress >= self.target_limit and self.target_progress > PROGRESS_START and self.target_progress < PROGRESS_STOP)

        self.print_values(
            self.actual_progress,
            self.target_progress,
            self.target_limit,
            self.actual_period,
            self.target_period,
            not block and not process_error,
            block and not process_error,
            process_error)

        # Do not sleep or block when there is an error.
        #
        # The "Lock()" synchronization above ensures that race
        # conditions in accessing self.process_error do not lead to:
        # 1. The following wait() function being invoked, even though an
        #    error was encountered. (In this case, the server would
        #    simply exit due to the error, but the client would block
        #    indefinitely).
        # 2. The following sleep() function being invoked, even though
        #    an error was encountered. (Instead, the client should
        #    not sleep and should immediately notify the user when an
        #    error occurs).
        if not process_error:
            if block:
                self.notify_block()
                self.wait()
            else:
                sleep(self.target_period)

    def print_values(self, actual_progress, target_progress, target_limit, actual_period, target_period, sleep, block, process_error, flag=''):

        global debug
        if not debug:
            return

        if flag:
            print()

        # https://docs.python.org/2/library/string.html
        print(
            '{:1s} | '
            'Actual: {:5.1f} % | '
            'Target: {:5.1f} % | '
            'Limit: {:5.1f} % | '
            'Process τ: {:10.8f} | '
            'Target τ: {:10.8f} | '
            '{:>8.8s} | '
            '{:>7.7s} | '
            '{:>10.10s} |'.format(
                flag,
                actual_progress / ZOOM,
                target_progress / ZOOM,
                target_limit / ZOOM,
                actual_period,
                target_period,
                'sleep' if sleep else 'no sleep',
                'block' if block else 'unblock',
                str(process_error) if process_error else 'no error'))


########################################################################
# Display Progress and Terminate Process Functions
########################################################################


def show_progress(command, progress_callback, working_directory=None):

    event = ProgressEvent()

    actual_progress_thread = Thread(target=track_actual_progress, args=(event, command, working_directory))
    actual_progress_thread.start()

    # This will block.
    track_target_progress(event, progress_callback)

    return event.process_error


def show_progress_ORIGINAL(command, progress_callback, percent_start=0, percent_stop=100, working_directory=None):

    event = ProgressEvent()

    target_progress_thread = Thread(target=track_target_progress, args=(event, progress_callback, percent_start, percent_stop))
    target_progress_thread.start()

    actual_progress_thread = Thread(target=track_actual_progress, args=(event, command, working_directory))
    actual_progress_thread.start()

    target_progress_thread.join()
    actual_progress_thread.join()

    return event.process_error


########################################################################
# Target Function
########################################################################


def track_target_progress(event, progress_callback):

    # print('{:.<35s} {:}'.format('Target progress thread', 'Started'))
    logger.log_value('Target progress thread', 'Started')

    # this_thread = current_thread()
    # thread_id = this_thread.ident
    # logger.log_value('The target progress thread id is', thread_id)

    progress_callback(PERCENT_START)

    target_progress = PROGRESS_START
    event.pause(target_progress)
    while target_progress < PROGRESS_STOP and not event.process_error:

        target_progress += 1
        progress_callback(target_progress / ZOOM)

        event.pause(target_progress)

    # print('{:.<35s} {:}'.format('Target thread', 'Stopped'))
    logger.log_value('Target thread', 'Stopped')


########################################################################
# Process Function
########################################################################

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


def track_actual_progress(event, command, working_directory=None):

    # print('{:.<35s} {:}'.format('Process thread', 'Started'))
    logger.log_value('Actual progress thread', 'Started')

    # this_thread = current_thread()
    # thread_id = this_thread.ident
    # logger.log_value('The actual progress thread id is', thread_id)

    current_time = datetime.now()
    # formatted_time = '{:%Y-%m-%d %I:%M:%S.%f %p}'.format(current_time)
    formatted_time = '{:%H:%M:%S.%f}'.format(current_time)
    logger.log_value('The start time is', formatted_time)

    actual_percent = PERCENT_START
    try:

        process = execute_asynchronous(command, working_directory)

        finished = False
        while actual_percent < PERCENT_STOP and not finished:

            # line = process.readline()
            # TODO: Verify the value of 80 with defauly pty size.
            line = process.read(80)
            # print('{:.<35s} {:}'.format('Line', line.strip()))
            # logger.log_value('Line', line.strip())
            result = re.search(r'([0-9]{1,3})%', str(line))
            if result:

                # Get the new process progress.
                actual_percent = int(result.group(1))

                # Notify clients of the new process percent.
                event.update(actual_percent)

            # Check if the process is finished.
            if process.exitstatus is not None:
                finished = True

            # Raise an exception if there was an error.
            if process.signalstatus:
                # print('{:.<35s} {:}'.format('Raise exception', 'Processing Error'))
                logger.log_value('Raise exception', 'Processing Error')
                raise ProcessingError('Processing error due to signalstatus %s' % process.signalstatus, process.exitstatus, process.signalstatus)

            # For testing only.
            # if actual_percent > 15: raise Exception('Test exception.')

        # If the process completed without error, adjust the process
        # percent to 100%.
        if actual_percent < PERCENT_STOP:
            # print('{:.<35s} from {:} to {:5.1f}'.format('Adjust final process progress', actual_percent, PERCENT_STOP))
            logger.log_value('Adjust final process progress', '%s%% to %s%%' % (actual_percent, PERCENT_STOP))
            actual_percent = PERCENT_STOP

        # Notify clients of the new process percent.
        event.update(actual_percent)

    # Notify clients there was an error. (It is possible to have an
    # exception after the process reports 100% completion).
    except ProcessingError as exception:
        # print('{:.<35s} {:}'.format('Error', exception))
        logger.log_value('Error', exception)
        # print('{:.<35s} {:}'.format('Exitstatus is', exception.exitstatus))
        logger.log_value('Exitstatus is', exception.exitstatus)
        # print('{:.<35s} {:}'.format('Signalstatus is', exception.signalstatus))
        logger.log_value('Signalstatus is', exception.signalstatus)
        # print('{:.<35s} {:}'.format('The tracekback is', traceback.format_exc()))
        logger.log_value('The tracekback is', traceback.format_exc())
        event.update(actual_percent, process_error=exception)
    except TIMEOUT as exception:
        # print('{:.<35s} {:}'.format('Error', exception))
        logger.log_value('Error', exception)
        # print('{:.<35s} {:}'.format('The tracekback is', traceback.format_exc()))
        logger.log_value('The tracekback is', traceback.format_exc())
        event.update(actual_percent, process_error=exception)
    except EOF as exception:
        # print('{:.<35s} {:}'.format('Error', exception))
        logger.log_value('Error', exception)
        # print('{:.<35s} {:}'.format('The tracekback is', traceback.format_exc()))
        logger.log_value('The tracekback is', traceback.format_exc())
        event.update(actual_percent, process_error=exception)
    except Exception as exception:
        # print('{:.<35s} {:}'.format('Error', exception))
        logger.log_value('Error', exception)
        # print('{:.<35s} {:}'.format('The tracekback is', traceback.format_exc()))
        logger.log_value('The tracekback is', traceback.format_exc())
        event.update(actual_percent, process_error=exception)

    # print('{:.<35s} {:5.1f}'.format('Final process percent', actual_percent))
    logger.log_value('Final process percent', '%s%%' % actual_percent)
    # print('{:.<35s} {:}'.format('Process thread', 'Stopped'))
    logger.log_value('Process thread', 'Stopped')

    current_time = datetime.now()
    # formatted_time = '{:%Y-%m-%d %I:%M:%S.%f %p}'.format(current_time)
    formatted_time = '{:%H:%M:%S.%f}'.format(current_time)
    logger.log_value('The stop time is', formatted_time)
