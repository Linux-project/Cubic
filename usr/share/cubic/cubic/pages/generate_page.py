#!/usr/bin/python3

########################################################################
#                                                                      #
# generate_page.py                                                     #
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

# http://manpages.ubuntu.com/manpages/groovy/man1/xorrisofs.1.html
# https://linux.die.net/man/8/mkisofs

########################################################################
# Imports
########################################################################

import getpass
import locale
import os
import re
import time

from cubic.constants import BOLD_RED, NORMAL
from cubic.constants import EXTENSION_SIZE, EXTENSION_SQUASHFS
from cubic.constants import FINAL_PERCENT
from cubic.constants import GAP
from cubic.constants import MIB, GIB, MAXIMUM_DISK_SIZE_BYTES, MAXIMUM_DISK_SIZE_GIB
from cubic.constants import SLEEP_0500_MS
from cubic.constants import TIME_STAMP_FORMAT_YYYYMMDD
from cubic.navigator import InterruptException
from cubic.pages import options_page
from cubic.utilities import constructor
from cubic.utilities import displayer
from cubic.utilities import file_utilities
from cubic.utilities import iso_utilities
from cubic.utilities import logger
from cubic.utilities import model
from cubic.utilities.processor import execute_synchronous
from cubic.utilities.progressor import track_progress

########################################################################
# Global Variables & Constants
########################################################################

name = 'generate_page'

########################################################################
# Navigation Functions
########################################################################


def setup(action, old_page=None):

    if action == 'generate':

        displayer.update_status('generate_page__copy_boot_files', displayer.BULLET)
        displayer.update_progress_bar_percent('generate_page__copy_boot_files_progress_bar', 0)
        # displayer.update_progress_bar_text('generate_page__copy_boot_files_progress_bar', ' ')
        displayer.update_label('generate_page__copy_boot_files_message', '...')

        displayer.update_status('generate_page__create_squashfs', displayer.BULLET)
        displayer.update_progress_bar_percent('generate_page__create_squashfs_progress_bar', 0)
        displayer.update_progress_bar_text('generate_page__create_squashfs_progress_bar', ' ')
        displayer.update_label('generate_page__create_squashfs_message', '...')

        displayer.update_status('generate_page__update_file_system_size', displayer.BULLET)
        displayer.update_label('generate_page__update_file_system_size_message', '...')

        displayer.update_status('generate_page__update_disk_name', displayer.BULLET)
        displayer.update_label('generate_page__update_disk_name_message', '...')

        displayer.update_status('generate_page__update_checksums', displayer.BULLET)
        displayer.update_progress_bar_percent('generate_page__update_checksums_progress_bar', 0)
        displayer.update_progress_bar_text('generate_page__update_checksums_progress_bar', ' ')
        displayer.update_label('generate_page__update_checksums_message', '...')

        displayer.update_status('generate_page__check_custom_disk_size', displayer.BULLET)
        displayer.update_label('generate_page__check_custom_disk_size_message', '...')

        displayer.update_status('generate_page__create_iso_image', displayer.BULLET)
        displayer.update_progress_bar_percent('generate_page__create_iso_image_progress_bar', 0)
        displayer.update_progress_bar_text('generate_page__create_iso_image_progress_bar', ' ')
        displayer.update_label('generate_page__create_iso_image_message', '...')

        displayer.update_status('generate_page__calculate_iso_image_checksum', displayer.BULLET)
        displayer.update_label('generate_page__calculate_iso_image_checksum_message', '...')

        displayer.reset_buttons(
            back_button_label='❬Back',
            back_action='back',
            back_button_style=None,
            is_back_sensitive=True,
            is_back_visible=True,
            next_button_label='Finish❭',
            next_action='finish',
            next_button_style=None,
            is_next_sensitive=False,
            is_next_visible=True)

        return

    else:

        logger.log_value('Error', f'{BOLD_RED}Unknown action for setup{NORMAL}')

        return 'unknown'


