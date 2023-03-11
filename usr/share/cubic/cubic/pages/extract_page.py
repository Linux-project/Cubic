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
• model.status.iso_template must be set to None whenever
  model.status.is_success_copy is set to False.
• model.status.squashfs_directory must be set to None whenever
  model.status.is_success_extract is set to False.
• model.status.squashfs_file_name must be set to None whenever
  model.status.is_success_extract is set to False.
• model.status.casper_directory must be set to None whenever
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

from cubic.constants import BOLD_RED, NORMAL
from cubic.constants import CASPER_DIRECTORIES, SQUASHFS_FILE_NAMES
from cubic.constants import EXTENSION_MANIFEST, EXTENSION_SIZE, EXTENSION_SQUASHFS, EXTENSION_SQUASHFS_GPG
from cubic.constants import IMAGE_FILE_NAME
from cubic.constants import SLEEP_1000_MS
from cubic.navigator import InterruptException
from cubic.utilities import constructor
from cubic.utilities import displayer
from cubic.utilities import file_utilities, iso_utilities
from cubic.utilities import logger
from cubic.utilities import model
from cubic.utilities.progressor import track_progress

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

        # The template must always be None if is_success_copy is None.
        # This should be set correctly on the Project page, but set it
        # here as a precaution (in case the user edited the
        # configuration file.
        if not model.status.is_success_copy:
            model.status.iso_template = None

        # The casper directory must always be None if is_success_extract
        # is None. This should be set correctly on the Project page, but
        # set it here as a precaution (in case the user edited the
        # configuration file.
        if not model.status.is_success_extract:
            model.status.squashfs_directory = None
            model.status.squashfs_file_name = None
            model.status.casper_directory = None

        # --------------------------------------------------------------
        # Identify important files on the original disk image.
        # --------------------------------------------------------------

        displayer.set_visible('extract_page__analyze_original_iso_section',
                              not model.status.iso_template or \
                              not model.status.squashfs_directory or \
                              not model.status.squashfs_file_name or \
                              not model.status.casper_directory)

        displayer.update_label('extract_page__analyze_original_iso_message', '...', False)
        displayer.update_status('extract_page__analyze_original_iso', displayer.BULLET)

        # --------------------------------------------------------------
        # Copy important files from the original disk image.
        # --------------------------------------------------------------

        displayer.set_visible('extract_page__copy_original_iso_files_section', not model.status.is_success_copy)
        displayer.update_progress_bar_percent('extract_page__copy_original_iso_files_progress_bar', 0)
        # displayer.update_progress_bar_text('extract_page__copy_original_iso_files_progress_bar', None)
        displayer.update_label('extract_page__copy_original_iso_files_message', '', False)
        displayer.update_status('extract_page__copy_original_iso_files', displayer.BULLET)

        # --------------------------------------------------------------
        # Extract the compressed Linux file system.
        # --------------------------------------------------------------

        displayer.set_visible('extract_page__unsquashfs_section', not model.status.is_success_extract)
        displayer.update_progress_bar_percent('extract_page__unsquashfs_progress_bar', 0)
        # displayer.update_progress_bar_text('extract_page__unsquashfs_progress_bar', None)
        displayer.update_label('extract_page__unsquashfs_message', '', False)
        displayer.update_status('extract_page__unsquashfs', displayer.BULLET)

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

        return

    else:

        logger.log_value('Error', f'{BOLD_RED}Unknown action for setup{NORMAL}')

        return 'unknown'


