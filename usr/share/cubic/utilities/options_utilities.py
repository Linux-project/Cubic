#!/usr/bin/python3

########################################################################
#                                                                      #
# options_utilities.py                                                 #
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
# Imports
########################################################################

from utilities import logger
from utilities import model
from utilities.process_utilities import execute_synchronous

import glob
import os
import pexpect
import platform
import re
import string
import traceback

########################################################################
# Manage Linux Kernels Functions
########################################################################

# ------------------------------------------------------------------------------
# Kernel Versions
# ------------------------------------------------------------------------------


def create_kernel_details_list(*directories):
    logger.log_label('Create kernel details list')

    # Create a consolidated kernel details list.
    kernel_details_list = []
    for directory in directories:
        # Realpath is necessary here.
        directory = os.path.realpath(directory)
        update_kernel_details_list_for_vmlinuz(directory, kernel_details_list)
        update_kernel_details_list_for_initrd(directory, kernel_details_list)

    # The resulting kernel_details is:
    # 0: version_integers
    # 1: version_name
    # 2: vmlinuz_filename
    # 3: new_vmlinuz_filename
    # 4: initrd_filename
    # 5: new_initrd_filename
    # 6: directory
    # 7: note
    # 8: is_selected
    # 9: is_remove

    # For debugging.
    # print_kernel_details_list(kernel_details_list)

    # total = len(kernel_details_list)
    # for index, kernel_details in enumerate(kernel_details_list):
    #     logger.log_value('version', kernel_details[0])
    #     logger.log_value('version', kernel_details[1])
    #     logger.log_value('• Index', '%s of %s' % (index, total - 1))
    #     logger.log_value('• Vmlinuz filename', kernel_details[2])
    #     logger.log_value('• New vmlinuz filename', kernel_details[3])
    #     logger.log_value('• Initrd filename', kernel_details[4])
    #     logger.log_value('• New initrd filename', kernel_details[5])
    #     logger.log_value('• Directory', kernel_details[6])
    #     logger.log_value('• Note', kernel_details[7])
    #     logger.log_value('• Is selected', kernel_details[8])
    #     # logger.log_value('• Is remove', kernel_details[9]

    # Remove kernels that do not have both vmlinuz filename and initrd filename.
    kernel_details_list = [kernel_details for kernel_details in kernel_details_list if kernel_details[2] and kernel_details[4]]

    # For debugging.
    # print_kernel_details_list(kernel_details_list)

    # total = len(kernel_details_list)
    # for index, kernel_details in enumerate(kernel_details_list):
    #     logger.log_value('version', kernel_details[0])
    #     logger.log_value('version', kernel_details[1])
    #     logger.log_value('• Index', '%s of %s' % (index, total - 1))
    #     logger.log_value('• Vmlinuz filename', kernel_details[2])
    #     logger.log_value('• New vmlinuz filename', kernel_details[3])
    #     logger.log_value('• Initrd filename', kernel_details[4])
    #     logger.log_value('• New initrd filename', kernel_details[5])
    #     logger.log_value('• Directory', kernel_details[6])
    #     logger.log_value('• Note', kernel_details[7])
    #     logger.log_value('• Is selected', kernel_details[8])
    #     # logger.log_value('• Is remove', kernel_details[9]

    # Reverse sort the kernel details list by kernel version number (1st column).
    kernel_details_list.sort(key=lambda list: ['' if value is None else value for value in list], reverse=True)

    # Set the new vmlinuz filename.
    # Set the new initrd filename.
    for kernel_details in kernel_details_list:
        directory = kernel_details[6]
        vmlinuz_filename = kernel_details[2]
        vmlinuz_filepath = os.path.join(directory, vmlinuz_filename)
        new_vmlinuz_filename = calculate_vmlinuz_filename(vmlinuz_filepath)
        kernel_details[3] = new_vmlinuz_filename
        initrd_filename = kernel_details[4]
        initrd_filepath = os.path.join(directory, initrd_filename)
        new_initrd_filename = calculate_initrd_filename(initrd_filepath)
        kernel_details[5] = new_initrd_filename

    # Set the selected index as the index of the most recent kernel.
    selected_index = 0

    # Set the notes, and update the selected index if necessary.
    current_kernel_release_name = get_current_kernel_release_name()
    current_kernel_version_name = get_current_kernel_version_name()
    original_iso_directory = os.path.join(model.project.iso_mount_point, model.status.casper_directory)
    for index, kernel_details in enumerate(kernel_details_list):
        note = ''
        version_name = kernel_details[1]
        if current_kernel_version_name == version_name:
            if note:
                note += ' '  # os.linesep
            note += 'This is the kernel version you are currently running.'
        if index == 0:
            if note:
                note += ' '  # os.linesep
            note += 'This is the newest kernel version that may be used to bootstrap the customized live ISO image.'
        directory = kernel_details[6]
        if directory == original_iso_directory:
            if note:
                note += ' '  # os.linesep
            note += 'This kernel is used to bootstrap the original live ISO image.'
            if len(kernel_details_list) > 1:
                if note:
                    note += ' '  # os.linesep
                note += 'Select this kernel if you encounter issues such as BusyBox when using other kernel versions.'
            # if is_server_image()
            #     # if note: note += ' ' # os.linesep
            #     # note += 'Since you are customizing a server image, select this option if you encounter issues using other kernel versions.'
            #     # Set the selected index for the the original live ISO image kernel.
            #     selected_index = index
        new_vmlinuz_filename = kernel_details[3]
        new_initrd_filename = kernel_details[5]
        if note:
            note += ' '  # os.linesep
        note += 'Reference these files as <tt>%s</tt> and <tt>%s</tt> in the ISO boot configurations.' % (new_vmlinuz_filename, new_initrd_filename)
        kernel_details[7] = note

    # For debugging.
    # TODO: add if debug like in progress module.
    print_kernel_details_list(kernel_details_list)

    # Set the selected kernel based on the selected index.
    if kernel_details_list:
        kernel_details_list[selected_index][8] = True

    # Remove the 1st column because it is a tuple and cannot be rendered.
    # The resulting kernel_details is:
    # 0: version_name
    # 1: vmlinuz_filename
    # 2: new_vmlinuz_filename
    # 3: initrd_filename
    # 4: new_initrd_filename
    # 5: directory
    # 6: note
    # 7: is_selected
    # 8: is_remove
    [kernel_details.pop(0) for kernel_details in kernel_details_list]

    # Log the resuting list of kernel versions.
    total = len(kernel_details_list)
    for index, kernel_details in enumerate(kernel_details_list):
        logger.log_value('version', kernel_details[0])
        logger.log_value('• Index', '%s of %s' % (index, total - 1))
        logger.log_value('• Vmlinuz filename', kernel_details[1])
        logger.log_value('• New vmlinuz filename', kernel_details[2])
        logger.log_value('• Initrd filename', kernel_details[3])
        logger.log_value('• New initrd filename', kernel_details[4])
        logger.log_value('• Directory', kernel_details[5])
        logger.log_value('• Note', kernel_details[6])
        logger.log_value('• Is selected', kernel_details[7])
        # logger.log_value('• Is remove', kernel_details[8])

    return kernel_details_list


