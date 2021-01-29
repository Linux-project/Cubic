#!/usr/bin/python3

########################################################################
#                                                                      #
# prepare_page.py                                                      #
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

import collections
import glob
import os
import platform
import re
import string
import time

from constants import OK, ERROR, OPTIONAL, BULLET, PROCESSING, BLANK
from constants import SLEEP_0125_MS, SLEEP_0250_MS, SLEEP_0500_MS, SLEEP_1000_MS
from utilities import constructor
from utilities import displayer
from utilities import file_utilities
from utilities import iso_utilities
from utilities import logger
from utilities import model
from utilities.processor import execute_synchronous, execute_asynchronous

########################################################################
# Global Variables & Constants
########################################################################

name = 'prepare_page'

INITRAMFS_VERSION_PATTERN = re.compile(r'lib/modules/(\d[\d\.-]*\d)')

# Valid compression formats are gzip, bzip2, lz4, lzma, lzop, or xz,
# ignoring case. (See /etc/initramfs-tools/initramfs.conf).
INITRAMFS_COMPRESSION_PATTERN = re.compile(r'(?i).*(gzip|bzip2|lz4|lzma|lzop|xz).*')
COMPRESSION_EXTENSIONS = {'gzip': 'gz', 'bzip2': 'bz', 'lz4': 'lz', 'lzma': 'lz', 'lzop': 'lz', 'xz': 'xz'}

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
            next_button_label='Next❭',
            next_action='next',
            next_button_style=None,
            is_next_sensitive=False,
            is_next_visible=True)

        displayer.update_status('prepare_page__boot_kernels', BULLET)
        displayer.empty_box('prepare_page__boot_kernels_box')

        displayer.update_status('prepare_page__installed_packages', BULLET)
        displayer.update_label('prepare_page__installed_packages_message', '...')

        displayer.update_status('prepare_page__package_manifest_1', BULLET)
        displayer.update_label('prepare_page__package_manifest_1_message', '...')

        displayer.update_status('prepare_page__package_manifest_2', BULLET)
        displayer.update_label('prepare_page__package_manifest_2_message', '...')

        displayer.update_status('prepare_page__save_package_manifest', BULLET)
        displayer.update_label('prepare_page__save_package_manifest_message', '...')

        return

    else:

        return 'unknown'


