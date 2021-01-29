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
"""
Prior to entering this page:
- model.status.iso_template must be set to None whenever
  model.status.is_success_copy is set to False.
- model.status.casper_directory must be set to None whenever
  model.status.is_success_extract is set to False.
"""

########################################################################
# References
########################################################################

# https://askubuntu.com/questions/1289400/remaster-installation-image-for-ubuntu-20-10
# http://manpages.ubuntu.com/manpages/groovy/man1/xorriso.1.html
# https://linux.die.net/man/8/mkisofs
# http://manpages.ubuntu.com/manpages/groovy/man1/dd.1.html
# https://stackoverflow.com/questions/65189149/best-regex-in-python-to-not-have-double-space-in-result-when-substring-is-remo/65189757#65189757

########################################################################
# Imports
########################################################################

import os
import time

from constants import IMAGE_FILE_NAME
from constants import SLEEP_1000_MS
from utilities import configuration
from utilities import constructor
from utilities import displayer
from utilities import file_utilities, iso_utilities
from utilities import logger
from utilities import model
from utilities.progressor import show_progress

########################################################################
# Global Variables & Constants
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

        # The template must always be None if is success copy is None.
        # This should be set correctly on the Project page, but set it
        # here as a precaution (in case the user edited the
        # configuration file.
        if not model.status.is_success_copy: model.status.iso_template = None

        # The casper directory must always be None if is success extract
        # is None. This should be set correctly on the Project page, but
        # set it here as a precaution (in case the user edited the
        # configuration file.
        if not model.status.is_success_extract: model.status.casper_directory = None

        # Identify important files on the original disk image.

        displayer.set_visible('extract_page__analyze_original_iso_section', not model.status.iso_template or not model.status.casper_directory)
        displayer.update_label('extract_page__analyze_original_iso_message', '')
        displayer.update_status('extract_page__analyze_original_iso', displayer.BULLET)

        # Copy important files from the original disk image.

        displayer.set_visible('extract_page__copy_original_iso_files_section', not model.status.is_success_copy)
        displayer.update_progress_bar_percent('extract_page__copy_original_iso_files_progress_bar', 0)
        # displayer.update_progress_bar_text('extract_page__copy_original_iso_files_progress_bar', None)
        displayer.update_label('extract_page__copy_original_iso_files_message', '')
        displayer.update_status('extract_page__copy_original_iso_files', displayer.BULLET)

        # Extract the compressed Linux file system.

        displayer.set_visible('extract_page__unsquashfs_section', not model.status.is_success_extract)
        displayer.update_progress_bar_percent('extract_page__unsquashfs_progress_bar', 0)
        # displayer.update_progress_bar_text('extract_page__unsquashfs_progress_bar', None)
        displayer.update_label('extract_page__unsquashfs_message', '')
        displayer.update_status('extract_page__unsquashfs', displayer.BULLET)

        return

    else:

        return 'unknown'


