#!/usr/bin/python3

########################################################################
#                                                                      #
# prepare_utilities.py                                                 #
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

from utilities import display
from utilities import logger
from utilities import model
from utilities.process_utilities import execute_synchronous

from collections import Counter
import glob
import os
import pexpect
import platform
import re
from time import sleep
import string

########################################################################
# Manage Linux Kernels Functions
########################################################################

# ----------------------------------------------------------------------
# Kernel Versions
# ----------------------------------------------------------------------


def create_kernel_details_list(*directories):
    logger.log_label('Create kernel details list')

    #
    # Vmlinuz
    #

    # Create a consolidated vmlinuz details list.
    vmlinuz_details_list = []
    for directory in directories:
        # Realpath is necessary here.
        directory = os.path.realpath(directory)
        update_vmlinuz_details_list(directory, vmlinuz_details_list)

    # For debugging.
    # print_details_list(vmlinuz_details_list)

    # Count vmlinuz directories.
    vmlinuz_directory_counter = Counter()
    vmlinuz_directory_counter.update([vmlinuz_details['directory'] for vmlinuz_details in vmlinuz_details_list])
    directories_with_one_vmlinuz = [directory for directory, count in vmlinuz_directory_counter.items() if count == 1]

    #
    # Initrd
    #

    # Create a consolidated initrd details list.
    initrd_details_list = []
    initrd_directory_counter = Counter()
    for directory in directories:
        # Realpath is necessary here.
        directory = os.path.realpath(directory)
        update_initrd_details_list(directory, initrd_details_list)

    # For debugging.
    # print_details_list(initrd_details_list)

    # Count initrd directories.
    initrd_directory_counter = Counter()
    initrd_directory_counter.update([initrd_details['directory'] for initrd_details in initrd_details_list])
    directories_with_one_initrd = [directory for directory, count in initrd_directory_counter.items() if count == 1]

    #
    # Kernels (vmlinuz and initrd)
    #

    # Create a list of directories that only contain one vmlinuz file
    # and one initrd file.
    directories_with_one_vmlinuz_and_initrd = list(set(directories_with_one_vmlinuz) & set(directories_with_one_initrd))

    # Create a consolidated kernel details list.
    kernel_details_list = []
    _create_kernel_details_list(vmlinuz_details_list, initrd_details_list, kernel_details_list, directories_with_one_vmlinuz_and_initrd)

    # Sort, select kernel, add notes, and remove the 1st column.
    update_kernel_details_list(kernel_details_list)

    # For debugging.
    # print_details_list(kernel_details_list, {'note': 10})

    return kernel_details_list