def enter(action, old_page=None):
    '''
    iso_count_text = constructor.number_as_text(len(iso_file_path_list))
    iso_files_text = 'file' if len(iso_file_path_list) == 1 else 'files'
    md5_count_text = constructor.number_as_text(len(iso_checksum_file_path_list))
    md5_files_text = 'file' if len(iso_checksum_file_path_list) == 1 else 'files'
    label = 'Delete %s disk image %s and %s MD5 checksum %s.' % (iso_count_text, iso_files_text, md5_count_text, md5_files_text)
    '''

    if action == 'next':

        #
        # Identify disk boot kernels.
        #

        displayer.update_status('prepare_page__boot_kernels', PROCESSING)
        time.sleep(SLEEP_0500_MS)
        model.kernel_details_list = create_boot_kernel_details_list()
        if model.kernel_details_list:
            displayer.update_status('prepare_page__boot_kernels', OK)
            count = len(model.kernel_details_list)
            logger.log_value('Number of valid disk boot kernels found', count)
            number_text = constructor.number_as_text(count)
            plural_text = constructor.get_plural('kernel', 'kernels', count)
            add_message_to_boot_kernels_box('\nFound %s valid disk boot %s.' % (number_text, plural_text))
        else:
            displayer.update_status('prepare_page__boot_kernels', ERROR)
            logger.log_value('Error. Number of valid disk boot kernels found', 0)
            add_message_to_boot_kernels_box('\nError. No valid disk boot kernels were found.')
            add_message_to_boot_kernels_box(
                'To correct this issue, click the Back button and install missing Linux kernel packages on the Terminal page, or select the original disk image on the Project page.'
            )
            return 'error'
        time.sleep(SLEEP_0500_MS)

        #
        # Identify installed packages.
        #

        displayer.update_status('prepare_page__installed_packages', PROCESSING)
        time.sleep(SLEEP_0500_MS)
        installed_packages_list = create_installed_packages_list()
        if installed_packages_list:
            count = len(installed_packages_list)
            logger.log_value('Number of installed packages found', count)
            number_text = constructor.number_as_text(count)
            plural_text = constructor.get_plural('package', 'packages', count)
            displayer.update_label('prepare_page__installed_packages_message', 'Found %s installed %s.' % (number_text, plural_text))
            displayer.update_status('prepare_page__installed_packages', OK)
        else:
            logger.log_value('Error. Number of installed packages found', 0)
            displayer.update_label('prepare_page__installed_packages_message', 'Error. No installed packages found.')
            displayer.update_status('prepare_page__installed_packages', ERROR)
            return 'error'
        time.sleep(SLEEP_0500_MS)

        #
        # Create the package manifest for a typical install.
        #

        displayer.update_status('prepare_page__package_manifest_1', PROCESSING)
        time.sleep(SLEEP_0500_MS)
        file_name = 'filesystem.manifest-remove'
        is_exists = is_exists_file_system_manifest_remove(file_name)
        if is_exists:
            removable_packages_list_1 = get_removable_packages_list(file_name)
            count_1 = len(removable_packages_list_1)
            logger.log_value('Number of packages matching typical install list', count_1)
            number_text = constructor.number_as_text(count_1, True)
            plural_text = constructor.get_plural('package is', 'packages are', count_1)
            displayer.update_label(
                'prepare_page__package_manifest_1_message',
                '%s %s flagged for removal after a typical install.' % (number_text,
                                                                        plural_text))
            displayer.update_status('prepare_page__package_manifest_1', OK)
        else:
            removable_packages_list_1 = []
            displayer.update_status('prepare_page__package_manifest_1', OPTIONAL)
            displayer.update_label(
                'prepare_page__package_manifest_1_message',
                'This disk does not have a list of packages to be removed after a typical install.')
        time.sleep(SLEEP_0500_MS)

        #
        # Create the package manifest for a minimal install.
        #

        displayer.update_status('prepare_page__package_manifest_2', PROCESSING)
        time.sleep(SLEEP_0500_MS)
        file_name = 'filesystem.manifest-minimal-remove'
        is_exists = is_exists_file_system_manifest_remove(file_name)
        if is_exists:
            removable_packages_list_2 = get_removable_packages_list(file_name)
            count_2 = len(removable_packages_list_2)
            logger.log_value('Number of packages matching minimal install list', count_2)
            number_text = constructor.number_as_text(count_1 + count_2, True)
            plural_text = constructor.get_plural('package is', 'packages are', count_1 + count_2)
            displayer.update_label(
                'prepare_page__package_manifest_2_message',
                '%s %s flagged for removal after a minimal install.' % (number_text,
                                                                        plural_text))
            displayer.update_status('prepare_page__package_manifest_2', OK)
        else:
            removable_packages_list_2 = []
            displayer.update_status('prepare_page__package_manifest_2', OPTIONAL)
            displayer.update_label(
                'prepare_page__package_manifest_2_message',
                'This disk does not have a list of packages to be removed after a minimal install.')
        time.sleep(SLEEP_0500_MS)

        #
        # Save the package manifests.
        #

        displayer.update_status('prepare_page__save_package_manifest', PROCESSING)
        time.sleep(SLEEP_0500_MS)
        model.package_details_list = create_package_details_list(installed_packages_list, removable_packages_list_1, removable_packages_list_2)
        if installed_packages_list:
            if removable_packages_list_2:
                displayer.set_column_visible('packages_page__remove_2_tree_view_column', True)
            else:
                displayer.set_column_visible('packages_page__remove_2_tree_view_column', False)
            save_file_system_manifest_file(installed_packages_list)
            displayer.update_status('prepare_page__save_package_manifest', OK)
            displayer.update_label('prepare_page__save_package_manifest_message', 'Saved the package manifest file.')
        else:
            displayer.update_status('prepare_page__save_package_manifest', ERROR)
            displayer.update_label('prepare_page__save_package_manifest_message', 'Unable to save the package manifest file.')
        # time.sleep(SLEEP_0500_MS)

        time.sleep(SLEEP_1000_MS)
        return 'next'


def leave(action, new_page=None):

    if action == 'back':

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        return

    elif action == 'next':

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        return

    elif action == 'quit':

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        iso_utilities.unmount_iso_and_delete_mount_point(model.project.iso_mount_point)

        return

    else:

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        iso_utilities.unmount_iso_and_delete_mount_point(model.project.iso_mount_point)

        return 'unknown'


########################################################################
# Handler Functions
########################################################################


def on_size_allocate__prepare_page__boot_kernels_view_port(widget, event, data=None):

    displayer.scroll_view_port_to_bottom('prepare_page__boot_kernels_view_port')


########################################################################
# Support Functions
########################################################################


def add_message_to_boot_kernels_box(message):
    displayer.insert_box_label('prepare_page__boot_kernels_box', message, 0.50)
    time.sleep(SLEEP_0125_MS)


########################################################################
# Linux Kernel Functions
########################################################################

# ----------------------------------------------------------------------
# Kernel Versions
# ----------------------------------------------------------------------

# TODO: Consider using a sorted set so the list doesn't need to be sorted later.


def create_boot_kernel_details_list():
    """
    Get the list of linux kernels from the following directories:
      1. custom-root/boot/vmlinuz-*; initrd.img-*
      2. source-disk/casper/vmlinuz.efi; initrd.lz
    """

    directory_1 = os.path.join(model.project.custom_root_directory, 'boot')
    directory_2 = os.path.join(model.project.iso_mount_point, model.status.casper_directory)
    kernel_details_list = create_kernel_details_list(directory_1, directory_2)

    return kernel_details_list


