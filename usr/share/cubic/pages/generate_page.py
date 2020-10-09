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

from datetime import datetime
from getpass import getuser
from os import linesep, listdir, makedirs, remove, symlink, walk
from os.path import dirname, exists, isfile, join, relpath
from re import search, sub
from time import sleep

from constants import MIB, GIB, MAXIMUM_DISK_SIZE_BYTES, MAXIMUM_DISK_SIZE_GIB
from utilities import configuration
from utilities import constructor
from utilities import displayer
from utilities import file_utilities
from utilities import iso_utilities
from utilities import logger
from utilities import model
from utilities.processor import execute_synchronous
from utilities.progressor import show_progress

########################################################################
# References
########################################################################

# N/A

########################################################################
# Globals & Constants
########################################################################

name = 'generate_page'

# Exist status 0 indicates the process completed successfully.
OK = 0

########################################################################
# Navigation Functions
########################################################################


def setup(action, old_page=None):

    if action == 'generate':

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

        displayer.update_status('generate_page__copy_boot_files', displayer.BULLET)
        displayer.empty_box('generate_page__copy_boot_files_box')

        displayer.update_status('generate_page__create_squashfs', displayer.BULLET)
        displayer.update_progress_bar_percent('generate_page__create_squashfs_progress_bar', 0)
        displayer.update_progress_bar_text('generate_page__create_squashfs_progress_bar', '')
        displayer.update_label('generate_page__create_squashfs_message', '...')

        displayer.update_status('generate_page__update_filesystem_size', displayer.BULLET)
        displayer.update_label('generate_page__update_filesystem_size_message', '...')

        displayer.update_status('generate_page__update_disk_name', displayer.BULLET)
        displayer.update_label('generate_page__update_disk_name_message', '...')

        displayer.update_status('generate_page__update_checksums', displayer.BULLET)
        displayer.update_progress_bar_percent('generate_page__update_checksums_progress_bar', 0)
        displayer.update_progress_bar_text('generate_page__update_checksums_progress_bar', '')
        displayer.update_label('generate_page__update_checksums_message', '...')

        displayer.update_status('generate_page__check_custom_disk_size', displayer.BULLET)
        displayer.update_label('generate_page__check_custom_disk_size_message', '...')

        displayer.update_status('generate_page__create_iso_image', displayer.BULLET)
        displayer.update_progress_bar_percent('generate_page__create_iso_image_progress_bar', 0)
        displayer.update_progress_bar_text('generate_page__create_iso_image_progress_bar', '')
        displayer.update_label('generate_page__create_iso_image_message', '...')

        displayer.update_status('generate_page__calculate_iso_image_checksum', displayer.BULLET)
        displayer.update_label('generate_page__calculate_iso_image_checksum_message', '...')

        return

    else:

        return 'unknown'


def enter(action, old_page=None):

    if action == 'generate':

        # --------------------------------------------------------------
        # Copy boot files.
        # --------------------------------------------------------------

        displayer.update_status('generate_page__copy_boot_files', displayer.PROCESSING)
        sleep(0.500)
        is_error = copy_preseed_and_boot_and_kernel_files()
        if is_error: return  # Stay on this page.
        sleep(0.500)

        # --------------------------------------------------------------
        # Create squashfs.
        # --------------------------------------------------------------

        displayer.update_status('generate_page__create_squashfs', displayer.PROCESSING)
        sleep(0.500)
        is_error = create_squashfs()
        if is_error: return  # Stay on this page.
        sleep(0.500)

        # --------------------------------------------------------------
        # Update file system size.
        # --------------------------------------------------------------

        displayer.update_status('generate_page__update_filesystem_size', displayer.PROCESSING)
        sleep(0.500)
        is_error = update_filesystem_size()
        if is_error: return  # Stay on this page.
        sleep(0.500)

        # --------------------------------------------------------------
        # Update disk name and disk info.
        # --------------------------------------------------------------

        displayer.update_status('generate_page__update_disk_name', displayer.PROCESSING)
        sleep(0.500)
        is_error = update_disk_name_and_disk_info()
        if is_error: return  # Stay on this page.
        sleep(0.500)

        # --------------------------------------------------------------
        # Update MD5 sums.
        # --------------------------------------------------------------

        displayer.update_status('generate_page__update_checksums', displayer.PROCESSING)
        sleep(0.500)
        is_error = update_checksums()
        if is_error: return  # Stay on this page.
        sleep(0.500)

        # --------------------------------------------------------------
        # Check ISO size.
        # --------------------------------------------------------------

        displayer.update_status('generate_page__check_custom_disk_size', displayer.PROCESSING)
        sleep(0.500)
        is_error = check_custom_directory_size()
        if is_error: return  # Stay on this page.
        sleep(0.500)

        # --------------------------------------------------------------
        # Create ISO image.
        # --------------------------------------------------------------

        displayer.update_status('generate_page__create_iso_image', displayer.PROCESSING)
        sleep(0.500)
        is_error = create_iso_image()
        if is_error: return  # Stay on this page.
        sleep(0.500)

        # --------------------------------------------------------------
        # Calculate ISO image MD5 checksum.
        # --------------------------------------------------------------

        displayer.update_status('generate_page__calculate_iso_image_checksum', displayer.PROCESSING)
        sleep(0.500)
        is_error = calculate_checksum_for_iso()
        if is_error: return  # Stay on this page.
        sleep(0.500)

        displayer.reset_buttons(is_back_sensitive=True, is_next_sensitive=True)

        return

    else:

        return 'unknown'


