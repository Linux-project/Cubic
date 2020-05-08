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

from constants import PERCENT_STOP
from utilities import configuration
from utilities import constructor
from utilities import displayer
from utilities import file_utilities
from utilities import iso_utilities
from utilities import logger
from utilities import model
from utilities.processor import execute_synchronous, terminate_process
from utilities.progress import show_progress

import datetime
import hashlib
import os
import re
from time import sleep

########################################################################
# Globals & Constants
########################################################################

name = 'generate_page'

# Move these to the constants module.
MAXIMUM_ISO_SIZE_GIB = 8000.0
MAXIMUM_ISO_SIZE_BYTES = MAXIMUM_ISO_SIZE_GIB * 1073741824.0

# TODO: These should not be global.
#       Fix show_progress()'s callback to take these as parameters.
total_files = 2
file_number = 0

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

        displayer.update_status('generate_page__update_filesystem_size', displayer.BULLET)
        displayer.update_label('generate_page__update_filesystem_size_message', '...')

        displayer.update_status('generate_page__update_disk_name', displayer.BULLET)
        displayer.update_label('generate_page__update_disk_name_message', '...')

        displayer.update_status('generate_page__update_checksums', displayer.BULLET)
        displayer.update_label('generate_page__update_checksums_message', '...')
        displayer.update_progress_bar_percent('generate_page__update_checksums_progress_bar', 0)
        displayer.update_progress_bar_text('generate_page__update_checksums_progress_bar', '')

        displayer.update_status('generate_page__check_iso_size', displayer.BULLET)
        displayer.update_label('generate_page__check_iso_size_message', '...')

        displayer.update_status('generate_page__create_iso_image', displayer.BULLET)
        displayer.update_progress_bar_percent('generate_page__create_iso_image_progress_bar', 0)
        displayer.update_progress_bar_text('generate_page__create_iso_image_progress_bar', '')

        displayer.update_status('generate_page__calculate_iso_image_checksum', displayer.BULLET)
        displayer.update_label('generate_page__calculate_iso_image_checksum_message', '...')

        return

    else:

        return 'unknown'


