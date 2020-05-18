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

from ctypes import c_long, py_object, pythonapi
from datetime import datetime
from re import compile
from os import sync
from os.path import join
from pexpect import TIMEOUT, EOF, ExceptionPexpect
from threading import Event, Thread
from time import sleep, time
from traceback import format_exc

from constants import BLUE, CYAN, GREEN, RED, MAGENTA, YELLOW, NORMAL
from constants import START_PERCENT, FINAL_PERCENT, DELAY_PER_PERCENT, SCALE_FACTOR
from utilities import logger
from utilities import processor

########################################################################
# References
########################################################################

# N/A

########################################################################
# Globals & Constants
########################################################################

# Number of steps in the progress at 0%.
START_POSITION = 0  # steps

# Number of steps in the progress at 100%.
FINAL_POSITION = int(FINAL_PERCENT * SCALE_FACTOR)  # steps

# TODO: If Option 3 is selected for the update() function, DELAY can be
#       removed from this module, and DELAY_PER_PERCENT can be removed
#       from the constants module.
# The number of seconds to delay before incrementing one step.
DELAY = DELAY_PER_PERCENT / SCALE_FACTOR  # seconds / step

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


class ProgressThread(Thread):

    def __init__(self, progress_callback):

        self.progress_callback = progress_callback

        self.position = START_POSITION
        self.unblock_event = Event()
        self.block(True)  # Block on initialization.

        self.target_position = START_POSITION
        self.time = time()
        self.delay = -1

        Thread.__init__(self)

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
        Update the target position and the delay, and unblock the thread.
        """

        previous_target_position = self.target_position
        target_position = percent * SCALE_FACTOR

        # Only update the target position and delay if the new target
        # position is greater than the previous target position. The
        # current position will always be less than or equal to the
        # (previous) target position, because the run function blocks
        # when the current position reaches the (previous) target
        # position. Therefore, it is not necessary to check if the
        # new target position is greater than the current position.

        if target_position > previous_target_position:
            previous_time = self.time
            self.time = time()
            delta_time = self.time - previous_time
            delta_target_position = target_position - previous_target_position
            self.delay = delta_time / delta_target_position
            self.target_position = target_position
            self.block(False)
        else:
            self.block(True)
            logger.log_label('Warning. Attempted to set an invalid target position.')
            logger.log_value('The new target position is', target_position)
            logger.log_value('The previous target position is', previous_target_position)

        if is_debug: self.print_values(self.position, self.target_position, self.delay, self.is_blocked())

    def run(self):

        logger.log_value('Progress thread', 'Started')
        current_time = datetime.now()
        # formatted_time = '{:%Y-%m-%d %I:%M:%S.%f %p}'.format(current_time)
        formatted_time = '{:%H:%M:%S.%f}'.format(current_time)
        logger.log_value('The start time is', formatted_time)

        try:
            while self.position < FINAL_POSITION:
                # Block when the current position reaches the target position.
                self.block(self.position >= self.target_position)
                self.progress_callback(self.position / SCALE_FACTOR)
                if is_debug: self.print_values(self.position, self.target_position, self.delay, self.is_blocked())
                self.wait()  # Wait until unblocked.
                self.position += 1
                sleep(self.delay)

            self.progress_callback(self.position / SCALE_FACTOR)
            if is_debug: self.print_values(self.position, self.target_position, self.delay, self.is_blocked())

        except InterruptException as exception:
            logger.log_value('Interrupted the progress thread', exception)
            # logger.log_value('The tracekback is', format_exc())
            return exception

        except Exception as exception:
            logger.log_value('Error while running the progress thread', exception)
            logger.log_value('The tracekback is', format_exc())
            return exception

        finally:
            logger.log_value('Progress thread', 'Stopped')
            logger.log_value('The final progress is', '%s%%' % (self.position / SCALE_FACTOR))
            current_time = datetime.now()
            # formatted_time = '{:%Y-%m-%d %I:%M:%S.%f %p}'.format(current_time)
            formatted_time = '{:%H:%M:%S.%f}'.format(current_time)
            logger.log_value('The stop time is', formatted_time)

    def stop(self):

        self.block(False)
        pythonapi.PyThreadState_SetAsyncExc(c_long(self.ident), py_object(InterruptException))
        self.join()
        sleep(0.500)

    def print_values(self, position, target_position, delay, is_blocked):

        # https://docs.python.org/2/library/string.html

        print(
            '| Position: {:6.2f} % | '
            'Target: {:6.2f} % | '
            'Delay: {:8.5f} | '
            '{:>9} |'.format(position / SCALE_FACTOR,
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
# then exitstatus will store the exit return code and signalstatus will
# be None. If the child was terminated abnormally with a signal then
# signalstatus will store the signal value and exitstatus will be None.

# When using rsync, note that the percentages can fluctuate, sometimes
# reverting to a lower value than previously reported.


def process_command(command, progress_thread, working_directory=None):

    try:
        pattern = compile(r'[0-9]{1,3}(\.[0-9]{2}){0,1}%')
        percent = START_PERCENT
        done = False
        process = processor.execute_asynchronous(command, working_directory)
        while not done:
            try:
                process.expect(pattern)
            except EOF as exception:
                # Close the process to obtain the exit status.
                process.wait()
                process.close()
                done = (process.exitstatus is OK)
                if not done: raise exception
            else:
                match = float((process.after)[:-1])
                if match > percent:
                    percent = match
                    if is_debug: print(CYAN + '▹ Percent:  {:6.2f} %'.format(percent) + NORMAL)
                    progress_thread.update(min(percent, FINAL_PERCENT))

        # The process completed successfully.
        sync()  # Save data to disk.
        logger.log_value('Success. Process complete at', '{:.2f}%'.format(percent))
        logger.log_value('The exit status, signal status is', '%s, %s' % (process.exitstatus, process.signalstatus))
        if percent < FINAL_PERCENT:
            logger.log_value('Adjust the final percent', 'from {:.2f}% to {:.2f}%'.format(percent, FINAL_PERCENT))
            progress_thread.update(FINAL_PERCENT)
        progress_thread.join()

    except EOF as exception:
        # The process was already closed above.
        # process.close()
        logger.log_value('Error. End of file reached at', '{:.2f}%'.format(percent))
        logger.log_value('The exception is', exception)
        logger.log_value('The tracekback is', format_exc())
        return exception
    except TIMEOUT as exception:
        process.close()
        logger.log_value('Error', 'A time out exception occurred.')
        logger.log_value('The exception is', exception)
        logger.log_value('The tracekback is', format_exc())
        return exception
    except KeyboardInterrupt as exception:
        process.close()
        logger.log_value('Error', 'A keyboard interrupt exception occurred.')
        logger.log_value('The exception is', exception)
        logger.log_value('The tracekback is', format_exc())
        return exception
    except ExceptionPexpect as exception:
        process.close()
        logger.log_value('Error', 'A Pexpect exception occurred.')
        logger.log_value('The exception is', exception)
        logger.log_value('The tracekback is', format_exc())
        return exception
    except Exception as exception:
        process.close()
        logger.log_value('Error', 'An exception occurred.')
        logger.log_value('The exception is', exception)
        logger.log_value('The tracekback is', format_exc())
        return exception
    finally:
        sync()  # Save data to disk.
        logger.log_value('The exit status, signal status is', '%s, %s' % (process.exitstatus, process.signalstatus))
        progress_thread.stop()

    return


########################################################################
# Show Progress Function
########################################################################


def show_progress(command, progress_callback, working_directory=None):

    # Start the thread to track the progress of the process.
    progress_thread = ProgressThread(progress_callback)
    progress_thread.start()

    # Start the process which should be tracked.
    process_command(command, progress_thread, working_directory)

    # Make sure data is saved to disk.
    sync()

    sleep(0.500)


########################################################################
# Test
########################################################################


def test_display_progress(percent):

    # print('PROGRESS: {:6.2f} %'.format(percent))
    pass


def test_create_squashfs():

    print('Compress the Linux file system.')

    source_path = '/mnt/ram/Ubuntu/custom-root'
    print('The source path is %s' % source_path)

    target_path = '/mnt/ram/Ubuntu/custom-disk/casper/filesystem.squashfs'
    print('The target path is %s' % target_path)

    # Pkexec is required.
    program = join('/usr/share/cubic', 'commands', 'compress-root')
    command = 'pkexec "%s" "%s" "%s"' % (program, source_path, target_path)

    progress_callback = test_display_progress
    show_progress(command, progress_callback)


def test_copy():
    command = (
        'rsync --info=progress2'
        ' "/mnt/ram/Ubuntu/source-disk/"'
        ' "/mnt/ram/Ubuntu/custom-disk/"'
        ' --delete --recursive --links'
        ' --chmod=u+rwX --exclude="md5sum.txt"'
        ' --exclude="/install/filesystem.manifest"'
        ' --exclude="/install/filesystem.size"'
        ' --exclude="/install/filesystem.squashfs"'
        ' --exclude="/install/filesystem.squashfs.gpg"')

    progress_callback = test_display_progress
    show_progress(command, progress_callback)


def test_xorriso():

    command = (
        'xorriso'
        '  -as mkisofs'
        '  -r'
        '  -V "Ubuntu 20.04.0 2020.05.16 LTS am"'
        '  -cache-inodes'
        '  -J'
        '  -l'
        '  -iso-level 3'
        '  -isohybrid-mbr /usr/lib/ISOLINUX/isohdpfx.bin'
        '  -c isolinux/boot.cat'
        '  -b isolinux/isolinux.bin'
        '    -no-emul-boot'
        '    -boot-load-size 4'
        '    -boot-info-table'
        '  -eltorito-alt-boot'
        '    -e boot/grub/efi.img'
        '    -no-emul-boot'
        '    -isohybrid-gpt-basdat'
        '  -o "/mnt/ram/Ubuntu/ubuntu-20.04.0-2020.05.16-desktop-amd64.B.iso" .')

    working_directory = '/mnt/ram/Ubuntu/custom-disk'
    progress_callback = test_display_progress
    show_progress(command, progress_callback, working_directory)


# test_copy()
# test_create_squashfs()
# test_xorriso()