def leave(action, new_page=None):

    if action == 'back':

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        configuration.save()

        return

    elif action == 'error':

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        return

    elif action == 'finish':

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        iso_utilities.unmount_iso_and_delete_mount_point(model.project.iso_mount_point)

        configuration.save()

        return

    elif action == 'quit':

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        iso_utilities.unmount_iso_and_delete_mount_point(model.project.iso_mount_point)

        configuration.save()

        return

    else:

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        iso_utilities.unmount_iso_and_delete_mount_point(model.project.iso_mount_point)

        configuration.save()

        return 'unknown'

    return


########################################################################
# Handler Functions
########################################################################


def on_size_allocate__generate_page__copy_boot_files_view_port(widget, event, data=None):

    displayer.scroll_view_port_to_bottom('generate_page__copy_boot_files_view_port')


########################################################################
# Support Functions
########################################################################


# TODO: Improve this function name.
def add_message(message):

    displayer.insert_box_label('generate_page__copy_boot_files_box', message, 0.50)


# TODO: Add error checking to this function.
def save_stack_buffers(stack_name):

    stack = model.builder.get_object(stack_name)
    scrolled_windows = stack.get_children()

    for scrolled_window in scrolled_windows:

        filepath = stack.child_get_property(scrolled_window, 'name')
        title = stack.child_get_property(scrolled_window, 'title')

        logger.log_value('Write file', filepath)
        add_message('Save %s' % title)

        # Get the updated text.
        source_view = scrolled_window.get_child()
        source_buffer = source_view.get_buffer()
        start_iter = source_buffer.get_start_iter()
        end_iter = source_buffer.get_end_iter()
        data = source_buffer.get_text(start_iter, end_iter, True)

        # Create the parent directories (/preseed, /boot/grub, /isolinux, etc.)
        # if they do not exist.
        directory = dirname(filepath)
        makedirs(directory, exist_ok=True)

        # Write the file.
        # TODO: Use try for all write operations on all pages.
        with open(filepath, 'w') as file:
            file.write(data)
        # file.flush()

        sleep(0.500)

    is_error = False
    return is_error


#-----------------------------------------------------------------------
# Copy Boot Files Functions
#-----------------------------------------------------------------------


