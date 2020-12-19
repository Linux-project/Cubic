#!/usr/bin/python3

########################################################################
#                                                                      #
# file_utilities.py                                                    #
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

import glob
import hashlib
import magic
import os
import re
import shutil

from utilities import logger
from utilities import model
from utilities.processor import execute_synchronous

########################################################################
# Global Variables & Constants
########################################################################

# N/A

########################################################################
# Directory Functions
########################################################################


def make_directory(directory):
    logger.log_value('Create directory', directory)
    if not os.path.exists(directory):
        os.mkdir(directory)
    else:
        logger.log_value('Cannot create directory', 'Directory already exists')


# TODO: Check if this function is terminated when the thread is killed?
def delete_directory(directory):
    logger.log_value('Delete directory', directory)
    if os.path.exists(directory):
        try:
            # TODO: Check if permissions prevent this operation?
            # https://docs.python.org/3.8/library/shutil.html#shutil.rmtree
            # rmtree(path, ignore_errors=False, onerror=HANDLER)
            # TODO: Path must point to a directory (but not a symbolic link to a directory).
            shutil.rmtree(directory)
            result = 'Successfully deleted %s' % directory
            exit_status = 0
            signal_status = None
        except OSError as exception:
            logger.log_value('Exception', exception)
            # type, value, traceback = sys.exc_info()
            result = 'Error deleting %s' % directory
            exit_status = None
            signal_status = 1
    else:
        logger.log_value('Cannot delete directory', 'Directory does not exist')
        result = 'Directory %s does not exist.' % directory
        exit_status = None
        signal_status = 1

    logger.log_value('The result is', result)
    logger.log_value('The exit status, signal status is', '%s, %s' % (exit_status, signal_status))

    return result, exit_status, signal_status


def get_files_with_pattern(pattern, exclusion_list=None):
    if exclusion_list:
        logger.log_value('Get files with pattern', pattern)
        logger.log_value('Exclude files files from the list', exclusion_list)
        return [file_path for file_path in glob.glob(pattern) if file_path not in exclusion_list]
    else:
        logger.log_value('Get files with pattern', pattern)
        return [file_path for file_path in glob.glob(pattern)]


def delete_files_with_pattern(pattern, exclusion_list=None):
    if exclusion_list:
        logger.log_value('Delete existing files with pattern', pattern)
        logger.log_value('Keep files', exclusion_list)
        [os.remove(delete_file_path) for delete_file_path in glob.glob(pattern) if delete_file_path not in exclusion_list]
    else:
        logger.log_value('Delete existing files with pattern', pattern)
        [os.remove(delete_file_path) for delete_file_path in glob.glob(pattern)]


# https://docs.python.org/3.8/library/shutil.html#shutil.rmtree
def delete_path_as_root(file_path):
    logger.log_value('Delete file as root', file_path)
    program = os.path.join(model.application.directory, 'commands', 'delete-path')
    command = 'pkexec "%s" "%s"' % (program, file_path)
    result, exit_status, signal_status = execute_synchronous(command)
    logger.log_value('The result is', result)
    logger.log_value('The exit status, signal status is', '%s, %s' % (exit_status, signal_status))

    return result, exit_status, signal_status


def get_directory_size(start_path):
    logger.log_label('Calculate directory size')
    logger.log_value('Directory', start_path)
    total_size = 0
    for dirpath, dirnames, file_names in os.walk(start_path):
        for file_name in file_names:
            file_path = os.path.join(dirpath, file_name)
            total_size += os.path.getsize(file_path)

    logger.log_value('Directory size is', total_size)
    return total_size


def directory_is_writable(directory):
    logger.log_value('Check if directory is writable', directory)
    is_writable = os.access(directory, os.R_OK | os.W_OK | os.X_OK)
    logger.log_value('Directory is writable?', is_writable)
    return is_writable


def get_directory_for_file(file_name, start_path):

    logger.log_value('Get directory for %s in' % file_name, start_path)

    directory = ''
    # The directory may be a symlink.
    for dirpath, dirnames, file_names in os.walk(start_path, followlinks=True):
        if file_name in file_names:
            directory = dirpath
            break

    if directory:
        logger.log_value('%s is in' % file_name, directory)
    else:
        logger.log_value('%s is not in' % file_name, directory)

    return directory


def get_file_paths(start_path):
    logger.log_value('Get all file paths in the directory', start_path)
    file_paths = []
    for dirpath, dirnames, file_names in os.walk(start_path):
        for file_name in file_names:
            file_path = os.path.join(dirpath, file_name)
            file_paths.append(file_path)
    return file_paths


def get_text_file_paths(start_path):
    logger.log_value('Get all text file paths in the directory', start_path)
    file_paths = []
    for dirpath, dirnames, file_names in os.walk(start_path):
        for file_name in file_names:
            file_path = os.path.join(dirpath, file_name)
            try:
                with open(file_path, 'r') as file:
                    file.read()
            except UnicodeDecodeError:
                pass
            else:
                file_paths.append(file_path)
    return file_paths


########################################################################
# File Functions
########################################################################


