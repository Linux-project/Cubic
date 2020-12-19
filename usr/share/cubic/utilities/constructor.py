#!/usr/bin/python3

########################################################################
#                                                                      #
# constructor.py                                                      #
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

# https://time.strftime.org/

########################################################################
# Imports
########################################################################

import os
import re
import time
import zlib

from constants import ISO_MOUNT_POINT, CUSTOM_ROOT_DIRECTORY, CUSTOM_DISK_DIRECTORY
from constants import NUMBERS_LOWER_CASE, NUMBERS_TITLE_CASE
from constants import TIME_STAMP_FORMAT, VERSION_NUMBER_FORMAT
from utilities import logger
from utilities.processor import execute_synchronous

########################################################################
# Global Variables & Constants
########################################################################

# N/A

########################################################################
# Functions
########################################################################


def number_as_text(number, title_case=False):

    if number < len(NUMBERS_TITLE_CASE):
        if title_case:
            return NUMBERS_TITLE_CASE[number]
        else:
            return NUMBERS_LOWER_CASE[number]
    else:
        return str(number)


def get_plural(singular_text, plural_text, count):

    return singular_text if count == 1 else plural_text


def get_os_distribution(root_directory='/'):
    """
    Read the value of ID from '/etc/os-release'
    Arguments:
    root_directory - The root directory of the OS.
                     May be '/' to get the distribution of the host OS.
                     May be model.project.custom_root_directory to get
                     the distribution of the custom OS.
    """

    distribution = None
    file_path = os.path.join(root_directory, 'etc/os-release')
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            for line in file:
                key, value = line.split('=')
                key = key.upper() if key else None
                if key == 'ID':
                    distribution = value.rstrip().lower() if value else None
                    break

    return distribution


def os_is_distribution(distribution, root_directory='/'):
    """
    Read the value of ID from '/etc/os-release'
    Arguments:
    root_directory - The root directory of the OS.
                     May be '/' to get the distribution of the host OS.
                     May be model.project.custom_root_directory to get
                     the distribution of the custom OS.
    distribution   - The distribution to check, for example, 'pop' for
                     Pop!_OS or 'elementary' for Elementary.
    """
    is_distribution = False
    distribution = distribution.lower()
    file_path = os.path.join(root_directory, 'etc/os-release')
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            for line in file:
                key, value = line.split('=')
                key = key.upper() if key else None
                value = value.rstrip().lower() if value else None
                if key == 'ID':
                    if root_directory == '/':
                        logger.log_value('The host OS distribution is', value)
                    else:
                        logger.log_value('The custom OS distribution is', value)
                    if distribution in value:
                        is_distribution = True
                        break
                elif key == 'ID_LIKE':
                    if root_directory == '/':
                        logger.log_value('The host OS distribution like is', value)
                    else:
                        logger.log_value('The custom OS distribution like is', value)
                    if distribution in value:
                        is_distribution = True
                        break

    return is_distribution


def get_kernel_version():

    command = 'uname -r'
    result, exit_status, signal_status = execute_synchronous(command)

    return result


def get_package_version(package_name):

    command = 'dpkg-query --showformat="${Version}\n" --show "%s"' % package_name
    result, exit_status, signal_status = execute_synchronous(command)

    return result


def get_major_minor_version(package_version):

    return '.'.join(package_version.split('-')[0:2])


def construct_custom_iso_version_number():

    # logger.log_label('Construct custom disk image version number')

    version = time.strftime(VERSION_NUMBER_FORMAT)

    # logger.log_value('The constructed custom disk image version number is', version)

    return version


def get_current_time_stamp():

    # logger.log_label('Get current time stamp in localized format')

    time_stamp = time.strftime(TIME_STAMP_FORMAT)

    return time_stamp


def reformat_time_stamp(time_stamp, new_format, old_format=TIME_STAMP_FORMAT):

    # logger.log_label('Get current time stamp in localized format')

    struct_time = time.strptime(time_stamp, old_format)
    time_stamp = time.strftime(new_format, struct_time)

    return time_stamp


def get_file_time_stamp(file_path):

    # logger.log_label('Get file create date time')

    time_stamp = os.path.getmtime(file_path)
    time_stamp = time.localtime(time_stamp)
    time_stamp = time.strftime(TIME_STAMP_FORMAT, time_stamp)

    return time_stamp


def construct_configuration_file_path(project_directory):

    # logger.log_label('Construct configuration file path')
    # logger.log_value('The project directory is', project_directory)

    configuration_file_path = os.path.join(project_directory, 'cubic.conf')
    # logger.log_value('The constructed configuration file path is', configuration_file_path)

    return configuration_file_path