# For debugging only.
def print_kernel_details_list(kernel_details_list):
    total = len(kernel_details_list)
    for index, kernel_details in enumerate(kernel_details_list):
        print_kernel_details(kernel_details, index, total)


# For debugging only.
def print_kernel_details(kernel_details, index, total):
    print(
        '| '
        '{:13.13s} | '
        '{:8.8s} | '
        '{:6.6s} | '
        'Vmlinuz: {:15.15s} | '
        'New: {:15.15s} | '
        'Initrd: {:15.15s} | '
        'New: {:15.15s} | '
        'Directory: {:50.50s} | '
        'Note: {:5.5s} | '
        'Selected: {:5.5s} | '
        'Remove: {:5.5s} | '.format(
            str(kernel_details[0]),
            str(kernel_details[1]),
            '%s of %s' % (index,
                          total - 1),
            str(kernel_details[2]),
            str(kernel_details[3]),
            str(kernel_details[4]),
            str(kernel_details[5]),
            str(kernel_details[6]),
            str(kernel_details[7]),
            str(kernel_details[8]),
            str(kernel_details[9])))


def get_current_kernel_version_name():
    version_name = None
    try:
        version_information = re.search(r'(\d+\.\d+\.\d+(?:-\d+))', platform.release())
        version_name = version_information.group(1)
    except AttributeError as exception:
        pass

    return version_name


def get_current_kernel_release_name():
    return platform.release()


def is_server_image():
    # Guess if we are customizing a server image by checking the file
    # name, volume id, or disk name. For example:
    # - original_iso_filename = ubuntu-18.04-live-server-amd64.iso
    # - original_iso_volume_id = Ubuntu-Server 18.04 LTS amd64
    # - original_iso_disk_name = Ubuntu-Server 18.04 LTS "Bionic Beaver" - Release amd64

    if re.search('server', model.original.iso_filename, re.IGNORECASE):
        return True
    if re.search('server', model.original.iso_volume_id, re.IGNORECASE):
        return True
    if re.search('server', model.original.iso_disk_name, re.IGNORECASE):
        return True

    return False


# ------------------------------------------------------------------------------
# Vmlinuz
# ------------------------------------------------------------------------------