def copy_preseed_and_boot_and_kernel_files():
    """
    Copies the following files to the custom disk:
      1. Preseed
      2. ISO Boot Configurations
      3. Vmlinuz & Initrd
    """

    # ------------------------------------------------------------------
    # Preseed
    # ------------------------------------------------------------------

    sleep(0.500)

    # Delete preseed files.
    logger.log_label('Delete preseed files')
    is_error = False
    for filepath in model.delete_list:
        try:
            logger.log_value('Delete file', filepath)
            # TODO: Make sure filepath is relative to project directory.
            add_message('Delete %s' % filepath)
            remove(filepath)
        except OSError as exception:
            is_error = True
            logger.log_value('Error deleting file', exception)
            add_message('Error deleting preseed file %s' % filepath)
    model.delete_list = []
    if is_error:
        add_message('\nError. Unable to delete all preseed files.')
        displayer.update_status('generate_page__copy_boot_files', displayer.ERROR)
    # else:
    #     add_message('\nSuccess.')
    #     displayer.update_status('generate_page__copy_boot_files', displayer.OK)
    if is_error: return True

    # Save preseed files.
    logger.log_label('Save preseed files')
    is_error = False
    is_error = save_stack_buffers('options_page__preseed_tab__stack')
    if is_error:
        displayer.update_status('generate_page__copy_boot_files', displayer.ERROR)
        add_message('\nError. Unable to save all preseed files.')
    # else:
    #     add_message('\nSuccess.')
    #     displayer.update_status('generate_page__copy_boot_files', displayer.OK)
    if is_error: return True

    # ------------------------------------------------------------------
    # ISO Boot Configurations
    # ------------------------------------------------------------------

    sleep(0.500)

    logger.log_label('Save ISO boot configurations')
    is_error = save_stack_buffers('options_page__boot_configuration_tab__stack')
    if is_error:
        add_message('\nError. Unable save ISO boot configurations.')
        displayer.update_status('generate_page__copy_boot_files', displayer.ERROR)
    # else:
    #     add_message('\nSuccess.')
    #     displayer.update_status('generate_page__copy_boot_files', displayer.OK)
    if is_error: return True

    # ------------------------------------------------------------------
    # Vmlinuz & Initrd
    # ------------------------------------------------------------------

    sleep(0.500)

    logger.log_label('Identify the selected kernel.')

    # Get the selected kernel.

    # 0: version_name
    # 1: vmlinuz_filename
    # 2: new_vmlinuz_filename
    # 3: initrd_filename
    # 4: new_initrd_filename
    # 5: directory
    # 6: note
    # 7: is_selected

    list_store = model.builder.get_object('options_page__linux_kernels_tab__list_store')
    for selected_index, kernel_details in enumerate(list_store):
        if kernel_details[7]:
            break
    else:
        selected_index = 0
    logger.log_value('The selected kernel is index number', selected_index)

    # Get the selected directory.
    source_directory = list_store[selected_index][5]

    # Get the target directory.
    target_directory = join(model.project.custom_disk_directory, model.status.casper_directory)

    # ------------------------------------------------------------------
    # Vmlinuz
    # ------------------------------------------------------------------

    logger.log_label('Update the vmlinuz boot file.')

    source_filename = list_store[selected_index][1]
    source_filepath = join(source_directory, source_filename)
    target_filename = list_store[selected_index][2]
    target_filepath = join(target_directory, target_filename)
    user = getuser()

    add_message('Update /%s/%s' % (model.status.casper_directory, target_filename))

    # Delete existing vmlinuz* files in the target directory. Do not
    # remove a file if it matches the target file name, because it will
    # be efficiently updated by rsync.
    filepath_pattern = join(target_directory, 'vmlinuz*')
    file_utilities.delete_files_with_pattern(filepath_pattern, [target_filepath])

    # Copy the new vmlinuz file.
    program = join(model.application.directory, 'commands', 'copy-path')
    command = 'pkexec "%s" "%s" "%s" "%s"' % (program, source_filepath, target_filepath, user)
    result, exitstatus, signalstatus = execute_synchronous(command)
    logger.log_value('The result is', result)
    logger.log_value('The exit status, signal status is', '%s, %s' % (exitstatus, signalstatus))

    # Create a symlink from vmlinuz.eft to vmlinuz.
    source_filename = target_filename
    target_filename = 'vmlinuz.efi'
    target_filepath = join(target_directory, target_filename)
    if source_filename != target_filename and not exists(target_filepath):
        logger.log_value('Create symlink', 'from %s to %s' % (source_filename, target_filename))
        add_message('Create symlink %s to %s' % (target_filename, source_filename))
        symlink(source_filename, target_filepath)

    # TODO: Remove the following eight lines in a future release.
    #       As of version 2020.06-28, the copy-path command will not use
    #       temporary files, so this code is no longer needed.
    # Delete ephemeral .vmlinuz* files created by rsync in the target directory.
    filenames = listdir(target_directory)
    for filename in filenames:
        if filename.startswith('.vmlinuz'):
            filepath = join(target_directory, filename)
            if isfile(filepath): file_utilities.delete_path_as_root(filepath)

    is_error = (exitstatus is not OK or signalstatus)
    if is_error:
        add_message('\nError. Unable to update the vmlinuz boot file.')
        displayer.update_status('generate_page__copy_boot_files', displayer.ERROR)
    # else:
    #     add_message('\nSuccess.')
    #     displayer.update_status('generate_page__copy_boot_files', displayer.OK)
    if is_error: return True

    # ------------------------------------------------------------------
    # Initrd
    # ------------------------------------------------------------------

    logger.log_label('Update the initrd boot file.')

    source_filename = list_store[selected_index][3]
    source_filepath = join(source_directory, source_filename)
    target_filename = list_store[selected_index][4]
    target_filepath = join(target_directory, target_filename)
    user = getuser()

    add_message('Update /%s/%s' % (model.status.casper_directory, target_filename))

    # Delete existing initrd* files in the target directory. Do not
    # remove a file if it matches the target file name, because it will
    # be efficiently updated by rsync.
    filepath_pattern = join(target_directory, 'initrd*')
    file_utilities.delete_files_with_pattern(filepath_pattern, [target_filepath])

    # Copy the new initrd file.
    program = join(model.application.directory, 'commands', 'copy-path')
    command = 'pkexec "%s" "%s" "%s" "%s"' % (program, source_filepath, target_filepath, user)
    result, exitstatus, signalstatus = execute_synchronous(command)
    logger.log_value('The result is', result)
    logger.log_value('The exit status, signal status is', '%s, %s' % (exitstatus, signalstatus))

    # TODO: Remove the following eight lines in a future release.
    #       As of version 2020.06-28, the copy-path command will not use
    #       temporary files, so this code is no longer needed.
    # Delete ephemeral .initrd* files created by rsync in the target directory.
    filenames = listdir(target_directory)
    for filename in filenames:
        if filename.startswith('.initrd'):
            filepath = join(target_directory, filename)
            if isfile(filepath): file_utilities.delete_path_as_root(filepath)

    is_error = (exitstatus is not OK or signalstatus)
    if is_error:
        add_message('\nError. Unable to update the initrd boot file.')
        displayer.update_status('generate_page__copy_boot_files', displayer.ERROR)
    # else:
    #     add_message('\nSuccess.')
    #     displayer.update_status('generate_page__copy_boot_files', displayer.OK)
    if is_error: return True

    add_message('\nSuccess.')
    displayer.update_status('generate_page__copy_boot_files', displayer.OK)

    return is_error


