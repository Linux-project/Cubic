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

# https://freedesktop.org/wiki/Specifications/file-manager-interface
# https://unix.stackexchange.com/questions/364997/open-a-directory-in-the-default-file-manager-and-select-a-file
# https://docs.python.org/3.9/library/functions.html#open

########################################################################
# Imports
########################################################################

import glob
import hashlib
import magic
import mimetypes
import os
import re
import shutil

from cubic.utilities import logger
from cubic.utilities import model
from cubic.utilities.processor import execute_synchronous

########################################################################
# Global Variables & Constants
########################################################################

# N/A

########################################################################
# Directory Functions
########################################################################


def make_directory(directory):
    """
    Create a single directory when the parent directory path exists.
    """

    logger.log_value('Create directory', directory)

    if not os.path.exists(directory):
        os.mkdir(directory)
    else:
        logger.log_value('Cannot create directory', 'Directory already exists')


def make_directories(file_path):
    """
    Create all directories in the specified file path.
    """

    logger.log_value('Create all directories in the path', file_path)

    if not os.path.exists(file_path):
        os.makedirs(file_path, exist_ok=True)
    else:
        logger.log_value('Cannot create directories', 'The directory path already exists')


# TODO: Check if this function is terminated when the thread is killed?
def delete_directory(directory):
    """
    If permissions prevent deleting the directory, use
    delete_path_as_root() instead.
    """

    logger.log_value('Delete directory', directory)

    if os.path.exists(directory):
        try:
            # https://docs.python.org/3.8/library/shutil.html#shutil.rmtree
            # rmtree(path, ignore_errors=False, onerror=HANDLER)
            # TODO: Path must point to a directory (but not a symbolic link to a directory).
            shutil.rmtree(directory)
            result = f'Successfully deleted {directory}'
            exit_status = 0
            signal_status = None
        except OSError as exception:
            logger.log_value('Exception', exception)
            # type, value, traceback = sys.exc_info()
            result = f'Error deleting {directory}'
            exit_status = None
            signal_status = 1
    else:
        logger.log_value('Cannot delete directory', 'Directory does not exist')
        result = f'Directory {directory} does not exist.'
        exit_status = None
        signal_status = 1

    logger.log_value('The result is', result)
    logger.log_value('The exit status, signal status is', f'{exit_status}, {signal_status}')

    return result, exit_status, signal_status


def delete_files_with_pattern(file_path_pattern, exclude_file_paths=None):

    if exclude_file_paths:
        logger.log_value('Delete existing files with pattern', file_path_pattern)
        logger.log_value('Keep files', exclude_file_paths)
        [delete_path_as_root(file_path) for file_path in glob.glob(file_path_pattern) if file_path not in exclude_file_paths]
    else:
        logger.log_value('Delete existing files with pattern', file_path_pattern)
        [delete_path_as_root(file_path) for file_path in glob.glob(file_path_pattern)]


# https://docs.python.org/3.8/library/shutil.html#shutil.rmtree
def delete_path_as_root(file_path):

    logger.log_value('Delete file', file_path)

    program = os.path.join(model.application.directory, 'commands', 'delete-path')
    command = f'pkexec "{program}" "{file_path}"'
    result, exit_status, signal_status = execute_synchronous(command)
    logger.log_value('The result is', result)
    logger.log_value('The exit status, signal status is', f'{exit_status}, {signal_status}')

    return result, exit_status, signal_status


def get_directory_size(start_path):

    logger.log_label('Calculate directory size')
    logger.log_value('Directory', start_path)

    total_size = 0
    for directory_path, directory_names, file_names in os.walk(start_path):
        for file_name in file_names:
            file_path = os.path.join(directory_path, file_name)
            total_size += os.path.getsize(file_path)

    logger.log_value('Directory size is', total_size)

    return total_size


def directory_is_writable(directory):

    logger.log_value('Check if directory is writable', directory)

    is_writable = os.access(directory, os.R_OK | os.W_OK | os.X_OK)
    logger.log_value('Directory is writable?', is_writable)

    return is_writable