def update_kernel_details_list_for_vmlinuz(directory, kernel_details_list):

    logger.log_label('Update kernel details list for vmlinuz')
    filepath_pattern = os.path.join(directory, 'vmlinuz*')
    # Exclude broken symlinks.
    vmlinuz_filepath_list = [vmlinuz_filepath for vmlinuz_filepath in glob.glob(filepath_pattern) if os.path.exists(vmlinuz_filepath)]
    logger.log_value('%i vmlinuz files found in' % len(vmlinuz_filepath_list), directory)
    for vmlinuz_filepath in vmlinuz_filepath_list:
        vmlinuz_filename = os.path.basename(vmlinuz_filepath)
        logger.log_label('Get vmlinuz version details')
        version_name = get_vmlinuz_version_name(vmlinuz_filepath)
        if not version_name:
            version_name = '0.0.0-0'
        logger.log_value('The vmlinuz version is', version_name)
        version_integers = tuple(map(int, re.split('[.-]', version_name)))
        update_kernel_details_for_vmlinuz(version_integers, version_name, vmlinuz_filename, directory, kernel_details_list)


def update_kernel_details_list_for_vmlinuz_EXPERIMENT(directory, kernel_details_list):

    logger.log_label('Update kernel details list for vmlinuz')
    filepath_pattern = os.path.join(directory, 'vmlinuz*')
    # vmlinuz_filepath_list = glob.glob(filepath_pattern)
    # vmlinuz_filepath_list = [ vmlinuz_filepath for vmlinuz_filepath in vmlinuz_filepath_list if os.path.exists(vmlinuz_filepath) ]
    vmlinuz_filepath_list = [vmlinuz_filepath for vmlinuz_filepath in glob.glob(filepath_pattern) if os.path.exists(vmlinuz_filepath)]
    logger.log_value('%i vmlinuz files found in' % len(vmlinuz_filepath_list), directory)
    for vmlinuz_filepath in vmlinuz_filepath_list:
        vmlinuz_filename = os.path.basename(vmlinuz_filepath)
        logger.log_label('Get vmlinuz version details')
        version_name = get_vmlinuz_version_name(vmlinuz_filepath)
        if not version_name:
            version_name = '0.0.0-0'
        logger.log_value('The vmlinuz version is', version_name)
        version_integers = tuple(map(int, re.split('[.-]', version_name)))
        update_kernel_details_for_vmlinuz(version_integers, version_name, vmlinuz_filename, directory, kernel_details_list)


def update_kernel_details_list_for_vmlinuz_ORIGINAL(directory, kernel_details_list):

    logger.log_label('Update kernel details list for vmlinuz')
    filepath_pattern = os.path.join(directory, 'vmlinuz*')
    vmlinuz_filepath_list = glob.glob(filepath_pattern)
    logger.log_value('%i vmlinuz files found in' % len(vmlinuz_filepath_list), directory)
    for vmlinuz_filepath in vmlinuz_filepath_list:
        vmlinuz_filename = os.path.basename(vmlinuz_filepath)
        logger.log_label('Get vmlinuz version details')
        version_name = get_vmlinuz_version_name(vmlinuz_filepath)
        if not version_name:
            version_name = '0.0.0-0'
        logger.log_value('The vmlinuz version is', version_name)
        version_integers = tuple(map(int, re.split('[.-]', version_name)))
        update_kernel_details_for_vmlinuz(version_integers, version_name, vmlinuz_filename, directory, kernel_details_list)


def update_kernel_details_for_vmlinuz(version_integers, version_name, vmlinuz_filename, directory, kernel_details_list):

    logger.log_label('Search kernel details list for matching version')
    logger.log_value('• Kernel version', version_name)
    logger.log_value('• Kernel version as integers', version_integers)
    logger.log_value('• Vmlinuz filename', vmlinuz_filename)
    logger.log_value('• Directory', directory)

    # 0: version_integers
    # 1: version_name
    # 2: vmlinuz_filename
    # 3: new_vmlinuz_filename
    # 4: initrd_filename
    # 5: new_initrd_filename
    # 6: directory
    # 7: note
    # 8: is_selected
    # 9: is_remove

    found = False
    for index, kernel_details in enumerate(list(kernel_details_list)):
        if (kernel_details[0] == version_integers and kernel_details[1] == version_name and kernel_details[6] == directory):
            found = True
            logger.log_value('• Matching kernel version found?', 'Yes')
            total = len(kernel_details_list)
            logger.log_value('• Index of match', '%i of %i' % (index, total - 1))
            if not kernel_details[2]:
                logger.log_label('Update kernel details')
                kernel_details[2] = vmlinuz_filename
                logger.log_value('• Index', '%s of %s' % (index, total - 1))
            elif kernel_details[2] == vmlinuz_filename:
                logger.log_label('Skip updating kernel details')
                logger.log_value('• Index', '%s of %s' % (index, total - 1))
            else:
                logger.log_label('Copy and add kernel details')
                kernel_details = list(kernel_details)
                kernel_details[2] = vmlinuz_filename
                kernel_details_list.append(kernel_details)
                total = len(kernel_details_list)
                logger.log_value('• Index', '%s of %s' % (total - 1, total - 1))

    if not found:
        logger.log_value('• Matching kernel version found?', 'No')

        logger.log_label('Add new kernel details')

        kernel_details = [None] * 10
        if not version_integers:
            version_integers = (0, 0, 0)
        kernel_details[0] = version_integers
        kernel_details[1] = version_name
        kernel_details[2] = vmlinuz_filename
        kernel_details[3] = None  # new_vmlinuz_filename
        kernel_details[4] = None  # initrd_filename
        kernel_details[5] = None  # new_initrd_filename
        kernel_details[6] = directory
        kernel_details[7] = None  # note
        kernel_details[8] = False  # is_selected
        kernel_details[9] = False  # is_remove
        kernel_details_list.append(kernel_details)

        total = len(kernel_details_list)
        logger.log_value('• Index', '%s of %s' % (total - 1, total - 1))

    logger.log_value('• Kernel version', kernel_details[1])
    logger.log_value('• Kernel version as integers', kernel_details[0])
    logger.log_value('• Vmlinuz filename', kernel_details[2])
    logger.log_value('• Initrd filename', kernel_details[4])
    logger.log_value('• Directory', kernel_details[6])