def create_kernel_details_list(*directories):

    logger.log_label('Create kernel details list')

    #
    # Vmlinuz
    #

    # Create a consolidated vmlinuz details list.
    vmlinuz_details_list = []
    for directory in directories:
        # Real path is necessary here.
        directory = os.path.realpath(directory)
        update_vmlinuz_details_list(directory, vmlinuz_details_list)

    # For debugging.
    # print_details_list(vmlinuz_details_list)

    # Count vmlinuz directories.
    vmlinuz_directory_counter = collections.Counter()
    vmlinuz_directory_counter.update([vmlinuz_details['directory'] for vmlinuz_details in vmlinuz_details_list])
    directories_with_one_vmlinuz = [directory for directory, count in vmlinuz_directory_counter.items() if count == 1]

    #
    # Initrd
    #

    # Create a consolidated initrd details list.
    initrd_details_list = []
    initrd_directory_counter = collections.Counter()
    for directory in directories:
        # Real path is necessary here.
        directory = os.path.realpath(directory)
        update_initrd_details_list(directory, initrd_details_list)

    # Delete temporary files.
    file_path_pattern = os.path.os.path.join(os.sep, 'var', 'tmp', 'unmkinitramfs_*')
    file_utilities.delete_files_with_pattern(file_path_pattern)

    # For debugging.
    # print_details_list(initrd_details_list)

    # Count initrd directories.
    initrd_directory_counter = collections.Counter()
    initrd_directory_counter.update([initrd_details['directory'] for initrd_details in initrd_details_list])
    directories_with_one_initrd = [directory for directory, count in initrd_directory_counter.items() if count == 1]

    #
    # Kernels (vmlinuz and initrd)
    #

    add_message_to_boot_kernels_box('Consolidated kernel files')

    # Create a list of directories that only contain one vmlinuz file
    # and one initrd file.
    directories_with_one_vmlinuz_and_initrd = list(set(directories_with_one_vmlinuz) & set(directories_with_one_initrd))

    # Create a consolidated kernel details list.
    kernel_details_list = []
    _create_kernel_details_list(kernel_details_list, vmlinuz_details_list, initrd_details_list, directories_with_one_vmlinuz_and_initrd)

    # Sort, select kernel, add notes, and remove the 1st column.
    if kernel_details_list:
        _update_kernel_details_list(kernel_details_list)

    # For debugging.
    # print_details_list(kernel_details_list, {'note': 10})

    return kernel_details_list


def _create_kernel_details_list(kernel_details_list, vmlinuz_details_list, initrd_details_list, directories_with_one_vmlinuz_and_initrd):
    """
    Add kernels to kernel_details_list.
    """

    note = ''
    is_selected = False

    for vmlinuz_details in vmlinuz_details_list:

        vmlinuz_version_integers = vmlinuz_details['version_integers']
        vmlinuz_version_name = vmlinuz_details['version_name']
        vmlinuz_file_name = vmlinuz_details['file_name']
        new_vmlinuz_file_name = vmlinuz_details['new_file_name']
        vmlinuz_directory = vmlinuz_details['directory']

        for initrd_details in initrd_details_list:

            initrd_version_integers = initrd_details['version_integers']
            initrd_version_name = initrd_details['version_name']
            initrd_file_name = initrd_details['file_name']
            new_initrd_file_name = initrd_details['new_file_name']
            initrd_directory = initrd_details['directory']

            # 0: version_integers
            # 1: version_name
            # 2: vmlinuz_file_name
            # 3: new_vmlinuz_file_name
            # 4: initrd_file_name
            # 5: new_initrd_file_name
            # 6: directory
            # 7: note
            # 8: is_selected

            if vmlinuz_directory == initrd_directory:
                if vmlinuz_version_name and initrd_version_name:
                    if vmlinuz_version_integers == initrd_version_integers:
                        kernel_details = {
                            'version_integers': vmlinuz_version_integers,
                            'version_name': vmlinuz_version_name,
                            'vmlinuz_file_name': vmlinuz_file_name,
                            'new_vmlinuz_file_name': new_vmlinuz_file_name,
                            'initrd_file_name': initrd_file_name,
                            'new_initrd_file_name': new_initrd_file_name,
                            'directory': vmlinuz_directory,
                            'note': note,
                            'is_selected': is_selected
                        }
                        kernel_details_list.append(kernel_details)
                elif vmlinuz_directory in directories_with_one_vmlinuz_and_initrd:
                    if vmlinuz_version_name and not initrd_version_name:
                        kernel_details = {
                            'version_integers': vmlinuz_version_integers,
                            'version_name': vmlinuz_version_name,
                            'vmlinuz_file_name': vmlinuz_file_name,
                            'new_vmlinuz_file_name': new_vmlinuz_file_name,
                            'initrd_file_name': initrd_file_name,
                            'new_initrd_file_name': new_initrd_file_name,
                            'directory': vmlinuz_directory,
                            'note': note,
                            'is_selected': is_selected
                        }
                        kernel_details_list.append(kernel_details)
                    elif not vmlinuz_version_name and initrd_version_name:
                        kernel_details = {
                            'version_integers': initrd_version_integers,
                            'version_name': initrd_version_name,
                            'vmlinuz_file_name': vmlinuz_file_name,
                            'new_vmlinuz_file_name': new_vmlinuz_file_name,
                            'initrd_file_name': initrd_file_name,
                            'new_initrd_file_name': new_initrd_file_name,
                            'directory': vmlinuz_directory,
                            'note': note,
                            'is_selected': is_selected
                        }
                        kernel_details_list.append(kernel_details)
                    else:
                        kernel_details = {
                            'version_integers': (0,
                                                 0,
                                                 0,
                                                 0),
                            # 'version_name': '0.0.0-0',
                            'version_name': None,
                            'vmlinuz_file_name': vmlinuz_file_name,
                            'new_vmlinuz_file_name': new_vmlinuz_file_name,
                            'initrd_file_name': initrd_file_name,
                            'new_initrd_file_name': new_initrd_file_name,
                            'directory': vmlinuz_directory,
                            'note': note,
                            'is_selected': is_selected
                        }
                        kernel_details_list.append(kernel_details)