def _create_kernel_details_list(vmlinuz_details_list, initrd_details_list, kernel_details_list, directories_with_one_vmlinuz_and_initrd):

    note = ''
    is_selected = False
    is_remove = False

    for vmlinuz_details in vmlinuz_details_list:

        vmlinuz_version_integers = vmlinuz_details['version_integers']
        vmlinuz_version_name = vmlinuz_details['version_name']
        vmlinuz_filename = vmlinuz_details['filename']
        new_vmlinuz_filename = vmlinuz_details['new_filename']
        vmlinuz_directory = vmlinuz_details['directory']

        for initrd_details in initrd_details_list:

            initrd_version_integers = initrd_details['version_integers']
            initrd_version_name = initrd_details['version_name']
            initrd_filename = initrd_details['filename']
            new_initrd_filename = initrd_details['new_filename']
            initrd_directory = initrd_details['directory']

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

            if vmlinuz_directory == initrd_directory:
                if vmlinuz_version_name and initrd_version_name:
                    if vmlinuz_version_integers == initrd_version_integers:
                        kernel_details = {
                            'version_integers': vmlinuz_version_integers,
                            'version_name': vmlinuz_version_name,
                            'vmlinuz_filename': vmlinuz_filename,
                            'new_vmlinuz_filename': new_vmlinuz_filename,
                            'initrd_filename': initrd_filename,
                            'new_initrd_filename': new_initrd_filename,
                            'directory': vmlinuz_directory,
                            'note': note,
                            'is_selected': is_selected,
                            'is_remove': is_remove
                        }
                        kernel_details_list.append(kernel_details)
                elif vmlinuz_directory in directories_with_one_vmlinuz_and_initrd:
                    if vmlinuz_version_name and not initrd_version_name:
                        kernel_details = {
                            'version_integers': vmlinuz_version_integers,
                            'version_name': vmlinuz_version_name,
                            'vmlinuz_filename': vmlinuz_filename,
                            'new_vmlinuz_filename': new_vmlinuz_filename,
                            'initrd_filename': initrd_filename,
                            'new_initrd_filename': new_initrd_filename,
                            'directory': vmlinuz_directory,
                            'note': note,
                            'is_selected': is_selected,
                            'is_remove': is_remove
                        }
                        kernel_details_list.append(kernel_details)
                    elif not vmlinuz_version_name and initrd_version_name:
                        kernel_details = {
                            'version_integers': initrd_version_integers,
                            'version_name': initrd_version_name,
                            'vmlinuz_filename': vmlinuz_filename,
                            'new_vmlinuz_filename': new_vmlinuz_filename,
                            'initrd_filename': initrd_filename,
                            'new_initrd_filename': new_initrd_filename,
                            'directory': vmlinuz_directory,
                            'note': note,
                            'is_selected': is_selected,
                            'is_remove': is_remove
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
                            'vmlinuz_filename': vmlinuz_filename,
                            'new_vmlinuz_filename': new_vmlinuz_filename,
                            'initrd_filename': initrd_filename,
                            'new_initrd_filename': new_initrd_filename,
                            'directory': vmlinuz_directory,
                            'note': note,
                            'is_selected': is_selected,
                            'is_remove': is_remove
                        }
                        kernel_details_list.append(kernel_details)


def _create_kernel_details_list_ORIGINAL(vmlinuz_details_list, initrd_details_list, kernel_details_list):

    note = ''
    is_selected = False
    is_remove = False

    for vmlinuz_details in vmlinuz_details_list:

        vmlinuz_version_integers = vmlinuz_details['version_integers']
        vmlinuz_version_name = vmlinuz_details['version_name']
        vmlinuz_filename = vmlinuz_details['filename']
        new_vmlinuz_filename = vmlinuz_details['new_filename']
        vmlinuz_directory = vmlinuz_details['directory']

        for initrd_details in initrd_details_list:

            initrd_version_integers = initrd_details['version_integers']
            initrd_version_name = initrd_details['version_name']
            initrd_filename = initrd_details['filename']
            new_initrd_filename = initrd_details['new_filename']
            initrd_directory = initrd_details['directory']

            if vmlinuz_version_integers == initrd_version_integers and vmlinuz_directory == initrd_directory:

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

                kernel_details = {
                    'version_integers': vmlinuz_version_integers,
                    'version_name': vmlinuz_version_name,
                    'vmlinuz_filename': vmlinuz_filename,
                    'new_vmlinuz_filename': new_vmlinuz_filename,
                    'initrd_filename': initrd_filename,
                    'new_initrd_filename': new_initrd_filename,
                    'directory': vmlinuz_directory,
                    'note': note,
                    'is_selected': is_selected,
                    'is_remove': is_remove
                }

                kernel_details_list.append(kernel_details)