def get_directory_for_file(file_name, start_path):

    logger.log_value(f'Find the directory for {file_name} in', start_path)

    directory = ''
    # The directory may be a symlink.
    for directory_path, directory_names, file_names in os.walk(start_path, followlinks=True):
        if file_name in file_names:
            directory = directory_path
            break

    return directory


def get_file_paths(start_path):

    logger.log_value('Get full file paths in the directory', start_path)

    file_paths = []
    for directory_path, directory_names, file_names in os.walk(start_path):
        for file_name in file_names:
            file_path = os.path.join(directory_path, file_name)
            file_paths.append(file_path)

    return file_paths


def get_relative_file_paths(start_path, exclude_paths):

    logger.log_value('Get relative file paths in the directory', start_path)

    file_paths = []
    for directory_path, directory_names, file_names in os.walk(start_path):
        if directory_path not in exclude_paths:
            for file_name in file_names:
                file_path = os.path.join(directory_path, file_name)
                if file_path not in exclude_paths:
                    relative_file_path = os.path.relpath(file_path, start_path)
                    file_paths.append(relative_file_path)

    return file_paths


def get_file_paths_for_text_file(start_path):

    logger.log_value('Get all text file paths in the directory', start_path)

    file_paths = []
    for directory_path, directory_names, file_names in os.walk(start_path):
        for file_name in file_names:
            file_path = os.path.join(directory_path, file_name)
            try:
                with open(file_path, 'r') as file:
                    file.read()
            except UnicodeDecodeError:
                pass
            else:
                file_paths.append(file_path)

    return file_paths


def get_file_system_type(file_path):

    # Local file system types:
    # • btrfs is reported as btrfs
    # • exfat is reported as exfat (or fuseblk?)
    # • ext2  is reported as ext2
    # • ext3  is reported as ext3
    # • ext4  is reported as ext4
    # • fat12 is reported as vfat (?)
    # • fat16 is reported as vfat
    # • fat32 is reported as vfat
    # • ntfs  is reported as fuseblk
    # • swap  is reported as devtmpfs
    # • xfs   is reported as xfs
    # • zfs   is reported as zfs

    # Remote file system types:
    # • fuse.gvfsd-fuse
    # • fuse.sshfs

    logger.log_value('Get file system type', file_path)

    command = f'df --output=fstype "{file_path}"'
    result, exit_status, signal_status = execute_synchronous(command)
    file_system_type = None
    if not exit_status and not signal_status:
        file_system_type = result.splitlines()[1].lower()
    logger.log_value('The file system type is', file_system_type)

    return file_system_type


########################################################################
# File Functions
########################################################################

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


def read_file(file_path, errors=None):
    """
    Read the contents of a file. This function does not raise an
    exception if there was an error reading the file.

    Arguments:
    file_path : str
        The file to read.
    errors: str
        Specifies how to handle encoding and decoding errors.
        (See https://docs.python.org/3.9/library/functions.html#open).
        • 'strict' (or None)
        • 'ignore'
        • 'replace'
        • 'surrogateescape'
        • 'xmlcharrefreplace'
        • 'backslashreplace'
        • 'namereplace'

    Returns:
    lines : list
        A string containing the file contents.
    """

    # errors - specifies how to handle encoding and decoding errors
    # https://docs.python.org/3.9/library/functions.html#open

    logger.log_value('Read file', file_path)

    file_contents = ''
    try:
        with open(file_path, 'r', errors=errors) as file:
            file_contents = file.read()
    except FileNotFoundError as exception:
        logger.log_value('Error. File does not exist', file_path)
        # logger.log_value('Error. The exception is', exception)
    except Exception as exception:
        logger.log_value('Error. The exception is', exception)

    return file_contents