def _update_kernel_details_list(kernel_details_list):
    """
    Sort, select kernel, add notes, and remove the 1st column.
    """

    # Reverse sort the kernel details list by kernel version number (1st
    # column).
    #
    # List sort can use a list as the sorting key, and the column values
    # may be tuples, strings, etc. However, list sort can only
    # compare tuples with tuples and stings with strings, and these
    # values may not be None. Since each row of details in
    # kernel_details_list is a dict, this approach uses list compression
    # to create a new list which may be used as the sorting key. The
    # list compression applies a value of (0,0,0,0) if the 1st colum is
    # None, because this column should contain a tuple. It also applies
    # a value of '' for the other columns, if they are None, because the
    # other columns should contain strings. Otherwise, the list
    # compression just uses the column's existing value from the dict
    # when creating the new list for the row.
    kernel_details_list.sort(
        key=lambda details: [(0,
                              0,
                              0,
                              0) if k == 'version_integers' and v is None else '' if v is None else v for k,
                             v in details.items()],
        reverse=True)

    # Set the selected index as the index of the most recent kernel.
    selected_index = 0

    # Set the notes, and update the selected index if necessary.
    # current_kernel_release_name = get_current_kernel_release_name()
    current_kernel_version_name = get_current_kernel_version_name()
    original_iso_image_directory = os.path.join(model.project.iso_mount_point, model.status.casper_directory)
    for index, kernel_details in enumerate(kernel_details_list):
        note = ''
        version_name = kernel_details['version_name']
        if current_kernel_version_name == version_name:
            if note: note += ' '  # os.os.linesep
            note += 'You are currently running kernel version %s.' % current_kernel_version_name
        # if index == 0:
        #     if note: note += ' '  # os.os.linesep
        #     note += 'This is the newest kernel version available to bootstrap the customized disk image.'
        directory = kernel_details['directory']
        if directory == original_iso_image_directory:
            if note: note += ' '  # os.os.linesep
            note += 'This kernel is used to bootstrap the original disk image.'
            if len(kernel_details_list) > 1:
                if note: note += ' '  # os.os.linesep
                note += 'Select this kernel if you encounter issues such as BusyBox when using other kernel versions.'
            # if is_server_image()
            #     # if note: note += ' ' # os.os.linesep
            #     # note += 'Since you are customizing a server image, select this option if you encounter issues using other kernel versions.'
            #     # Set the selected index for the the original disk image kernel.
            #     selected_index = index
        new_vmlinuz_file_name = kernel_details['new_vmlinuz_file_name']
        new_initrd_file_name = kernel_details['new_initrd_file_name']
        if note: note += ' '  # os.os.linesep
        note += 'Reference these files as <span font_family="monospace">%s</span> and <span font_family="monospace">%s</span> in the disk boot configurations.' % (
            new_vmlinuz_file_name,
            new_initrd_file_name)
        kernel_details['note'] = note

    # Set the selected kernel based on the selected index.
    kernel_details_list[selected_index]['is_selected'] = True

    # For debugging.
    # print_details_list(kernel_details_list, {'note': 10})

    # Remove the 1st column because it is a tuple and cannot be rendered.
    # The resulting kernel_details is:
    #
    # 0: version_name
    # 1: vmlinuz_file_name
    # 2: new_vmlinuz_file_name
    # 3: initrd_file_name
    # 4: new_initrd_file_name
    # 5: directory
    # 6: note
    # 7: is_selected
    #
    # It is not necessary to remove the 1st column because because items
    # are selectively added to the list_store in the
    # displayer.update_list_store() function.
    #
    # (list_store_name, data_list)
    # [
    #     kernel_details.pop('version_integers')
    #     for kernel_details in kernel_details_list
    # ]

    # For debugging.
    # print_details_list(kernel_details_list, {'note': 10})

    # Log the resuting list of kernel versions.
    total = len(kernel_details_list)
    for index, kernel_details in enumerate(kernel_details_list):
        logger.log_value('Version', kernel_details['version_name'])
        logger.log_value('▹ Index', '%s of %s' % (index + 1, total))
        logger.log_value('▹ Vmlinuz file name', kernel_details['vmlinuz_file_name'])
        logger.log_value('▹ New vmlinuz file name', kernel_details['new_vmlinuz_file_name'])
        logger.log_value('▹ Initrd file name', kernel_details['initrd_file_name'])
        logger.log_value('▹ New initrd file name', kernel_details['new_initrd_file_name'])
        logger.log_value('▹ Directory', kernel_details['directory'])
        logger.log_value('▹ Note', kernel_details['note'])
        logger.log_value('▹ Is selected', kernel_details['is_selected'])


def get_current_kernel_version_name():

    version_name = None
    try:
        version_information = (r'(\d+\.\d+\.\d+(?:-\d+))', platform.release())
        version_name = version_information.group(1)
    except AttributeError as exception:
        pass

    return version_name


def get_current_kernel_release_name():

    return platform.release()