# Sort, select kernel, add notes, and remove the 1st column.
def update_kernel_details_list(kernel_details_list):

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
    kernel_details_list.sort(key=lambda details: [(0, 0, 0, 0) if k == 'version_integers' and v is None else '' if v is None else v for k, v in details.items()], reverse=True)

    # Set the selected index as the index of the most recent kernel.
    selected_index = 0

    # Set the notes, and update the selected index if necessary.
    current_kernel_release_name = get_current_kernel_release_name()
    current_kernel_version_name = get_current_kernel_version_name()
    original_iso_image_directory = os.path.join(model.project.iso_mount_point, model.status.casper_directory)
    for index, kernel_details in enumerate(kernel_details_list):
        note = ''
        version_name = kernel_details['version_name']
        if current_kernel_version_name == version_name:
            if note: note += ' '  # os.linesep
            note += 'You are currently running kernel version %s.' % current_kernel_version_name
        # if index == 0:
        #     if note: note += ' '  # os.linesep
        #     note += 'This is the newest kernel version available to bootstrap the customized live ISO image.'
        directory = kernel_details['directory']
        if directory == original_iso_image_directory:
            if note: note += ' '  # os.linesep
            note += 'This kernel is used to bootstrap the original live ISO image.'
            if len(kernel_details_list) > 1:
                if note: note += ' '  # os.linesep
                note += 'Select this kernel if you encounter issues such as BusyBox when using other kernel versions.'
            # if is_server_image()
            #     # if note: note += ' ' # os.linesep
            #     # note += 'Since you are customizing a server image, select this option if you encounter issues using other kernel versions.'
            #     # Set the selected index for the the original live ISO image kernel.
            #     selected_index = index
        new_vmlinuz_filename = kernel_details['new_vmlinuz_filename']
        new_initrd_filename = kernel_details['new_initrd_filename']
        if note: note += ' '  # os.linesep
        note += 'Reference these files as <tt>%s</tt> and <tt>%s</tt> in the ISO boot configurations.' % (new_vmlinuz_filename, new_initrd_filename)
        kernel_details['note'] = note

    # Set the selected kernel based on the selected index.
    kernel_details_list[selected_index]['is_selected'] = True

    # For debugging.
    # print_details_list(kernel_details_list, {'note': 10})

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

    # It is not necessary to remove the 1st column because because items
    # are selectively added to the list_store in the
    # display.update_list_store() function.

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
        logger.log_value('• Index', '%s of %s' % (index + 1, total))
        logger.log_value('• Vmlinuz filename', kernel_details['vmlinuz_filename'])
        logger.log_value('• New vmlinuz filename', kernel_details['new_vmlinuz_filename'])
        logger.log_value('• Initrd filename', kernel_details['initrd_filename'])
        logger.log_value('• New initrd filename', kernel_details['new_initrd_filename'])
        logger.log_value('• Directory', kernel_details['directory'])
        logger.log_value('• Note', kernel_details['note'])
        logger.log_value('• Is selected', kernel_details['is_selected'])
        # logger.log_value('• Is remove', kernel_details['is_remove'])


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
    # - original.iso_filename = ubuntu-18.04-live-server-amd64.iso
    # - original.iso_volume_id = Ubuntu-Server 18.04 LTS amd64
    # - original.iso_disk_name = Ubuntu-Server 18.04 LTS "Bionic Beaver" - Release amd64

    if re.search('server', model.original.iso_filename, re.IGNORECASE):
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
    logger.log_value('• Search directory', directory)

    filepath_list = []

    # Replace simlinks with the actual filepath.
    directory = os.path.realpath(directory)
    filepath_pattern = os.path.join(directory, 'vmlinuz*')
    for filepath in glob.glob(filepath_pattern):
        # Replace simlinks with the actual filepath.
        realpath = os.path.realpath(filepath)
        if not os.path.exists(realpath):
            # The realpath may not exist because it may be relative to
            # the root directory of the virtual environment. If this is
            # the case, the link will appear broken outside of the
            # virtual environment, because it will seem to point to the
            # root of the host system.
            # The following remedies this situation by appending the
            # virtual environment's root directory to the realpath.
            # However, if another file with the same path actually
            # exists on the host system, realpath will point to that
            # file instead, and this 'if not' block will not be
            # executed. This is considered a negligable risk.
            # It is necessary to concatenate the directory and real path
            # using "+" because os.path.join() discards the virtual
            # environment's root directory, because the realpath may be
            # considered and absolute path: "If a component is an
            # absolute path, all previous components are thrown away and
            # joining continues from the absolute path component."
            # (See https://docs.python.org/3/library/os.path.html).
            filepath = os.path.abspath(model.project.custom_root_directory + realpath)
            # Replace simlinks with the actual filepath.
            realpath = os.path.realpath(filepath)

        if os.path.exists(realpath):
            filepath_list.append(realpath)

    filepath_list = list(set(filepath_list))

    logger.log_value('• Number of vmlinuz files found', len(filepath_list))
    relative_directory = os.path.relpath(directory, model.project.directory)
    if len(filepath_list) == 0:
        add_message('Found no vmlinuz files in .../%s' % relative_directory)
    elif len(filepath_list) == 1:
        add_message('Found one vmlinuz file in .../%s' % relative_directory)
    else:
        add_message('Found %d vmlinuz files in .../%s' % (len(filepath_list), relative_directory))
    sleep(0.50)

    for index, filepath in enumerate(filepath_list):
        filename = os.path.basename(filepath)
        directory = os.path.dirname(filepath)
        version_name = get_vmlinuz_version_name(filepath)
        # if not version_name: version_name = '0.0.0-0'
        logger.log_value('• The vmlinuz version is', version_name)
        if version_name:
            version_integers = tuple(map(int, re.split('[.-]', version_name)))
        else:
            version_integers = tuple(map(int, re.split('[.-]', '0.0.0-0')))
        new_filename = calculate_vmlinuz_filename(filepath)

        details = {'version_integers': version_integers, 'version_name': version_name, 'filename': filename, 'new_filename': new_filename, 'directory': directory}
        details_list.append(details)
        sleep(0.50)