def enter(action, old_page=None):

    if action == 'generate':

        # --------------------------------------------------------------
        # Copy boot files.
        # --------------------------------------------------------------

        displayer.update_status('generate_page__copy_boot_files', displayer.PROCESSING)
        time.sleep(SLEEP_0500_MS)
        is_error = copy_kernel_files()
        if is_error: return  # Stay on this page.
        time.sleep(SLEEP_0500_MS)

        # --------------------------------------------------------------
        # Create squashfs.
        # --------------------------------------------------------------

        displayer.update_status('generate_page__create_squashfs', displayer.PROCESSING)
        time.sleep(SLEEP_0500_MS)
        is_error = create_squashfs()
        if is_error: return  # Stay on this page.
        time.sleep(SLEEP_0500_MS)

        # --------------------------------------------------------------
        # Update file system size.
        # --------------------------------------------------------------

        displayer.update_status('generate_page__update_file_system_size', displayer.PROCESSING)
        time.sleep(SLEEP_0500_MS)
        is_error = update_file_system_size()
        if is_error: return  # Stay on this page.
        time.sleep(SLEEP_0500_MS)

        # --------------------------------------------------------------
        # Update disk name and disk info.
        # --------------------------------------------------------------

        displayer.update_status('generate_page__update_disk_name', displayer.PROCESSING)
        time.sleep(SLEEP_0500_MS)
        is_error = update_disk_name_and_disk_info()
        if is_error: return  # Stay on this page.
        time.sleep(SLEEP_0500_MS)

        # --------------------------------------------------------------
        # Update MD5 checksums.
        # --------------------------------------------------------------

        displayer.update_status('generate_page__update_checksums', displayer.PROCESSING)
        time.sleep(SLEEP_0500_MS)
        is_error = update_checksums()
        if is_error: return  # Stay on this page.
        time.sleep(SLEEP_0500_MS)

        # --------------------------------------------------------------
        # Check disk size.
        # --------------------------------------------------------------

        displayer.update_status('generate_page__check_custom_disk_size', displayer.PROCESSING)
        time.sleep(SLEEP_0500_MS)
        is_error = check_custom_disk_directory_size()
        if is_error: return  # Stay on this page.
        time.sleep(SLEEP_0500_MS)

        # --------------------------------------------------------------
        # Create disk image.
        # --------------------------------------------------------------

        displayer.update_status('generate_page__create_iso_image', displayer.PROCESSING)
        time.sleep(SLEEP_0500_MS)
        is_error = create_iso_image()
        if is_error: return  # Stay on this page.
        time.sleep(SLEEP_0500_MS)

        # --------------------------------------------------------------
        # Calculate disk image checksum.
        # --------------------------------------------------------------

        displayer.update_status('generate_page__calculate_iso_image_checksum', displayer.PROCESSING)
        time.sleep(SLEEP_0500_MS)
        is_error = calculate_checksum_for_iso()
        if is_error: return  # Stay on this page.
        time.sleep(SLEEP_0500_MS)

        # Success. Pause to allow the user to see the page.
        time.sleep(SLEEP_0500_MS)

        return 'finish'

    else:

        logger.log_value('Error', f'{BOLD_RED}Unknown action for enter{NORMAL}')

        return 'unknown'


def leave(action, new_page=None):

    if action == 'back':

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        model.project.configuration.save()

        return

    elif action == 'error':

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        return

    elif action == 'finish':

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        model.project.configuration.save()

        return

    elif action == 'quit':

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        options_page.preseed_tab.remove_tree()
        options_page.boot_tab.remove_tree()

        iso_utilities.unmount_iso_and_delete_mount_point(model.project.iso_mount_point)

        model.project.configuration.save()

        return

    else:

        logger.log_value('Error', f'{BOLD_RED}Unknown action for leave{NORMAL}')

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        iso_utilities.unmount_iso_and_delete_mount_point(model.project.iso_mount_point)

        model.project.configuration.save()

        return 'unknown'

    return


########################################################################
# Handler Functions
########################################################################

# N/A

########################################################################
# Support Functions
########################################################################

# ----------------------------------------------------------------------
# Copy Disk Kernel Files Functions
# ----------------------------------------------------------------------


def copy_kernel_files():
    """
    Copies vmlinuz & initrd files to the custom disk.
    """

    # ------------------------------------------------------------------
    # Vmlinuz & Initrd
    # ------------------------------------------------------------------

    time.sleep(SLEEP_0500_MS)

    logger.log_label('Identify the selected kernel')

    # Get the selected kernel.

    # 0: version_name
    # 1: vmlinuz_file_name
    # 2: new_vmlinuz_file_name
    # 3: initrd_file_name
    # 4: new_initrd_file_name
    # 5: directory
    # 6: note
    # 7: is_selected

    list_store = model.builder.get_object('kernel_tab__list_store')
    for selected_index, kernel_details in enumerate(list_store):
        if kernel_details[7]:
            break
    else:
        selected_index = 0
    logger.log_value('The selected kernel is index number', selected_index)

    # Get the selected directory.
    source_directory = list_store[selected_index][5]

    # Get the target directory.
    target_directory = os.path.join(model.project.custom_disk_directory, model.status.casper_directory)

    # displayer.update_progress_bar_percent('generate_page__copy_boot_files_progress_bar', 0)

    # ------------------------------------------------------------------
    # Vmlinuz
    # ------------------------------------------------------------------

    logger.log_label('Update the vmlinuz boot file')

    source_file_name = list_store[selected_index][1]
    source_file_path = os.path.join(source_directory, source_file_name)
    target_file_name = list_store[selected_index][2]
    target_file_path = os.path.join(target_directory, target_file_name)
    user = getpass.getuser()

    # Delete existing vmlinuz* files in the target directory. Do not
    # remove a file if it matches the target file name, because it will
    # be efficiently updated by rsync.
    file_path_pattern = os.path.join(target_directory, 'vmlinuz*')
    file_utilities.delete_files_with_pattern(file_path_pattern, [target_file_path])

    # Copy the new vmlinuz file.
    try:
        _copy_kernel_file(source_file_path, target_file_path, user, file_number=0, total_files=2)
    except InterruptException as exception:
        displayer.update_label('generate_page__copy_boot_files_message', '<span foreground="red">Error. Unable to update the vmlinuz boot file.</span>')
        displayer.update_status('generate_page__copy_boot_files', displayer.ERROR)
        logger.log_value('Propagate exception', exception)
        raise exception
    except Exception as exception:
        displayer.update_label('generate_page__copy_boot_files_message', '<span foreground="red">Error. Unable to update the vmlinuz boot file.</span>')
        displayer.update_status('generate_page__copy_boot_files', displayer.ERROR)
        logger.log_value('Do not propagate exception', exception)
        return True  # (Error)

    # Workaround for Pop!_OS.

    # Create a symlink from vmlinuz.eft to vmlinuz.
    # Workaround for Bug #1900917, "Kernel Panic on Boot After
    # Installation (No initrd in grub.cfg)."
    # Reference Bug #1898749, "Pop!_OS expects vmlinuz on the ISO to
    # have the *.efi extension."
    # Reference Bug #1895770, "Pop!_OS expects the initramfs bootstrap
    # file to be explicitly named "initrd.gz"
    is_pop_os_based = constructor.os_is_distribution('pop', model.project.custom_root_directory)
    if is_pop_os_based:
        source_file_name = target_file_name
        target_file_name = 'vmlinuz.efi'
        target_file_path = os.path.join(target_directory, target_file_name)
        if source_file_name != target_file_name and not os.path.exists(target_file_path):
            logger.log_value('For Pop!_OS, create symlink', f'from {source_file_name} to {target_file_name}')
            os.symlink(source_file_name, target_file_path)

    # ------------------------------------------------------------------
    # Initrd
    # ------------------------------------------------------------------

    logger.log_label('Update the initrd boot file')

    source_file_name = list_store[selected_index][3]
    source_file_path = os.path.join(source_directory, source_file_name)
    target_file_name = list_store[selected_index][4]
    target_file_path = os.path.join(target_directory, target_file_name)
    user = getpass.getuser()

    # Delete existing initrd* files in the target directory. Do not
    # remove a file if it matches the target file name, because it will
    # be efficiently updated by rsync.
    file_path_pattern = os.path.join(target_directory, 'initrd*')
    file_utilities.delete_files_with_pattern(file_path_pattern, [target_file_path])

    # Copy the new initrd file.
    try:
        _copy_kernel_file(source_file_path, target_file_path, user, file_number=1, total_files=2)
    except InterruptException as exception:
        displayer.update_label('generate_page__copy_boot_files_message', '<span foreground="red">Error. Unable to update the initrd boot file.</span>')
        displayer.update_status('generate_page__copy_boot_files', displayer.ERROR)
        logger.log_value('Propagate exception', exception)
        raise exception
    except Exception as exception:
        displayer.update_label('generate_page__copy_boot_files_message', '<span foreground="red">Error. Unable to update the initrd boot file.</span>')
        displayer.update_status('generate_page__copy_boot_files', displayer.ERROR)
        logger.log_value('Do not propagate exception', exception)
        return True  # (Error)

    displayer.update_label('generate_page__copy_boot_files_message', 'Success.')
    displayer.update_status('generate_page__copy_boot_files', displayer.OK)
    return False  # (No error)