def is_server_image():

    # Guess if we are customizing a server image by checking the file
    # name, volume id, or disk name. For example:
    # - original.iso_file_name = ubuntu-18.04-live-server-amd64.iso
    # - original.iso_volume_id = Ubuntu-Server 18.04 LTS amd64
    # - original.iso_disk_name = Ubuntu-Server 18.04 LTS "Bionic Beaver" - Release amd64

    if re.search('server', model.original.iso_file_name, re.IGNORECASE):
        return True
    if re.search('server', model.original.iso_volume_id, re.IGNORECASE):
        return True
    if re.search('server', model.original.iso_disk_name, re.IGNORECASE):
        return True

    return False


# ----------------------------------------------------------------------
# Vmlinuz
# ----------------------------------------------------------------------


def update_vmlinuz_details_list(directory, details_list):

    logger.log_label('Create vmlinuz details list')
    logger.log_value('▹ Search directory', directory)

    relative_directory = os.path.relpath(directory, model.project.directory)
    add_message_to_boot_kernels_box('Search for vmlinuz files in %s' % relative_directory)

    file_path_list = []

    # Replace simlinks with the actual file_path.
    directory = os.path.realpath(directory)
    file_path_pattern = os.path.join(directory, 'vmlinuz*')
    for file_path in glob.glob(file_path_pattern):
        # Replace simlinks with the actual file_path.
        real_path = os.path.realpath(file_path)
        if not os.path.exists(real_path):
            # The real path may not exist because it may be relative to
            # the root directory of the virtual environment. If this is
            # the case, the link will appear broken outside of the
            # virtual environment, because it will seem to point to the
            # root of the host system.

            # The following remedies this situation by appending the
            # virtual environment's root directory to the real path.
            # However, if another file with the same path actually
            # exists on the host system, real path will point to that
            # file instead, and this 'if not' block will not be
            # executed. This is considered a negligible risk.

            # TODO: Is there a more reliable remedy?

            # It is necessary to strip the leading '/' from the real
            # path, otherwise os.path.join() considers the real path to be an
            # absolute path and discards the custom root directory
            # prefix: "If a component is an absolute path, all previous
            # components are thrown away and os.path.joining continues from the
            # absolute path component."
            # (See https://docs.python.org/3/library/os.path.html).
            file_path = os.path.abspath(os.path.join(model.project.custom_root_directory, real_path.strip(os.path.sep)))

            # Replace simlinks with the actual file_path.
            real_path = os.path.realpath(file_path)

        if os.path.exists(real_path):
            file_path_list.append(real_path)

    file_path_list = list(set(file_path_list))

    count = len(file_path_list)
    logger.log_value('▹ Number of vmlinuz files found', count)
    number_text = constructor.number_as_text(count)
    plural_text = constructor.get_plural('file', 'files', count)
    add_message_to_boot_kernels_box('Found %s vmlinuz %s' % (number_text, plural_text))
    time.sleep(SLEEP_0250_MS)

    for index, file_path in enumerate(file_path_list):
        file_name = os.path.basename(file_path)
        directory = os.path.dirname(file_path)
        version_name = get_vmlinuz_version_name(file_path)
        # if not version_name: version_name = '0.0.0-0'
        logger.log_value('▹ The vmlinuz version is', version_name)
        if version_name:
            version_integers = tuple(map(int, re.split('[.-]', version_name)))
        else:
            version_integers = tuple(map(int, re.split('[.-]', '0.0.0-0')))
        new_file_name = calculate_vmlinuz_file_name(file_path)

        details = {
            'version_integers': version_integers,
            'version_name': version_name,
            'file_name': file_name,
            'new_file_name': new_file_name,
            'directory': directory
        }
        details_list.append(details)
        time.sleep(SLEEP_0250_MS)


def calculate_vmlinuz_file_name(file_path):

    # Just use vmlinuz (instead of vmlinuz or vmlinuz.efi).
    file_name = 'vmlinuz'

    return file_name


def get_vmlinuz_version_name(file_path):

    # logger.log_value('Get vmlinuz version', file_path)
    # relative_file_path = os.path.relpath(file_path, model.project.directory)
    file_name = os.path.basename(file_path)
    add_message_to_boot_kernels_box('Identify version for %s' % file_name)

    version_name = (
        _get_vmlinuz_version_name_from_file_name(file_path) or _get_vmlinuz_version_name_from_file_type(file_path)
        or _get_vmlinuz_version_name_from_file_contents(file_path))

    # add_message_to_boot_kernels_box('The version is %s' % version_name)
    return version_name


def _get_vmlinuz_version_name_from_file_name(file_path):

    logger.log_value('Get vmlinuz version name from file name', file_path)
    file_name = os.path.basename(file_path)
    version_name = re.search(r'\d[\d\.-]*\d', file_name)
    version_name = version_name.group(0) if version_name else None
    logger.log_value('▹ The version name is', version_name)

    return version_name


def _get_vmlinuz_version_name_from_file_type(file_path):

    logger.log_value('Get vmlinuz version name from file type', file_path)
    command = 'file "%s"' % file_path
    result, exit_status, signal_status = execute_synchronous(command)
    version_name = None
    if not exit_status and not signal_status:
        version_information = re.search(r'(\d+\.\d+\.\d+(?:-\d+))', str(result))
        if version_information:
            version_name = version_information.group(1)
    logger.log_value('▹ The version name is', version_name)

    return version_name