def enter(action, old_page=None):
    """
    Specific success or error messages should be displayed in the called
    functions, but the display status should be set here because they
    depend on the outcome of multiple functions.

    The following values are checked and set to None accordingly, in the
    setup() function, prior to entering this page.

    • model.status.iso_template must be set to None whenever
      model.status.is_success_copy is set to False.

    • model.status.squashfs_directory must be set to None whenever
      model.status.is_success_extract is set to False.

    • model.status.squashfs_file_name must be set to None whenever
      model.status.is_success_extract is set to False.

    • model.status.casper_directory must be set to None whenever
      model.status.is_success_extract is set to False.
    """

    if action == 'next':

        # --------------------------------------------------------------
        # Identify important files on the original disk image.
        # --------------------------------------------------------------

        if not model.status.iso_template or \
           not model.status.squashfs_directory or \
           not model.status.squashfs_file_name or \
           not model.status.casper_directory:

            displayer.update_status('extract_page__analyze_original_iso', displayer.PROCESSING)
            time.sleep(SLEEP_1000_MS)

            # Identify the template for the original disk image.
            if not model.status.iso_template:

                # Delete the old image files. Ignore errors.
                file_path_pattern = os.path.join(model.project.directory, IMAGE_FILE_NAME % '[1-9]')
                file_utilities.delete_files_with_pattern(file_path_pattern)

                # Set model.status.iso_template.
                is_error = identify_iso_template()
                if is_error: return  # Stay on this page.

            # Identify the squashfs relative file path.
            if not model.status.squashfs_directory or \
               not model.status.squashfs_file_name:

                is_error = identify_squashfs_file_path()
                if is_error: return  # Stay on this page.

            # Identify the casper relative directory.
            if not model.status.casper_directory:

                is_error = identify_casper_directory()
                if is_error: return  # Stay on this page.

            # ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
            # TODO: Remove this section in a future release. (12/27/2020)
            #       Also, remove similar code from start_page and extract_page.

            # Correct an error in the ISO template.
            if model.status.iso_template:
                template = constructor.decode(model.status.iso_template)
                if '{{volume_id}}' in template:
                    template = template.replace('{{volume_id}}', '{volume_id}')
                    model.status.iso_template = constructor.encode(template)
            # ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

            # Success. Pause to allow the user to see the result.
            message = 'Success.'
            displayer.update_label('extract_page__analyze_original_iso_message', message, False)
            displayer.update_status('extract_page__analyze_original_iso', displayer.OK)
            time.sleep(SLEEP_1000_MS)

        # --------------------------------------------------------------
        # Copy important files from the original disk image.
        # --------------------------------------------------------------

        if not model.status.is_success_copy:

            displayer.update_status('extract_page__copy_original_iso_files', displayer.PROCESSING)

            # Copy original disk files.
            is_error = copy_original_iso_files()
            if is_error: return  # Stay on this page.

            # Success. Pause to allow the user to see the result.
            model.status.is_success_copy = True
            displayer.update_status('extract_page__copy_original_iso_files', displayer.OK)
            time.sleep(SLEEP_1000_MS)

        # --------------------------------------------------------------
        # Extract the compressed Linux file system.
        # --------------------------------------------------------------

        if not model.status.is_success_extract:

            displayer.update_status('extract_page__unsquashfs', displayer.PROCESSING)

            # Extract the squashfs.
            is_error = extract_squashfs()
            if is_error: return  # Stay on this page.

            # Success. Pause to allow the user to see the result.
            model.status.is_success_copy = True
            displayer.update_status('extract_page__unsquashfs', displayer.OK)
            time.sleep(SLEEP_1000_MS)

        return 'next'

    else:

        logger.log_value('Error', f'{BOLD_RED}Unknown action for enter{NORMAL}')

        return 'unknown'


def leave(action, new_page=None):

    if action == 'back':

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        return

    elif action == 'next':

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        return

    elif action == 'quit':

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        # Save the model values.
        model.project.configuration.save()

        iso_utilities.unmount_iso_and_delete_mount_point(model.project.iso_mount_point)

        return

    else:

        logger.log_value('Error', f'{BOLD_RED}Unknown action for leave{NORMAL}')

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        return 'unknown'


########################################################################
# Handler Functions
########################################################################

# N/A

########################################################################
# Support Functions
########################################################################

# ----------------------------------------------------------------------
# Analyze Original Disk Functions
# ----------------------------------------------------------------------