#-----------------------------------------------------------------------
# Create Squashfs Functions
#-----------------------------------------------------------------------


def create_squashfs():

    # return _create_squashfs_TESTING_2()
    # return _create_squashfs_TESTING_1()
    return _create_squashfs()


def _create_squashfs():

    logger.log_label('Compress the Linux file system.')

    source_path = model.project.custom_root_directory
    logger.log_value('The source path is', source_path)

    target_path = join(model.project.custom_disk_directory, model.status.casper_directory, 'filesystem.squashfs')
    logger.log_value('The target path is', target_path)

    displayer.update_label('generate_page__create_squashfs_message', 'Using %s compression.' % model.options.compression)

    # Create filesystem.squashfs.

    # Pkexec is required.
    program = join(model.application.directory, 'commands', 'compress-root')
    command = 'pkexec "%s" "%s" "%s" %s' % (program, source_path, target_path, model.options.compression)

    # Show % in progress by setting text to None.
    # displayer.update_progress_bar_text('generate_page__create_squashfs_progress_bar', None)
    displayer.update_progress_bar_text('generate_page__create_squashfs_progress_bar', '0.0 %')

    # The progress callback function.
    def progress_callback(percent):
        displayer.update_progress_bar_text('generate_page__create_squashfs_progress_bar', '%.1f %%' % float(percent))
        displayer.update_progress_bar_percent('generate_page__create_squashfs_progress_bar', percent)
        if percent % 10 == 0:
            logger.log_value('Completed', '%i%%' % percent)

    exception, message = show_progress(command, progress_callback)

    is_error = bool(exception)
    if is_error:
        if 'No space left on device' in message:
            displayer.update_label('generate_page__create_squashfs_message', 'Error. Not enough space on the disk.')
        else:
            displayer.update_label('generate_page__create_squashfs_message', 'Error. Unable to create the compressed Linux file system.')
        displayer.update_status('generate_page__create_squashfs', displayer.ERROR)
    else:
        displayer.update_label('generate_page__create_squashfs_message', 'Success.')
        displayer.update_status('generate_page__create_squashfs', displayer.OK)
    return is_error


def _create_squashfs_TESTING_1():
    """
    This function does nothing.
    """

    logger.log_label('Create squashfs (Testing)')

    source_path = model.project.custom_root_directory
    logger.log_value('The source path is', source_path)

    target_path = join(model.project.custom_disk_directory, model.status.casper_directory, 'filesystem.squashfs')
    logger.log_value('The target path is', target_path)

    is_error = False

    displayer.update_label('generate_page__create_squashfs_message', 'Testing.')
    displayer.update_status('generate_page__create_squashfs', displayer.OK)

    is_error = is_error


def _create_squashfs_TESTING_2():
    """
    This function copies the original filesystem.squashfs file.
    """

    logger.log_label('Create squashfs (Testing)')

    source_path = join(model.project.iso_mount_point, model.status.casper_directory, 'filesystem.squashfs')
    logger.log_value('The source path is', source_path)

    target_path = join(model.project.custom_disk_directory, model.status.casper_directory, 'filesystem.squashfs')
    logger.log_value('The target path is', target_path)

    # Copy the original filesystem.squashfs.
    file_utilities.copy_file(source_path, target_path)

    is_error = exists(target_path)
    if is_error:
        displayer.update_label('generate_page__create_squashfs_message', 'Testing. Error. filesystem.squashfs already exists.')
        displayer.update_status('generate_page__create_squashfs', displayer.ERROR)
    else:
        displayer.update_label('generate_page__create_squashfs_message', 'Testing.')
        displayer.update_status('generate_page__create_squashfs', displayer.OK)

    return is_error


#-----------------------------------------------------------------------
# Update File System Size Functions
#-----------------------------------------------------------------------