def _copy_kernel_file(source_file_path, target_file_path, user, file_number, total_files):
    """
    Raises exception.
    """

    # TODO: Can this function be consolidated outside this module?

    logger.log_label(f'Copy file number {file_number+1} of {total_files}')

    logger.log_value('The source file path is', source_file_path)
    logger.log_value('The target file path is', target_file_path)

    program = os.path.join(model.application.directory, 'commands', 'copy-path')
    command = ['pkexec', program, source_file_path, target_file_path, user]

    # The progress callback function.
    def progress_callback(percent):
        total_percent = (FINAL_PERCENT * file_number + percent) / total_files
        displayer.update_progress_bar_percent('generate_page__copy_boot_files_progress_bar', total_percent)
        if total_percent % 10 == 0:
            logger.log_value('Completed', f'{total_percent:n}%')

    track_progress(command, progress_callback)


# ----------------------------------------------------------------------
# Create Squashfs Functions
# ----------------------------------------------------------------------


def create_squashfs():

    logger.log_label('Compress the Linux file system')

    file_name = f'{model.status.squashfs_file_name}.{EXTENSION_SQUASHFS}'

    source_file_path = model.project.custom_root_directory
    logger.log_value('The source file path is', source_file_path)

    target_file_path = os.path.join(model.project.custom_disk_directory, model.status.squashfs_directory, file_name)
    logger.log_value('The target file path is', target_file_path)

    displayer.update_label('generate_page__create_squashfs_message', f'Using {model.options.compression} compression.')

    # Create filesystem.squashfs or
    # ubuntu-server-minimal.ubuntu-server.squashfs.

    # Pkexec is required.
    program = os.path.join(model.application.directory, 'commands', 'compress-root')
    command = ['pkexec', program, source_file_path, target_file_path, model.options.compression]

    # Show % in progress by setting text to None.
    # displayer.update_progress_bar_text('generate_page__create_squashfs_progress_bar', None)
    displayer.update_progress_bar_text('generate_page__create_squashfs_progress_bar', f'0.0{GAP}%')

    # The progress callback function.
    def progress_callback(percent):
        displayer.update_progress_bar_text('generate_page__create_squashfs_progress_bar', f'{locale.format_string("%.1f", percent, True)}{GAP}%')
        displayer.update_progress_bar_percent('generate_page__create_squashfs_progress_bar', percent)
        if percent % 10 == 0:
            logger.log_value('Completed', f'{percent:n}%')

    try:
        track_progress(command, progress_callback)
    except InterruptException as exception:
        if 'No space left on device' in str(exception):
            displayer.update_label('generate_page__create_squashfs_message', 'Error. Not enough space on the disk.')
        else:
            displayer.update_label('generate_page__create_squashfs_message', 'Error. Unable to create the compressed Linux file system.')
        displayer.update_status('generate_page__create_squashfs', displayer.ERROR)
        logger.log_value('Propagate exception', exception)
        raise exception
    except Exception as exception:
        if 'No space left on device' in str(exception):
            displayer.update_label('generate_page__create_squashfs_message', 'Error. Not enough space on the disk.')
        else:
            displayer.update_label('generate_page__create_squashfs_message', 'Error. Unable to create the compressed Linux file system.')
        displayer.update_status('generate_page__create_squashfs', displayer.ERROR)
        logger.log_value('Do not propagate exception', exception)
        return True  # (Error)

    displayer.update_label('generate_page__create_squashfs_message', 'Success.')
    displayer.update_status('generate_page__create_squashfs', displayer.OK)
    return False  # (No error)