def construct_original_iso_mount_point(project_directory):

    # logger.log_label('Construct original disk image mount point')
    # logger.log_value('The project directory is', project_directory)

    original_iso_mount_point = os.path.join(project_directory, ISO_MOUNT_POINT)
    # logger.log_value('The constructed original disk image mount point is', original_iso_mount_point)

    return original_iso_mount_point


def construct_custom_root_directory(project_directory):

    # logger.log_label('Construct custom root directory')
    # logger.log_value('The project directory is', project_directory)

    custom_root_directory = os.path.join(project_directory, CUSTOM_ROOT_DIRECTORY)
    # logger.log_value('The constructed custom root directory is', custom_root_directory)

    return custom_root_directory


def construct_custom_disk_directory(project_directory):

    # logger.log_label('Construct custom disk directory')
    # logger.log_value('The project directory is', project_directory)

    custom_disk_directory = os.path.join(project_directory, CUSTOM_DISK_DIRECTORY)
    # logger.log_value('The constructed custom disk directory is', custom_disk_directory)

    return custom_disk_directory


def construct_custom_iso_file_name(original_iso_file_name, custom_iso_version_number):

    logger.log_label('Construct custom disk image file name')
    logger.log_value('The original disk image file name is', original_iso_file_name)
    logger.log_value('The custom disk image version number is', custom_iso_version_number)

    if original_iso_file_name:

        # original_iso_file_name = re.sub('\.iso$', '',
        #                                      original_iso_file_name)
        original_iso_file_name = original_iso_file_name[:-4]

        # original_iso_file_name ◀ (text_a)(version)(text_b)
        pattern = r'(^.*)(\d{4}\.\d{2}\.\d{2})(.*$)'
        match = re.search(pattern, original_iso_file_name)
        if match:
            # Version exists in original_iso_file_name.
            text_a = match.group(1)
            version = match.group(2)
            text_b = match.group(3)
            logger.log_value('text a', text_a)
            logger.log_value('version', version)
            logger.log_value('text b', text_b)
            # text_a ◀ (text_c)(release)(point_release)(text_d)
            pattern = r'(^.*?)(\d{2}\.\d{1,2})(\.\d{1,2}){0,1}(.*$)'
            match = re.search(pattern, text_a)
            if match:
                # Release exists in text_a.
                text_c = match.group(1)
                release = match.group(2)
                point_release = match.group(3)
                text_d = match.group(4)
                logger.log_value('text c', text_c)
                logger.log_value('release', release)
                logger.log_value('point release', point_release)
                logger.log_value('text d', text_d)
                if not point_release:
                    point_release = '.0'
                    logger.log_value('new point_release', point_release)
                    # text_a = text_c + release + point_release + text_d
                    text_a = '%s%s%s%s' % (text_c, release, point_release, text_d)
                    logger.log_value('new text a', text_a)
            else:
                # text_b ◀ (text_c)(release)(point_release)(text_d)
                match = re.search(pattern, text_b)
                if match:
                    # Release exists in text_b.
                    text_c = match.group(1)
                    release = match.group(2)
                    point_release = match.group(3)
                    text_d = match.group(4)
                    logger.log_value('text c', text_c)
                    logger.log_value('release', release)
                    logger.log_value('point release', point_release)
                    logger.log_value('text d', text_d)
                    if not point_release:
                        point_release = '.0'
                        logger.log_value('new point_release', point_release)
                        # text_b = text_c + release + point_release + text_d
                        text_b = '%s%s%s%s' % (text_c, release, point_release, text_d)
                        logger.log_value('new text b', text_b)
            # custom_iso_file_name = text_a + custom_iso_version_number + text_b + '.iso'
            custom_iso_file_name = '%s%s%s.iso' % (text_a, custom_iso_version_number, text_b)
        else:
            # original_volume_id ◀ (text_a)(release)(point_release)(text_b)
            pattern = r'(^.*?)(\d{2}\.\d{1,2})(\.\d{1,2}){0,1}(.*$)'
            match = re.search(pattern, original_iso_file_name)
            if match:
                # Release exists in original_iso_file_name.
                text_a = match.group(1)
                release = match.group(2)
                point_release = match.group(3)
                text_b = match.group(4)
                logger.log_value('text a', text_a)
                logger.log_value('release', release)
                logger.log_value('point release', point_release)
                logger.log_value('text b', text_b)
                if not point_release:
                    point_release = '.0'
                    logger.log_value('new point_release', point_release)
                # custom_iso_file_name = text_a + release + point_release + '-' + custom_iso_version_number + text_b + '.iso'
                custom_iso_file_name = '%s%s%s-%s%s.iso' % (text_a, release, point_release, custom_iso_version_number, text_b)
            else:
                # custom_iso_file_name = original_iso_file_name + '-' + custom_iso_version_number + '.iso'
                custom_iso_file_name = '%s-%s.iso' % (original_iso_file_name, custom_iso_version_number)
        # logger.log_value('The constructed custom disk image file name is', custom_iso_file_name)
    else:
        custom_iso_file_name = None
        # logger.log_value('The constructed custom disk image file name is', custom_iso_file_name)

    return custom_iso_file_name


