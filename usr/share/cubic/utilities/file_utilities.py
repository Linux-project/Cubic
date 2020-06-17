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

from glob import glob
from hashlib import md5
from os import mkdir, remove, walk
from os.path import exists, getsize, join
from re import sub
from shutil import copy, rmtree

from utilities import logger
from utilities import model
from utilities.processor import execute_synchronous

########################################################################
# References
########################################################################

# N/A

########################################################################
# Globals & Constants
########################################################################

# N/A

########################################################################
# Directory Functions
########################################################################


def make_directory(directory):
    logger.log_label('Create directory')
    logger.log_value('Directory', directory)
    if not exists(directory):
        mkdir(directory)
    else:
        logger.log_value('Cannot create directory', 'Directory already exists')


# TODO: Check if this function is terminated when the thread is killed?
def delete_directory(directory):
    logger.log_value('Delete directory', directory)
    if exists(directory):
        try:
            # TODO: Check if permissions prevent this operation?
            # https://docs.python.org/3.8/library/shutil.html#shutil.rmtree
            # rmtree(path, ignore_errors=False, onerror=HANDLER)
            # TODO: Path must point to a directory (but not a symbolic link to a directory).
            rmtree(directory)
            result = 'Successfully deleted %s' % directory
            exitstatus = 0
            signalstatus = None
        except OSError as exception:
            logger.log_value('Exception', exception)
            # type, value, traceback = sys.exc_info()
            result = 'Error deleting %s' % directory
            exitstatus = None
            signalstatus = 1
    else:
        logger.log_value('Cannot delete directory', 'Directory does not exist')
        result = 'Directory %s does not exist.' % directory
        exitstatus = None
        signalstatus = 1

    logger.log_value('The result is', result)
    logger.log_value('The exit status, signal status is', '%s, %s' % (exitstatus, signalstatus))

    return result, exitstatus, signalstatus


def delete_files_with_pattern(pattern):
    logger.log_value('Delete existing  files with pattern', pattern)
    # TODO: Make this code more clear.
    [remove(delete_filepath) for delete_filepath in glob(pattern)]


# https://docs.python.org/3.8/library/shutil.html#shutil.rmtree
def delete_path_as_root(filepath):
    logger.log_value('Delete file as root', filepath)
    program = join(model.application.directory, 'commands', 'delete')
    command = 'pkexec "%s" "%s"' % (program, filepath)
    result, exitstatus, signalstatus = execute_synchronous(command)
    logger.log_value('The result is', result)
    logger.log_value('The exit status, signal status is', '%s, %s' % (exitstatus, signalstatus))

    return result, exitstatus, signalstatus


def get_directory_size(start_path):
    logger.log_label('Calculate directory size')
    logger.log_value('Directory', start_path)
    total_size = 0
    for dirpath, dirnames, filenames in walk(start_path):
        for filename in filenames:
            filepath = join(dirpath, filename)
            total_size += getsize(filepath)

    logger.log_value('Directory size is', total_size)
    return total_size


def get_directory_for_file(filename, start_path):
    logger.log_label('Get directory for file')
    logger.log_value('Filename', filename)
    logger.log_value('Directory', start_path)

    # TODO" can we return None, instead of '' ?
    directory = ''
    for dirpath, dirnames, filenames in walk(start_path):
        if filename in filenames:
            directory = dirpath

    if directory:
        logger.log_value('%s is in' % filename, directory)
    else:
        logger.log_value('%s is not in' % filename, directory)


def get_filepaths(start_path):
    logger.log_value('Get all file paths in the directory', start_path)
    filepaths = []
    for dirpath, dirnames, filenames in walk(start_path):
        for filename in filenames:
            filepath = join(dirpath, filename)
            filepaths.append(filepath)
    return filepaths


def get_text_file_paths(start_path):
    logger.log_value('Get all text file paths in the directory', start_path)
    filepaths = []
    for dirpath, dirnames, filenames in walk(start_path):
        for filename in filenames:
            filepath = join(dirpath, filename)
            try:
                with open(filepath, 'r') as file:
                    file.read()
            except UnicodeDecodeError:
                pass
            else:
                filepaths.append(filepath)
    return filepaths


########################################################################
# File Functions
########################################################################


def calculate_md5_hash(filepath, block_size=2**20):

    md5_hash = md5()
    try:
        with open(filepath, 'rb') as file:
            buffer = file.read(block_size)
            while buffer:
                md5_hash.update(buffer)
                buffer = file.read(block_size)
        return md5_hash.hexdigest()
    except Exception as exception:
        logger.log_value('Unable to calculate the md5 hash for file', filepath)
        logger.log_value('The exception is', exception)
        return None


def copy_file(source_path, target_path):

    logger.log_label('Copy file')
    logger.log_value('Source file path', source_path)
    logger.log_value('Target file path', target_path)

    copy(source_path, target_path)


# TODO: Check if this function is terminated when the thread is killed?
def delete_file(filepath):
    logger.log_value('Delete file', filepath)
    if exists(filepath):
        try:
            # TODO: Check if permissions prevent this operation?
            remove(filepath)
            result = 'Successfully deleted %s' % filepath
            exitstatus = 0
            signalstatus = None
        except OSError as exception:
            logger.log_value('Exception', exception)
            # type, value, traceback = sys.exc_info()
            result = 'Error deleting %s' % filepath
            exitstatus = None
            signalstatus = 1
    else:
        logger.log_value('Cannot delete file', 'File does not exist')
        result = 'File %s does not exist.' % filepath
        exitstatus = None
        signalstatus = 1

    logger.log_value('The result is', result)
    logger.log_value('The exit status, signal status is', '%s, %s' % (exitstatus, signalstatus))

    return result, exitstatus, signalstatus


def replace_text_in_file(filepath, search_text, replacement_text):
    logger.log_label('Replace text in file')
    logger.log_value('Filepath', filepath)
    logger.log_value('Search text', search_text)
    logger.log_value('Replacement text', replacement_text)

    error = True

    if not filepath:
        logger.log_value('Cannot replace text', 'File not specified')
        return error

    if not exists(filepath):
        logger.log_value('Cannot replace text', 'File %s does not exist' % filepath)
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

    with open(filepath, 'r+') as file:
        file_contents = file.read()
        file_contents = sub(search_text, replacement_text, file_contents)
        file.seek(0)
        file.truncate()
        file.write(file_contents)

    return error