def create_squashfs_TESTING_1():
    """
    This function does nothing.
    """

    logger.log_label('Create squashfs (Testing)')

    file_name = f'{model.status.squashfs_file_name}.{EXTENSION_SQUASHFS}'

    source_file_path = model.project.custom_root_directory
    logger.log_value('The source file path is', source_file_path)

    target_file_path = os.path.join(model.project.custom_disk_directory, model.status.squashfs_directory, file_name)
    logger.log_value('The target file path is', target_file_path)

    displayer.update_label('generate_page__create_squashfs_message', 'Testing.')
    displayer.update_status('generate_page__create_squashfs', displayer.OK)
    return False  # (No error)


def create_squashfs_TESTING_2():
    """
    This function simply copies the original filesystem.squashfs file or
    the ubuntu-server-minimal.ubuntu-server.squashfs file.
    """

    logger.log_label('Create squashfs (Testing)')

    file_name = f'{model.status.squashfs_file_name}.{EXTENSION_SQUASHFS}'

    source_file_path = os.path.join(model.project.iso_mount_point, model.status.squashfs_directory, file_name)
    logger.log_value('The source file path is', source_file_path)

    target_file_path = os.path.join(model.project.custom_disk_directory, model.status.squashfs_directory, file_name)
    logger.log_value('The target file path is', target_file_path)

    # Copy the original filesystem.squashfs or
    # ubuntu-server-minimal.ubuntu-server.squashfs.
    file_utilities.copy_file(source_file_path, target_file_path)

    if not os.path.exists(target_file_path):
        displayer.update_label('generate_page__create_squashfs_message', f'Testing. Error. {file_name} already exists.')
        displayer.update_status('generate_page__create_squashfs', displayer.ERROR)
        return True  # (Error)

    displayer.update_label('generate_page__create_squashfs_message', 'Testing.')
    displayer.update_status('generate_page__create_squashfs', displayer.OK)
    return False  # (No error)


def create_squashfs_TESTING_3():
    """
    This function displays a progress from 0 to 1,000.
    """

    logger.log_label('Create squashfs (Testing)')

    total_files = 1000
    for file_number in range(0, 1000):
        percent = 100 * file_number / total_files
        displayer.update_progress_bar_percent('generate_page__create_squashfs_progress_bar', percent)
        displayer.update_progress_bar_text('generate_page__create_squashfs_progress_bar', f'Processing {file_number:n} of {total_files:n}')
        time.sleep(SLEEP_0500_MS)

    displayer.update_status('generate_page__create_squashfs', displayer.OK)
    return False  # (No error)


# ----------------------------------------------------------------------
# Update File System Size Functions
# ----------------------------------------------------------------------


def update_file_system_size():

    logger.log_label('Update the file system size')

    # Get the file system size.
    try:
        # Pkexec is required.
        program = os.path.join(model.application.directory, 'commands', 'file-size')
        command = ['pkexec', program, model.project.custom_root_directory]
        result, exit_status, signal_status = execute_synchronous(command)
        size_information = re.search(r'^([0-9]+)\s', result)
        size_in_bytes = int(size_information.group(1))
        size_in_mib = size_in_bytes / MIB
        size_in_gib = size_in_bytes / GIB
        logger.log_value('The file system size is', f'{locale.format_string("%.2f", size_in_gib, True)} GiB ({size_in_bytes:n} bytes)')
        if size_in_bytes > GIB:
            displayer.update_label(
                'generate_page__update_file_system_size_message',
                f'The file system size is {locale.format_string("%.2f", size_in_gib, True)} GiB ({size_in_bytes:n} bytes).')
        else:
            displayer.update_label(
                'generate_page__update_file_system_size_message',
                f'The file system size is {locale.format_string("%.2f", size_in_mib, True)} MiB ({size_in_bytes:n} bytes).')
    except InterruptException as exception:
        logger.log_value(f'Unable to get file system size for {model.project.custom_root_directory}', result)
        logger.log_value('The exception is', exception)
        displayer.update_label('generate_page__update_file_system_size_message', 'Error. Unable to get file system size.')
        displayer.update_status('generate_page__update_file_system_size', displayer.ERROR)
        logger.log_value('Propagate exception', exception)
        raise exception
    except Exception as exception:
        logger.log_value(f'Unable to get file system size for {model.project.custom_root_directory}', result)
        logger.log_value('The exception is', exception)
        displayer.update_label('generate_page__update_file_system_size_message', 'Error. Unable to get file system size.')
        displayer.update_status('generate_page__update_file_system_size', displayer.ERROR)
        logger.log_value('Do not propagate exception', exception)
        return True  # (Error)

    # Write the file system size.
    try:
        file_name = f'{model.status.squashfs_file_name}.{EXTENSION_SIZE}'
        file_path = os.path.join(model.project.custom_disk_directory, model.status.squashfs_directory, file_name)
        file_utilities.write_line(str(size_in_bytes), file_path)
    except InterruptException as exception:
        displayer.update_label('generate_page__update_file_system_size_message', 'Error. Unable to save file system size.')
        displayer.update_status('generate_page__update_file_system_size', displayer.ERROR)
        logger.log_value('Do not propagate exception', exception)
        return True  # (Error)
    except Exception as exception:
        displayer.update_label('generate_page__update_file_system_size_message', 'Error. Unable to save file system size.')
        displayer.update_status('generate_page__update_file_system_size', displayer.ERROR)
        logger.log_value('Propagate exception', exception)
        raise exception

    displayer.update_status('generate_page__update_file_system_size', displayer.OK)
    return False  # (No error)