def read_lines(file_path):
    """
    Read lines from a file; exclude blank lines and trim each line. This
    function does not raise an exception if there was an error reading
    the file.

    Arguments:
    file_path : str
        The file to read.

    Returns:
    lines : list
        A list of strings. The list may be empty.
    """

    logger.log_value('Read lines from file', file_path)

    lines = []
    try:
        with open(file_path, 'r') as file:
            lines = [line.strip() for line in file.readlines() if line.strip()]
    except FileNotFoundError as exception:
        logger.log_value('Error. File does not exist', file_path)
        # logger.log_value('The exception is', exception)
    except Exception as exception:
        logger.log_value('Error. Unable to read lines from file', file_path)
        logger.log_value('The exception is', exception)
    else:
        logger.log_value('Number of lines read', len(lines))

    return lines


def write_line(line, file_path):
    """
    Write the line to the specified file path. If the file path does
    not exist, it will be created.

    Arguments:
    line : str
        The line to write.
    file_path : string
        The file path to write to.
    """

    logger.log_value('Write to file', file_path)

    # Write the line to a new empty file.
    try:
        with open(file_path, 'w') as file:
            # When writing in text mode, the default is to convert
            # occurrences of \n back to platform-specific line endings.
            # (See https://docs.python.org/3/tutorial/inputoutput.html)
            if line: file.write(line)
    except Exception as exception:
        logger.log_value('Error. Unable to write to file', file_path)
        logger.log_value('The exception is', exception)
        raise exception


def write_lines(lines, file_path):
    """
    Write the specified lines to the specified file path. If the file
    path does not exist, it will be created.

    Arguments:
    lines : list or str
        A list of strings or the string to write; may be an empty list
        or None.
    file_path : string
        The file path to write to.
    """

    logger.log_value('Write to file', file_path)

    # Write the lines to a new empty file.
    try:
        if len(lines) <= 100:
            _write_lines_1(lines, file_path)
        else:
            _write_lines_2(lines, file_path)
    except Exception as exception:
        logger.log_value('Error. Unable to write lines to file', file_path)
        logger.log_value('The exception is', exception)
        raise exception


def _write_lines_1(lines, file_path):
    """
    Write 0-100 lines to the specified file path. If the file path does
    not exist, it will be created.

    Arguments:
    lines : list
        A list of strings; may be an empty list.
    file_path : string
        The file path to write to.
    """

    # Write the lines to a new empty file.
    with open(file_path, 'w') as file:
        # When writing in text mode, the default is to convert
        # occurrences of \n back to platform-specific line endings.
        # (See https://docs.python.org/3/tutorial/inputoutput.html)
        file.write('\n'.join(lines))


def _write_lines_2(file_path, lines):
    """
    Write > 100 lines to the specified file path. If the file path does
    not exist, it will be created.

    Arguments:
    lines : list
        A list of strings; may not be an empty list.
    file_path : string
        The file path to write to.
    """

    # Write the lines to a new empty file.
    with open(file_path, 'w') as file:
        for line in lines[:-1]:
            # When writing in text mode, the default is to convert
            # occurrences of \n back to platform-specific line endings.
            # (See https://docs.python.org/3/tutorial/inputoutput.html)
            file.write(line + '\n')
        if line:
            line = lines[-1]
            file.write(line)


def find_in_file(search_regex, file_path):
    """
    Search the file using the regular expression.

    Arguments:
    search_regex : r-str
        The regular expression to search for.
        file_path
    file_path : str
        The file to search.

    Returns:
    results : list
        A list of strings matching the regular expression, or an empty
        list if nothing matched.
    """

    try:
        with open(file_path, 'r') as file:
            file_contents = file.read()
        return re.findall(search_regex, file_contents)
    except FileNotFoundError as exception:
        logger.log_value('File does not exist', file_path)
        return []


