#!/usr/bin/python3

########################################################################
#                                                                      #
# delete_page.py                                                       #
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

from constants import OK, ERROR, OPTIONAL, BULLET, PROCESSING, BLANK

from utilities import constructors
from utilities import display
from utilities import file_utilities
from utilities import iso_utilities
from utilities import logger
from utilities import model

import glob
import os
from time import sleep

########################################################################
# Globals & Constants
########################################################################

name = 'delete_page'
custom = None

########################################################################
# Navigation Functions
########################################################################

# TODO: .#custom-root.lck
#       Perhaps always remove it after exiting the terminal page?


def setup(action, old_page=None):

    if action == 'delete':

        display.reset_buttons(
            back_button_label='Cancel',
            back_action='cancel',
            back_button_style=None,
            is_back_sensitive=True,
            is_back_visible=True,
            next_button_label='Delete',
            next_action='delete',
            next_button_style='destructive-action',
            is_next_sensitive=True,
            is_next_visible=True)

        display.update_entry('delete_page__project_directory_entry', model.project.directory)

        # TODO: If custom.iso_filename does not exist, then display a message below the entry.
        filepath = os.path.join(model.custom.iso_directory, model.custom.iso_filename)
        if os.path.isfile(filepath):
            display.update_entry('delete_page__custom_iso_filename_entry', model.custom.iso_filename)
        else:
            display.update_entry('delete_page__custom_iso_filename_entry', '(not available)')

        display.update_entry('delete_page__custom_iso_version_number_entry', model.custom.iso_version_number)
        # display.update_entry('delete_page__custom_iso_directory_entry', model.custom.iso_directory)
        display.update_entry('delete_page__custom_iso_volume_id_entry', model.custom.iso_volume_id)
        display.update_entry('delete_page__custom_iso_release_name_entry', model.custom.iso_release_name)
        display.update_entry('delete_page__custom_iso_disk_name_entry', model.custom.iso_disk_name)

        display.update_status('delete_page__project_configuration_file', BULLET)
        display.update_label('delete_page__project_configuration_file_message', '')

        display.update_status('delete_page__project_iso_mount_point', BULLET)
        display.update_label('delete_page__project_iso_mount_point_message', '')

        display.update_status('delete_page__custom_root_directory', BULLET)
        display.update_label('delete_page__custom_root_directory_message', '')

        display.update_status('delete_page__custom_disk_directory', BULLET)
        display.update_label('delete_page__custom_disk_directory_message', '')

        display.update_status('delete_page__custom_iso_and_checksum', BULLET)

        filepath_pattern = os.path.join(model.project.directory, '*.iso')
        iso_filepath_list = glob.glob(filepath_pattern)

        filepath_pattern = os.path.join(model.project.directory, '*.md5')
        iso_checksum_filepath_list = glob.glob(filepath_pattern)

        # This must be consistent with on_toggled__delete_page__custom_iso_and_checksum_check_button()
        if iso_checksum_filepath_list and iso_filepath_list:
            iso_count_text = constructors.number_as_text(len(iso_filepath_list))
            iso_files_text = 'file' if len(iso_filepath_list) == 1 else 'files'
            md5_count_text = constructors.number_as_text(len(iso_checksum_filepath_list))
            md5_files_text = 'file' if len(iso_checksum_filepath_list) == 1 else 'files'
            label = 'Delete %s ISO disk image %s and %s MD5 checksum %s.' % (iso_count_text, iso_files_text, md5_count_text, md5_files_text)
            enable = True
        elif iso_filepath_list:
            iso_count_text = constructors.number_as_text(len(iso_filepath_list))
            iso_files_text = 'file' if len(iso_filepath_list) == 1 else 'files'
            label = 'Delete %s ISO disk image %s.' % (iso_count_text, iso_files_text)
            enable = True
        elif iso_checksum_filepath_list:
            md5_count_text = constructors.number_as_text(len(iso_checksum_filepath_list))
            md5_files_text = 'file' if len(iso_checksum_filepath_list) == 1 else 'files'
            label = 'Delete %s MD5 checksum %s.' % (md5_count_text, md5_files_text)
            enable = True
        else:
            label = 'There are no ISO files or MD5 files in this project directory.'
            enable = False

        display.update_check_button_label('delete_page__custom_iso_and_checksum_check_button', label)
        display.activate_check_button('delete_page__custom_iso_and_checksum_check_button', enable)
        display.set_sensitive('delete_page__custom_iso_and_checksum_check_button', enable)

        return

    else:

        return 'unknown'


def enter(action, old_page=None):

    if action == 'delete':

        return

    else:

        return 'unknown'


def leave(action, new_page=None):

    if action == 'cancel':

        display.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        return

    elif action == 'delete':

        display.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        is_error = delete_project_files()

        if is_error:
            return 'error'
            # Wait before transitioning away from the page.
            sleep(1.00)
        else:
            # Wait before transitioning away from the page.
            sleep(1.00)
            return

    elif action == 'quit':

        display.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        return

    else:

        return 'unknown'


########################################################################
# Handler Functions
########################################################################


