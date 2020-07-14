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

from datetime import datetime
from os.path import exists, getctime, join
from re import search, sub
from time import localtime, strftime

from constants import ISO_MOUNT_POINT, CUSTOM_ROOT_DIRECTORY, CUSTOM_DISK_DIRECTORY
from constants import NUMBERS_LOWER_CASE, NUMBERS_TITLE_CASE
from utilities import logger
from utilities.processor import execute_synchronous

########################################################################
# References
########################################################################

# https://strftime.org/

########################################################################
# Globals & Constants
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


def get_distribution():
    """
    Read the value of ID from '/etc/os-release'
    """

    distribution = None
    file_path = '/etc/os-release'
    if exists(file_path):
        with open(file_path, 'r') as file:
            for line in file:
                key, value = line.split('=')
                key = key.upper() if key else None
                if key == 'ID':
                    distribution = value.rstrip().lower() if value else None
                    break

    return distribution


def os_is_elementary_based():
    """
    Read the value of ID or ID_LIKE from '/etc/os-release'
    """

    is_elementary_based = False
    file_path = '/etc/os-release'
    if exists(file_path):
        with open(file_path, 'r') as file:
            for line in file:
                key, value = line.split('=')
                key = key.upper() if key else None
                value = value.rstrip().lower() if value else None
                if (key == 'ID' or key == 'ID_LIKE') and 'elementary' in value:
                    is_elementary_based = True
                    break

    return is_elementary_based


def get_kernel_version():

    command = 'uname -r'
    result, exitstatus, signalstatus = execute_synchronous(command)

    return result


def get_package_version(package_name):

    command = 'dpkg-query --showformat="${Version}\n" --show "%s"' % package_name
    result, exitstatus, signalstatus = execute_synchronous(command)

    return result


def get_major_minor_version(package_version):

    return '.'.join(package_version.split('-')[0:2])


def construct_custom_iso_version_number():

    # logger.log_label('Construct custom ISO image version number')

    version = datetime.now().strftime('%Y.%m.%d')

    # logger.log_value('The constructed custom ISO image version number is', date_time)

    return version


def get_current_date_time():

    # logger.log_label('Get current date time')

    date_time = datetime.now().strftime('%A %B %d, %Y %I:%M %p')

    return date_time


def get_file_date_time(filepath):

    # logger.log_label('Get file create date time')

    date_time = getctime(filepath)
    date_time = localtime(date_time)
    date_time = strftime('%A %B %d, %Y %I:%M %p', date_time)

    return date_time


def construct_configuration_filepath(project_directory):

    # logger.log_label('Construct configuration filepath')
    # logger.log_value('The project directory is', project_directory)

    configuration_filepath = join(project_directory, 'cubic.conf')
    # logger.log_value('The constructed configuration filepath is', configuration_filepath)

    return configuration_filepath


def construct_original_iso_mount_point(project_directory):

    # logger.log_label('Construct original ISO image mount point')
    # logger.log_value('The project directory is', project_directory)

    original_iso_mount_point = join(project_directory, ISO_MOUNT_POINT)
    # logger.log_value('The constructed original ISO image mount point is', original_iso_mount_point)

    return original_iso_mount_point


def construct_custom_root_directory(project_directory):

    # logger.log_label('Construct custom root directory')
    # logger.log_value('The project directory is', project_directory)

    custom_root_directory = join(project_directory, CUSTOM_ROOT_DIRECTORY)
    # logger.log_value('The constructed custom root directory is', custom_root_directory)

    return custom_root_directory


def construct_custom_disk_directory(project_directory):

    # logger.log_label('Construct custom live ISO directory')
    # logger.log_value('The project directory is', project_directory)

    custom_disk_directory = join(project_directory, CUSTOM_DISK_DIRECTORY)
    # logger.log_value('The constructed custom live ISO directory is', custom_disk_directory)

    return custom_disk_directory