def enter(action, old_page=None):

    if action == 'generate':

        # TODO: Stop processing and return on error.

        #
        # Copy boot files.
        #

        displayer.update_status('generate_page__copy_boot_files', displayer.PROCESSING)
        sleep(0.50)
        is_error = copy_boot_files()
        if not is_error:
            displayer.update_status('generate_page__copy_boot_files', displayer.OK)
            add_message('\nSuccess.')
        else:
            displayer.update_status('generate_page__copy_boot_files', displayer.ERROR)
            add_message('\nError. Unable to copy all boot files.')
            return 'error'
        sleep(0.50)

        #
        # Create squashfs.
        #

        displayer.update_status('generate_page__create_squashfs', displayer.PROCESSING)
        sleep(0.50)
        is_error = create_squashfs()
        if not is_error:
            displayer.update_status('generate_page__create_squashfs', displayer.OK)
            displayer.update_label('generate_page__create_squashfs_message', 'Success.')
        else:
            displayer.update_status('generate_page__create_squashfs', displayer.ERROR)
            displayer.update_label('generate_page__create_squashfs_message', 'Error. Unable to create the compressed Linux file system.')
            return 'error'
        sleep(0.50)

        #
        # Update filesystem size.
        #

        displayer.update_status('generate_page__update_filesystem_size', displayer.PROCESSING)
        sleep(0.50)
        is_error = update_filesystem_size()
        # TODO: Update label for success and error "...message"
        if not is_error:
            displayer.update_status('generate_page__update_filesystem_size', displayer.OK)
        else:
            displayer.update_status('generate_page__update_filesystem_size', displayer.ERROR)
            return 'error'
        sleep(0.50)

        #
        # Update disk name and disk info.
        #

        displayer.update_status('generate_page__update_disk_name', displayer.PROCESSING)
        sleep(0.50)
        is_error = update_disk_name_and_disk_info()
        # TODO: Update label for success and error "...message"
        if not is_error:
            displayer.update_status('generate_page__update_disk_name', displayer.OK)
        else:
            displayer.update_status('generate_page__update_disk_name', displayer.ERROR)
            return 'error'
        sleep(0.50)

        #
        # Update MD5 sums.
        #

        displayer.update_status('generate_page__update_checksums', displayer.PROCESSING)
        sleep(0.50)
        is_error = update_checksums()
        # TODO: Update label for success and error "...message"
        if not is_error:
            displayer.update_status('generate_page__update_checksums', displayer.OK)
        else:
            displayer.update_status('generate_page__update_checksums', displayer.ERROR)
            return 'error'
        sleep(0.50)

        #
        # Check ISO size and create ISO image.
        #

        displayer.update_status('generate_page__check_iso_size', displayer.PROCESSING)
        sleep(0.50)
        is_error = check_iso_size()
        # TODO: Update label for success and error "...message"
        if not is_error:
            displayer.update_status('generate_page__check_iso_size', displayer.OK)
        else:
            displayer.update_status('generate_page__check_iso_size', displayer.ERROR)
            return 'error'
        sleep(0.50)

        #
        # Create ISO image.
        #

        displayer.update_status('generate_page__create_iso_image', displayer.PROCESSING)
        sleep(0.50)
        is_error = create_iso_image()
        if not is_error:
            displayer.update_status('generate_page__create_iso_image', displayer.OK)
            displayer.update_label('generate_page__create_iso_image_message', 'Success.')
        else:
            displayer.update_status('generate_page__create_iso_image', displayer.ERROR)
            displayer.update_label('generate_page__create_iso_image_message', 'Success.')
            return 'error'
        sleep(0.50)

        #
        # Calculate ISO image MD5 checksum.
        #

        displayer.update_status('generate_page__calculate_iso_image_checksum', displayer.PROCESSING)
        sleep(0.50)
        is_error = calculate_md5_hash_for_iso()
        # TODO: Update label for success and error "...message"
        if not is_error:
            displayer.update_status('generate_page__calculate_iso_image_checksum', displayer.OK)
        else:
            displayer.update_status('generate_page__calculate_iso_image_checksum', displayer.ERROR)
            return 'error'
        sleep(0.50)

        # TODO: Only activate the next button if no error.
        # TODO: Double check page validators on other pages to ensure
        #       the complex version of displayer.reset_buttons() is not used.
        displayer.reset_buttons(is_back_sensitive=True, is_next_sensitive=True)

        return

    else:

        return 'unknown'


def leave(action, new_page=None):

    if action == 'back':

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        configuration.save()

    elif action == 'finish':

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        # TODO: When the original ISO image is unmounted we leave the
        #       extract page, remove the following:
        if model.project.iso_mount_point:
            # Unmount the ISO image.
            if iso_utilities.is_mounted(model.project.iso_mount_point):
                iso_utilities.unmount(model.project.iso_mount_point)
            # Delete the mount point.
            file_utilities.delete_directory(model.project.iso_mount_point)

        configuration.save()

        return

    elif action == 'quit':

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        # TODO: When the original ISO image is unmounted we leave the
        #       extract page, remove the following:
        if model.project.iso_mount_point:
            # Unmount the ISO image.
            if iso_utilities.is_mounted(model.project.iso_mount_point):
                iso_utilities.unmount(model.project.iso_mount_point)
            # Delete the mount point.
            file_utilities.delete_directory(model.project.iso_mount_point)

        configuration.save()

        return

    else:

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

#-----------------------------------------------------------------------
# Repackage Functions
#-----------------------------------------------------------------------


# TODO: Improve this function name.
def add_message(message):

    displayer.insert_box_label('generate_page__copy_boot_files_box', message, 0.50)


# TODO: This function is in generate_page.py and options_page.py. Consider refactoring.
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
        directory = os.path.dirname(filepath)
        os.makedirs(directory, exist_ok=True)

        # Write the file.
        # TODO: Use try except block.
        with open(filepath, 'w') as file:
            file.write(data)
        # file.flush()

        sleep(0.50)

    is_error = False
    return is_error