def update_filesystem_size():

    logger.log_label('Update the file system size')

    try:
        # Pkexec is required.
        program = join(model.application.directory, 'commands', 'file-size')
        command = 'pkexec "%s" "%s"' % (program, model.project.custom_root_directory)
        result, exitstatus, signalstatus = execute_synchronous(command)
        size_information = search(r'^([0-9]+)\s', result)
        size_in_bytes = int(size_information.group(1))
        size_in_mib = size_in_bytes / MIB
        size_in_gib = size_in_bytes / GIB
        logger.log_value('The file system size is', '%.2f GiB (%s bytes)' % (size_in_gib, size_in_bytes))
        filepath = join(model.project.custom_disk_directory, model.status.casper_directory, 'filesystem.size')
        logger.log_value('Write file system size to', filepath)
        with open(filepath, 'w') as file:
            file.write('%s' % size_in_bytes)
    except Exception as exception:
        logger.log_value('Unable to get file system size for %s' % model.project.custom_root_directory, result)
        logger.log_value('The exception is', exception)
        displayer.update_label('generate_page__update_filesystem_size_message', 'Error. Unable to get file system size.')
        displayer.update_status('generate_page__update_filesystem_size', displayer.ERROR)
        is_error = True
    else:
        if size_in_bytes > GIB:
            displayer.update_label('generate_page__update_filesystem_size_message', 'The file system size is %.2f GiB (%s bytes).' % (size_in_gib, size_in_bytes))
        else:
            displayer.update_label('generate_page__update_filesystem_size_message', 'The file system size is %.2f MiB (%s bytes).' % (size_in_mib, size_in_bytes))
        displayer.update_status('generate_page__update_filesystem_size', displayer.OK)
        is_error = False
    return is_error


#-----------------------------------------------------------------------
# Update Disk Name and Disk Info Functions
#-----------------------------------------------------------------------


def update_disk_name_and_disk_info():

    is_error = update_disk_name()
    if is_error:
        logger.log_value('Unable to update the disk name to', model.custom.iso_disk_name)
        displayer.update_label('generate_page__update_disk_name_message', 'Error. Unable to update the disk name.')
        displayer.update_status('generate_page__update_disk_name', displayer.ERROR)
        return True

    is_error = update_disk_info()
    if is_error:
        logger.log_value('Unable to update the disk name to', model.custom.iso_disk_name)
        displayer.update_label('generate_page__update_disk_name_message', 'Error. Unable to update the disk name.')
        displayer.update_status('generate_page__update_disk_name', displayer.ERROR)
        return True

    displayer.update_label('generate_page__update_disk_name_message', 'Success.')
    displayer.update_status('generate_page__update_disk_name', displayer.OK)

    return False


def update_disk_name():

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

    logger.log_label('Update the disk name')

    try:

        filepath = join(model.project.custom_disk_directory, 'README.diskdefines')

        if isfile(filepath):
            logger.log_value('Update the existing file', filepath)
            mode = 'r+'
        else:
            logger.log_value('Create a new file', filepath)
            mode = 'w+'

        with open(filepath, mode) as file:

            file_contents = file.read()

            # Update disk name.
            search_text = r'#define DISKNAME.*'
            replacement_text = '#define DISKNAME %s' % model.custom.iso_disk_name
            if search(search_text, file_contents):
                logger.log_value('Update disk name', replacement_text)
                file_contents = sub(search_text, replacement_text, file_contents)
            else:
                logger.log_value('Append disk name', replacement_text)
                if not file_contents:
                    file_contents = replacement_text
                elif file_contents[-1] == '\n':
                    file_contents = file_contents + replacement_text
                else:
                    file_contents = file_contents + '\n' + replacement_text

            # Update cubic information.
            search_text = r'#define CUBIC_INFO.*'
            display_version = constructor.get_major_minor_version(model.application.cubic_version)
            date_time = datetime.now().strftime('%d/%m/%Y %I:%M %p')
            replacement_text = '#define CUBIC_INFO Generated using Cubic version %s on %s based on %s' % (display_version, date_time, model.original.iso_filename)
            if search(search_text, file_contents):
                logger.log_value('Update cubic information', replacement_text)
                file_contents = sub(search_text, replacement_text, file_contents)
            else:
                logger.log_value('Append cubic information', replacement_text)
                if not file_contents:
                    file_contents = replacement_text
                elif file_contents[-1] == '\n':
                    file_contents = file_contents + replacement_text
                else:
                    file_contents = file_contents + '\n' + replacement_text

            # Update file.
            file.seek(0)
            file.truncate()
            file.write(file_contents)

    except IOError as exception:
        logger.log_value('Unable to update the disk information in', filepath)
        logger.log_value('The exception is', exception)
        is_error = True

    except Exception as exception:
        logger.log_value('Unable to update the disk information in', filepath)
        logger.log_value('The exception is', exception)
        is_error = True

    else:
        is_error = False

    return is_error


def update_disk_info():

    logger.log_label('Update the disk information')

    try:
        filepath = join(model.project.custom_disk_directory, '.disk', 'info')
        current_time = datetime.now()
        formatted_time = '{:%Y%m%d}'.format(current_time)
        text = '%s (%s)' % (model.custom.iso_disk_name, formatted_time)
        logger.log_value('The custom ISO image disk name and release date are', text)
        logger.log_value('Write disk information to %s.', filepath)
        with open(filepath, 'w') as file:
            file.write('%s' % text)
    except Exception as exception:
        logger.log_value('Unable to update the disk information in', filepath)
        logger.log_value('The exception is', exception)
        is_error = True
    else:
        is_error = False

    return is_error


