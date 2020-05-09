#!/usr/bin/python3

########################################################################
#                                                                      #
# extract_page.py                                                      #
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

from utilities import configuration
from utilities import displayer
from utilities import file_utilities
from utilities import iso_utilities
from utilities import logger
from utilities import model
from utilities.processor import terminate_process
from utilities.progress import show_progress

import os
from time import sleep

########################################################################
# Globals & Constants
########################################################################

name = 'extract_page'

is_page_valid = False

########################################################################
# Navigation Functions
########################################################################


def setup(action, old_page=None):

    if action == 'next':

        displayer.reset_buttons(
            back_button_label='❬Back',
            back_action='back',
            back_button_style=None,
            is_back_sensitive=True,
            is_back_visible=True,
            next_button_label='Customize❭',
            next_action='next',
            next_button_style='suggested-action',
            is_next_sensitive=False,
            is_next_visible=True)

        # Setup the "Identify Casper Directory" section.

        displayer.set_visible('extract_page__casper_directory_section', not model.status.casper_directory)
        displayer.update_label('extract_page__casper_directory_message', '')
        displayer.update_status('extract_page__casper_directory', displayer.BULLET)

        # Setup the "Extract Linux File System" section.

        displayer.set_visible('extract_page__unsquashfs_section', not model.status.is_success_extract)
        displayer.update_progress_bar_percent('extract_page__unsquashfs_progress_bar', 0)
        # displayer.update_progress_bar_text('extract_page__unsquashfs_progress_bar', None)
        displayer.update_label('extract_page__unsquashfs_message', '')
        displayer.update_status('extract_page__unsquashfs', displayer.BULLET)

        # Setup the "Copy Original ISO Files" section.

        displayer.set_visible('extract_page__copy_original_iso_files_section', not model.status.is_success_copy)
        displayer.update_progress_bar_percent('extract_page__copy_original_iso_files_progress_bar', 0)
        # displayer.update_progress_bar_text('extract_page__copy_original_iso_files_progress_bar', None)
        displayer.update_label('extract_page__copy_original_iso_files_message', '')
        displayer.update_status('extract_page__copy_original_iso_files', displayer.BULLET)

        return

    else:

        return 'unknown'


def enter(action, old_page=None):

    if action == 'next':

        # Determine casper relative directory
        if not model.status.casper_directory:
            error = identify_casper_relative_directory()
            # Pause to allow the user to see the result.
            sleep(1.00)
            if error: return 'error'

        # Extract the Linux file system.
        if not model.status.is_success_extract:
            error = extract_squashfs()
            # Pause to allow the user to see the result.
            sleep(1.00)
            if error: return 'error'

        # Copy original ISO files.
        if not model.status.is_success_copy:
            error = copy_original_iso_files()
            # Pause to allow the user to see the result.
            sleep(1.00)
            if error: return 'error'

        return 'next'

    else:

        return 'unknown'


def leave(action, new_page=None):

    if action == 'back':

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        configuration.save()

        return

    elif action == 'next':

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        configuration.save()

        return

    elif action == 'quit':

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        iso_utilities.unmount_iso_and_delete_mount_point(model.project.iso_mount_point)

        configuration.save()

        return

    else:

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        configuration.save()

        return 'unknown'


########################################################################
# Handler Functions
########################################################################

# N/A

########################################################################
# Support Functions
########################################################################

#-----------------------------------------------------------------------
# Identify the Casper Directory Functions
#-----------------------------------------------------------------------

# TODO: Add log statements.


def identify_casper_relative_directory():

    logger.log_label('Find the compressed Linux file system.')

    displayer.update_status('extract_page__casper_directory', displayer.PROCESSING)

    sleep(1.00)

    relative_directory = None

    # Look for the casper relative directory in the mounted iso directory.
    if not relative_directory:
        try:
            directory = get_directory_for_file('filesystem.squashfs', model.project.iso_mount_point)
            relative_directory = os.path.relpath(directory, model.project.iso_mount_point)
            logger.log_value('The compressed Linux file system directory is', relative_directory)
        except ValueError as exception:
            logger.log_value('Unable to find the compressed Linux file system in %s' % model.project.iso_mount_point, exception)

    # Look for the casper relative directory in the custom disk directory.
    if not relative_directory:
        try:
            directory = get_directory_for_file('filesystem.squashfs', model.project.custom_disk_directory)
            relative_directory = os.path.relpath(directory, model.project.custom_disk_directory)
            logger.log_value('The compressed Linux file system directory is', relative_directory)
        except ValueError as exception:
            logger.log_value('Unable to find the compressed Linux file system in %s' % model.project.custom_disk_directory, exception)

    # TODO: If the casper directory in the mounted iso is different from
    #       the casper directory in the custom disk directory, then
    #       rename the casper directory in the custom disk directory to
    #       match the casper directory in mounted iso. The casper
    #       directory in the mounted iso will become the new casper
    #       directory, and all files will be copied from there.

    if relative_directory:
        error = False
        model.status.casper_directory = relative_directory
        # displayer.update_label('extract_page__casper_directory_message', '')
        # displayer.update_label('extract_page__casper_directory_message', 'The compressed Linux file system directory is /%s.' % model.status.casper_directory)
        displayer.update_status('extract_page__casper_directory', displayer.OK)
    else:
        error = True
        model.status.casper_directory = None
        displayer.update_label('extract_page__casper_directory_message', 'The compressed Linux file system was not found.')
        displayer.update_status('extract_page__casper_directory', displayer.ERROR)

    return error


def get_directory_for_file(filename, start_path):

    logger.log_value('Get directory for %s in' % filename, start_path)

    directory = ''
    for dirpath, dirnames, filenames in os.walk(start_path):
        if filename in filenames:
            directory = dirpath

    if directory:
        logger.log_value('%s is in' % filename, directory)
    else:
        logger.log_value('%s is not in' % filename, directory)

    return directory