def copy_boot_files():

    #
    # Preseed
    #

    is_error = False

    logger.log_label('Save preseed files')
    save_stack_buffers('options_page__preseed_tab__stack')

    # Delete preseed files.

    logger.log_label('Delete preseed files')
    for filepath in model.delete_list:
        try:
            logger.log_value('Delete file', filepath)
            # TODO: Make sure filepath is relative to project directory.
            add_message('Delete %s' % filepath)
            os.remove(filepath)
        except OSError as exception:
            is_error = True
            logger.log_value('Error deleting file', exception)
            add_message('Error deleting preseed file %s' % filepath)
        sleep(0.50)
    model.delete_list = []
    if is_error: return True

    #
    # ISO Boot Configurations
    #

    is_error = False

    sleep(0.50)
    logger.log_label('Save ISO boot configurations')
    is_error = save_stack_buffers('options_page__boot_configuration_tab__stack')
    if is_error: return True

    #
    # Vmlinuz & Initrd
    #

    #
    # Get selected kernel.
    #

    is_error = False

    sleep(0.50)

    logger.log_label('Update vmlinuz boot file.')
    # Get the selected kernel details.
    # 0: version_name
    # 1: vmlinuz_filename
    # 2: new_vmlinuz_filename
    # 3: initrd_filename
    # 4: new_initrd_filename
    # 5: directory
    # 6: note
    # 7: is_selected
    # 8: is_remove
    list_store = model.builder.get_object('options_page__linux_kernels_tab__list_store')
    for selected_index, kernel_details in enumerate(list_store):
        if kernel_details[7]:
            break
    else:
        selected_index = 0
    logger.log_value('The selected kernel is index number', selected_index)

    # Get selected directory.
    source_directory = list_store[selected_index][5]

    # Get target directory.
    target_directory = os.path.join(model.project.custom_disk_directory, model.status.casper_directory)

    #
    # Vmlinuz
    #

    logger.log_label('Update vmlinuz boot file.')
    source_filename = list_store[selected_index][1]
    source_filepath = os.path.join(source_directory, source_filename)
    target_filename = list_store[selected_index][2]
    target_filepath = os.path.join(target_directory, target_filename)
    add_message('Update /%s/%s' % (model.status.casper_directory, source_filename))
    # Delete existing vmlinuz* file(s) in target directory.
    pattern = os.path.join(target_directory, 'vmlinuz*')
    file_utilities.delete_files_with_pattern(pattern)
    # Copy new vmlinuz file.
    command = 'rsync --archive "%s" "%s"' % (source_filepath, target_filepath)
    # Rsync returns an exitstatus = 0 when successful.
    result, exitstatus, signalstatus = execute_synchronous(command)
    print('result=%s, exitstatus=%s, signalstatus=%s' % (result, exitstatus, signalstatus))
    if exitstatus:
        is_error = True
    sleep(0.50)
    if is_error: return True

    #
    # Initrd
    #

    logger.log_label('Update initrd boot file.')
    source_filename = list_store[selected_index][3]
    source_filepath = os.path.join(source_directory, source_filename)
    target_filename = list_store[selected_index][4]
    target_filepath = os.path.join(target_directory, target_filename)
    add_message('Update /%s/%s' % (model.status.casper_directory, source_filename))
    # Delete existing initrd* file in target directory
    pattern = os.path.join(target_directory, 'initrd*')
    file_utilities.delete_files_with_pattern(pattern)
    # Copy new initrd file.
    # Rsync returns an exitstatus = 0 when successful.
    command = 'rsync --archive "%s" "%s"' % (source_filepath, target_filepath)
    result, exitstatus, signalstatus = execute_synchronous(command)
    if exitstatus:
        is_error = True
    sleep(0.50)
    if is_error: return True

    return is_error


#
# Create relative links
#

# TODO: Make sure the following *relative* links are created:
#       - squashfs-root/initrd.img --> /boot/initrd.img-4.8.0-37-generic
#       - squashfs-root/vmlinuz    --> /boot/vmlinuz-4.8.0-37-generic
#       - Use the function: os.symlink(src, dst)


def create_squashfs():

    # return _create_squashfs_TESTING_2()
    # return _create_squashfs_TESTING_1()
    return _create_squashfs()


