#!/usr/bin/python3

########################################################################
#                                                                      #
# iso_utilities.py                                                     #
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

from os.path import exists, ismount, join, realpath, relpath
from re import DOTALL, escape, search, sub

from utilities import file_utilities
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
# ISO Mount / Unmount
########################################################################


def mount(iso_mount_point, iso_filepath):

    logger.log_label('Mount the iso image')
    logger.log_value('The mount point is', iso_mount_point)
    logger.log_value('The iso filepath is', iso_mount_point)

    program = join(model.application.directory, 'commands', 'mount')
    command = 'pkexec "%s" "%s" "%s"' % (program, iso_mount_point, iso_filepath)
    result, exitstatus, signalstatus = execute_synchronous(command)

    logger.log_value('The result is', result)
    logger.log_value('The exit status, signal status is', '%s, %s' % (exitstatus, signalstatus))

    return result, exitstatus, signalstatus


def unmount(iso_mount_point):

    logger.log_value('Unmount iso', iso_mount_point)

    program = join(model.application.directory, 'commands', 'unmount')
    command = 'pkexec "%s" "%s"' % (program, iso_mount_point)
    result, exitstatus, signalstatus = execute_synchronous(command)

    logger.log_value('The result is', result)
    logger.log_value('The exit status, signal status is', '%s, %s' % (exitstatus, signalstatus))

    return result, exitstatus, signalstatus


def is_mounted(iso_mount_point, iso_filepath=None):

    if iso_filepath:
        return _is_mounted_1(iso_mount_point, iso_filepath)
    else:
        return _is_mounted_2(iso_mount_point)


def _is_mounted_1(iso_mount_point, iso_filepath):

    logger.log_label('Check if the iso image is mounted')
    logger.log_value('The mount point is', iso_mount_point)
    logger.log_value('The iso filepath is', iso_filepath)

    # Real path is necessary here.
    # The the output of the mount command only includes real paths.
    real_iso_mount_point = realpath(iso_mount_point)
    real_iso_filepath = realpath(iso_filepath)

    # The function os.path.islink() can not be used because it only
    # checks if the last item in the path is a link.
    if iso_mount_point != real_iso_mount_point:
        iso_mount_point = real_iso_mount_point
        logger.log_value('The mount point is a link to', iso_mount_point)
    if iso_filepath != real_iso_filepath:
        iso_filepath = real_iso_filepath
        logger.log_value('The iso filepath is a link to', iso_filepath)

    command = 'mount'
    result, exitstatus, signalstatus = execute_synchronous(command)
    is_mounted = False
    if not exitstatus and not signalstatus:
        mount_information = search(r'%s\s*on\s*%s' % (escape(iso_filepath), escape(iso_mount_point)), result)
        is_mounted = bool(mount_information)

    logger.log_value('Is mounted?', is_mounted)

    return is_mounted


def _is_mounted_2(iso_mount_point):

    logger.log_label('Check if the mount point is mounted')
    logger.log_value('The mount point is', iso_mount_point)

    # The link target is provided for information purposes only.
    # The function os.path.islink() can not be used because it only
    # checks if the last item in the path is a link.
    real_iso_mount_point = realpath(iso_mount_point)
    if iso_mount_point != real_iso_mount_point:
        logger.log_value('The mount point is a link to', real_iso_mount_point)

    # Realpath is not necessary here, because the function
    # ismount() also works for symlinks.
    is_mounted = ismount(iso_mount_point)

    logger.log_value('Is mounted?', is_mounted)

    return is_mounted


def unmount_iso_and_delete_mount_point(iso_mount_point):
    """
    Unmount the ISO and delete the mount point.
    """

    logger.log_value('Unmount the ISO and delete the mount point', iso_mount_point)
    if exists(iso_mount_point):
        result, exitstatus, signalstatus = unmount(iso_mount_point)
        if not signalstatus:
            logger.log_value('Delete the mount point', iso_mount_point)
            result, exitstatus, signalstatus = file_utilities.delete_directory(iso_mount_point)
            if not signalstatus:
                logger.log_value('Deleted the mount point', iso_mount_point)
                pass
            else:
                logger.log_value('Unable to delete the mount point', iso_mount_point)
        else:
            logger.log_value('Unable to unmount the ISO and delete the mount point', iso_mount_point)
    else:
        logger.log_value('Skipping. The mount point does not exist', iso_mount_point)


########################################################################
# ISO Information
########################################################################


def get_iso_volume_id(iso_filepath):

    logger.log_label('Get ISO image volume id')
    logger.log_value('ISO image', iso_filepath)

    # Get the original ISO image volume id.
    command = 'isoinfo -d -i "%s"' % iso_filepath
    result, exitstatus, signalstatus = execute_synchronous(command)
    # iso_volume_id = 'Unknown iso image volume id'
    iso_volume_id = ''
    if not exitstatus and not signalstatus:
        iso_volume_id = sub(r'.*Volume id:\s+(.*[^\n]).*Volume\s+set\s+id.*', r'\1', result, 0, DOTALL)[:32]
    logger.log_value('ISO image volume id', iso_volume_id)
    return iso_volume_id


def get_iso_release_name(iso_mount_point):

    logger.log_label('Get ISO image release name')
    logger.log_value('ISO image mount point', iso_mount_point)

    # Read the original ISO image README.diskdefines file.
    command = 'cat "%s"' % join(iso_mount_point, 'README.diskdefines')
    result, exitstatus, signalstatus = execute_synchronous(command)
    # Get the original ISO image release name.
    # iso_release_name = 'Unknown iso image release name'
    iso_release_name = ''
    if not exitstatus and not signalstatus:
        iso_release_name_infromation = search(r'DISKNAME.*"(.*)"', result)
        if iso_release_name_infromation:
            iso_release_name = iso_release_name_infromation.group(1)
    logger.log_value('ISO image release name', iso_release_name)
    return iso_release_name


def get_iso_disk_name(iso_mount_point):

    logger.log_label('Get ISO image disk name')
    logger.log_value('ISO image mount point', iso_mount_point)

    # Read the original ISO image README.diskdefines file.
    command = 'cat "%s"' % join(iso_mount_point, 'README.diskdefines')
    result, exitstatus, signalstatus = execute_synchronous(command)
    # Get the original ISO image disk name.
    # iso_disk_name = 'Unknown iso image disk name'
    iso_disk_name = ''
    if not exitstatus and not signalstatus:
        iso_disk_name_information = search(r'DISKNAME *(.*)', result)
        if iso_disk_name_information:
            iso_disk_name = iso_disk_name_information.group(1)
    logger.log_value('ISO image disk name', iso_disk_name)
    return iso_disk_name


# TODO: the argument can also be: custom_disk_directory
# filesystem.squashfs may not have been generated in custom_disk_directory, yet.
# Therefore, how to determine the casper_directory ?
# Should we save it from previously, when the image was mounted?
def get_casper_directory(iso_mount_point):

    logger.log_label('Get casper relative directory')
    logger.log_value('ISO image mount point', iso_mount_point)

    casper_directory = file_utilities.get_directory_for_file('filesystem.squashfs', iso_mount_point)
    if casper_directory:
        casper_directory = relpath(casper_directory, iso_mount_point)
    else:
        casper_directory = None

    logger.log_value('Casper relative directory', casper_directory)
    return casper_directory