def on_clicked__delete_page__project_directory_open_button(widget):

    print('on_clicked__delete_page__project_directory_open_button')

    command = 'xdg-open %s &' % model.project.directory
    os.system(command)


def on_clicked__delete_page__custom_iso_filename_open_button(widget):

    print('on_clicked__delete_page__project_directory_open_button')

    if os.path.isfile('/bin/nautilus'):
        filepath = os.path.join(model.custom.iso_directory, model.custom.iso_filename)
        if not os.path.isfile(filepath):
            filepath = model.custom.iso_directory
        command = 'nautilus %s &' % filepath
        os.system(command)
    else:
        command = 'xdg-open %s &' % model.custom.iso_directory
        os.system(command)


# TODO: remove this function and remove from *.ui file.
def on_toggled__delete_page__custom_iso_and_checksum_check_button(widget):

    print('on_toggled__delete_page__custom_iso_and_checksum_check_button')


########################################################################
# Support Functions
########################################################################


def delete_project_files_TEST():

    is_error = False

    #
    # Unmount and delete the original ISO mount point.
    #
    logger.log_value('Unmount the original ISO and delete the mount point', model.project.iso_mount_point)
    display.update_status('delete_page__project_iso_mount_point', PROCESSING)
    sleep(1.00)
    display.update_status('delete_page__project_iso_mount_point', OK)
    display.update_label('delete_page__project_iso_mount_point_message', 'Testing testing testing.')
    # Pause to allow the user to see the result.
    sleep(1.00)

    #
    # Delete the configuration file
    #
    logger.log_value('Delete the configuration file', model.project.configuration_filepath)
    display.update_status('delete_page__project_configuration_file', PROCESSING)
    sleep(1.00)
    display.update_status('delete_page__project_configuration_file', OK)
    display.update_label('delete_page__project_configuration_file_message', 'Testing testing testing.')
    sleep(1.00)

    #
    # Delete the custom root directory.
    #
    logger.log_value('Delete the custom root directory', model.project.custom_root_directory)
    display.update_status('delete_page__custom_root_directory', PROCESSING)
    sleep(1.00)
    display.update_status('delete_page__custom_root_directory', OK)
    display.update_label('delete_page__custom_root_directory_message', 'Testing testing testing.')
    # Pause to allow the user to see the result.
    sleep(1.00)

    #
    # Delete the custom ISO directory.
    #
    logger.log_value('Delete the custom ISO directory', model.project.custom_disk_directory)
    display.update_status('delete_page__custom_disk_directory', PROCESSING)
    sleep(1.00)
    display.update_status('delete_page__custom_disk_directory', OK)
    display.update_label('delete_page__custom_disk_directory_message', 'Testing testing testing.')
    # Pause to allow the user to see the result.
    sleep(1.00)

    #
    # Delete the custom ISO checksum files and the custom ISO files.
    #
    display.update_status('delete_page__custom_iso_and_checksum', PROCESSING)
    sleep(1.00)
    display.update_status('delete_page__custom_iso_and_checksum', OK)
    display.update_label('delete_page__custom_iso_and_checksum_message', 'Testing testing testing.')
    # Pause to allow the user to see the result.
    sleep(1.00)

    return is_error