#-----------------------------------------------------------------------
# Update Checksums Functions
#-----------------------------------------------------------------------


# TODO: This doesn't use a pexpect process.
#       How do we kill/stop this when back, or quit are clicked?
#       Do we use a flag and/or break in all loops?
def update_checksums():

    logger.log_label('Update checksums')

    # Show % in progress by setting text to None.
    displayer.update_progress_bar_text('generate_page__update_checksums_progress_bar', None)

    checksums_filepath = join(model.project.custom_disk_directory, 'md5sum.txt')
    start_directory = model.project.custom_disk_directory
    exclude_paths = [join(model.project.custom_disk_directory, 'isolinux'), checksums_filepath]

    # TODO: Validate if we need realpath here?
    # checksums_filepath = realpath(checksums_filepath)
    # start_directory = realpath(start_directory)
    # exclude_paths = [realpath(path) for path in exclude_paths]

    logger.log_value('Write MD5 checksums to', checksums_filepath)

    # Get filepaths.

    filepaths = []
    for directory, directory_names, filenames in walk(start_directory):
        if directory not in exclude_paths:
            for filename in filenames:
                filepath = join(directory, filename)
                if filepath not in exclude_paths:
                    filepaths.append(filepath)
    filepaths.sort(key=lambda filepath: filepath.lower())

    # Calculate MD5 checksums and display progress.

    total_files = len(filepaths)
    if total_files == 0:
        logger.log_value('Unable to update checksums. No files found in', checksums_filepath)
        displayer.update_label('generate_page__update_checksums_message', 'Error. Unable to calculate checksums.')
        displayer.update_status('generate_page__update_checksums', displayer.ERROR)
        return True

    try:
        with open(checksums_filepath, 'w') as file:
            for file_number, filepath in enumerate(filepaths, start=1):
                # displayer.update_label('generate_page__update_checksums_message', 'Calculating checksum for file %i of %i.' % (file_number, total_files))
                checksum = file_utilities.calculate_md5_hash(filepath)
                relative_filepath = relpath(filepath, start_directory)
                file.write('%s  ./%s\n' % (checksum, relative_filepath))
                displayer.update_progress_bar_percent('generate_page__update_checksums_progress_bar', 100 * file_number / total_files)
                displayer.update_progress_bar_text('generate_page__update_checksums_progress_bar', 'Calculating checksum for file %i of %i' % (file_number, total_files))

    except Exception as exception:
        logger.log_value('Unable to update checksums', checksums_filepath)
        logger.log_value('The exception is', exception)
        if 'No space left on device' in str(exception):
            displayer.update_label('generate_page__update_checksums_message', 'Error. Not enough space on the disk.')
        else:
            displayer.update_label('generate_page__update_checksums_message', 'Error. Unable to calculate checksums.')
        displayer.update_status('generate_page__update_checksums', displayer.ERROR)
        return True

    else:
        logger.log_value('Calculated checksums for', '%i files' % total_files)
        displayer.update_progress_bar_text('generate_page__update_checksums_progress_bar', '100%')
        displayer.update_label('generate_page__update_checksums_message', 'Calculated checksums for %i files.' % total_files)
        displayer.update_status('generate_page__update_checksums', displayer.OK)
        return False


#-----------------------------------------------------------------------
# Check ISO Size Functions
#-----------------------------------------------------------------------


def check_custom_directory_size():

    logger.log_label('Get the custom disk size')

    try:
        # Pkexec is not required.
        program = join(model.application.directory, 'commands', 'file-size')
        command = 'pkexec "%s" "%s"' % (program, model.project.custom_disk_directory)
        result, exitstatus, signalstatus = execute_synchronous(command)
        size_information = search(r'^([0-9]+)\s', result)
        size_in_bytes = int(size_information.group(1))
        size_in_mib = size_in_bytes / MIB
        size_in_gib = size_in_bytes / GIB
    except Exception as exception:
        logger.log_value('Unable to get the total size', model.project.custom_disk_directory)
        logger.log_value('The exception is', exception)
        displayer.update_label('generate_page__check_custom_disk_size_message', 'Error. Unable to get the total size.')
        displayer.update_status('generate_page__check_custom_disk_size', displayer.ERROR)
        is_error = True
    else:
        logger.log_value('The total size is', '%.2f GiB (%i bytes)' % (size_in_gib, size_in_bytes))
        logger.log_value('The maximum size limit for all files on the disk is', '%.2f GiB (%i bytes)' % (MAXIMUM_DISK_SIZE_GIB, MAXIMUM_DISK_SIZE_BYTES))
        if size_in_bytes > MAXIMUM_DISK_SIZE_BYTES:
            logger.log_value('Error', 'The total size exceeds the maximum size')
            displayer.update_label(
                'generate_page__check_custom_disk_size_message',
                'The the custom disk directory size is %.2f GiB (%s bytes).' % (size_in_gib,
                                                                                size_in_bytes) + linesep + 'This is larger than the %.2f GiB (%i bytes) limit.' %
                (MAXIMUM_DISK_SIZE_GIB,
                 MAXIMUM_DISK_SIZE_BYTES) + linesep + 'Click the Back button, and reduce the size of the Linux file system.')
            displayer.update_status('generate_page__check_custom_disk_size', displayer.ERROR)
            is_error = True
        else:
            if size_in_bytes > GIB:
                displayer.update_label('generate_page__check_custom_disk_size_message', 'The total size of all files is %.2f GiB (%s bytes).' % (size_in_gib, size_in_bytes))
            else:
                displayer.update_label('generate_page__check_custom_disk_size_message', 'The total size of all files is %.2f MiB (%s bytes).' % (size_in_mib, size_in_bytes))
            displayer.update_status('generate_page__check_custom_disk_size', displayer.OK)
            is_error = False
    return is_error