def identify_iso_template():

    logger.log_label('Generate the ISO template')

    iso_report = iso_utilities.get_iso_report()
    template = iso_utilities.generate_iso_template(iso_report)
    if template:
        model.status.iso_template = constructor.encode(template)
    else:
        model.status.iso_template = None

    if not model.status.iso_template:
        logger.log_value('Error', 'Unable to identify information about this disk')
        # message = '<span foreground="red">Error. Unable to identify information about this disk.</span>'
        message = 'Error. Unable to identify information about this disk'
        displayer.update_label('extract_page__analyze_original_iso_message', message, True)
        displayer.update_status('extract_page__analyze_original_iso', displayer.ERROR)
        return True
    else:
        return False


def identify_squashfs_file_path():
    """
    Set the squashfs directory and file name (without extension) in the
    model. If there are multiple squashfs files, only the first one
    matching the default squashfs file names will be selected.
    """

    logger.log_label('Find the compressed Linux file system')

    # Set model.status.squashfs_directory
    # Set model.status.squashfs_file_name

    # Remove the extension from the squashfs file name because this name
    # is reused for various other files with different extensions:
    # - filesystem.manifest
    # - filesystem.manifest-minimal-remove
    # - filesystem.manifest-remove
    # - filesystem.size
    # - filesystem.squashfs

    # For Pop!_OS the identified squashfs directories will be "casper"
    # and "casper_pop-os_20.04_amd64_intel_debug_25". However,
    # identify_squashfs_file_path() will select "casper" because it
    # appears in constants.CASPER_DIRECTORIES.

    file_paths = _get_squashfs_file_paths()

    if not file_paths:
        model.status.squashfs_directory = None
        model.status.squashfs_file_name = None
    if len(file_paths) == 1:
        directory, file_name = os.path.split(file_paths[0])
        model.status.squashfs_directory = directory
        model.status.squashfs_file_name, _ = os.path.splitext(file_name)
    else:
        # Handle multiple squashfs file paths.
        for file_path in file_paths:
            directory, file_name = os.path.split(file_path)
            # Compare the file name to the list of squash file names.
            if file_name in SQUASHFS_FILE_NAMES:
                model.status.squashfs_directory = directory
                model.status.squashfs_file_name, _ = os.path.splitext(file_name)
                break

    # logger.log_value('The selected squashfs directory is', model.status.squashfs_directory)
    # logger.log_value('The selected squashfs file name is', model.status.squashfs_file_name)

    if not model.status.squashfs_directory or \
       not model.status.squashfs_file_name:
        logger.log_value('Error', 'Unable to locate the squashfs file path')
        # message = '<span foreground="red">Unable to locate the compressed Linux file system.</span>'
        message = 'Unable to locate the compressed Linux file system.'
        displayer.update_label('extract_page__analyze_original_iso_message', message, True)
        displayer.update_status('extract_page__analyze_original_iso', displayer.ERROR)
        return True  # (Error)
    return False  # (No error)


def identify_casper_directory():
    """
    Set the casper directory in the model. The casper directory contains
    the vmlinuz annd initrd kernel files. If there are multiple casper
    directories, only the first one matching the default casper
    directories will be selected.
    """

    logger.log_label('Find the casper kernel files')

    # Set model.status.casper_directory

    # Assume vmlinuz and initrd are in the same directories.
    # file_paths = _get_initrd_file_paths()
    file_paths = _get_vmlinuz_file_paths()

    if not file_paths:
        model.status.casper_directory = None
    elif len(file_paths) == 1:
        model.status.casper_directory = os.path.dirname(file_paths[0])
    else:
        # Handle multiple casper directories.
        for file_path in file_paths:
            # Compare the root directory to the list of casper directories.
            if file_path.split(os.path.sep)[0] in CASPER_DIRECTORIES:
                # Get the full relative path (exclude the file name).
                model.status.casper_directory = os.path.dirname(file_path)
                break

    if not model.status.casper_directory:
        logger.log_value('Error', 'Unable to locate the casper directory')
        # message = '<span foreground="red">Unable to locate the casper kernel files.</span>'
        message = 'Unable to locate the casper kernel files.'
        displayer.update_label('extract_page__analyze_original_iso_message', message, True)
        displayer.update_status('extract_page__analyze_original_iso', displayer.ERROR)
        return True  # (Error)

    return False  # (No error)