# ----------------------------------------------------------------------
# Update Disk Name and Disk Info Functions
# ----------------------------------------------------------------------


def update_disk_name_and_disk_info():

    try:
        _update_disk_name()
    except InterruptException as exception:
        logger.log_value('Unable to update the disk name to', model.custom.iso_disk_name)
        displayer.update_label('generate_page__update_disk_name_message', 'Error. Unable to update the disk name.')
        displayer.update_status('generate_page__update_disk_name', displayer.ERROR)
        logger.log_value('Propagate exception', exception)
        raise exception
    except Exception as exception:
        logger.log_value('Unable to update the disk name to', model.custom.iso_disk_name)
        displayer.update_label('generate_page__update_disk_name_message', 'Error. Unable to update the disk name.')
        displayer.update_status('generate_page__update_disk_name', displayer.ERROR)
        logger.log_value('Do not propagate exception', exception)
        return True  # (Error)

    try:
        _update_disk_info()
    except InterruptException as exception:
        logger.log_value('Unable to update the disk name to', model.custom.iso_disk_name)
        displayer.update_label('generate_page__update_disk_name_message', 'Error. Unable to update the disk name.')
        displayer.update_status('generate_page__update_disk_name', displayer.ERROR)
        logger.log_value('Propagate exception', exception)
        raise exception
    except Exception as exception:
        logger.log_value('Unable to update the disk name to', model.custom.iso_disk_name)
        displayer.update_label('generate_page__update_disk_name_message', 'Error. Unable to update the disk name.')
        displayer.update_status('generate_page__update_disk_name', displayer.ERROR)
        logger.log_value('Do not propagate exception', exception)
        return True  # (Error)

    displayer.update_label('generate_page__update_disk_name_message', 'Success.')
    displayer.update_status('generate_page__update_disk_name', displayer.OK)
    return False  # (No error)


def _update_disk_name():
    """
    Raises exception.
    """

    logger.log_label('Update the disk name')

    file_path = os.path.join(model.project.custom_disk_directory, 'README.diskdefines')

    # Read the original file if it exists.
    lines = []
    if os.path.isfile(file_path):
        logger.log_value('The existing file will be updated', file_path)
        lines = file_utilities.read_lines(file_path)
    else:
        logger.log_value('A new file will be created', file_path)

    # Create the new lines.
    new_lines = []
    # Append the new disk name line.
    line = f'#define DISKNAME  {model.custom.iso_disk_name}'
    new_lines.append(line)
    logger.log_value('Update disk name', line)
    # Append the new disk note line.
    display_version = constructor.get_display_version(model.application.cubic_version)
    # Use the modify date from the model.
    line = f'#define DISKNOTE  Generated using Cubic version {display_version} on {model.project.modify_date} based on {model.original.iso_file_name}'
    new_lines.append(line)
    logger.log_value('Update disk note', line)
    # Append only existing lines that should be retained.
    for line in lines:
        if 'DISKNAME' in line:
            # Exclude old disk name line.
            pass
        elif 'DISKNOTE' in line:
            # Exclude old disk note line.
            pass
        elif 'CUBIC_INFO' in line:
            # TODO: Remove this block in a future release (2012-12-11).
            pass
        else:
            # Retain existing line.
            new_lines.append(line.strip())

    # Create a new README.diskdefines file.
    file_utilities.write_lines(new_lines, file_path)


def _update_disk_info():
    """
    Raises exception.
    """

    logger.log_label('Update the disk information')

    # Use the modify date from the model.
    time_stamp = constructor.reformat_time_stamp(model.project.modify_date, TIME_STAMP_FORMAT_YYYYMMDD)
    line = f'{model.custom.iso_disk_name} ({time_stamp})'
    logger.log_value('The custom disk image name and release date are', line)
    file_path = os.path.join(model.project.custom_disk_directory, '.disk', 'info')
    file_utilities.write_line(line, file_path)


# ----------------------------------------------------------------------
# Update Checksums Functions
# ----------------------------------------------------------------------