#-----------------------------------------------------------------------
# Create ISO Image Functions
#-----------------------------------------------------------------------


def create_iso_image():

    logger.log_label('Create ISO image')

    efi_image_filepath = join(model.project.custom_disk_directory, 'boot/grub/efi.img')
    custom_iso_filepath = join(model.custom.iso_directory, model.custom.iso_filename)

    # Bug #1623261
    # https://www.gnu.org/software/xorriso/man_1_xorrisofs.html
    # http://www.syslinux.org/wiki/index.php?title=Isohybrid
    if exists('/usr/lib/ISOLINUX/isohdpfx.bin'):
        # Ubuntu 15.04 uses isolinux (/usr/lib/ISOLINUX/isohdpfx.bin).
        logger.log_value('Use xorriso with isohybrid MBR', '/usr/lib/ISOLINUX/isohdpfx.bin')

        if exists(efi_image_filepath):
            command = (
                'xorriso'
                ' -as mkisofs -r -V "%s" -cache-inodes -J -l'
                ' -iso-level 3'
                ' -isohybrid-mbr /usr/lib/ISOLINUX/isohdpfx.bin'
                ' -c isolinux/boot.cat'
                ' -b isolinux/isolinux.bin'
                '  -no-emul-boot'
                '  -boot-load-size 4'
                '  -boot-info-table'
                ' -eltorito-alt-boot'
                '  -e boot/grub/efi.img'
                '  -no-emul-boot'
                '  -isohybrid-gpt-basdat'
                ' -o "%s" .' % (model.custom.iso_volume_id,
                                custom_iso_filepath))
        else:
            command = (
                'xorriso'
                ' -as mkisofs -r -V "%s" -cache-inodes -J -l'
                ' -iso-level 3'
                ' -isohybrid-mbr /usr/lib/ISOLINUX/isohdpfx.bin'
                ' -c isolinux/boot.cat'
                ' -b isolinux/isolinux.bin'
                '  -no-emul-boot'
                '  -boot-load-size 4'
                '  -boot-info-table'
                ' -o "%s" .' % (model.custom.iso_volume_id,
                                custom_iso_filepath))
    elif exists('/usr/lib/syslinux/isohdpfx.bin'):
        # Ubuntu 14.04 uses syslinux-common (/usr/lib/syslinux/isohdpfx.bin).
        logger.log_value('Use xorriso with isohybrid MBR', '/usr/lib/syslinux/isohdpfx.bin')

        if exists(efi_image_filepath):
            command = (
                'xorriso'
                ' -as mkisofs -r -V "%s" -cache-inodes -J -l'
                ' -iso-level 3'
                ' -isohybrid-mbr /usr/lib/syslinux/isohdpfx.bin'
                ' -c isolinux/boot.cat'
                ' -b isolinux/isolinux.bin'
                '  -no-emul-boot'
                '  -boot-load-size 4'
                '  -boot-info-table'
                ' -eltorito-alt-boot'
                '  -e boot/grub/efi.img'
                '  -no-emul-boot'
                '  -isohybrid-gpt-basdat'
                ' -o "%s" .' % (model.custom.iso_volume_id,
                                custom_iso_filepath))
        else:
            command = (
                'xorriso'
                ' -as mkisofs -r -V "%s" -cache-inodes -J -l'
                ' -iso-level 3'
                ' -isohybrid-mbr /usr/lib/syslinux/isohdpfx.bin'
                ' -c isolinux/boot.cat'
                ' -b isolinux/isolinux.bin'
                '  -no-emul-boot'
                '  -boot-load-size 4'
                '  -boot-info-table'
                ' -o "%s" .' % (model.custom.iso_volume_id,
                                custom_iso_filepath))
    else:
        logger.log_value('Use mkisofs', 'No isohybrid MBR available.')
        command = (
            'mkisofs -r -V "%s" -cache-inodes -J -l'
            ' -iso-level 3'
            ' -c isolinux/boot.cat'
            ' -b isolinux/isolinux.bin'
            '  -no-emul-boot'
            '  -boot-load-size 4'
            '  -boot-info-table'
            ' -o "%s" .' % (model.custom.iso_volume_id,
                            custom_iso_filepath))

    # Show % in progress by setting text to None.
    # displayer.update_progress_bar_text('generate_page__create_iso_image_progress_bar', None)
    displayer.update_progress_bar_text('generate_page__create_iso_image_progress_bar', '0.0 %')

    # The progress callback function.
    def progress_callback(percent):
        displayer.update_progress_bar_percent('generate_page__create_iso_image_progress_bar', percent)
        displayer.update_progress_bar_text('generate_page__create_iso_image_progress_bar', '%.1f %%' % float(percent))
        if percent % 10 == 0:
            logger.log_value('Completed', '%i%%' % percent)

    exception, message = show_progress(command, progress_callback, working_directory=model.project.custom_disk_directory)

    is_error = bool(exception)
    if is_error:
        if 'exceeds free space on media' in message:
            displayer.update_label('generate_page__create_iso_image_message', 'Error. Not enough space on the disk.')
        else:
            displayer.update_label('generate_page__create_iso_image_message', 'Error. Unable to create the customized disk image.')
        displayer.update_status('generate_page__create_iso_image', displayer.ERROR)
        return True
    # else:
    #     displayer.update_label('generate_page__create_iso_image_message', 'Success.')
    #     displayer.update_status('generate_page__create_iso_image', displayer.OK)

    #
    # Get the size.
    #

    logger.log_label('Get the custom disk size')

    try:
        # Pkexec is not required.
        program = join(model.application.directory, 'commands', 'file-size')
        command = 'pkexec "%s" "%s"' % (program, custom_iso_filepath)
        result, exitstatus, signalstatus = execute_synchronous(command)
        size_information = search(r'^([0-9]+)\s', result)
        size_in_bytes = int(size_information.group(1))
        size_in_mib = size_in_bytes / MIB
        size_in_gib = size_in_bytes / GIB
    except Exception as exception:
        logger.log_value('Unable to get the size of the custom ISO', custom_iso_filepath)
        logger.log_value('The exception is', exception)
        displayer.update_label('generate_page__create_iso_image_message', 'Error. Unable to get the size of the custom ISO.')
        displayer.update_status('generate_page__create_iso_image', displayer.ERROR)
        is_error = True
    else:
        if size_in_bytes > GIB:
            logger.log_value('The size of the custom ISO is', '%.2f MiB (%i bytes)' % (size_in_gib, size_in_bytes))
            displayer.update_label('generate_page__create_iso_image_message', 'Successfully created the %.2f GiB disk image,\n%s.' % (size_in_gib, model.custom.iso_filename))
        else:
            logger.log_value('The size of the custom ISO is', '%.2f MiB (%i bytes)' % (size_in_mib, size_in_bytes))
            displayer.update_label('generate_page__create_iso_image_message', 'Successfully created the %.2f MiB disk image,\n%s.' % (size_in_mib, model.custom.iso_filename))
        displayer.update_status('generate_page__create_iso_image', displayer.OK)
        is_error = False

    return is_error