def _get_vmlinuz_version_name_from_file_contents(file_path):

    logger.log_value('Get vmlinuz version name from file contents', file_path)
    version_name = None
    with open(file_path, errors='ignore') as file:
        contents = file.read()
    candidate = ''
    for character in contents:
        if character in string.printable:
            candidate += character
        elif len(candidate) > 4:
            try:
                version_information = re.search(r'(\d+\.\d+\.\d+(?:-\d+))', str(candidate))
                version_name = version_information.group(1)
                break
            except:
                candidate = ''
        else:
            candidate = ''
    logger.log_value('▹ The version name is', version_name)

    return version_name


# ----------------------------------------------------------------------
# Initrd
# ----------------------------------------------------------------------


def update_initrd_details_list(directory, details_list):

    logger.log_label('Create initrd details list')
    logger.log_value('▹ Search directory', directory)

    relative_directory = os.path.relpath(directory, model.project.directory)
    add_message_to_boot_kernels_box('Search for initrd files in %s' % relative_directory)

    file_path_list = []

    # Replace simlinks with the actual file_path.
    directory = os.path.realpath(directory)
    file_path_pattern = os.path.join(directory, 'initrd*')
    for file_path in glob.glob(file_path_pattern):
        # Replace simlinks with the actual file_path.
        real_path = os.path.realpath(file_path)
        if not os.path.exists(real_path):
            # The real path may not exist because it may be relative to
            # the root directory of the virtual environment. If this is
            # the case, the link will appear broken outside of the
            # virtual environment, because it will seem to point to the
            # root of the host system.

            # The following remedies this situation by appending the
            # virtual environment's root directory to the real path.
            # However, if another file with the same path actually
            # exists on the host system, real path will point to that
            # file instead, and this 'if not' block will not be
            # executed. This is considered a negligable risk.

            # TODO: Is there a more reliable remedy?

            # It is necessary to strip the leading '/' from the real
            # path, otherwise os.path.join() considers the real path to be an
            # absolute path and discards the custom root directory
            # prefix: "If a component is an absolute path, all previous
            # components are thrown away and os.path.joining continues from the
            # absolute path component."
            # (See https://docs.python.org/3/library/os.path.html).
            file_path = os.path.abspath(os.path.join(model.project.custom_root_directory, real_path.strip(os.path.sep)))

            # Replace simlinks with the actual file_path.
            real_path = os.path.realpath(file_path)

        if os.path.exists(real_path):
            file_path_list.append(real_path)

    file_path_list = list(set(file_path_list))

    count = len(file_path_list)
    logger.log_value('▹ Number of initrd files found', count)
    number_text = constructor.number_as_text(count)
    plural_text = constructor.get_plural('file', 'files', count)
    add_message_to_boot_kernels_box('Found %s initrd %s' % (number_text, plural_text))
    time.sleep(SLEEP_0250_MS)

    for index, file_path in enumerate(file_path_list):
        file_name = os.path.basename(file_path)
        directory = os.path.dirname(file_path)
        version_name = get_initrd_version_name(file_path)
        # if not version_name: version_name = '0.0.0-0'
        logger.log_value('▹ The initrd version is', version_name)
        if version_name:
            version_integers = tuple(map(int, re.split('[.-]', version_name)))
        else:
            version_integers = tuple(map(int, re.split('[.-]', '0.0.0-0')))
        new_file_name = calculate_initrd_file_name(file_path)

        details = {
            'version_integers': version_integers,
            'version_name': version_name,
            'file_name': file_name,
            'new_file_name': new_file_name,
            'directory': directory
        }
        details_list.append(details)
        time.sleep(SLEEP_0250_MS)


def calculate_initrd_file_name(file_path):

    # logger.log_value('Calculate initrd file name', file_path)

    compression_format = get_initrd_compression_format(file_path)
    compression_extension = COMPRESSION_EXTENSIONS.get(compression_format)
    if compression_extension:
        file_name = 'initrd.' + compression_extension
    else:
        file_name = 'initrd'

    return file_name


def get_initrd_compression_format(file_path):

    # logger.log_value('Get initrd compression format', file_path)

    file_name = os.path.basename(file_path)
    add_message_to_boot_kernels_box('Identify correct compression format for %s' % file_name)

    compression_format = (_get_initrd_compression_format_from_file_type(file_path) or _get_initrd_compression_format_from_file_contents(file_path))

    logger.log_value('The compression format is', compression_format)

    return compression_format


def _get_initrd_compression_format_from_file_type(file_path):
    """
    Get the compression format in lower case.
    Valid compression formats are 'gzip', 'bzip2', 'lz4', 'lzma', 'lzop', and 'xz'.
    """

    logger.log_value('Get initrd compression format from file type', file_path)

    command = 'file "%s"' % file_path
    result, exit_status, signal_status = execute_synchronous(command)
    logger.log_value('The initrd file type information is', result)

    compression_format = None
    match = re.search(r':\s(.*)\scompressed data', result)
    if match:
        compression_format = match.group(1).lower()
        logger.log_value('Initrd compression format found?', 'Yes')
    else:
        logger.log_value('Initrd compression format found?', 'No')

    return compression_format