# TODO: This doesn't use a pexpect process.
#       How do we kill/stop this when back, or quit are clicked?
#       Do we use a flag and/or break in all loops?
def update_checksums():

    # TODO: Should os.path.realpath should be used for?...
    #       1. checksums_file_path
    #       2. exclude_paths

    logger.log_label('Update checksums')

    # Show % in progress by setting text to None.
    displayer.update_progress_bar_text('generate_page__update_checksums_progress_bar', None)

    checksums_file_path = os.path.join(model.project.custom_disk_directory, 'md5sum.txt')
    start_path = model.project.custom_disk_directory

    #
    # Identify file paths to exclude from the checksums.
    #

    exclude_paths = []

    # Exclude the checksums file.
    exclude_paths.append(checksums_file_path)

    # Exclude the eltorito boot image and the boot catalog.

    template = constructor.decode(model.status.iso_template)

    # Exclude the eltorito boot image file path (if it exists).
    result = re.search(r"-b '(.*?)'", template)
    if result:
        file_path = result.group(1).strip(os.path.sep)
        file_path = os.path.join(model.project.custom_disk_directory, file_path)
        exclude_paths.append(file_path)

    # Exclude the boot catalog file path (if it exists).
    result = re.search(r"-c '(.*?)'", template)
    if result:
        file_path = result.group(1).strip(os.path.sep)
        file_path = os.path.join(model.project.custom_disk_directory, file_path)
        exclude_paths.append(file_path)

    #
    # Get file paths to include in the checksums.
    #

    file_paths = file_utilities.get_relative_file_paths(start_path, exclude_paths)
    file_paths.sort(key=lambda file_path: file_path.lower())

    total_files = len(file_paths)
    if total_files == 0:
        logger.log_value('Unable to update checksums. No files found in', checksums_file_path)
        displayer.update_label('generate_page__update_checksums_message', 'Error. Unable to calculate checksums.')
        displayer.update_status('generate_page__update_checksums', displayer.ERROR)
        return True  # (Error)

    #
    # Update checksums and display progress.
    #

    # https://docs.python.org/3/library/functions.html#open
    #
    # r   Open text file for reading. The stream is positioned at the
    #     beginning of the file.
    #
    # r+  Open for reading and writing. The stream is positioned at the
    #     beginning of the file.
    #
    # w   Truncate file to zero length or create text file for writing.
    #     The stream is positioned at the beginning of the file.
    #
    # w+  Open for reading and writing. The file is created if it does
    #     not exist, otherwise it is truncated. The stream is positioned
    #     at the beginning of the file.
    #
    # a   Open for writing. The file is created if it does not exist.
    #     The stream is positioned at the end of the file.  Subsequent
    #     writes to the file will always end up at the then current end
    #     of file, irrespective of any intervening fseek(3) or similar.
    #
    # a+  Open for reading and writing. The file is created if it does
    #     not exist. The stream is positioned at the end of the file.
    #     Subsequent writes to the file will always end up at the then
    #     current end of file, irrespective of any intervening fseek(3)
    #     or similar.

    try:
        logger.log_value('Write to file', checksums_file_path)
        with open(checksums_file_path, 'w') as file:
            for file_number, file_path in enumerate(file_paths, start=1):
                # displayer.update_label('generate_page__update_checksums_message', f'Calculating checksum for file {file_number} of {total_files}.')
                checksum, file_path = file_utilities.calculate_md5_hash(file_path, start_path)
                if file_number == 1:
                    file.write(f'{checksum}  ./{file_path}')
                else:
                    file.write(f'\n{checksum}  ./{file_path}')
                percent = 100 * file_number / total_files
                displayer.update_progress_bar_percent('generate_page__update_checksums_progress_bar', percent)
                displayer.update_progress_bar_text(
                    'generate_page__update_checksums_progress_bar',
                    f'Calculating checksum for file {file_number:n} of {total_files:n}')
    except InterruptException as exception:
        logger.log_value('Error', 'Unable to update checksums')
        logger.log_value('The exception is', exception)
        if 'No space left on device' in str(exception):
            displayer.update_label('generate_page__update_checksums_message', 'Error. Not enough space on the disk.')
        else:
            displayer.update_label('generate_page__update_checksums_message', 'Error. Unable to calculate checksums.')
        displayer.update_status('generate_page__update_checksums', displayer.ERROR)
        logger.log_value('Propagate exception', exception)
        raise exception
    except Exception as exception:
        logger.log_value('Error', 'Unable to update checksums')
        logger.log_value('The exception is', exception)
        if 'No space left on device' in str(exception):
            displayer.update_label('generate_page__update_checksums_message', 'Error. Not enough space on the disk.')
        else:
            displayer.update_label('generate_page__update_checksums_message', 'Error. Unable to calculate checksums.')
        displayer.update_status('generate_page__update_checksums', displayer.ERROR)
        logger.log_value('Do not propagate exception', exception)
        return True  # (Error)

    logger.log_value('Calculated checksums for', f'{total_files} files')
    displayer.update_progress_bar_text('generate_page__update_checksums_progress_bar', '100%')
    displayer.update_label('generate_page__update_checksums_message', f'Calculated checksums for {total_files} files.')
    displayer.update_status('generate_page__update_checksums', displayer.OK)
    return False  # (No error)


# ----------------------------------------------------------------------
# Check Disk Size Functions
# ----------------------------------------------------------------------