#-----------------------------------------------------------------------
# Calculate ISO Image MDS Checksum Functions
#-----------------------------------------------------------------------


def calculate_checksum_for_iso():

    logger.log_label('Calculate checksum for iso')

    custom_iso_filepath = join(model.custom.iso_directory, model.custom.iso_filename)

    model.status.iso_checksum_filename = constructor.construct_custom_iso_checksum_filename(model.custom.iso_filename)
    custom_iso_checksum_filepath = join(model.custom.iso_directory, model.status.iso_checksum_filename)

    checksum = file_utilities.calculate_md5_hash(custom_iso_filepath)
    model.status.iso_checksum = checksum

    displayer.update_label('generate_page__calculate_iso_image_checksum_message', 'The checksum is %s.' % model.status.iso_checksum)
    sleep(0.500)

    try:
        logger.log_value('Write checksum for iso to', custom_iso_checksum_filepath)
        with open(custom_iso_checksum_filepath, 'w') as file:
            file.write('%s  %s' % (checksum, model.custom.iso_filename))
    except:
        displayer.update_label(
            'generate_page__calculate_iso_image_checksum_message',
            'Unable to save the checksum file %s.\nThe checksum file is %s.' % (model.status.iso_checksum,
                                                                                model.status.iso_checksum_filename))
        displayer.update_status('generate_page__calculate_iso_image_checksum', displayer.ERROR)
        is_error = True
    else:
        displayer.update_label('generate_page__calculate_iso_image_checksum_message', 'The checksum is %s.\nThe checksum file is %s.' % (model.status.iso_checksum, model.status.iso_checksum_filename))
        displayer.update_status('generate_page__calculate_iso_image_checksum', displayer.OK)
        is_error = False

    return is_error