#-----------------------------------------------------------------------
# Extract the Linux File System Functions
#-----------------------------------------------------------------------


def extract_squashfs():

    logger.log_label('Extract the compressed Linux file system.')

    displayer.update_status('extract_page__unsquashfs', displayer.PROCESSING)

    # sleep(1.00)

    # Clear the terminal because the history will no longer be valid
    # when the new *.squashfs file is extracted.
    terminal = model.builder.get_object('terminal_page__terminal')
    terminal.reset(True, True)

    target_path = model.project.custom_root_directory
    logger.log_value('The target path is', target_path)

    # Delete custom squashfs directory, if it exists.
    # file_utilities.delete_directory(target_path)

    source_path = os.path.join(model.project.iso_mount_point, model.status.casper_directory, 'filesystem.squashfs')
    logger.log_value('The source path is', source_path)

    # Extract filesystem.squashfs.

    program = os.path.join(model.application.directory, 'commands', 'extract-root')
    command = 'pkexec "%s" "%s" "%s"' % (program, target_path, source_path)

    # The progress callback function.
    def progress_callback(percent):
        displayer.update_progress_bar_percent('extract_page__unsquashfs_progress_bar', percent)
        if percent % 10 == 0:
            logger.log_value('• Completed', '%i%%' % percent)

    # Error may be None or an exception.
    error = show_progress(command, progress_callback)

    if not error:
        model.status.is_success_extract = True
        # displayer.update_label('extract_page__unsquashfs_message', '')
        displayer.update_status('extract_page__unsquashfs', displayer.OK)
    else:
        # TODO: Log error, since error may be an exception?
        model.status.is_success_extract = False
        displayer.update_label('extract_page__unsquashfs_message', 'Unable to extract the compressed Linux file system.')
        displayer.update_status('extract_page__unsquashfs', displayer.ERROR)

    return bool(error)


#-----------------------------------------------------------------------
# Copy Original ISO Files Functions
#-----------------------------------------------------------------------


def copy_original_iso_files():

    logger.log_label('Copy important files from the original disk image.')

    displayer.update_status('extract_page__copy_original_iso_files', displayer.PROCESSING)

    # sleep(1.00)

    # Add a "/" at the end of the path so rsync copies the contents
    # of the source directory to the target directory.
    source_path = os.path.join(model.project.iso_mount_point, '')
    logger.log_value('The source path is', source_path)

    # Add a "/" at the end of the path so rsync copies files into
    # the target directory. This is not required, but is consistent
    # with the source directory path above.
    target_path = os.path.join(model.project.custom_disk_directory, '')
    logger.log_value('The target path is', target_path)

    # Copy files from the original iso.

    # Exclude or copy the following files as indicated.
    #
    # do not copy: /md5sum.txt
    # do not copy: /casper/filesystem.manifest
    # ~ ~ ~  copy: /casper/filesystem.manifest-remove
    # ~ ~ ~  copy: /casper/filesystem.manifest-minimal-remove
    # do not copy: /casper/filesystem.size
    # do not copy: /casper/filesystem.squashfs
    # do not copy: /casper/filesystem.squashfs.gpg
    # ~ ~ ~  copy: /casper/initrd.lz
    # ~ ~ ~  copy: /casper/vmlinuz.efi
    #
    # Some important rsync options:
    #
    #   -rlptgoD
    #
    #     -r --recursive
    #     -l --links
    #     -p --perms (do not use)
    #     -t --times
    #     -g --group
    #     -O --owner
    #     -D --devices --specials

    command = (
        'rsync'
        ' --info=progress2 "%s" "%s"'
        ' --delete'
        # ' --archive'
        ' --recursive'
        ' --links'
        ' --chmod=u+rwX'
        ' --exclude="md5sum.txt"'
        ' --exclude="/%s/filesystem.manifest"'
        ' --exclude="/%s/filesystem.size"'
        ' --exclude="/%s/filesystem.squashfs"'
        ' --exclude="/%s/filesystem.squashfs.gpg"' %
        (source_path,
         target_path,
         model.status.casper_directory,
         model.status.casper_directory,
         model.status.casper_directory,
         model.status.casper_directory))

    # The progress callback function.
    def progress_callback(percent):
        displayer.update_progress_bar_percent('extract_page__copy_original_iso_files_progress_bar', percent)
        if percent % 10 == 0:
            logger.log_value('• Completed', '%i%%' % percent)

    # Error may be None or an exception.
    error = show_progress(command, progress_callback)

    if not error:
        model.status.is_success_copy = True
        # displayer.update_label('extract_page__copy_original_iso_files_message', '')
        displayer.update_status('extract_page__copy_original_iso_files', displayer.OK)
    else:
        model.status.is_success_copy = False
        displayer.update_label('extract_page__copy_original_iso_files_message', 'Unable to copy files from the original disk image.')
        displayer.update_status('extract_page__copy_original_iso_files', displayer.ERROR)

    return bool(error)


'''
# TODO: Set boot_configurations on a different page.
from constants import DEFAULT_BOOT_CONFIGURATIONS_STRING
if model.status.is_success_copy:
    # Options (configurations)
    boot_configurations_string = DEFAULT_BOOT_CONFIGURATIONS_STRING
    boot_configurations = []
    for boot_configuration in boot_configurations_string.split(','):
        boot_configuration = boot_configuration.strip(' ' + os.sep)
        # Do not use the real path for model.project.custom_disk_directory.
        filepath = os.path.join(model.project.custom_disk_directory, boot_configuration)
        if os.path.exists(filepath):
            boot_configurations.append(boot_configuration)
    model.options.boot_configurations = boot_configurations
'''