def construct_custom_iso_volume_id(original_iso_volume_id, custom_iso_version_number):

    logger.log_label('Construct custom disk image volume id')
    logger.log_value('The original disk image volume id is', original_iso_volume_id)
    logger.log_value('The custom disk image version number is', custom_iso_version_number)

    if original_iso_volume_id:
        # original_iso_volume_id ◀ (text_a)(version)(text_b)
        pattern = r'(^.*)(\d{4}\.\d{2}\.\d{2})(.*$)'
        match = re.search(pattern, original_iso_volume_id)
        if match:
            # Version exists in original_iso_volume_id.
            text_a = match.group(1)
            version = match.group(2)
            text_b = match.group(3)
            logger.log_value('text a', text_a)
            logger.log_value('version', version)
            logger.log_value('text b', text_b)
            # text_a ◀ (text_c)(release)(point_release)(text_d)
            pattern = r'(^.*?)(\d{2}\.\d{1,2})(\.\d{1,2}){0,1}(.*$)'
            match = re.search(pattern, text_a)
            if match:
                # Release exists in text_a.
                text_c = match.group(1)
                release = match.group(2)
                point_release = match.group(3)
                text_d = match.group(4)
                logger.log_value('text c', text_c)
                logger.log_value('release', release)
                logger.log_value('point release', point_release)
                logger.log_value('text d', text_d)
                if not point_release:
                    point_release = '.0'
                    logger.log_value('new point_release', point_release)
                    # text_a = text_c + release + point_release + text_d
                    text_a = '%s%s%s%s' % (text_c, release, point_release, text_d)
                    logger.log_value('new text a', text_a)
            else:
                # text_b ◀ (text_c)(release)(point_release)(text_d)
                match = re.search(pattern, text_b)
                if match:
                    # Release exists in text_b.
                    text_c = match.group(1)
                    release = match.group(2)
                    point_release = match.group(3)
                    text_d = match.group(4)
                    logger.log_value('text c', text_c)
                    logger.log_value('release', release)
                    logger.log_value('point release', point_release)
                    logger.log_value('text d', text_d)
                    if not point_release:
                        point_release = '.0'
                        logger.log_value('new point_release', point_release)
                        # text_b = text_c + release + point_release + text_d
                        text_b = '%s%s%s%s' % (text_c, release, point_release, text_d)
                        logger.log_value('new text b', text_b)
            # custom_iso_volume_id = text_a + custom_iso_version_number + text_b
            custom_iso_volume_id = '%s%s%s' % (text_a, custom_iso_version_number, text_b)
        else:
            # original_volume_id ◀ (text_a)(release)(point_release)(text_b)
            pattern = r'(^.*?)(\d{2}\.\d{1,2})(\.\d{1,2}){0,1}(.*$)'
            match = re.search(pattern, original_iso_volume_id)
            if match:
                # Release exists in original_iso_volume_id.
                text_a = match.group(1)
                release = match.group(2)
                point_release = match.group(3)
                text_b = match.group(4)
                logger.log_value('text a', text_a)
                logger.log_value('release', release)
                logger.log_value('point release', point_release)
                logger.log_value('text b', text_b)
                if not point_release:
                    point_release = '.0'
                    logger.log_value('new point_release', point_release)
                # custom_iso_volume_id = text_a + release + point_release + ' ' + custom_iso_version_number + text_b
                custom_iso_volume_id = '%s%s%s %s%s' % (text_a, release, point_release, custom_iso_version_number, text_b)
            else:
                # custom_iso_volume_id = original_iso_volume_id + ' ' + custom_iso_version_number
                custom_iso_volume_id = '%s %s' % (original_iso_volume_id, custom_iso_version_number)
        # If volume id is longer than 32 characters, and there is a space
        # within the last five positions, trim the space and subsequent
        # characters.
        if len(custom_iso_volume_id) > 32:
            try:
                index_of_space = custom_iso_volume_id.rindex(' ', 27, 32)
                logger.log_value('The custom iso volume id is too long', 'Trim all characters after the space at index %s' % index_of_space)
            except ValueError as exception:
                custom_iso_volume_id = custom_iso_volume_id[:32]
                logger.log_value('The custom iso volume id is too long', 'Trim to 32 characters')
            else:
                custom_iso_volume_id = custom_iso_volume_id[:index_of_space]
        # logger.log_value('The constructed custom disk image volume id is', custom_iso_volume_id)
    else:
        custom_iso_volume_id = None
        # logger.log_value('The constructed custom disk image volume id is', custom_iso_volume_id)

    return custom_iso_volume_id