def _get_squashfs_file_paths():
    """
    Get the squashfs file paths relative to the rood directory of the
    original ISO or custom ISO. The custom ISO is only searched if the
    original ISO is not available/mounted.

    Returns:
    file_paths : list of str
        The relative squashfs file paths.
    """

    # Follow symlinks to accommodate Pop!_OS, because the init script
    # specifically requires "casper" directory, instead of the real path
    # to the squashfs directory. Pop!_OS has a symlink to the
    # squashfs directory named "casper":
    #   lrwxrwxrwx  casper -> casper_pop-os_20.04_amd64_intel_debug_25
    #   drwxr-xr-x  casper_pop-os_20.04_amd64_intel_debug_25
    # For Pop!_OS the identified squashfs directories will be "casper"
    # and "casper_pop-os_20.04_amd64_intel_debug_25". However,
    # identify_squashfs_file_path() will select "casper" because it
    # appears in constants.CASPER_DIRECTORIES.

    # Search the mounted ISO directory, first. Follow symlinks.
    file_paths = file_utilities.find_files_with_pattern(rf'.*\.{EXTENSION_SQUASHFS}$', model.project.iso_mount_point, follow_links=True)

    # Search the custom disk directory, second. Follow symlinks.
    if not file_paths:
        file_paths = file_utilities.find_files_with_pattern(rf'.*\.{EXTENSION_SQUASHFS}$', model.project.custom_disk_directory, follow_links=True)

    logger.log_value('The squashfs file paths are', file_paths)

    return file_paths


def _get_vmlinuz_file_paths():
    """
    Get the vmlinuz file paths relative to the rood directory of the
    original ISO or custom ISO. The custom ISO is only searched if the
    original ISO is not available/mounted.

    Returns:
    file_paths : list of str
        The relative vmlinuz file paths.
    """

    # logger.log_label('Find the vmlinuz file paths')

    # Search the mounted ISO directory, first. Do not follow symlinks.
    file_paths = file_utilities.find_files_with_pattern(r'vmlinuz.*', model.project.iso_mount_point)

    # Search the custom disk directory, second. Do not follow symlinks.
    if not file_paths:
        file_paths = file_utilities.find_files_with_pattern(r'vmlinuz.*', model.project.custom_disk_directory)

    logger.log_value('The vmlinuz file paths are', file_paths)

    return file_paths


def _get_initrd_file_paths():
    """
    Get the initrd file paths relative to the rood directory of the
    original ISO or custom ISO. The custom ISO is only searched if the
    original ISO is not available/mounted.

    Returns:
    file_paths : list of str
        The relative initrd file paths.
    """

    # logger.log_label('Find the initrd file paths')

    # Search the mounted ISO directory, first.
    file_paths = file_utilities.find_files_with_pattern(r'initrd.*', model.project.iso_mount_point)

    # Search the custom disk directory, second.
    if not file_paths:
        file_paths = file_utilities.find_files_with_pattern(r'initrd.*', model.project.custom_disk_directory)

    logger.log_value('The initrd file paths are', file_paths)

    return file_paths


# ----------------------------------------------------------------------
# Copy Original Disk Files Functions
# ----------------------------------------------------------------------