def update_kernel_details_for_vmlinuz_ORIGINAL(version_integers, version_name, vmlinuz_filename, directory, kernel_details_list):

    logger.log_label('Search kernel details list for matching version')
    logger.log_value('• Kernel version', version_name)
    logger.log_value('• Kernel version as integers', version_integers)
    logger.log_value('• Vmlinuz filename', vmlinuz_filename)
    logger.log_value('• Directory', directory)

    # 0: version_integers
    # 1: version_name
    # 2: vmlinuz_filename
    # 3: new_vmlinuz_filename
    # 4: initrd_filename
    # 5: new_initrd_filename
    # 6: directory
    # 7: note
    # 8: is_selected
    # 9: is_remove

    found = False
    for index, kernel_details in enumerate(list(kernel_details_list)):
        if (kernel_details[0] == version_integers and kernel_details[1] == version_name and kernel_details[6] == directory):
            found = True
            if kernel_details[2] == vmlinuz_filename:
                logger.log_value('• Matching kernel version found?', 'Yes')
                total = len(kernel_details_list)
                logger.log_value('• Index of match', '%i of %i' % (index, total - 1))

                logger.log_label('Skip updating kernel details')

                logger.log_value('• Index', '%s of %s' % (index, total - 1))
                logger.log_value('• Kernel version', kernel_details[1])
                logger.log_value('• Kernel version as integers', kernel_details[0])
                logger.log_value('• Vmlinuz filename', kernel_details[2])
                logger.log_value('• Initrd filename', kernel_details[4])
                logger.log_value('• Directory', kernel_details[6])
                break  # TODO: break is not needed here.
            elif not kernel_details[2]:
                logger.log_value('• Matching kernel version found?', 'Yes')
                total = len(kernel_details_list)
                logger.log_value('• Index of match', '%i of %i' % (index, total - 1))

                logger.log_label('Update kernel details')
                kernel_details[2] = vmlinuz_filename

                logger.log_value('• Index', '%s of %s' % (index, total - 1))
                logger.log_value('• Kernel version', kernel_details[1])
                logger.log_value('• Kernel version as integers', kernel_details[0])
                logger.log_value('• Vmlinuz filename', kernel_details[2])
                logger.log_value('• Initrd filename', kernel_details[4])
                logger.log_value('• Directory', kernel_details[6])
            else:
                logger.log_value('• Matching kernel version found?', 'Yes')
                total = len(kernel_details_list)
                logger.log_value('• Index of match', '%i of %i' % (index, total - 1))

                logger.log_label('Copy and add kernel details')
                kernel_details = list(kernel_details)
                kernel_details[2] = vmlinuz_filename
                kernel_details_list.append(kernel_details)

                total = len(kernel_details_list)
                logger.log_value('• Index', '%s of %s' % (total - 1, total - 1))
                logger.log_value('• Kernel version', kernel_details[1])
                logger.log_value('• Kernel version as integers', kernel_details[0])
                logger.log_value('• Vmlinuz filename', kernel_details[2])
                logger.log_value('• Initrd filename', kernel_details[4])
                logger.log_value('• Directory', kernel_details[6])
    if not found:
        logger.log_value('• Matching kernel version found?', 'No')

        logger.log_label('Add new kernel details')

        kernel_details = [None] * 10
        if not version_integers:
            version_integers = (0, 0, 0)
        kernel_details[0] = version_integers
        kernel_details[1] = version_name
        kernel_details[2] = vmlinuz_filename
        kernel_details[3] = None  # new_vmlinuz_filename
        kernel_details[4] = None  # initrd_filename
        kernel_details[5] = None  # new_initrd_filename
        kernel_details[6] = directory
        kernel_details[7] = None  # note
        kernel_details[8] = False  # is_selected
        kernel_details[9] = False  # is_remove
        kernel_details_list.append(kernel_details)

        total = len(kernel_details_list)
        logger.log_value('• Index', '%s of %s' % (total - 1, total - 1))
        logger.log_value('• Kernel version', kernel_details[1])
        logger.log_value('• Kernel version as integers', kernel_details[0])
        logger.log_value('• Vmlinuz filename', kernel_details[2])
        logger.log_value('• Initrd filename', kernel_details[4])
        logger.log_value('• Directory', kernel_details[6])