def calculate_vmlinuz_filename(filepath):

    # Just use vmlinuz (instead of vmlinuz or vmlinuz.efi).
    filename = 'vmlinuz'

    return filename


def get_vmlinuz_version_name(filepath):

    # logger.log_value('Get vmlinuz version', filepath)
    # relative_filepath = os.path.relpath(filepath, model.project.directory)
    filename = os.path.basename(filepath)
    add_message('Processing %s' % filename)

    version_name = (_get_vmlinuz_version_name_from_file_name(filepath) or _get_vmlinuz_version_name_from_file_type(filepath) or _get_vmlinuz_version_name_from_file_contents(filepath))

    # add_message('The version is %s' % version_name)
    return version_name


def _get_vmlinuz_version_name_from_file_name(filepath):

    logger.log_value('Get vmlinuz version name from file name', filepath)
    filename = os.path.basename(filepath)
    version_name = re.search(r'\d[\d\.-]*\d', filename)
    version_name = version_name.group(0) if version_name else None
    logger.log_value('• The version name is', version_name)

    return version_name


def _get_vmlinuz_version_name_from_file_type(filepath):

    logger.log_value('Get vmlinuz version name from file type', filepath)
    command = 'file "%s"' % filepath
    result, exitstatus, signalstatus = execute_synchronous(command)
    version_name = None
    if not exitstatus and not signalstatus:
        version_information = re.search(r'(\d+\.\d+\.\d+(?:-\d+))', str(result))
        if version_information:
            version_name = version_information.group(1)
    logger.log_value('• The version name is', version_name)

    return version_name


def _get_vmlinuz_version_name_from_file_contents(filepath):

    logger.log_value('Get vmlinuz version name from file contents', filepath)
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
                break
            except:
                candidate = ''
        else:
            candidate = ''
    logger.log_value('• The version name is', version_name)

    return version_name


# ----------------------------------------------------------------------
# Initrd
# ----------------------------------------------------------------------