def copy_original_iso_files():
    """
    Exclude or copy the following files as indicated.

    do not copy: /md5sum.txt
    do not copy: /MD5SUMS (for Linux Mint)

    ~ ~ ~  copy: /squashfs_directory/filesystem.manifest-remove
    ~ ~ ~  copy: /squashfs_directory/filesystem.manifest-minimal-remove

    do not copy: /squashfs_directory/filesystem.manifest
    do not copy: /squashfs_directory/filesystem.size
    do not copy: /squashfs_directory/filesystem.squashfs
    do not copy: /squashfs_directory/filesystem.squashfs.gpg

    ~ ~ ~  copy: /squashfs_directory/ubuntu-server-minimal.manifest
    ~ ~ ~  copy: /squashfs_directory/ubuntu-server-minimal.size
    ~ ~ ~  copy: /squashfs_directory/ubuntu-server-minimal.squashfs
    ~ ~ ~  copy: /squashfs_directory/ubuntu-server-minimal.squashfs.gpg

    ~ ~ ~  copy: /squashfs_directory/ubuntu-server-minimal.ubuntu-server.installer.generic.manifest
    ~ ~ ~  copy: /squashfs_directory/ubuntu-server-minimal.ubuntu-server.installer.generic.size
    ~ ~ ~  copy: /squashfs_directory/ubuntu-server-minimal.ubuntu-server.installer.generic.squashfs
    ~ ~ ~  copy: /squashfs_directory/ubuntu-server-minimal.ubuntu-server.installer.generic.squashfs.gpg

    ~ ~ ~  copy: /squashfs_directory/ubuntu-server-minimal.ubuntu-server.installer.manifest
    ~ ~ ~  copy: /squashfs_directory/ubuntu-server-minimal.ubuntu-server.installer.size
    ~ ~ ~  copy: /squashfs_directory/ubuntu-server-minimal.ubuntu-server.installer.squashfs
    ~ ~ ~  copy: /squashfs_directory/ubuntu-server-minimal.ubuntu-server.installer.squashfs.gpg

    do not copy: /squashfs_directory/ubuntu-server-minimal.ubuntu-server.manifest
    do not copy: /squashfs_directory/ubuntu-server-minimal.ubuntu-server.size
    do not copy: /squashfs_directory/ubuntu-server-minimal.ubuntu-server.squashfs
    do not copy: /squashfs_directory/ubuntu-server-minimal.ubuntu-server.squashfs.gpg

    ~ ~ ~  copy: /casper/initrd
    ~ ~ ~  copy: /casper/vmlinuz
    """

    logger.log_label('Copy important files from the original disk image')

    # Add a "/" at the end of the path so rsync copies the contents
    # of the source directory to the target directory.
    source_file_path = os.path.join(model.project.iso_mount_point, '')
    logger.log_value('The source file path is', source_file_path)

    # Add a "/" at the end of the path so rsync copies files into
    # the target directory. This is not required, but is consistent
    # with the source directory path above.
    target_file_path = os.path.join(model.project.custom_disk_directory, '')
    logger.log_value('The target file path is', target_file_path)

    # Copy files from the original iso.

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
        f' --info=progress2 "{source_file_path}" "{target_file_path}"'
        ' --delete'
        # ' --archive'
        ' --recursive'
        ' --links'
        ' --chmod=u+rwX,g=rX,o=rX'
        ' --exclude="md5sum.txt"'
        ' --exclude="MD5SUMS"'
        ' --exclude=".disk/release_notes_url"'
        f' --exclude="/{model.status.squashfs_directory}/{model.status.squashfs_file_name}.{EXTENSION_MANIFEST}"'
        f' --exclude="/{model.status.squashfs_directory}/{model.status.squashfs_file_name}.{EXTENSION_SIZE}"'
        f' --exclude="/{model.status.squashfs_directory}/{model.status.squashfs_file_name}.{EXTENSION_SQUASHFS}"'
        f' --exclude="/{model.status.squashfs_directory}/{model.status.squashfs_file_name}.{EXTENSION_SQUASHFS_GPG}"')

    # The progress callback function.
    def progress_callback(percent):
        displayer.update_progress_bar_percent('extract_page__copy_original_iso_files_progress_bar', percent)
        if percent % 10 == 0:
            logger.log_value('Completed', f'{percent:n}%')

    try:
        track_progress(command, progress_callback)
    except InterruptException as exception:
        model.status.is_success_copy = False
        if 'No space left on device' in str(exception):
            # message = '<span foreground="red">Error. Not enough space on the disk.</span>'
            message = 'Error. Not enough space on the disk.'
        else:
            # message = '<span foreground="red">Error. Unable to copy files from the original disk image.</span>'
            message = 'Error. Unable to copy files from the original disk image.'
        displayer.update_label('extract_page__copy_original_iso_files_message', message, True)
        displayer.update_status('extract_page__copy_original_iso_files', displayer.ERROR)
        logger.log_value('Propagate exception', exception)
        raise exception
    except Exception as exception:
        model.status.is_success_copy = False
        if 'No space left on device' in str(exception):
            # message = '<span foreground="red">Error. Not enough space on the disk.</span>'
            message = 'Error. Not enough space on the disk.'
        else:
            # message = '<span foreground="red">Error. Unable to copy files from the original disk image.</span>'
            message = 'Error. Unable to copy files from the original disk image.'
        displayer.update_label('extract_page__copy_original_iso_files_message', message, True)
        displayer.update_status('extract_page__copy_original_iso_files', displayer.ERROR)
        logger.log_value('Do not propagate exception', exception)
        return True  # (Error)

    model.status.is_success_copy = True
    return False  # (No error)