def _get_initrd_compression_format_from_file_contents(file_path):
    """
    Get the compression format in lower case.
    Valid compression formats are 'gzip', 'bzip2', 'lz4', 'lzma', 'lzop', and 'xz'.
    """

    logger.log_value('Get initrd compression format from file contents', file_path)
    compression_format = None
    try:
        # Only show results that match "compressed data"
        command = 'binwalk --include="compressed data" "%s"' % file_path
        process = execute_asynchronous(command)

        # Assume the first occurrence "compressed data" contains the
        # compression format used. This immediately follows the line:
        # ASCII cpio archive (SVR4 with no CRC), file name: "TRAILER!!!"
        process.expect(INITRAMFS_COMPRESSION_PATTERN)
        # Close the process to obtain the exit status, if needed.
        process.close()
        logger.log_value('The initrd file contents information is', process.match.group(0))
        compression_format = process.match.group(1).lower()
        logger.log_value('Initrd compression format found?', 'Yes')
    except IndexError as exception:
        process.close()
        logger.log_value('Initrd compression format found?', 'No')
    except Exception as exception:
        # Exceptions include TIMEOUT, EOF, ExceptionPexpect, or IndexError.
        # Close the process to obtain the exit status, if needed.
        process.close()
        logger.log_value('Initrd compression format found?', 'No')
        logger.log_value('Encountered an exception while getting initrd compression format from file contents', exception)

    return compression_format


def get_vmlinuz_version_from_kernel_details_list(kernel_details_list, directory):

    # The kernel_details is:
    # 0: version_integers
    # 1: version_name
    # 2: vmlinuz_file_name
    # 3: new_vmlinuz_file_name
    # 4: initrd_file_name
    # 5: new_initrd_file_name
    # 6: directory
    # 7: note
    # 8: is_selected

    version_name = '0.0.0-0'
    for kernel_details in kernel_details_list:
        if directory == kernel_details[6]:
            version_name = kernel_details[1]
            break
    return version_name


def get_initrd_version_name(file_path):

    # logger.log_value('Get initrd version', file_path)
    # TODO: Investigate if relative file path should have been used below.
    # relative_file_path = os.path.relpath(file_path, model.project.directory)
    # add_message_to_boot_kernels_box('▹ Processing .../%s' % relative_file_path)
    file_name = os.path.basename(file_path)
    add_message_to_boot_kernels_box('Identify version for %s' % file_name)

    version_name = (
        _get_initrd_version_name_from_file_name(file_path) or _get_initrd_version_name_from_file_contents(file_path)
        or _get_initrd_version_name_from_file_type(file_path))

    # add_message_to_boot_kernels_box('The version is %s' % version_name)
    return version_name


def _get_initrd_version_name_from_file_name(file_path):

    logger.log_value('Get initrd version name from file name', file_path)
    file_name = os.path.basename(file_path)
    version_name = re.search(r'\d[\d\.-]*\d', file_name)
    version_name = version_name.group(0) if version_name else None

    return version_name


def _get_initrd_version_name_from_file_type(file_path):

    logger.log_value('Get initrd version name from file type', file_path)
    command = 'file "%s"' % file_path
    result, exit_status, signal_status = execute_synchronous(command)
    version_name = None
    if not exit_status and not signal_status:
        version_information = re.search(r'(\d+\.\d+\.\d+(?:-\d+))', str(result))
        if version_information:
            version_name = version_information.group(1)
    logger.log_value('▹ The version name is', version_name)

    return version_name


def _get_initrd_version_name_from_file_contents(file_path):

    logger.log_value('Get initrd version name from file contents', file_path)
    version_name = None
    try:
        command = 'lsinitramfs "%s"' % file_path
        process = execute_asynchronous(command)
        process.expect(INITRAMFS_VERSION_PATTERN)
        # Close the process to obtain the exit status, if needed.
        process.close()
        version_name = process.match.group(1)
    except Exception as exception:
        # Exceptions include TIMEOUT, EOF, ExceptionPexpect, or IndexError.
        # Close the process to obtain the exit status, if needed.
        process.close()
        logger.log_value('Encountered an exception while getting initrd version name from file contents', exception)

    logger.log_value('▹ The version name is', version_name)

    return version_name


# ----------------------------------------------------------------------
# Print
# ----------------------------------------------------------------------


# For debugging only.
def get_widths(details_list, default_widths):
    """
    details_list   - a list of lists or dicts
    default_widths - dictionary of str:int
    """
    widths = {}
    for details in details_list:
        if not isinstance(details, dict):
            # Assume details is a list; convert into a dictionary.
            details = {index: details[index] for index in range(0, len(details))}
        for key, value in details.items():
            if key in default_widths:
                widths[key] = default_widths[key]
            else:
                value_width = 0 if value is None else len(str(value))
                saved_width = 0 if key not in widths else widths[key]
                widths[key] = max(saved_width, value_width)
    return widths