def enter(action, old_page=None):
    """
    Specific success or error messages should be displayed in the called
    functions, but the display status the model status values should be
    set here because they depend on the outcome of multiple functions.

    Assume that prior to entering this page:

    - model.status.iso_template is set to None whenever
      model.status.is_success_copy is set to False.

    - model.status.casper_directory is set to None whenever
      model.status.is_success_extract is set to False.
    """

    if action == 'next':

        # Identify important files on the original disk image.
        if not model.status.iso_template or not model.status.casper_directory:

            displayer.update_status('extract_page__analyze_original_iso', displayer.PROCESSING)
            time.sleep(SLEEP_1000_MS)

            # Identify the template for the original disk image.
            if not model.status.iso_template:

                # Delete the old image files. Ignore errors.
                pattern = os.path.join(model.project.directory, IMAGE_FILE_NAME % '[1-9]')
                file_utilities.delete_files_with_pattern(pattern)

                # Set model.status.iso_template.
                is_error = identify_iso_template()
                if is_error:
                    # Stay on this page.
                    return

            # Identify the casper relative directory.
            if not model.status.casper_directory:

                is_error = identify_casper_directory()
                if is_error:
                    # Stay on this page.
                    return

            #-----------------------------------------------------------
            # TODO: Remove this section in a future release. (12/27/2020)
            #       Also, remove similar code from start_page and extract_page.

            # Correct an error in the ISO template.
            if model.status.iso_template:
                template = constructor.decode(model.status.iso_template)
                if '{{volume_id}}' in template:
                    template = template.replace('{{volume_id}}', '{volume_id}')
                    model.status.iso_template = constructor.encode(template)
            #-----------------------------------------------------------

            # Success. Pause to allow the user to see the result.
            displayer.update_label('extract_page__analyze_original_iso_message', 'Success.')
            displayer.update_status('extract_page__analyze_original_iso', displayer.OK)
            time.sleep(SLEEP_1000_MS)

        # Copy original disk files.
        if not model.status.is_success_copy:

            displayer.update_status('extract_page__copy_original_iso_files', displayer.PROCESSING)

            # Copy original disk files.
            is_error = copy_original_iso_files()
            if is_error: return  # Stay on this page.

            # Success. Pause to allow the user to see the result.
            model.status.is_success_copy = True
            displayer.update_status('extract_page__copy_original_iso_files', displayer.OK)
            time.sleep(SLEEP_1000_MS)

        # Extract the Linux file system.
        if not model.status.is_success_extract:

            displayer.update_status('extract_page__unsquashfs', displayer.PROCESSING)

            is_error = extract_squashfs()
            if is_error: return  # Stay on this page.

            # Success. Pause to allow the user to see the result.
            model.status.is_success_copy = True
            displayer.update_status('extract_page__unsquashfs', displayer.OK)
            time.sleep(SLEEP_1000_MS)

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
# Analyze the Original Disk Functions
#-----------------------------------------------------------------------


def identify_iso_template():

    logger.log_label('Generate the ISO template')

    iso_report = iso_utilities.get_iso_report()
    template = iso_utilities.generate_iso_template(iso_report)
    if template:
        model.status.iso_template = constructor.encode(template)
    else:
        model.status.iso_template = None

    if not model.status.iso_template:
        is_error = True
        displayer.update_label(
            'extract_page__analyze_original_iso_message',
            '<span foreground="red">Error. Unable to identify information about this disk.</span>')
        displayer.update_status('extract_page__analyze_original_iso', displayer.ERROR)
    else:
        is_error = False

    return is_error


def identify_casper_directory():
    """
    Set the relative casper directory.
    """

    logger.log_label('Find the compressed Linux file system')

    # Look for the casper relative directory in the mounted iso directory.
    if not model.status.casper_directory:
        try:
            directory = file_utilities.get_directory_for_file('filesystem.squashfs', model.project.iso_mount_point)
            model.status.casper_directory = os.path.relpath(directory, model.project.iso_mount_point)
            # logger.log_value('The compressed Linux file system directory is', model.status.casper_directory)
        except ValueError as exception:
            logger.log_value('Unable to find the compressed Linux file system in %s' % model.project.iso_mount_point, exception)

    # Look for the casper relative directory in the custom disk directory.
    if not model.status.casper_directory:
        try:
            directory = file_utilities.get_directory_for_file('filesystem.squashfs', model.project.custom_disk_directory)
            model.status.casper_directory = os.path.relpath(directory, model.project.custom_disk_directory)
            # logger.log_value('The compressed Linux file system directory is', model.status.casper_directory)
        except ValueError as exception:
            logger.log_value('Unable to find the compressed Linux file system in %s' % model.project.custom_disk_directory, exception)

    # TODO: If the casper directory in the mounted iso is different from
    #       the casper directory in the custom disk directory, then
    #       rename the casper directory in the custom disk directory to
    #       match the casper directory in mounted iso. The casper
    #       directory in the mounted iso will become the new casper
    #       directory, and all files will be copied from there.

    if not model.status.casper_directory:
        is_error = True
        displayer.update_label('extract_page__analyze_original_iso_message', '<span foreground="red">Unable to locate the compressed Linux file system.</span>')
        displayer.update_status('extract_page__analyze_original_iso', displayer.ERROR)
    else:
        is_error = False

    return is_error