def construct_custom_iso_filename(original_iso_filename, custom_iso_version_number):

    logger.log_label('Construct custom ISO image filename')
    logger.log_value('The original ISO image filename is', original_iso_filename)
    logger.log_value('The custom ISO image version number is', custom_iso_version_number)

    if original_iso_filename:

        # original_iso_filename = sub('\.iso$', '',
        #                                      original_iso_filename)
        original_iso_filename = original_iso_filename[:-4]

        # original_iso_filename ◀ (text_a)(version)(text_b)
        pattern = r'(^.*)(\d{4}\.\d{2}\.\d{2})(.*$)'
        match = search(pattern, original_iso_filename)
        if match:
            # Version exists in original_iso_filename.
            text_a = match.group(1)
            version = match.group(2)
            text_b = match.group(3)
            logger.log_value('text a', text_a)
            logger.log_value('version', version)
            logger.log_value('text b', text_b)
            # text_a ◀ (text_c)(release)(point_release)(text_d)
            pattern = r'(^.*?)(\d{2}\.\d{1,2})(\.\d{1,2}){0,1}(.*$)'
            match = search(pattern, text_a)
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
                match = search(pattern, text_b)
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
            # custom_iso_filename = text_a + custom_iso_version_number + text_b + '.iso'
            custom_iso_filename = '%s%s%s.iso' % (text_a, custom_iso_version_number, text_b)
        else:
            # original_volume_id ◀ (text_a)(release)(point_release)(text_b)
            pattern = r'(^.*?)(\d{2}\.\d{1,2})(\.\d{1,2}){0,1}(.*$)'
            match = search(pattern, original_iso_filename)
            if match:
                # Release exists in original_iso_filename.
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
                # custom_iso_filename = text_a + release + point_release + '-' + custom_iso_version_number + text_b + '.iso'
                custom_iso_filename = '%s%s%s-%s%s.iso' % (text_a, release, point_release, custom_iso_version_number, text_b)
            else:
                # custom_iso_filename = original_iso_filename + '-' + custom_iso_version_number + '.iso'
                custom_iso_filename = '%s-%s.iso' % (original_iso_filename, custom_iso_version_number)
        # logger.log_value('The constructed custom ISO image filename is', custom_iso_filename)
    else:
        custom_iso_filename = None
        # logger.log_value('The constructed custom ISO image filename is', custom_iso_filename)

    return custom_iso_filename


def construct_custom_iso_volume_id(original_iso_volume_id, custom_iso_version_number):

    logger.log_label('Construct custom ISO image volume id')
    logger.log_value('The original ISO image volume id is', original_iso_volume_id)
    logger.log_value('The custom ISO image version number is', custom_iso_version_number)

    if original_iso_volume_id:
        # original_iso_volume_id ◀ (text_a)(version)(text_b)
        pattern = r'(^.*)(\d{4}\.\d{2}\.\d{2})(.*$)'
        match = search(pattern, original_iso_volume_id)
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
            match = search(pattern, text_a)
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
                match = search(pattern, text_b)
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
            match = search(pattern, original_iso_volume_id)
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
        custom_iso_volume_id = custom_iso_volume_id[:32]
        # logger.log_value('The constructed custom ISO image volume id is', custom_iso_volume_id)
    else:
        custom_iso_volume_id = None
        # logger.log_value('The constructed custom ISO image volume id is', custom_iso_volume_id)

    return custom_iso_volume_id


def construct_custom_iso_release_name(original_iso_release_name):

    # logger.log_label('Construct custom ISO image release name')
    # logger.log_value('The original ISO image release name is', original_iso_release_name)

    try:
        custom_iso_release_name = 'Custom %s' % sub(r'^Custom\s*', '', original_iso_release_name)
    except Exception as exception:
        logger.log_value('Encountered exception while creating custom ISO image release name', exception)
        custom_iso_release_name = ''
    # logger.log_value('The constructed custom ISO image release name is', custom_iso_release_name)

    return custom_iso_release_name


def construct_custom_iso_disk_name(custom_iso_volume_id, custom_iso_release_name):

    # logger.log_label('Construct custom ISO image disk name')
    # logger.log_value('The custom ISO image volume id is', custom_iso_volume_id)
    # logger.log_value('The custom ISO image release name is', custom_iso_release_name)

    if custom_iso_volume_id and custom_iso_release_name:
        custom_iso_disk_name = '%s "%s"' % (custom_iso_volume_id, custom_iso_release_name)
    elif custom_iso_volume_id:
        custom_iso_disk_name = '%s' % custom_iso_volume_id
    elif custom_iso_release_name:
        custom_iso_disk_name = '"%s"' % custom_iso_release_name
    else:
        custom_iso_disk_name = ''

    # logger.log_value('The constructed custom ISO image disk name is', custom_iso_disk_name)

    return custom_iso_disk_name


def construct_custom_iso_disk_name_ORIGINAL(custom_iso_volume_id, custom_iso_release_name):

    # logger.log_label('Construct custom ISO image disk name')
    # logger.log_value('The custom ISO image volume id is', custom_iso_volume_id)
    # logger.log_value('The custom ISO image release name is', custom_iso_release_name)

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
    # logger.log_value('The constructed custom ISO image disk name is', custom_iso_disk_name)

    return custom_iso_disk_name


def construct_custom_iso_checksum_filename(custom_iso_filename):

    # logger.log_label('Construct custom ISO image checksum filename')
    # logger.log_value('The custom ISO image filename is', custom_iso_filename)

    try:
        # filename_root = splitext(custom_iso_filename)[0]
        # filename_root = search(r'(.*?)\.iso*', custom_iso_filename).group(1)
        # filename_root = search(r'(.*?)(?:(?:\.iso)*)$', custom_iso_filename).group(1)
        custom_iso_checksum_filename = '%s.md5' % custom_iso_filename[:-4]
    except Exception as exception:
        logger.log_value('Encountered exception while creating custom ISO image checksum filename', exception)
        custom_iso_checksum_filename = 'custom.md5'

    # logger.log_value('The constructed custom ISO image checksum filename is', custom_iso_checksum_filename)

    return custom_iso_checksum_filename