def get_vmlinuz_version_name(filepath):

    # logger.log_value('Get vmlinuz version', filepath)
    version_name = (_get_vmlinuz_version_name_from_file_name(filepath) or _get_vmlinuz_version_name_from_file_type(filepath) or _get_vmlinuz_version_name_from_file_contents(filepath))

    return version_name


def _get_vmlinuz_version_name_from_file_name(filepath):

    logger.log_value('Get vmlinuz version from file name', filepath)
    filename = os.path.basename(filepath)
    version_name = re.search(r'\d[\d\.-]*\d', filename)
    version_name = version_name.group(0) if version_name else None

    return version_name


def _get_vmlinuz_version_name_from_file_type(filepath):

    logger.log_value('Get vmlinuz version from file type', filepath)
    command = 'file "%s"' % filepath
    result, exitstatus, signalstatus = execute_synchronous(command)
    version_name = None
    if not exitstatus and not signalstatus:
        version_information = re.search(r'(\d+\.\d+\.\d+(?:-\d+))', str(result))
        if version_information:
            version_name = version_information.group(1)
            logger.log_value('Found version', version_name)

    return version_name


def _get_vmlinuz_version_name_from_file_contents(filepath):

    logger.log_value('Get vmlinuz version from file contents', filepath)
    version_name = None
    with open(filepath, errors='ignore') as file:
        contents = file.read()
    candidate = ''
    for character in contents:
        if character in string.printable:
            candidate += character
        elif len(candidate) > 4:
            try:
                version_information = re.search(r'(\d+\.\d+\.\d+(?:-\d+))', str(candidate))
                version_name = version_information.group(1)
                logger.log_value('Found version', version_name)
                break
            except:
                candidate = ''
        else:
            candidate = ''

    return version_name


def calculate_vmlinuz_filename(filepath):

    # Just use vmlinuz (instead of vmlinuz or vmlinuz.efi).
    filename = 'vmlinuz'

    return filename


# ------------------------------------------------------------------------------
# Initrd
# ------------------------------------------------------------------------------


def update_kernel_details_list_for_initrd(directory, kernel_details_list):

    logger.log_label('Update kernel details list for initrd')
    filepath_pattern = os.path.join(directory, 'initrd*')
    # Exclude broken symlinks.
    initrd_filepath_list = [initrd_filepath for initrd_filepath in glob.glob(filepath_pattern) if os.path.exists(initrd_filepath)]
    logger.log_value('%i initrd files found in' % len(initrd_filepath_list), directory)
    for initrd_filepath in initrd_filepath_list:
        initrd_filename = os.path.basename(initrd_filepath)
        logger.log_label('Get initrd version details')
        version_name = get_initrd_version_name(initrd_filepath)

        # TODO: See if this hack can be improved?
        # As a last resort, grab the first vmlinuz version from this
        # directory, and assume the initrd version is the same. The
        # situation where the initrd version is unknown should only
        # happen in the casper directory of the ISO; this is a critical
        # assumption. In the casper directory, the initrd version should
        # correspond to the vmlinuz version, and it is reasonable to
        # simply use the vmlinuz version, whenever the version of initrd
        # cannot be determined in this directory.
        if not version_name:
            version_name = get_vmlinuz_version_from_kernel_details_list(kernel_details_list, directory)

        logger.log_value('The initrd version is', version_name)
        version_integers = tuple(map(int, re.split('[.-]', version_name)))
        update_kernel_details_for_initrd(version_integers, version_name, initrd_filename, directory, kernel_details_list)


def get_vmlinuz_version_from_kernel_details_list(kernel_details_list, directory):

    # The kernel_details is:
    # 0: version_integers
    # 1: version_name
    # 2: vmlinuz_filename
    # 3: new_vmlinuz_filename
    # 4: initrd_filename
    # 5: new_initrd_filename
    # 6: directory
    # 7: note
    # 8: is_selected
    # 9: is_remove

    version_name = '0.0.0-0'
    for kernel_details in kernel_details_list:
        if directory == kernel_details[6]:
            version_name = kernel_details[1]
            break
    return version_name