def file_contains_any_word(file_path, *words):
    """
    Searches the file for any of the specified words. Stops searching
    when any word is found.

    Arguments:
    file_path : str
        The file to search.
    words : *args str
        The words to search for.

    Returns:
    : boolean
        True if one of the words appears in the file.
        False if none of words appears in the file.
    """

    with open(file_path, 'r') as file:
        for line in file:
            for word in words:
                if word in line:
                    return True

    return False


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
        logger.log_value('Cannot replace text', f'File {file_path} does not exist')
        return error

    if not search_text:
        logger.log_value('Cannot replace text', 'Search text not specified')
        return error

    if not replacement_text:
        logger.log_value('Cannot replace text', 'Replacement text not specified')
        return error

    # TODO: Add a try statement and return error accordingly.
    #       Currently, this is done in repackage_iso_page.update_disk_name(), but it should be done here.
    error = False

    with open(file_path, 'r+') as file:
        file_contents = file.read()
        file_contents = re.sub(search_text, replacement_text, file_contents)
        file.seek(0)
        file.truncate()
        file.write(file_contents)

    return error


def calculate_md5_hash_ALTERNATIVE(file_path, start_path=None):
    """
    Calculate the md5 hash using the m55sum command. This function
    returns the md5 hash and relative file name.
    """

    if start_path:
        command = f'md5sum "./{file_path}"'
    else:
        command = f'md5sum "{file_path}"'
    result, exit_status, signal_status = execute_synchronous(command, start_path)

    logger.log_value('The result is', result)
    logger.log_value('The exit status, signal status is', f'{exit_status}, {signal_status}')

    if not exit_status and not signal_status:
        logger.log_value('Calculate the md5 hash for file', file_path)
        logger.log_value('The md5 hash is', result)
        return result
    else:
        logger.log_value('Unable to calculate the md5 hash for file', file_path)
        return None


def calculate_md5_hash(file_path, start_path=os.path.sep, buffer_size=2**20):
    """
    Calculate the md5 hash by reading a file into a buffer. The default
    buffer size is 2^20 bytes = 1048576 bytes = 1 MiB (Mebibytes).
    """

    # It is necessary to strip the leading '/' from the file_path,
    # otherwise os.path.join() considers the file path to be an absolute
    # path and discards the start path prefix: "If a component is an
    # absolute path, all previous components are thrown away and
    # os.path.joining continues from the absolute path component."
    # (See https://docs.python.org/3/library/os.path.html).
    file_path = file_path.strip(os.path.sep)
    full_file_path = os.path.abspath(os.path.join(start_path, file_path))

    md5_algorithm = hashlib.md5()
    try:
        with open(full_file_path, 'rb') as file:
            data = file.read(buffer_size)
            while data:
                md5_algorithm.update(data)
                data = file.read(buffer_size)
        digest = md5_algorithm.hexdigest()
        # return f'{digest}  ./{file_path}'
        return digest, file_path
    except Exception as exception:
        logger.log_value('Unable to calculate the md5 hash for file', file_path)
        logger.log_value('The exception is', exception)
        raise exception


def copy_file(source_path, target_path):

    logger.log_label('Copy file')
    logger.log_value('Source file path', source_path)
    logger.log_value('Target file path', target_path)

    shutil.copy(source_path, target_path)


# TODO: Check if this function is terminated when the thread is killed?
def delete_file(file_path):
    """
    If permissions prevent deleting the file path, use
    delete_path_as_root() instead.
    """

    logger.log_value('Delete file', file_path)

    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            result = f'Successfully deleted {file_path}'
            exit_status = 0
            signal_status = None
        except OSError as exception:
            logger.log_value('Exception', exception)
            # type, value, traceback = sys.exc_info()
            result = f'Error deleting {file_path}'
            exit_status = None
            signal_status = 1
    else:
        logger.log_value('Cannot delete file', 'File does not exist')
        result = f'File {file_path} does not exist.'
        exit_status = None
        signal_status = 1

    logger.log_value('The result is', result)
    logger.log_value('The exit status, signal status is', f'{exit_status}, {signal_status}')

    return result, exit_status, signal_status