def construct_custom_iso_release_name(original_iso_release_name):

    # logger.log_label('Construct custom disk image release name')
    # logger.log_value('The original disk image release name is', original_iso_release_name)

    try:
        custom_iso_release_name = 'Custom %s' % re.sub(r'^Custom\s*', '', original_iso_release_name)
    except Exception as exception:
        logger.log_value('Encountered exception while creating custom disk image release name', exception)
        custom_iso_release_name = ''
    # logger.log_value('The constructed custom disk image release name is', custom_iso_release_name)

    return custom_iso_release_name


def construct_custom_iso_disk_name(custom_iso_volume_id, custom_iso_release_name):

    # logger.log_label('Construct custom disk image disk name')
    # logger.log_value('The custom disk image volume id is', custom_iso_volume_id)
    # logger.log_value('The custom disk image release name is', custom_iso_release_name)

    if custom_iso_volume_id and custom_iso_release_name:
        custom_iso_disk_name = '%s "%s"' % (custom_iso_volume_id, custom_iso_release_name)
    elif custom_iso_volume_id:
        custom_iso_disk_name = '%s' % custom_iso_volume_id
    elif custom_iso_release_name:
        custom_iso_disk_name = '"%s"' % custom_iso_release_name
    else:
        custom_iso_disk_name = ''

    # logger.log_value('The constructed custom disk image disk name is', custom_iso_disk_name)

    return custom_iso_disk_name


def construct_custom_iso_disk_name_ORIGINAL(custom_iso_volume_id, custom_iso_release_name):

    # logger.log_label('Construct custom disk image disk name')
    # logger.log_value('The custom disk image volume id is', custom_iso_volume_id)
    # logger.log_value('The custom disk image release name is', custom_iso_release_name)

    # The custom_iso_volume_id and custom_iso_release_name may be empty
    # strings but are never None.
    custom_iso_disk_name = '%s "%s"' % (custom_iso_volume_id, custom_iso_release_name)
    #
    custom_iso_disk_name.strip()[:32]
    '''
    if custom_iso_volume_id and custom_iso_release_name:
        custom_iso_disk_name = '%s "%s"' % (custom_iso_volume_id, custom_iso_release_name)
    elif custom_iso_volume_id:
        custom_iso_disk_name = custom_iso_volume_id
    elif custom_iso_release_name:
        custom_iso_disk_name = custom_iso_release_name
    else:
        custom_iso_disk_name = ''
    '''
    # logger.log_value('The constructed custom disk image disk name is', custom_iso_disk_name)

    return custom_iso_disk_name


def construct_custom_iso_checksum_file_name(custom_iso_file_name):

    # logger.log_label('Construct custom disk image checksum file name')
    # logger.log_value('The custom disk image file name is', custom_iso_file_name)

    try:
        # file_name_root = splitext(custom_iso_file_name)[0]
        # file_name_root = re.search(r'(.*?)\.iso*', custom_iso_file_name).group(1)
        # file_name_root = re.search(r'(.*?)(?:(?:\.iso)*)$', custom_iso_file_name).group(1)
        custom_iso_checksum_file_name = '%s.md5' % custom_iso_file_name[:-4]
    except Exception as exception:
        logger.log_value('Encountered exception while creating custom disk image checksum file name', exception)
        custom_iso_checksum_file_name = 'custom.md5'

    # logger.log_value('The constructed custom disk image checksum file name is', custom_iso_checksum_file_name)

    return custom_iso_checksum_file_name


def encode(t):

    b = t.encode('utf-8')
    z = zlib.compress(b)
    h = z.hex().upper()

    return h


def decode(h):

    z = bytes.fromhex(h)
    b = zlib.decompress(z)
    t = b.decode('utf-8')

    return t