def update_initrd_details_list(directory, details_list):

    logger.log_label('Create initrd details list')
    logger.log_value('• Search directory', directory)

    filepath_list = []

    # Replace simlinks with the actual filepath.
    directory = os.path.realpath(directory)
    filepath_pattern = os.path.join(directory, 'initrd*')
    for filepath in glob.glob(filepath_pattern):
        # Replace simlinks with the actual filepath.
        realpath = os.path.realpath(filepath)
        if not os.path.exists(realpath):
            # The realpath may not exist because it may be relative to
            # the root directory of the virtual environment. If this is
            # the case, the link will appear broken outside of the
            # virtual environment, because it will seem to point to the
            # root of the host system.
            # The following remedies this situation by appending the
            # virtual environment's root directory to the realpath.
            # However, if another file with the same path actually
            # exists on the host system, realpath will point to that
            # file instead, and this 'if not' block will not be
            # executed. This is considered a negligable risk.
            # It is necessary to concatenate the directory and real path
            # using "+" because os.path.join() discards the virtual
            # environment's root directory, because the realpath may be
            # considered and absolute path: "If a component is an
            # absolute path, all previous components are thrown away and
            # joining continues from the absolute path component."
            # (See https://docs.python.org/3/library/os.path.html).
            filepath = os.path.abspath(model.project.custom_root_directory + realpath)
            # Replace simlinks with the actual filepath.
            realpath = os.path.realpath(filepath)

        if os.path.exists(realpath):
            filepath_list.append(realpath)

    filepath_list = list(set(filepath_list))

    logger.log_value('• Number of initrd files found', len(filepath_list))
    relative_directory = os.path.relpath(directory, model.project.directory)
    if len(filepath_list) == 0:
        add_message('Found no initrd files in .../%s' % relative_directory)
    elif len(filepath_list) == 1:
        add_message('Found one initrd file in .../%s' % relative_directory)
    else:
        add_message('Found %d initrd files in .../%s' % (len(filepath_list), relative_directory))
    sleep(0.50)

    for index, filepath in enumerate(filepath_list):
        filename = os.path.basename(filepath)
        directory = os.path.dirname(filepath)
        version_name = get_initrd_version_name(filepath)
        # if not version_name: version_name = '0.0.0-0'
        logger.log_value('• The initrd version is', version_name)
        if version_name:
            version_integers = tuple(map(int, re.split('[.-]', version_name)))
        else:
            version_integers = tuple(map(int, re.split('[.-]', '0.0.0-0')))
        new_filename = calculate_initrd_filename(filepath)

        details = {'version_integers': version_integers, 'version_name': version_name, 'filename': filename, 'new_filename': new_filename, 'directory': directory}
        details_list.append(details)
        sleep(0.50)


def calculate_initrd_filename(filepath):

    # Determine extension for initrd file.
    # Use initrd.lz, initrd.gz, or initrd depending on the compression type.
    command = 'file "%s"' % filepath
    result, exitstatus, signalstatus = execute_synchronous(command)
    logger.log_value('The file type informaton is', result)

    compression = None
    match = re.search(r':\s(.*)\scompressed data', result)
    if match: compression = match.group(1)
    else: logger.log_value('Compression for initrd not found in', filepath)
    logger.log_value('The compression for initrd is', compression)

    if compression == 'LZMA': filename = 'initrd.lz'
    elif compression == 'gzip': filename = 'initrd.gz'
    else: filename = 'initrd'

    return filename


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


def get_initrd_version_name(filepath):

    # logger.log_value('Get initrd version', filepath)
    relative_filepath = os.path.relpath(filepath, model.project.directory)
    # add_message('• Processing .../%s' % relative_filepath)
    filename = os.path.basename(filepath)
    add_message('Processing %s' % filename)

    version_name = (_get_initrd_version_name_from_file_name(filepath) or _get_initrd_version_name_from_file_contents(filepath) or _get_initrd_version_name_from_file_type(filepath))

    # add_message('The version is %s' % version_name)
    return version_name


def _get_initrd_version_name_from_file_name(filepath):

    logger.log_value('Get initrd version name from file name', filepath)
    filename = os.path.basename(filepath)
    version_name = re.search(r'\d[\d\.-]*\d', filename)
    version_name = version_name.group(0) if version_name else None

    return version_name


def _get_initrd_version_name_from_file_type(filepath):

    logger.log_value('Get initrd version name from file type', filepath)
    command = 'file "%s"' % filepath
    result, exitstatus, signalstatus = execute_synchronous(command)
    version_name = None
    if not exitstatus and not signalstatus:
        version_information = re.search(r'(\d+\.\d+\.\d+(?:-\d+))', str(result))
        if version_information:
            version_name = version_information.group(1)
    logger.log_value('• The version name is', version_name)

    return version_name