def delete_project_files():

    display.set_sensitive('delete_page__custom_iso_and_checksum_check_button', False)

    is_error = False

    #
    # Unmount and delete the original ISO mount point.
    #
    logger.log_value('Unmount the original ISO and delete the mount point', model.project.iso_mount_point)
    display.update_status('delete_page__project_iso_mount_point', PROCESSING)
    sleep(1.00)
    if os.path.exists(model.project.iso_mount_point):
        # Unmount the original ISO disk image.
        result, exitstatus, signalstatus = iso_utilities.unmount(model.project.iso_mount_point)
        if not signalstatus:
            display.update_status('delete_page__project_iso_mount_point', OK)
            display.update_label('delete_page__project_iso_mount_point_message', '')
            sleep(0.50)
            # Delete the mount point.
            logger.log_value('Delete the original ISO mount point', model.project.iso_mount_point)
            result, exitstatus, signalstatus = file_utilities.delete_directory(model.project.iso_mount_point)
            if not signalstatus:
                display.update_status('delete_page__project_iso_mount_point', OK)
                display.update_label('delete_page__project_iso_mount_point_message', '')
            else:
                display.update_status('delete_page__project_iso_mount_point', ERROR)
                display.update_label('delete_page__project_iso_mount_point_message', 'Unable to delete the mount point.')
                is_error = True
        else:
            display.update_status('delete_page__project_iso_mount_point', ERROR)
            display.update_label('delete_page__project_iso_mount_point_message', 'Unable to unmount the iso.')
            is_error = True
    else:
        display.update_status('delete_page__project_iso_mount_point', OK)
        display.update_label('delete_page__project_iso_mount_point_message', 'Nothing to unmount.')
    # Pause to allow the user to see the result.
    sleep(1.00)

    #
    # Delete the configuration file
    #
    logger.log_value('Delete the configuration file', model.project.configuration_filepath)
    display.update_status('delete_page__project_configuration_file', PROCESSING)
    sleep(1.00)
    if os.path.exists(model.project.configuration_filepath):
        result, exitstatus, signalstatus = file_utilities.delete_file(model.project.configuration_filepath)
        if not signalstatus:
            display.update_status('delete_page__project_configuration_file', OK)
            display.update_label('delete_page__project_configuration_file_message', '')
        else:
            display.update_status('delete_page__project_configuration_file', ERROR)
            display.update_label('delete_page__project_configuration_file_message', 'Unable to delete this file.')
            is_error = True
    else:
        display.update_status('delete_page__project_configuration_file', OK)
        display.update_label('delete_page__project_configuration_file_message', 'Nothing to delete. This file does not exist.')
    # Pause to allow the user to see the result.
    sleep(1.00)

    #
    # Delete the custom root directory.
    #
    logger.log_value('Delete the custom root directory', model.project.custom_root_directory)
    display.update_status('delete_page__custom_root_directory', PROCESSING)
    sleep(1.00)
    if os.path.exists(model.project.custom_root_directory):
        result, exitstatus, signalstatus = file_utilities.delete_path_as_root(model.project.custom_root_directory)
        if not signalstatus:
            display.update_status('delete_page__custom_root_directory', OK)
            display.update_label('delete_page__custom_root_directory_message', '')
        else:
            display.update_status('delete_page__custom_root_directory', ERROR)
            display.update_label('delete_page__custom_root_directory_message', 'Unable to delete the customized Linux files.')
            is_error = True
    else:
        display.update_status('delete_page__custom_root_directory', OK)
        display.update_label('delete_page__custom_root_directory_message', 'Nothing to delete. These files not exist.')
    # Pause to allow the user to see the result.
    sleep(1.00)

    #
    # Delete the custom disk directory.
    #
    logger.log_value('Delete the custom ISO directory', model.project.custom_disk_directory)
    # display.update_label('delete_page__custom_disk_directory_message', model.project.custom_disk_directory)
    display.update_status('delete_page__custom_disk_directory', PROCESSING)
    sleep(1.00)
    if os.path.exists(model.project.custom_disk_directory):
        result, exitstatus, signalstatus = file_utilities.delete_directory(model.project.custom_disk_directory)
        if not signalstatus:
            display.update_status('delete_page__custom_disk_directory', OK)
            display.update_label('delete_page__custom_disk_directory_message', '')
        else:
            display.update_status('delete_page__custom_disk_directory', ERROR)
            display.update_label('delete_page__custom_disk_directory_message', 'Unable to delete the customized disk image files.')
            is_error = True
    else:
        display.update_status('delete_page__custom_disk_directory', OK)
        display.update_label('delete_page__custom_disk_directory_message', 'Nothing to delete. These files do not exist.')
    # Pause to allow the user to see the result.
    sleep(1.00)

    #
    # Delete the custom ISO checksum files and the custom ISO files.
    #
    check_button = model.builder.get_object('delete_page__custom_iso_and_checksum_check_button')
    is_active = check_button.get_active()

    logger.log_value('Delete the custom ISO checksum files and the custom ISO files?', is_active)
    if is_active:

        display.update_status('delete_page__custom_iso_and_checksum', PROCESSING)
        sleep(1.00)

        filepath_pattern = os.path.join(model.project.directory, '*.md5')
        iso_checksum_filepath_list = glob.glob(filepath_pattern)

        filepath_pattern = os.path.join(model.project.directory, '*.iso')
        iso_filepath_list = glob.glob(filepath_pattern)

        is_error_1 = False
        for filepath in iso_checksum_filepath_list:
            # filename = os.path.basename(filepath)
            logger.log_value('Delete the custom ISO checksum file', filepath)
            result, exitstatus, signalstatus = file_utilities.delete_file(filepath)
            if signalstatus:
                is_error_1 = True

        is_error_2 = False
        for filepath in iso_filepath_list:
            # filename = os.path.basename(filepath)
            logger.log_value('Delete the custom ISO file', filepath)
            result, exitstatus, signalstatus = file_utilities.delete_file(filepath)
            if signalstatus:
                is_error_2 = True

        if is_error_1 or is_error_2:
            display.update_status('delete_page__custom_iso_and_checksum', ERROR)
        else:
            display.update_status('delete_page__custom_iso_and_checksum', OK)

    else:

        display.update_status('delete_page__custom_iso_and_checksum', OK)

    # Pause to allow the user to see the result.
    sleep(1.00)

    # Reset the model.
    # TODO: reset these as the files are deleted.

    model.status.is_success_copy = None
    model.status.is_success_extract = None
    model.status.casper_directory = None
    model.status.iso_checksum = None
    model.status.iso_checksum_filename = None

    model.original.iso_filename = None
    model.original.iso_directory = None
    model.original.iso_volume_id = None
    model.original.iso_release_name = None
    model.original.iso_disk_name = None

    model.custom.iso_version_number = None
    model.custom.iso_filename = None
    model.custom.iso_directory = None
    model.custom.iso_volume_id = None
    model.custom.iso_release_name = None
    model.custom.iso_disk_name = None

    model.options.boot_configurations = None

    return is_error