def select_file_in_browser(file_path):
    """
    Opens the file browser and selects the file.
    """

    command = (
        'dbus-send'
        ' --session'
        # ' --print-reply'
        ' --dest=org.freedesktop.FileManager1'
        ' --type=method_call'
        ' /org/freedesktop/FileManager1'
        ' org.freedesktop.FileManager1.ShowItems'
        f' array:string:"file://{file_path}"'
        ' string:""')
    # logger.log_value(('Open in file browser', command)
    logger.log_value('Open in file browser', file_path)
    os.system(command)


def open_directory_in_browser(file_path):
    """
    Opens the file browser and displays the contents of the directory.
    """

    command = (
        'dbus-send'
        ' --session'
        # ' --print-reply'
        ' --dest=org.freedesktop.FileManager1'
        ' --type=method_call'
        ' /org/freedesktop/FileManager1'
        ' org.freedesktop.FileManager1.ShowFolders'
        f' array:string:"file://{file_path}"'
        ' string:""')
    # logger.log_value(('Open in file browser', command)
    logger.log_value('Open in file browser', file_path)
    os.system(command)


def guess_mime_type(full_file_path):
    """
    Guess the mime type using the file extension. This is faster
    than reading the file, but may be inaccurate.

    Arguments:
    full_file_path - Full file path of the file.

    Returns:
    The mime type of the file.
    """

    if os.path.isdir(full_file_path):
        # https://specifications.freedesktop.org/shared-mime-info-spec/shared-mime-info-spec-latest.html#idm140625828597376
        # inode/directory
        mime_type = 'directory'
    else:
        mime_info = mimetypes.guess_type(full_file_path)[0]
        if mime_info:
            mime_type, mime_subtype = mime_info.split(os.path.sep)
            if mime_type == 'application' and mime_subtype == 'octet-stream' and os.path.getsize(full_file_path) == 1:
                mime_type = 'text'
        else:
            mime_type = None

    return mime_type


def read_mime_type(full_file_path):
    """
    Identify the mime type by reading the file. This is slower than
    using the file extension, but is more accurate.

    Arguments:
    full_file_path : str
        Full file path of the file.

    Returns:
    mine_type : str
        The mime type of the file.
    """

    if os.path.isdir(full_file_path):
        # https://specifications.freedesktop.org/shared-mime-info-spec/shared-mime-info-spec-latest.html#idm140625828597376
        # inode/directory
        mime_type = 'directory'
    else:
        mime_info = magic.from_file(full_file_path, True)
        if mime_info:
            mime_type, mime_subtype = mime_info.split(os.path.sep)
            if mime_type == 'application' and mime_subtype == 'octet-stream' and os.path.getsize(full_file_path) == 1:
                mime_type = 'text'
            elif mime_type == 'inode' and mime_subtype == 'x-empty':
                mime_type = 'text'
        else:
            mime_type = None

    return mime_type


def get_icon_name(mime_type):
    """
    Get the standard icon name for the specified mime type using the
    following mapping.

        Mime Type    Icon Name
        ---------    ------------------------
        audio        audio-x-generic
        directory    folder-symbolic
        font         font-x-generic
        image        image-x-generic
        package      package-x-generic
        text         text-x-generic
        video        video-x-generic
        unknown      application-x-executable

    Arguments:
    mime_type : str
        The mime type of the file.

    Returns:
    icon_name : str
        The standard icon name for the specified mime type.
    """

    # TODO: *.pcx files are image files with a mime type of
    #       image/x-pcx, but can not be opened in Cubic as pixbuf.

    if mime_type == 'audo':
        icon_name = 'audio-x-generic'

    elif mime_type == 'directory':
        icon_name = 'folder-symbolic'

    elif mime_type == 'font':
        icon_name = 'font-x-generic'

    elif mime_type == 'image':
        icon_name = 'image-x-generic'

    elif mime_type == 'package':
        icon_name = 'package-x-generic'

    elif mime_type == 'text':
        icon_name = 'text-x-generic'

    elif mime_type == 'video':
        icon_name = 'video-x-generic'

    else:
        icon_name = 'application-x-executable'

    return icon_name