def check_custom_disk_directory_size():

    logger.log_label('Get the custom disk size')

    try:
        # Pkexec is not required.
        program = os.path.join(model.application.directory, 'commands', 'file-size')
        command = ['pkexec', program, model.project.custom_disk_directory]
        result, exit_status, signal_status = execute_synchronous(command)
        size_information = re.search(r'^([0-9]+)\s', result)
        size_in_bytes = int(size_information.group(1))
        size_in_mib = size_in_bytes / MIB
        size_in_gib = size_in_bytes / GIB
    except InterruptException as exception:
        logger.log_value('Unable to get the total size', model.project.custom_disk_directory)
        logger.log_value('The exception is', exception)
        displayer.update_label('generate_page__check_custom_disk_size_message', 'Error. Unable to get the total size.')
        displayer.update_status('generate_page__check_custom_disk_size', displayer.ERROR)
        logger.log_value('Propagate exception', exception)
        raise exception
    except Exception as exception:
        logger.log_value('Unable to get the total size', model.project.custom_disk_directory)
        logger.log_value('The exception is', exception)
        displayer.update_label('generate_page__check_custom_disk_size_message', 'Error. Unable to get the total size.')
        displayer.update_status('generate_page__check_custom_disk_size', displayer.ERROR)
        logger.log_value('Do not propagate exception', exception)
        return True  # (Error)

    logger.log_value('The total size is', f'{locale.format_string("%.2f", size_in_gib, True)} GiB ({size_in_bytes:n} bytes)')

    logger.log_value('The maximum size limit for all files on the disk is', f'{MAXIMUM_DISK_SIZE_GIB:.2f} GiB ({MAXIMUM_DISK_SIZE_BYTES:n} bytes)')
    if size_in_bytes > MAXIMUM_DISK_SIZE_BYTES:
        logger.log_value('Error', 'The total size exceeds the maximum size')
        displayer.update_label(
            'generate_page__check_custom_disk_size_message',
            f'The the custom disk directory size is {locale.format_string("%.2f", size_in_gib, True)} GiB ({size_in_bytes:n} bytes).{os.linesep}'
            f'This is larger than the {MAXIMUM_DISK_SIZE_GIB:.2f} GiB ({MAXIMUM_DISK_SIZE_BYTES:n} bytes) limit.{os.linesep}'
            f'Click the Back button, and reduce the size of the Linux file system.')
        displayer.update_status('generate_page__check_custom_disk_size', displayer.ERROR)
        return True  # (Error)

    if size_in_bytes > GIB:
        displayer.update_label(
            'generate_page__check_custom_disk_size_message',
            f'The total size of all files is {locale.format_string("%.2f", size_in_gib, True)} GiB ({size_in_bytes:n} bytes).')
    else:
        displayer.update_label(
            'generate_page__check_custom_disk_size_message',
            f'The total size of all files is {locale.format_string("%.2f", size_in_mib, True)} MiB ({size_in_bytes:n} bytes).')
    displayer.update_status('generate_page__check_custom_disk_size', displayer.OK)
    return False  # (No error)


# ----------------------------------------------------------------------
# Create Disk Image Functions
# ----------------------------------------------------------------------
'''
https://askubuntu.com/questions/1289400/remaster-installation-image-for-ubuntu-20-10
https://unix.stackexchange.com/users/135084/thomas-schmitt
https://stackoverflow.com/questions/60731231/xorriso-boot-catalog-and-eltorito-catalog-not-working
https://askubuntu.com/questions/457528/how-do-i-create-an-efi-bootable-iso-of-a-customized-version-of-ubuntu

1. Exclude every folder under boot/grub
2. Exclude the entire EFI folder
3. Exclude the file boot.catalog
'''


def create_iso_image():

    #
    # Create disk image.
    #

    logger.log_label('Create disk image')

    # Get the correct xorriso command.
    command = _get_xorriso_command()

    # Show % in progress by setting text to None.
    # displayer.update_progress_bar_text('generate_page__create_iso_image_progress_bar', None)
    displayer.update_progress_bar_text('generate_page__create_iso_image_progress_bar', f'0.0{GAP}%')

    # The progress callback function.
    def progress_callback(percent):
        displayer.update_progress_bar_percent('generate_page__create_iso_image_progress_bar', percent)
        displayer.update_progress_bar_text('generate_page__create_iso_image_progress_bar', f'{locale.format_string("%.1f", percent, True)}{GAP}%')
        if percent % 10 == 0:
            logger.log_value('Completed', f'{percent:n}%')

    try:
        track_progress(command, progress_callback, working_directory=model.project.custom_disk_directory)
    except InterruptException as exception:
        if 'exceeds free space on media' in str(exception):
            displayer.update_label('generate_page__create_iso_image_message', 'Error. Not enough space on the disk.')
        else:
            displayer.update_label('generate_page__create_iso_image_message', 'Error. Unable to create the customized disk image.')
        displayer.update_status('generate_page__create_iso_image', displayer.ERROR)
        logger.log_value('Propagate exception', exception)
        raise exception
    except Exception as exception:
        if 'exceeds free space on media' in str(exception):
            displayer.update_label('generate_page__create_iso_image_message', 'Error. Not enough space on the disk.')
        else:
            displayer.update_label('generate_page__create_iso_image_message', 'Error. Unable to create the customized disk image.')
        displayer.update_status('generate_page__create_iso_image', displayer.ERROR)
        logger.log_value('Do not propagate exception', exception)
        return True  # (Error)

    #
    # Get the size.
    #

    logger.log_label('Get the custom disk size')

    iso_file_path = os.path.join(model.custom.iso_directory, model.custom.iso_file_name)
    try:
        # Pkexec is not required.
        program = os.path.join(model.application.directory, 'commands', 'file-size')
        command = ['pkexec', program, iso_file_path]
        result, exit_status, signal_status = execute_synchronous(command)
        size_information = re.search(r'^([0-9]+)\s', result)
        size_in_bytes = int(size_information.group(1))
        size_in_mib = size_in_bytes / MIB
        size_in_gib = size_in_bytes / GIB
        model.iso_file_size = size_in_bytes
    except InterruptException as exception:
        logger.log_value('Unable to get the size of the custom disk', iso_file_path)
        logger.log_value('The exception is', exception)
        displayer.update_label('generate_page__create_iso_image_message', 'Error. Unable to get the size of the custom disk.')
        displayer.update_status('generate_page__create_iso_image', displayer.ERROR)
        logger.log_value('Propagate exception', exception)
        raise exception
    except Exception as exception:
        logger.log_value('Unable to get the size of the custom disk', iso_file_path)
        logger.log_value('The exception is', exception)
        displayer.update_label('generate_page__create_iso_image_message', 'Error. Unable to get the size of the custom disk.')
        displayer.update_status('generate_page__create_iso_image', displayer.ERROR)
        logger.log_value('Do not propagate exception', exception)
        return True  # (Error)

    if size_in_bytes > GIB:
        logger.log_value('The size of the custom disk is', f'{locale.format_string("%.2f", size_in_gib, True)} GiB ({size_in_bytes:n} bytes)')
        displayer.update_label(
            'generate_page__create_iso_image_message',
            f'Generated {model.custom.iso_file_name}. The disk image size is {locale.format_string("%.2f", size_in_gib, True)} GiB.')
    else:
        logger.log_value('The size of the custom disk is', f'{locale.format_string("%.2f", size_in_mib, True)} MiB ({size_in_bytes:n} bytes)')
        displayer.update_label(
            'generate_page__create_iso_image_message',
            f'Generated {model.custom.iso_file_name}. The disk image size is {locale.format_string("%.2f", size_in_mib, True)} MiB.')

    displayer.update_status('generate_page__create_iso_image', displayer.OK)
    return False  # (No error)