# For debugging only.
def print_details_list(details_list, default_widths={}):
    """
    details_list   - a list of lists or dicts
    default_widths - dictionary of str:int
    """
    total = len(details_list)
    widths = get_widths(details_list, default_widths)
    index_width = len(str(total))
    for index, details in enumerate(details_list):
        print(('| {:%d}' % index_width).format(index + 1), end='')
        print((' of {:%d}' % index_width).format(total), end='')
        if not isinstance(details, dict):
            # Assume details is a list; convert into a dictionary.
            details = {index: details[index] for index in range(0, len(details))}
        for key in widths.keys():
            width = widths[key]
            if width:
                value = str(details[key])
                print((' | {:%s.%s}' % (width, width)).format(value), end='')
        print(' |')


########################################################################
# Filesystem Manifest Functions
########################################################################


# TODO: This function is needed on multiple pages. Consider refactoring.
#       - packages_page
#       - prepare_page
def is_exists_file_system_manifest_remove(file_name):

    # Check custom disk directory
    file_path = os.path.join(model.project.custom_disk_directory, model.status.casper_directory, file_name)

    is_exists = os.path.exists(file_path)
    if is_exists:
        logger.log_value('%s found in' % file_name, os.path.join(model.project.custom_disk_directory, model.status.casper_directory))
        return True
    else:
        logger.log_value('%s not found in' % file_name, os.path.join(model.project.custom_disk_directory, model.status.casper_directory))
        return False


def create_installed_packages_list():

    logger.log_label('Create list of installed packages')

    # command = 'chroot "%s" dpkg-query -W' % model.project.custom_root_directory
    # command = 'chroot "%s" dpkg-query --showformat="${Package}\t${Version}\n" --show' % model.project.custom_root_directory
    # command = 'chroot "%s" dpkg-query --show' % model.project.custom_root_directory
    # command = 'pkexec chroot "%s" dpkg-query --show' % model.project.custom_root_directory
    dpkg_database_directory = os.path.join(model.project.custom_root_directory, 'var', 'lib', 'dpkg')
    command = 'dpkg-query --show --admindir="%s"' % dpkg_database_directory
    result, exit_status, signal_status = execute_synchronous(command)
    installed_packages_list = result.splitlines()

    package_count = len(installed_packages_list)
    logger.log_value('Total number of installed packages', package_count)

    return installed_packages_list


def save_file_system_manifest_file(installed_packages_list):

    logger.log_label('Create new file system manifest file')

    file_path = os.path.join(model.project.custom_disk_directory, model.status.casper_directory, 'filesystem.manifest')
    logger.log_value('Write file system manifest to', file_path)
    with open(file_path, 'w') as file:
        for line in installed_packages_list:
            file.write('%s\n' % line)


def get_removable_packages_list(file_name):

    # Read filesystem.manifest-remove to get list of packages to remove.
    removable_packages_list = []
    file_path = os.path.join(model.project.custom_disk_directory, model.status.casper_directory, file_name)
    logger.log_value('Read list of packages to remove from', file_path)
    with open(file_path, 'r') as file:
        removable_packages_list = file.read().splitlines()

    return removable_packages_list


def create_package_details_list(installed_packages_list, removable_packages_list_1, removable_packages_list_2):
    logger.log_label('Create package details list')

    # List installed packages and mark packages that will be removed.

    number_of_packages_to_remove_1 = 0
    number_of_packages_to_retain_1 = 0
    number_of_packages_to_remove_2 = 0
    number_of_packages_to_retain_2 = 0
    package_details_list = []

    for line in installed_packages_list:

        package_details = line.split()
        package_name = package_details[0]

        # Somme package names in installed_packages_list specify the
        # architecture suffix (ex. gir1.2-rb-3.0:amd64).
        # However, removable_packages_list may or may not contain
        # packages with the architectre suffix (ex. gir1.2-rb-3.0).
        # • filesystem.manifest-remove lists packages with the
        #   architectre suffix.
        # • filesystem.manifest-minimal-remove lists packages without
        #   the architectre suffix.
        # Therefore, check the package name with and without the
        # architectre suffix.

        is_remove_1 = (package_name in removable_packages_list_1) or (package_name.rpartition(':')[0] in removable_packages_list_1)
        number_of_packages_to_remove_1 += is_remove_1
        number_of_packages_to_retain_1 += not is_remove_1

        is_remove_2 = (package_name in removable_packages_list_2) or (package_name.rpartition(':')[0] in removable_packages_list_2)
        number_of_packages_to_remove_2 += is_remove_2
        number_of_packages_to_retain_2 += not is_remove_2

        # Insert columns at the beginning of package_details to indicate if the
        # package_name should be removed (True) or kept (False).

        # Set typical check button selected or unselected
        package_details.insert(0, is_remove_1)
        # Set minimal check button selected or unselected
        package_details.insert(1, is_remove_2 or is_remove_1)
        # Backup original minimal check button value
        package_details.insert(2, is_remove_2)
        # Set minimal check button active or inactive
        package_details.insert(3, not is_remove_1)

        package_details_list.append(package_details)

    logger.log_value('Total number of installed packages', len(installed_packages_list))
    logger.log_value('Number of packages to be removed after a typical install', number_of_packages_to_remove_1)
    logger.log_value('Number of packages to be retained after a typical install', number_of_packages_to_retain_1)
    logger.log_value('Number of packages to be removed after a minimal install', number_of_packages_to_remove_2)
    logger.log_value('Number of packages to be retained after a minimal install', number_of_packages_to_retain_2)

    return package_details_list