def _create_squashfs_TESTING_2():
    """
    This function copies the original filesystem.squashfs file.
    """

    logger.log_label('Create squashfs (Testing)')

    source_path = os.path.join(model.project.iso_mount_point, model.status.casper_directory, 'filesystem.squashfs')
    logger.log_value('The source path is', source_path)

    target_path = os.path.join(model.project.custom_disk_directory, model.status.casper_directory, 'filesystem.squashfs')
    logger.log_value('The target path is', target_path)

    # Copy the original filesystem.squashfs.
    file_utilities.copy_file(source_path, target_path)

    if os.path.exists(target_path):
        is_error = False
        logger.log_value('The file exists', target_path)
    else:
        logger.log_value('The file exists', target_path)
        is_error = True

    return is_error


def _create_squashfs_TESTING_1():
    """
    This function does nothing.
    """

    logger.log_label('Create squashfs (Testing)')

    source_path = model.project.custom_root_directory
    logger.log_value('The source path is', source_path)

    target_path = os.path.join(model.project.custom_disk_directory, model.status.casper_directory, 'filesystem.squashfs')
    logger.log_value('The target path is', target_path)

    is_error = False


def _create_squashfs():

    logger.log_label('Compress the Linux file system.')

    is_error = False

    source_path = model.project.custom_root_directory
    logger.log_value('The source path is', source_path)

    target_path = os.path.join(model.project.custom_disk_directory, model.status.casper_directory, 'filesystem.squashfs')
    logger.log_value('The target path is', target_path)

    # Create filesystem.squashfs.

    # Pkexec is required.
    program = os.path.join(model.application.directory, 'commands', 'compress-root')
    command = 'pkexec "%s" "%s" "%s"' % (program, source_path, target_path)

    # Show % in progress by setting text to None.
    displayer.update_progress_bar_text('generate_page__create_squashfs_progress_bar', None)

    # The progress callback function.
    def progress_callback(percent):
        displayer.update_progress_bar_percent('generate_page__create_squashfs_progress_bar', percent)
        if percent % 10 == 0:
            logger.log_value('• Completed', '%i%%' % percent)

    error = show_progress(command, progress_callback)

    is_error = bool(error)

    return is_error


def _create_squashfs_ORIGINAL():

    logger.log_label('Create squashfs')

    source_path = model.project.custom_root_directory
    logger.log_value('The source path is', source_path)

    target_path = os.path.join(model.project.custom_disk_directory, model.status.casper_directory, 'filesystem.squashfs')
    logger.log_value('The target path is', target_path)

    # https://catchchallenger.first-world.info/wiki/Quick_Benchmark:_Gzip_vs_Bzip2_vs_LZMA_vs_XZ_vs_LZ4_vs_LZO
    # Optionally use gzip (lower compression) or xz (higher compression).
    # Originally added etc/ssh/ssh_host*to resolve Bug #1824715.
    # Removed etc/ssh/ssh_host* due to Bug #1825566.
    command = (
        'mksquashfs "%s" "%s"'
        ' -noappend'
        # ' -comp xz'
        ' -comp gzip'
        ' -wildcards'
        ' -e "root/.bash_history"'
        ' -e "root/.cache"'
        ' -e "root/.wget-hsts"'
        ' -e "home/*/.bash_history"'
        ' -e "home/*/.cache"'
        ' -e "home/*/.wget-hsts"'
        ' -e "tmp/*"'
        ' -e "tmp/.*"' % (source_path,
                          target_path))

    # Show % in progress by setting text to None.
    displayer.update_progress_bar_text('generate_page__create_squashfs_progress_bar', None)

    def progress_callback(percent):
        displayer.update_progress_bar_percent('generate_page__create_squashfs_progress_bar', percent)
        if percent % 10 == 0:
            logger.log_value('• Completed', '%i%%' % percent)

    error = show_progress(command, progress_callback)

    is_error = bool(error)

    return is_error