def update_kernel_details_list_for_initrd_EXPERIMENT(directory, kernel_details_list):

    logger.log_label('Update kernel details list for initrd')
    filepath_pattern = os.path.join(directory, 'initrd*')
    # initrd_filepath_list = glob.glob(filepath_pattern)
    # initrd_filepath_list = [ initrd_filepath for initrd_filepath in initrd_filepath_list if not os.path.exists(initrd_filepath) ]
    initrd_filepath_list = [initrd_filepath for initrd_filepath in glob.glob(filepath_pattern) if os.path.exists(initrd_filepath)]
    logger.log_value('%i initrd files found in' % len(initrd_filepath_list), directory)
    for initrd_filepath in initrd_filepath_list:
        initrd_filename = os.path.basename(initrd_filepath)
        logger.log_label('Get initrd version details')
        version_name = get_initrd_version_name(initrd_filepath)
        if not version_name:
            version_name = '0.0.0-0'
        logger.log_value('The initrd version is', version_name)
        version_integers = tuple(map(int, re.split('[.-]', version_name)))
        update_kernel_details_for_initrd(version_integers, version_name, initrd_filename, directory, kernel_details_list)


def update_kernel_details_list_for_initrd_ORIGINAL(directory, kernel_details_list):

    logger.log_label('Update kernel details list for initrd')
    filepath_pattern = os.path.join(directory, 'initrd*')
    initrd_filepath_list = glob.glob(filepath_pattern)
    logger.log_value('%i initrd files found in' % len(initrd_filepath_list), directory)
    for initrd_filepath in initrd_filepath_list:
        initrd_filename = os.path.basename(initrd_filepath)
        logger.log_label('Get initrd version details')
        version_name = get_initrd_version_name(initrd_filepath)
        if not version_name:
            version_name = '0.0.0-0'
        logger.log_value('The initrd version is', version_name)
        version_integers = tuple(map(int, re.split('[.-]', version_name)))
        update_kernel_details_for_initrd(version_integers, version_name, initrd_filename, directory, kernel_details_list)


def update_kernel_details_for_initrd(version_integers, version_name, initrd_filename, directory, kernel_details_list):

    logger.log_label('Search kernel details list for matching version')
    logger.log_value('• Kernel version', version_name)
    logger.log_value('• Kernel version as integers', version_integers)
    logger.log_value('• Initrd filename', initrd_filename)
    logger.log_value('• Directory', directory)

    # 0: version_integers
    # 1: version_name
    # 2: vmlinuz_filename
    # 3: new_vmlinuz_filename
    # 4: initrd_filename
    # 5: new_initrd_filename
    # 6: directory
    # 7: note
    # 8: is_selected
    # 9: is_remove

    found = False
    for index, kernel_details in enumerate(list(kernel_details_list)):
        if (kernel_details[0] == version_integers and kernel_details[1] == version_name and kernel_details[6] == directory):
            found = True
            logger.log_value('• Matching kernel version found?', 'Yes')
            total = len(kernel_details_list)
            logger.log_value('• Index of match', '%i of %i' % (index, total - 1))
            if not kernel_details[4]:
                logger.log_label('Update kernel details')
                kernel_details[4] = initrd_filename
                logger.log_value('• Index', '%s of %s' % (index, total - 1))
            elif kernel_details[4] == initrd_filename:
                logger.log_label('Skip updating kernel details')
                logger.log_value('• Index', '%s of %s' % (index, total - 1))
            else:
                logger.log_label('Copy and add kernel details')
                kernel_details = list(kernel_details)
                kernel_details[4] = initrd_filename
                kernel_details_list.append(kernel_details)
                total = len(kernel_details_list)
                logger.log_value('• Index', '%s of %s' % (total - 1, total - 1))

    if not found:
        logger.log_value('• Matching kernel version found?', 'No')

        logger.log_label('Add new kernel details')

        kernel_details = [None] * 10
        if not version_integers:
            version_integers = (0, 0, 0)
        kernel_details[0] = version_integers
        kernel_details[1] = version_name
        kernel_details[2] = None  # vmlinuz_filename
        kernel_details[3] = None  # new_vmlinuz_filename
        kernel_details[4] = initrd_filename
        kernel_details[5] = None  # new_initrd_filename
        kernel_details[6] = directory
        kernel_details[7] = None  # note
        kernel_details[8] = False  # is_selected
        kernel_details[9] = False  # is_remove
        kernel_details_list.append(kernel_details)

        total = len(kernel_details_list)
        logger.log_value('• Index', '%s of %s' % (total - 1, total - 1))

    logger.log_value('• Kernel version', kernel_details[1])
    logger.log_value('• Kernel version as integers', kernel_details[0])
    logger.log_value('• Vmlinuz filename', kernel_details[2])
    logger.log_value('• Initrd filename', kernel_details[4])
    logger.log_value('• Directory', kernel_details[6])