def get_file_system_type(file_path):

    # ext, ext2, ext3, ext4, nfs, ntfs, vfat, zfs
    logger.log_value('Get file system type', file_path)
    command = 'df --output=fstype "%s"' % file_path
    result, exit_status, signal_status = execute_synchronous(command)
    file_system_type = None
    if not exit_status and not signal_status:
        file_system_type = result.splitlines()[1].upper()
    logger.log_value('The file system type is', file_system_type)
    return file_system_type


def get_mime_information(file_path):
    """
    Arguments:
        file_path: The full file path
    Returns:
        file_type (str) - The mime type
        file_icon (str) - The icon name
    """

    # Icons:
    #
    # 'application': 'application-x-executable',
    # 'audo': 'audio-x-generic',
    # 'folder': 'folder-symbolic',
    # 'font': 'font-x-generic',
    # 'image': 'image-x-generic',
    # 'package': 'package-x-generic',
    # 'text': 'text-x-generic',
    # 'video': 'video-x-generic'

    # Get mime type and mime subtype.
    if os.path.isdir(file_path):
        mime_type, mime_subtype = 'folder', None
    else:
        _, extension = os.path.splitext(file_path)
        if extension in ['.txt', '.seed']:
            mime_type, mime_subtype = 'text', None
        else:
            content_mime_type = magic.from_file(file_path, True)
            mime_type, mime_subtype = content_mime_type.split('/')

    # TODO *.pcx files are image files, but can not be opened in Cubic as pixbuf.

    # Return mime type and icon name.
    if mime_type == 'image':
        return 'image', 'image-x-generic'
    if mime_type == 'audo':
        return 'audio', 'audio-x-generic'
    if mime_type == 'folder':
        return 'folder', 'folder-symbolic'
    if mime_type == 'font':
        return 'font', 'font-x-generic'
    if mime_type == 'image':
        return 'image', 'image-x-generic'
    if mime_type == 'inode' and mime_subtype == 'x-empty':
        return 'text', 'text-x-generic'
    if mime_type == 'package':
        return 'package', 'package-x-generic'
    if mime_type == 'text':
        return 'text', 'text-x-generic'
    if mime_type == 'video':
        return 'video', 'video-x-generic'
    if mime_type == 'application' and mime_subtype == 'octet-stream' and os.path.getsize(file_path) == 1:
        return 'text', 'text-x-generic'
    return None, 'application-x-executable'


def calculate_md5_hash(file_path, buffer_size=2**20):
    """
    Calculate the md5 hash by reading a file into a buffer. The default buffer
    size is 2^20 bytes = 1048576 bytes = 1 MiB (Mebibytes).
    """

    md5_hash = hashlib.md5()
    try:
        with open(file_path, 'rb') as file:
            data = file.read(buffer_size)
            while data:
                md5_hash.update(data)
                data = file.read(buffer_size)
        return md5_hash.hexdigest()
    except Exception as exception:
        logger.log_value('Unable to calculate the md5 hash for file', file_path)
        logger.log_value('The exception is', exception)
        return None


def copy_file(source_path, target_path):

    logger.log_label('Copy file')
    logger.log_value('Source file path', source_path)
    logger.log_value('Target file path', target_path)

    shutil.copy(source_path, target_path)


# TODO: Check if this function is terminated when the thread is killed?
def delete_file(file_path):
    logger.log_value('Delete file', file_path)
    if os.path.exists(file_path):
        try:
            # TODO: Check if permissions prevent this operation?
            os.remove(file_path)
            result = 'Successfully deleted %s' % file_path
            exit_status = 0
            signal_status = None
        except OSError as exception:
            logger.log_value('Exception', exception)
            # type, value, traceback = sys.exc_info()
            result = 'Error deleting %s' % file_path
            exit_status = None
            signal_status = 1
    else:
        logger.log_value('Cannot delete file', 'File does not exist')
        result = 'File %s does not exist.' % file_path
        exit_status = None
        signal_status = 1

    logger.log_value('The result is', result)
    logger.log_value('The exit status, signal status is', '%s, %s' % (exit_status, signal_status))

    return result, exit_status, signal_status


def replace_text_in_file(file_path, search_text, replacement_text):
    logger.log_label('Replace text in file')
    logger.log_value('Filepath', file_path)
    logger.log_value('Search text', search_text)
    logger.log_value('Replacement text', replacement_text)

    error = True

    if not file_path:
        logger.log_value('Cannot replace text', 'File not specified')
        return error

    if not os.path.exists(file_path):
        logger.log_value('Cannot replace text', 'File %s does not exist' % file_path)
        return error

    if not search_text:
        logger.log_value('Cannot replace text', 'Search text not specified')
        return error

    if not replacement_text:
        logger.log_value('Cannot replace text', 'Replacement text not specified')
        return error

    # TODO: Add a try statment and return error accordingly.
    #       Currently, this is done in repackage_iso_page.update_disk_name(), but it should be done here.
    error = False

    with open(file_path, 'r+') as file:
        file_contents = file.read()
        file_contents = re.sub(search_text, replacement_text, file_contents)
        file.seek(0)
        file.truncate()
        file.write(file_contents)

    return error