def update_filesystem_size():

    logger.log_label('Update filesystem size')

    is_error = False

    # Pkexec is required.
    program = os.path.join(model.application.directory, 'commands', 'disk-usage')
    command = 'pkexec "%s" "%s"' % (program, model.project.custom_root_directory)
    result, exitstatus, signalstatus = execute_synchronous(command)

    if not exitstatus and not signalstatus:
        try:
            size_information = re.search(r'^([0-9]+)\s', result)
            size = int(size_information.group(1))
        except AttributeError as exception:
            is_error = True
            logger.log_value('1. Unable to get filesystem size for %s' % model.project.custom_root_directory, result)
            displayer.update_label('generate_page__update_filesystem_size_message', 'Error. Unable to get filesystem size.')
        except IndexError as exception:
            is_error = True
            logger.log_value('2. Unable to get filesystem size for %s' % model.project.custom_root_directory, result)
            displayer.update_label('generate_page__update_filesystem_size_message', 'Error. Unable to get filesystem size.')
        except TypeError as exception:
            is_error = True
            logger.log_value('3. Unable to get filesystem size for %s' % model.project.custom_root_directory, result)
            displayer.update_label('generate_page__update_filesystem_size_message', 'Error. Unable to get filesystem size.')
        else:
            logger.log_value('The file system size is', '%.2f GiB (%s bytes)' % ((size / 1073741824.0), size))
            if size > 0:
                filepath = os.path.join(model.project.custom_disk_directory, model.status.casper_directory, 'filesystem.size')
                logger.log_value('Write filesystem size to', filepath)
                # TODO: Use try for all write operations.
                try:
                    # TODO: Use try except block.
                    with open(filepath, 'w') as file:
                        file.write('%s' % size)
                    displayer.update_label('generate_page__update_filesystem_size_message', 'The file system size is %.2f GiB (%s bytes).' % ((size / 1073741824.0), size))
                    is_error = False
                except Exception as exception:
                    is_error = True
                    logger.log_value('Unable to write filesystem size due to exception', exception)
                    displayer.update_label('generate_page__update_filesystem_size_message', 'Error. Unable to save filesystem size, %.2f GiB (%s bytes).' % ((size / 1073741824.0), size))
            else:
                is_error = False
                logger.log_value('4. Unable to get filesystem size for %s' % model.project.custom_root_directory, result)
                displayer.update_label('generate_page__update_filesystem_size_message', 'Error. Unable to get filesystem size.')
    else:
        is_error = True
        logger.log_value('5. Unable to get filesystem size for %s' % model.project.custom_root_directory, result)
        displayer.update_label('generate_page__update_filesystem_size_message', 'Error. Unable to get filesystem size.')

    return is_error


def update_disk_name_and_disk_info():

    # TODO: Use if statements.
    update_disk_name()
    update_disk_info()


def update_disk_name():
    logger.log_label('Update disk name')

    error = False

    try:
        filepath = os.path.join(model.project.custom_disk_directory, 'README.diskdefines')
        search_text = r'^#define DISKNAME.*'
        replacement_text = '#define DISKNAME %s' % model.custom.iso_disk_name
        logger.log_value('Write disk name to', filepath)
        error = file_utilities.replace_text_in_file(filepath, search_text, replacement_text)
        logger.log_value('Updated the disk name', model.custom.iso_disk_name)
        displayer.update_label('generate_page__update_disk_name_message', model.custom.iso_disk_name)
    except Exception as exception:
        logger.log_value('Ignoring exception while updating disk name in README.diskdefines', exception)
        # TODO: display error
        error = True

    return error


# TODO: Consider moving this to ISO utilities?
def update_disk_info():
    logger.log_label('Update disk information')

    error = False

    try:
        filepath = os.path.join(model.project.custom_disk_directory, '.disk', 'info')
        current_time = datetime.datetime.now()
        formatted_time = '{:%Y%m%d}'.format(current_time)
        text = '%s (%s)' % (model.custom.iso_disk_name, formatted_time)
        logger.log_value('Write custom ISO image disk name and release date', text)
        logger.log_value('Write to', filepath)
        # TODO: Use try except block.
        with open(filepath, 'w') as file:
            file.write('%s' % text)
        # TODO: Correct the log message.
        logger.log_value('Updated the disk info', text)
        # displayer.update_label('generate_page__update_disk_name_message', 'Saved disk information to %s.' % filepath)
    except Exception as exception:
        logger.log_value('Ignoring exception while updating disk name in .disk/info', exception)
        # TODO: display error
        error = True

    return error


def calculate_md5_hash_for_file(filepath, blocksize=2**20):
    hash = hashlib.md5()
    # TODO: Use try except block.
    with open(filepath, 'rb') as file:
        while True:
            buffer = file.read(blocksize)
            if not buffer:
                break
            hash.update(buffer)
    return hash.hexdigest()