def update_kernel_details_for_initrd_ORIGINAL(version_integers, version_name, initrd_filename, directory, kernel_details_list):

    logger.log_label('Search kernel details list for matching version')
    logger.log_value('• Kernel version', version_name)
    logger.log_value('• Kernel version as integers', version_integers)
    logger.log_value('• Initrd filename', initrd_filename)
    logger.log_value('• Directory', directory)

    # 0: version_integers
    # 1: version_name
    # 2: vmlinuz_filename
    # 3: new_vmlinuz_filename
    # 4: initrd_filename
    # 5: new_initrd_filename
    # 6: directory
    # 7: note
    # 8: is_selected
    # 9: is_remove

    found = False
    for index, kernel_details in enumerate(list(kernel_details_list)):
        if (kernel_details[0] == version_integers and kernel_details[1] == version_name and kernel_details[6] == directory):
            found = True
            if kernel_details[4] == initrd_filename:
                logger.log_value('• Matching kernel version found?', 'Yes')
                total = len(kernel_details_list)
                logger.log_value('• Index of match', '%i of %i' % (index, total - 1))

                logger.log_label('Skip updating kernel details')

                logger.log_value('• Index', '%s of %s' % (index, total - 1))
                logger.log_value('• Kernel version', kernel_details[1])
                logger.log_value('• Kernel version as integers', kernel_details[0])
                logger.log_value('• Vmlinuz filename', kernel_details[2])
                logger.log_value('• Initrd filename', kernel_details[4])
                logger.log_value('• Directory', kernel_details[6])
                break  # TODO: break is not needed here.
            elif not kernel_details[4]:
                logger.log_value('• Matching kernel version found?', 'Yes')
                total = len(kernel_details_list)
                logger.log_value('• Index of match', '%i of %i' % (index, total - 1))

                logger.log_label('Update kernel details')
                kernel_details[4] = initrd_filename

                logger.log_value('• Index', '%s of %s' % (index, total - 1))
                logger.log_value('• Kernel version', kernel_details[1])
                logger.log_value('• Kernel version as integers', kernel_details[0])
                logger.log_value('• Vmlinuz filename', kernel_details[2])
                logger.log_value('• Initrd filename', kernel_details[4])
                logger.log_value('• Directory', kernel_details[6])
            else:
                logger.log_value('• Matching kernel version found?', 'Yes')
                total = len(kernel_details_list)
                logger.log_value('• Index of match', '%i of %i' % (index, total - 1))

                logger.log_label('Copy and add kernel details')
                kernel_details = list(kernel_details)
                kernel_details[4] = initrd_filename
                kernel_details_list.append(kernel_details)

                total = len(kernel_details_list)
                logger.log_value('• Index', '%s of %s' % (total - 1, total - 1))
                logger.log_value('• Kernel version', kernel_details[1])
                logger.log_value('• Kernel version as integers', kernel_details[0])
                logger.log_value('• Vmlinuz filename', kernel_details[2])
                logger.log_value('• Initrd filename', kernel_details[4])
                logger.log_value('• Directory', kernel_details[6])
    if not found:
        logger.log_value('• Matching kernel version found?', 'No')

        logger.log_label('Add new kernel details')

        kernel_details = [None] * 10
        if not version_integers:
            version_integers = (0, 0, 0)
        kernel_details[0] = version_integers
        kernel_details[1] = version_name
        kernel_details[2] = None  # vmlinuz_filename
        kernel_details[3] = None  # new_vmlinuz_filename
        kernel_details[4] = initrd_filename
        kernel_details[5] = None  # new_initrd_filename
        kernel_details[6] = directory
        kernel_details[7] = None  # note
        kernel_details[8] = False  # is_selected
        kernel_details[9] = False  # is_remove
        kernel_details_list.append(kernel_details)

        total = len(kernel_details_list)
        logger.log_value('• Index', '%s of %s' % (total - 1, total - 1))
        logger.log_value('• Kernel version', kernel_details[1])
        logger.log_value('• Kernel version as integers', kernel_details[0])
        logger.log_value('• Vmlinuz filename', kernel_details[2])
        logger.log_value('• Initrd filename', kernel_details[4])
        logger.log_value('• Directory', kernel_details[6])


def get_initrd_version_name(filepath):

    # logger.log_value('Get initrd version', filepath)
    version_name = (_get_initrd_version_name_from_file_name(filepath) or _get_initrd_version_name_from_file_contents(filepath) or _get_initrd_version_name_from_file_type(filepath))

    return version_name


def _get_initrd_version_name_from_file_name(filepath):

    logger.log_value('Get initrd version from file name', filepath)
    filename = os.path.basename(filepath)
    version_name = re.search(r'\d[\d\.-]*\d', filename)
    version_name = version_name.group(0) if version_name else None

    return version_name