# ----------------------------------------------------------------------
# Extract Linux File System Functions
# ----------------------------------------------------------------------


def extract_squashfs():

    logger.log_label('Extract the compressed Linux file system')

    # Clear the terminal because the history will no longer be valid
    # when the new *.squashfs file is extracted.
    terminal = model.builder.get_object('terminal_page__terminal')
    terminal.reset(True, True)

    target_file_path = model.project.custom_root_directory
    logger.log_value('The target file path is', target_file_path)

    file_name = f'{model.status.squashfs_file_name}.{EXTENSION_SQUASHFS}'
    source_file_path = os.path.join(model.project.iso_mount_point, model.status.squashfs_directory, file_name)
    logger.log_value('The source file path is', source_file_path)

    program = os.path.join(model.application.directory, 'commands', 'extract-root')
    command = ['pkexec', program, target_file_path, source_file_path]

    # The progress callback function.
    def progress_callback(percent):
        displayer.update_progress_bar_percent('extract_page__unsquashfs_progress_bar', percent)
        if percent % 10 == 0:
            logger.log_value('Completed', f'{percent:n}%')

    try:
        track_progress(command, progress_callback)
    except InterruptException as exception:
        model.status.is_success_extract = False
        if 'No space left on device' in str(exception):
            # message = '<span foreground="red">Error. Not enough space on the disk.</span>'
            message = 'Error. Not enough space on the disk.'
        else:
            # message = '<span foreground="red">Error. Unable to extract the compressed Linux file system.</span>'
            message = 'Error. Unable to extract the compressed Linux file system.'
        displayer.update_label('extract_page__unsquashfs_message', message, True)
        displayer.update_status('extract_page__unsquashfs', displayer.ERROR)
        logger.log_value('Propagate exception', exception)
        raise exception
    except Exception as exception:
        model.status.is_success_extract = False
        if 'No space left on device' in str(exception):
            # message = '<span foreground="red">Error. Not enough space on the disk.</span>'
            message = 'Error. Not enough space on the disk.'
        else:
            # message = '<span foreground="red">Error. Unable to extract the compressed Linux file system.</span>'
            message = 'Error. Unable to extract the compressed Linux file system.'
        displayer.update_label('extract_page__unsquashfs_message', message, True)
        displayer.update_status('extract_page__unsquashfs', displayer.ERROR)
        logger.log_value('Do not propagate exception', exception)
        return True  # (Error)

    model.status.is_success_extract = True
    return False  # (No error)