def update_checksums_WITHOUT_PROGRESS(checksums_filepath, start_directory, exclude_paths):
    logger.log_label('Update md5 sums')
    # TODO: Validate if we need realpath here?
    checksums_filepath = os.path.realpath(checksums_filepath)
    start_directory = os.path.realpath(start_directory)
    exclude_paths = [os.path.realpath(path) for path in exclude_paths]
    logger.log_value('Write md5 sums to', checksums_filepath)
    count = 0
    # TODO: Use try except block.
    with open(checksums_filepath, 'w') as file:
        for directory, directory_names, filenames in os.walk(start_directory):
            if directory not in exclude_paths:
                for filename in filenames:
                    filepath = os.path.join(directory, filename)
                    if (filepath not in exclude_paths):
                        count += 1
                        hash = calculate_md5_hash_for_file(filepath)
                        relative_filepath = os.path.relpath(filepath, start_directory)
                        file.write('%s  ./%s\n' % (hash, relative_filepath))
                        # logger.log_label('%s  ./%s' % (hash, relative_filepath))
    return count


# TODO: This doesn't use a pexpect process.
#       How do we kill/stop this when back, or quit are clicked?
#       Do we use a flag and/or break in all loops?
def update_checksums():

    logger.log_label('Update MD5 checksums')

    checksums_filepath = os.path.join(model.project.custom_disk_directory, 'md5sum.txt')
    start_directory = model.project.custom_disk_directory
    exclude_paths = [os.path.join(model.project.custom_disk_directory, 'isolinux'), checksums_filepath]

    # TODO: Validate if we need realpath here?
    # checksums_filepath = os.path.realpath(checksums_filepath)
    # start_directory = os.path.realpath(start_directory)
    # exclude_paths = [os.path.realpath(path) for path in exclude_paths]

    logger.log_value('Write MD5 checksums to', checksums_filepath)

    # Get filepaths.
    filepaths = []
    for directory, directory_names, filenames in os.walk(start_directory):
        if directory not in exclude_paths:
            for filename in filenames:
                filepath = os.path.join(directory, filename)
                if (filepath not in exclude_paths):
                    filepaths.append(filepath)
    filepaths.sort(key=lambda filepath: filepath.lower())

    # Calculate MD5 checksums and display progress.
    total_files = len(filepaths)

    # Show % in progress by setting text to None.
    displayer.update_progress_bar_text('generate_page__update_checksums_progress_bar', None)
    # TODO: This doesn't use a pexpect process.
    # TODO: Use try except block.
    with open(checksums_filepath, 'w') as file:
        for file_number, filepath in enumerate(filepaths, start=1):
            # displayer.update_label('generate_page__update_checksums_message', 'Calculating checksum for file %i of %i.' % (file_number, total_files))
            hash = calculate_md5_hash_for_file(filepath)
            relative_filepath = os.path.relpath(filepath, start_directory)
            file.write('%s  ./%s\n' % (hash, relative_filepath))
            displayer.update_progress_bar_percent('generate_page__update_checksums_progress_bar', 100 * file_number / total_files)
            displayer.update_progress_bar_text('generate_page__update_checksums_progress_bar', 'Calculating checksum for file %i of %i' % (file_number, total_files))
            sleep(0.0025)

    displayer.update_progress_bar_text('generate_page__update_checksums_progress_bar', '100%')
    displayer.update_label('generate_page__update_checksums_message', 'Calculated checksums for %i files.' % total_files)

    if not total_files:
        is_error = True
    else:
        is_error = False

    return is_error