def _get_initrd_version_name_from_file_type(filepath):

    logger.log_value('Get initrd version from file type', filepath)
    command = 'file "%s"' % filepath
    result, exitstatus, signalstatus = execute_synchronous(command)
    version_name = None
    if not exitstatus and not signalstatus:
        version_information = re.search(r'(\d+\.\d+\.\d+(?:-\d+))', str(result))
        if version_information:
            version_name = version_information.group(1)
            logger.log_value('Found version', version_name)

    return version_name


def _get_initrd_version_name_from_file_contents(filepath):

    logger.log_value('Get initrd version from file contents', filepath)
    version_name = None
    try:
        command = 'lsinitramfs "%s"' % filepath
        process = pexpect.spawnu(command, timeout=60)
        match = False
        while process.exitstatus is None and not match:
            line = process.readline()
            # print('%s' % line, end='')
            match = re.search(r'lib/modules/(\d[\d\.-]*\d)', line)
            # TODO: Check if cannot and error both have spaces around
            #       them in the actual messages. The spaces have been
            #       added there to avoid matching file names with these
            #       words.
            #       Ex. lib/x86_64-linux-gnu/libgpg-error.so.0
            #           lib/x86_64-linux-gnu/libgpg-error.so.0.22.0
            if (' cannot ' in line or ' error ' in line or 'premature' in line):
                # TODO:
                logger.log_value('A. Encountered exception while getting initrd version from file contents', line)
        if match:
            process.terminate(True)
            version_name = match.group(1)
    except pexpect.TIMEOUT as exception:
        # TODO:
        logger.log_value('B. Encountered exception while getting initrd version from file contents', exception)
        logger.log_value('The tracekback is', traceback.format_exc())
    except pexpect.EOF as exception:
        # TODO:
        logger.log_value('C. Encountered exception while getting initrd version from file contents', exception)
        logger.log_value('The tracekback is', traceback.format_exc())
    except pexpect.ExceptionPexpect as exception:
        # TODO:
        logger.log_value('D. Encountered exception while getting initrd version from file contents', exception)
        logger.log_value('The tracekback is', traceback.format_exc())

    return version_name


def calculate_initrd_filename(filepath):

    # Determine extension for initrd file.
    # Use initrd.lz, initrd.gz, or initrd depending on the compression type.
    command = 'file "%s"' % filepath
    result, exitstatus, signalstatus = execute_synchronous(command)
    logger.log_value('The file type informaton is', result)

    compression = None
    match = re.search(r':\s(.*)\scompressed data', result)
    if match:
        compression = match.group(1)
    else:
        logger.log_value('Compression for initrd not found in', filepath)
    logger.log_value('The compression for initrd is', compression)

    if compression == 'LZMA':
        filename = 'initrd.lz'
    elif compression == 'gzip':
        filename = 'initrd.gz'
    else:
        filename = 'initrd'

    return filename


########################################################################
# Create Filesystem Manifest Functions
########################################################################


def create_installed_packages_list():

    logger.log_label('Create list of installed packages')

    # command = 'chroot "%s" dpkg-query -W' % model.project.custom_root_directory
    # command = 'chroot "%s" dpkg-query --showformat="${Package}\t${Version}\n" --show' % model.project.custom_root_directory
    # command = 'chroot "%s" dpkg-query --show' % model.project.custom_root_directory
    # command = 'pkexec chroot "%s" dpkg-query --show' % model.project.custom_root_directory
    dpkg_database_directory = os.path.join(model.project.custom_root_directory, '/var', 'lib', 'dpkg')
    command = 'dpkg-query --show --admindir="%s"' % dpkg_database_directory
    result, exitstatus, signalstatus = execute_synchronous(command)
    installed_packages_list = result.splitlines()

    package_count = len(installed_packages_list)
    logger.log_value('Total number of installed packages', package_count)

    return installed_packages_list


# TODO: Consider movinf this to the options page, where we write the
#       filesystem_manifest_remove_file(s).
#       See repackage_utilities.create_filesystem_manifest_remove_file()
def create_filesystem_manifest_file(installed_packages_list):

    logger.log_label('Create new filesystem manifest file')

    filepath = os.path.join(model.project.custom_disk_directory, model.status.casper_directory, 'filesystem.manifest')
    logger.log_value('Write filesystem manifest to', filepath)

    with open(filepath, 'w') as file:
        for line in installed_packages_list:
            file.write('%s\n' % line)


def get_removable_packages_list(filename):

    # Read filesystem.manifest-remove to get list of packages to remove.
    removable_packages_list = []
    filepath = os.path.join(model.project.custom_disk_directory, model.status.casper_directory, filename)
    logger.log_value('Read list of packages to remove from', filepath)
    with open(filepath, 'r') as file:
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