#-----------------------------------------------------------------------
# Copy Original Disk Files Functions
#-----------------------------------------------------------------------


def copy_original_iso_files():

    logger.log_label('Copy important files from the original disk image')

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
    # do not copy: /MD5SUMS (for Linux Mint)
    # do not copy: /casper/filesystem.manifest
    # ~ ~ ~  copy: /casper/filesystem.manifest-remove
    # ~ ~ ~  copy: /casper/filesystem.manifest-minimal-remove
    # do not copy: /casper/filesystem.size
    # do not copy: /casper/filesystem.squashfs
    # do not copy: /casper/filesystem.squashfs.gpg
    # ~ ~ ~  copy: /casper/initrd
    # ~ ~ ~  copy: /casper/vmlinuz
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

    # Use info=progress2 to get the total progress, instead of the
    # progress for individual files.
    # Add read and write permissions for the user.
    # Set read and write permissions for group and other.
    command = (
        'rsync'
        ' --info=progress2 "{source_path}" "{target_path}"'
        ' --delete'
        # ' --archive'
        ' --recursive'
        ' --links'
        ' --chmod=u+rwX,g=rX,o=rX'
        ' --exclude="md5sum.txt"'
        ' --exclude="MD5SUMS"'
        ' --exclude=".disk/release_notes_url"'
        ' --exclude="/{casper_directory}/filesystem.manifest"'
        ' --exclude="/{casper_directory}/filesystem.size"'
        ' --exclude="/{casper_directory}/filesystem.squashfs"'
        ' --exclude="/{casper_directory}/filesystem.squashfs.gpg"').format(
            source_path=source_path,
            target_path=target_path,
            casper_directory=model.status.casper_directory)

    # The progress callback function.
    def progress_callback(percent):
        displayer.update_progress_bar_percent('extract_page__copy_original_iso_files_progress_bar', percent)
        if percent % 10 == 0:
            logger.log_value('Completed', '%i%%' % percent)

    exception, message = show_progress(command, progress_callback)

    if exception:
        is_error = True
        model.status.is_success_copy = False
        if 'No space left on device' in message:
            displayer.update_label('extract_page__copy_original_iso_files_message', '<span foreground="red">Error. Not enough space on the disk.</span>')
        else:
            displayer.update_label(
                'extract_page__copy_original_iso_files_message',
                '<span foreground="red">Error. Unable to copy files from the original disk image.</span>')
        displayer.update_status('extract_page__copy_original_iso_files', displayer.ERROR)
    else:
        is_error = False
        model.status.is_success_copy = True

    return is_error


#-----------------------------------------------------------------------
# Extract the Linux File System Functions
#-----------------------------------------------------------------------


def extract_squashfs():

    logger.log_label('Extract the compressed Linux file system')

    # Clear the terminal because the history will no longer be valid
    # when the new *.squashfs file is extracted.
    terminal = model.builder.get_object('terminal_page__terminal')
    terminal.reset(True, True)

    target_path = model.project.custom_root_directory
    logger.log_value('The target path is', target_path)

    source_path = os.path.join(model.project.iso_mount_point, model.status.casper_directory, 'filesystem.squashfs')
    logger.log_value('The source path is', source_path)

    program = os.path.join(model.application.directory, 'commands', 'extract-root')
    command = 'pkexec "%s" "%s" "%s"' % (program, target_path, source_path)

    # The progress callback function.
    def progress_callback(percent):
        displayer.update_progress_bar_percent('extract_page__unsquashfs_progress_bar', percent)
        if percent % 10 == 0:
            logger.log_value('Completed', '%i%%' % percent)

    exception, message = show_progress(command, progress_callback)

    if exception:
        is_error = True
        model.status.is_success_extract = False
        if 'No space left on device' in message:
            displayer.update_label('extract_page__unsquashfs_message', '<span foreground="red">Error. Not enough space on the disk.</span>')
        else:
            displayer.update_label(
                'extract_page__unsquashfs_message',
                '<span foreground="red">Error. Unable to extract the compressed Linux file system.</span>')
        displayer.update_status('extract_page__unsquashfs', displayer.ERROR)
    else:
        is_error = False
        model.status.is_success_extract = True

    return is_error