def _get_initrd_version_name_from_file_contents(filepath):

    logger.log_value('Get initrd version name from file contents', filepath)
    version_name = None
    try:
        command = 'lsinitramfs "%s"' % filepath
        process = pexpect.spawnu(command, timeout=60)
        match = False
        while process.exitstatus is None and not match:
            line = process.readline()
            # print('%s' % line, end='')
            match = re.search(r'lib/modules/(\d[\d\.-]*\d)', line)
            if ('cannot' in line or 'error' in line or 'premature' in line):
                logger.log_value('Encountered exception while getting initrd version name from file contents', line)
        if match:
            process.terminate(True)
            version_name = match.group(1)
    except pexpect.TIMEOUT as exception:
        logger.log_value('Encountered exception while getting initrd version name from file contents', exception)
    except pexpect.EOF as exception:
        logger.log_value('Encountered exception while getting initrd version name from file contents', exception)
    except pexpect.ExceptionPexpect as exception:
        logger.log_value('Encountered exception while getting initrd version name from file contents', exception)
    logger.log_value('• The version name is', version_name)

    return version_name


# ----------------------------------------------------------------------
# Print
# ----------------------------------------------------------------------


# For debugging only.
def get_widths(details_list, default_widths):
    """
    details_list   - a list of lists or dicts
    default_widths - dictinary of str:int
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
    default_widths - dictinary of str:int
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
# Create Filesystem Manifest Functions
########################################################################


def is_exists_filesystem_manifest_remove(filename):

    # Check custom live iso directory
    filepath = os.path.join(model.project.custom_disk_directory, model.status.casper_directory, filename)

    is_exists = os.path.exists(filepath)
    if is_exists:
        logger.log_value('%s found in' % filename, os.path.join(model.project.custom_disk_directory, model.status.casper_directory))
        return True
    else:
        logger.log_value('%s not found in' % filename, os.path.join(model.project.custom_disk_directory, model.status.casper_directory))
        return False


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


def create_typical_removable_packages_list():
    logger.log_label('Create typical removable packages list')

    listore_name = 'options_page__package_manifest_tab__list_store'
    logger.log_value('Get user selections from', listore_name)
    list_store = model.builder.get_object(listore_name)
    removable_packages_list = []
    item = list_store.get_iter_first()
    while item is not None:
        flag = list_store.get_value(item, 0)
        package_name = list_store.get_value(item, 4)
        if flag: removable_packages_list.append(package_name)
        item = list_store.iter_next(item)
    removable_packages_list
    logger.log_value('New number of packages to be removed', len(removable_packages_list))

    return removable_packages_list


def create_minimal_removable_packages_list():
    logger.log_label('Create minimal removable packages list')

    listore_name = 'options_page__package_manifest_tab__list_store'
    logger.log_value('Get user selections from', listore_name)
    list_store = model.builder.get_object(listore_name)
    removable_packages_list = []
    item = list_store.get_iter_first()
    while item is not None:
        flag = list_store.get_value(item, 1) and list_store.get_value(item, 3)
        package_name = list_store.get_value(item, 4)
        if flag: removable_packages_list.append(package_name)
        item = list_store.iter_next(item)
    removable_packages_list
    logger.log_value('New number of packages to be removed', len(removable_packages_list))

    return removable_packages_list


# TODO: This function is not used.
def create_removable_packages_list(listore_name, index):
    logger.log_label('Get removable packages list from user selections')
    logger.log_value('Get user selections from', listore_name)
    list_store = model.builder.get_object(listore_name)
    removable_packages_list = []
    item = list_store.get_iter_first()
    while item is not None:
        flag = list_store.get_value(item, index)
        package_name = list_store.get_value(item, 2)
        if flag: removable_packages_list.append(package_name)
        item = list_store.iter_next(item)
    removable_packages_list
    logger.log_value('New number of packages to be removed', len(removable_packages_list))

    return removable_packages_list


def create_filesystem_manifest_remove_file(filename, removable_packages_list):
    logger.log_label('Create new filesystem manifest remove file')

    filepath = os.path.join(model.project.custom_disk_directory, model.status.casper_directory, filename)
    logger.log_value('Write filesystem manifest remove file to', filepath)
    with open(filepath, 'w') as file:
        first_line = True
        for packages_name in removable_packages_list:
            if first_line:
                file.write('%s' % packages_name)
                first_line = False
            else:
                file.write('\n%s' % packages_name)


def add_message(message):
    display.insert_box_label('prepare_page__iso_boot_kernels_box', message, 0.50)