# ----------------------------------------------------------------------
# Get Xorriso Command Functions
# ----------------------------------------------------------------------


def _get_xorriso_command():

    template = constructor.decode(model.status.iso_template)

    # In the xorriso command, the volume_id and boot_image_directory are
    # single quoted bash strings, so these values may not internally
    # contain single quote characters. Therefore, escape each single
    # quote character (') by replacing it with the sequence '"'"'. This
    # sequence is defied as:
    #   ' = terminate the original single quoted bash string
    #   " = start a new double quoted bash string
    #   ' = apply the single quite character
    #   " = terminate the new double quoted bash string
    #   ' = restart the original single quoted bash string
    # Note, the triple quotes below delineate the python string.
    volume_id = model.custom.iso_volume_id.replace("'", """'"'"'""")
    boot_image_directory = model.project.directory.replace("'", """'"'"'""")

    complete_template = template.format(volume_id=volume_id, boot_image_directory=boot_image_directory)
    iso_file_path = os.path.join(model.custom.iso_directory, model.custom.iso_file_name)
    command = ('xorriso '               \
               '-as mkisofs '           \
               '-r '                    \
               '-J '                    \
               '-joliet-long '          \
               '-l '                    \
               '-iso-level 3 '          \
               f'{complete_template} '  \
               f'-o "{iso_file_path}" .')

    return command


# ----------------------------------------------------------------------
# Calculate Disk Image Checksum Functions
# ----------------------------------------------------------------------


def calculate_checksum_for_iso():

    logger.log_label('Calculate checksum for ISO')

    model.status.iso_checksum, _ = file_utilities.calculate_md5_hash(model.custom.iso_file_name, model.custom.iso_directory)
    displayer.update_label('generate_page__calculate_iso_image_checksum_message', f'The checksum is {model.status.iso_checksum}.')
    time.sleep(SLEEP_0500_MS)

    model.status.iso_checksum_file_name = constructor.construct_custom_iso_checksum_file_name(model.custom.iso_file_name)
    try:
        file_path = os.path.join(model.custom.iso_directory, model.status.iso_checksum_file_name)
        file_utilities.write_line(f'{model.status.iso_checksum}  {model.custom.iso_file_name}', file_path)
    except InterruptException as exception:
        displayer.update_label(
            'generate_page__calculate_iso_image_checksum_message',
            f'Unable to save the checksum file {model.status.iso_checksum}.{os.linesep}The checksum file is {model.status.iso_checksum_file_name}.')
        displayer.update_status('generate_page__calculate_iso_image_checksum', displayer.ERROR)
        logger.log_value('Propagate exception', exception)
        raise exception
    except Exception as exception:
        displayer.update_label(
            'generate_page__calculate_iso_image_checksum_message',
            f'Unable to save the checksum file {model.status.iso_checksum}.{os.linesep}The checksum file is {model.status.iso_checksum_file_name}.')
        displayer.update_status('generate_page__calculate_iso_image_checksum', displayer.ERROR)
        logger.log_value('Do not propagate exception', exception)
        return True  # (Error)

    displayer.update_label(
        'generate_page__calculate_iso_image_checksum_message',
        f'The checksum is {model.status.iso_checksum}.{os.linesep}The checksum file is {model.status.iso_checksum_file_name}.')
    displayer.update_status('generate_page__calculate_iso_image_checksum', displayer.OK)
    return False  # (No error)