def check_iso_size():

    directory_size_bytes = file_utilities.get_directory_size(model.project.custom_disk_directory)
    # TODO: How do we stop this loop when user clicks back or quit?
    #       This loop runs in another module.
    #       Perhaps we can use model.error as a loop control.
    #       Ex. if model.error return True (where error = True)
    #           if model.interrupt return True (where interrupt = True)
    # if error: return None
    directory_size_gib = directory_size_bytes / 1073741824.0
    logger.log_value('The total size of all files on the disk is', '%.2f GiB (%i bytes)' % (directory_size_gib, directory_size_bytes))
    logger.log_value('The maximum size limit for all files on the disk is', '%.2f GiB (%i bytes)' % (MAXIMUM_ISO_SIZE_GIB, MAXIMUM_ISO_SIZE_BYTES))
    # TODO: Add or improve log statments below.
    if directory_size_bytes > MAXIMUM_ISO_SIZE_BYTES:
        # Show directory size error message.
        displayer.update_status('generate_page__check_iso_size', displayer.ERROR)
        displayer.update_label(
            'generate_page__check_iso_size_message',
            'The total size of all files is %.2f GiB (%i bytes).' % (directory_size_gib,
                                                                     directory_size_bytes) + os.linesep + 'This is larger than the %.2f GiB (%i bytes) limit.' %
            (MAXIMUM_ISO_SIZE_GIB,
             MAXIMUM_ISO_SIZE_BYTES) + os.linesep + 'Click the Back button, and reduce the size of the Linux file system.')
        logger.log_value(displayer.ERROR, 'Disk size exceeds maximum')

        error = True
    else:
        # Show directory size.
        displayer.update_status('generate_page__check_iso_size', displayer.OK)
        displayer.update_label('generate_page__check_iso_size_message', 'The total size of all files is %.2f GiB (%i bytes).' % (directory_size_gib, directory_size_bytes))

        error = False

    return error


def create_iso_image():

    logger.log_label('Create ISO image')

    efi_image_filepath = os.path.join(model.project.custom_disk_directory, 'boot/grub/efi.img')
    custom_iso_filepath = os.path.join(model.custom.iso_directory, model.custom.iso_filename)

    # Bug #1623261
    # https://www.gnu.org/software/xorriso/man_1_xorrisofs.html
    # http://www.syslinux.org/wiki/index.php?title=Isohybrid
    if os.path.exists('/usr/lib/ISOLINUX/isohdpfx.bin'):
        # Ubuntu 15.04 uses isolinux (/usr/lib/ISOLINUX/isohdpfx.bin).
        logger.log_value('Use xorriso with isohybrid MBR', '/usr/lib/ISOLINUX/isohdpfx.bin')

        if os.path.exists(efi_image_filepath):
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
    elif os.path.exists('/usr/lib/syslinux/isohdpfx.bin'):
        # Ubuntu 14.04 uses syslinux-common (/usr/lib/syslinux/isohdpfx.bin).
        logger.log_value('Use xorriso with isohybrid MBR', '/usr/lib/syslinux/isohdpfx.bin')

        if os.path.exists(efi_image_filepath):
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

    def progress_callback(percent):
        displayer.update_progress_bar_percent('generate_page__create_iso_image_progress_bar', percent)
        if percent % 10 == 0:
            logger.log_value('• Completed', '%i%%' % percent)

    # Show % in progress by setting text to None.
    displayer.update_progress_bar_text('generate_page__create_iso_image_progress_bar', None)
    error = show_progress(command, progress_callback, working_directory=model.project.custom_disk_directory)

    is_error = bool(error)

    return is_error


def calculate_md5_hash_for_iso():
    logger.log_label('Calculate md5 sum')

    custom_iso_filepath = os.path.join(model.custom.iso_directory, model.custom.iso_filename)
    model.status.iso_checksum_filename = constructor.construct_custom_iso_checksum_filename(model.custom.iso_filename)
    custom_iso_checksum_filepath = os.path.join(model.custom.iso_directory, model.status.iso_checksum_filename)

    md5_sum = calculate_md5_hash_for_file(custom_iso_filepath)
    model.status.iso_checksum = md5_sum

    logger.log_value('Write ISO md5sum to', custom_iso_checksum_filepath)
    with open(custom_iso_checksum_filepath, 'w') as md5_sum_file:
        md5_sum_file.write('%s  %s' % (md5_sum, model.custom.iso_filename))

    # displayer.update_label('generate_page__calculate_iso_image_checksum_message', 'The checksum is %s.\nThe checksum file is %s.' % (model.status.iso_checksum, model.status.iso_checksum_filename))
    displayer.update_label('generate_page__calculate_iso_image_checksum_message', 'The checksum is %s.' % model.status.iso_checksum)
    sleep(0.50)
    displayer.update_label('generate_page__calculate_iso_image_checksum_message', 'The checksum is %s.\nThe checksum file is %s.' % (model.status.iso_checksum, model.status.iso_checksum_filename))

    return False
