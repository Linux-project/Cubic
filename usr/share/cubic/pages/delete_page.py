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

from glob import glob
from os import system
from os.path import exists, isfile, join
from time import sleep

from constants import OK, ERROR, OPTIONAL, BULLET, PROCESSING, BLANK
from utilities import constructor
from utilities import displayer
from utilities import file_utilities
from utilities import iso_utilities
from utilities import logger
from utilities import model

########################################################################
# References
########################################################################

# N/A

########################################################################
# Globals & Constants
########################################################################

name = 'delete_page'
custom = None

########################################################################
# Navigation Functions
########################################################################


def setup(action, old_page=None):

    if action == 'delete':

        displayer.reset_buttons(
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

        displayer.update_entry('delete_page__project_directory_entry', model.project.directory)

        # TODO: If custom.iso_filename does not exist, then display a message below the entry.
        filepath = join(model.custom.iso_directory, model.custom.iso_filename)
        if isfile(filepath):
            displayer.update_entry('delete_page__custom_iso_filename_entry', model.custom.iso_filename)
        else:
            displayer.update_entry('delete_page__custom_iso_filename_entry', '(not available)')

        displayer.update_entry('delete_page__custom_iso_version_number_entry', model.custom.iso_version_number)
        # displayer.update_entry('delete_page__custom_iso_directory_entry', model.custom.iso_directory)
        displayer.update_entry('delete_page__custom_iso_volume_id_entry', model.custom.iso_volume_id)
        displayer.update_entry('delete_page__custom_iso_release_name_entry', model.custom.iso_release_name)
        displayer.update_entry('delete_page__custom_iso_disk_name_entry', model.custom.iso_disk_name)

        displayer.update_status('delete_page__project_configuration_file', BULLET)
        displayer.update_label('delete_page__project_configuration_file_message', '')

        displayer.update_status('delete_page__project_iso_mount_point', BULLET)
        displayer.update_label('delete_page__project_iso_mount_point_message', '')

        displayer.update_status('delete_page__custom_root_directory', BULLET)
        displayer.update_label('delete_page__custom_root_directory_message', '')

        displayer.update_status('delete_page__custom_disk_directory', BULLET)
        displayer.update_label('delete_page__custom_disk_directory_message', '')

        displayer.update_status('delete_page__custom_iso_and_checksum', BULLET)

        filepath_pattern = join(model.project.directory, '*.iso')
        iso_filepath_list = glob(filepath_pattern)

        filepath_pattern = join(model.project.directory, '*.md5')
        iso_checksum_filepath_list = glob(filepath_pattern)

        # TOOD: Use constructor.get_plural and format on prepare_page.

        # This must be consistent with on_toggled__delete_page__custom_iso_and_checksum_check_button()
        if iso_checksum_filepath_list and iso_filepath_list:
            iso_count_text = constructor.number_as_text(len(iso_filepath_list))
            iso_files_text = 'file' if len(iso_filepath_list) == 1 else 'files'
            md5_count_text = constructor.number_as_text(len(iso_checksum_filepath_list))
            md5_files_text = 'file' if len(iso_checksum_filepath_list) == 1 else 'files'
            label = 'Delete %s ISO disk image %s and %s MD5 checksum %s.' % (iso_count_text, iso_files_text, md5_count_text, md5_files_text)
            enable = True
        elif iso_filepath_list:
            iso_count_text = constructor.number_as_text(len(iso_filepath_list))
            iso_files_text = 'file' if len(iso_filepath_list) == 1 else 'files'
            label = 'Delete %s ISO disk image %s.' % (iso_count_text, iso_files_text)
            enable = True
        elif iso_checksum_filepath_list:
            md5_count_text = constructor.number_as_text(len(iso_checksum_filepath_list))
            md5_files_text = 'file' if len(iso_checksum_filepath_list) == 1 else 'files'
            label = 'Delete %s MD5 checksum %s.' % (md5_count_text, md5_files_text)
            enable = True
        else:
            label = 'There are no ISO files or MD5 files in this project directory.'
            enable = False

        displayer.update_check_button_label('delete_page__custom_iso_and_checksum_check_button', label)
        displayer.activate_check_button('delete_page__custom_iso_and_checksum_check_button', enable)
        displayer.set_sensitive('delete_page__custom_iso_and_checksum_check_button', enable)

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

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        return

    elif action == 'delete':

        # The following fields must be set before leaving this page:
        #
        # 1. model.project.cubic_version
        # 2. model.project.create_date
        # 3. model.project.modify_date
        # 4. model.project.directory
        # 5. model.project.configuration_filepath
        # 6. model.project.iso_mount_point
        # 7. model.project.custom_root_directory
        # 8. model.project.custom_disk_directory

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        is_error = delete_project_files()

        if is_error:
            # Stay on the page.
            return 'error'
        else:
            # Reset the model.
            reset_model()
            # This is a new project, so set the create and modify dates.
            current_date_time = constructor.get_current_date_time()
            model.project.create_date = current_date_time
            model.project.modify_date = current_date_time
            # Pause to allow the user to see the results.
            sleep(1.000)
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


def on_clicked__delete_page__project_directory_open_button(widget):

    command = 'xdg-open %s &' % model.project.directory
    system(command)


def on_clicked__delete_page__custom_iso_filename_open_button(widget):

    if isfile('/bin/nautilus'):
        filepath = join(model.custom.iso_directory, model.custom.iso_filename)
        if not isfile(filepath):
            filepath = model.custom.iso_directory
        command = 'nautilus %s &' % filepath
        system(command)
    else:
        command = 'xdg-open %s &' % model.custom.iso_directory
        system(command)


########################################################################
# Support Functions
########################################################################


def delete_project_files_TEST():

    is_error = False

    #
    # Unmount and delete the original ISO mount point.
    #
    logger.log_value('Unmount the original ISO and delete the mount point', model.project.iso_mount_point)
    displayer.update_status('delete_page__project_iso_mount_point', PROCESSING)
    sleep(1.000)
    displayer.update_status('delete_page__project_iso_mount_point', OK)
    displayer.update_label('delete_page__project_iso_mount_point_message', 'Testing testing testing.')
    # Pause to allow the user to see the result.
    sleep(1.000)

    #
    # Delete the configuration file
    #
    logger.log_value('Delete the configuration file', model.project.configuration_filepath)
    displayer.update_status('delete_page__project_configuration_file', PROCESSING)
    sleep(1.000)
    displayer.update_status('delete_page__project_configuration_file', OK)
    displayer.update_label('delete_page__project_configuration_file_message', 'Testing testing testing.')
    sleep(1.000)

    #
    # Delete the custom root directory.
    #
    logger.log_value('Delete the custom root directory', model.project.custom_root_directory)
    displayer.update_status('delete_page__custom_root_directory', PROCESSING)
    sleep(1.000)
    displayer.update_status('delete_page__custom_root_directory', OK)
    displayer.update_label('delete_page__custom_root_directory_message', 'Testing testing testing.')
    # Pause to allow the user to see the result.
    sleep(1.000)

    #
    # Delete the custom ISO directory.
    #
    logger.log_value('Delete the custom ISO directory', model.project.custom_disk_directory)
    displayer.update_status('delete_page__custom_disk_directory', PROCESSING)
    sleep(1.000)
    displayer.update_status('delete_page__custom_disk_directory', OK)
    displayer.update_label('delete_page__custom_disk_directory_message', 'Testing testing testing.')
    # Pause to allow the user to see the result.
    sleep(1.000)

    #
    # Delete the custom ISO checksum files and the custom ISO files.
    #
    displayer.update_status('delete_page__custom_iso_and_checksum', PROCESSING)
    sleep(1.000)
    displayer.update_status('delete_page__custom_iso_and_checksum', OK)
    displayer.update_label('delete_page__custom_iso_and_checksum_message', 'Testing testing testing.')
    # Pause to allow the user to see the result.
    sleep(1.000)

    return is_error


def delete_project_files():

    displayer.set_sensitive('delete_page__custom_iso_and_checksum_check_button', False)

    is_error = False

    #
    # Unmount and delete the original ISO mount point.
    #
    logger.log_value('Unmount the original ISO and delete the mount point', model.project.iso_mount_point)
    displayer.update_status('delete_page__project_iso_mount_point', PROCESSING)
    sleep(1.000)
    if exists(model.project.iso_mount_point):
        # Unmount the original ISO disk image.
        result, exitstatus, signalstatus = iso_utilities.unmount(model.project.iso_mount_point)
        if not signalstatus:
            displayer.update_status('delete_page__project_iso_mount_point', OK)
            displayer.update_label('delete_page__project_iso_mount_point_message', '')
            sleep(0.500)
            # Delete the mount point.
            logger.log_value('Delete the original ISO mount point', model.project.iso_mount_point)
            result, exitstatus, signalstatus = file_utilities.delete_directory(model.project.iso_mount_point)
            if not signalstatus:
                displayer.update_status('delete_page__project_iso_mount_point', OK)
                displayer.update_label('delete_page__project_iso_mount_point_message', '')
            else:
                displayer.update_status('delete_page__project_iso_mount_point', ERROR)
                displayer.update_label('delete_page__project_iso_mount_point_message', 'Unable to delete the mount point.')
                is_error = True
        else:
            displayer.update_status('delete_page__project_iso_mount_point', ERROR)
            displayer.update_label('delete_page__project_iso_mount_point_message', 'Unable to unmount the iso.')
            is_error = True
    else:
        displayer.update_status('delete_page__project_iso_mount_point', OK)
        displayer.update_label('delete_page__project_iso_mount_point_message', 'Nothing to unmount.')
    # Pause to allow the user to see the result.
    sleep(1.000)

    #
    # Delete the configuration file
    #
    logger.log_value('Delete the configuration file', model.project.configuration_filepath)
    displayer.update_status('delete_page__project_configuration_file', PROCESSING)
    sleep(1.000)
    if exists(model.project.configuration_filepath):
        result, exitstatus, signalstatus = file_utilities.delete_file(model.project.configuration_filepath)
        if not signalstatus:
            displayer.update_status('delete_page__project_configuration_file', OK)
            displayer.update_label('delete_page__project_configuration_file_message', '')
        else:
            displayer.update_status('delete_page__project_configuration_file', ERROR)
            displayer.update_label('delete_page__project_configuration_file_message', 'Unable to delete this file.')
            is_error = True
    else:
        displayer.update_status('delete_page__project_configuration_file', OK)
        displayer.update_label('delete_page__project_configuration_file_message', 'Nothing to delete. This file does not exist.')
    # Pause to allow the user to see the result.
    sleep(1.000)

    #
    # Delete the custom root directory.
    #
    logger.log_value('Delete the custom root directory', model.project.custom_root_directory)
    displayer.update_status('delete_page__custom_root_directory', PROCESSING)
    sleep(1.000)
    if exists(model.project.custom_root_directory):
        result, exitstatus, signalstatus = file_utilities.delete_path_as_root(model.project.custom_root_directory)
        if not signalstatus:
            displayer.update_status('delete_page__custom_root_directory', OK)
            displayer.update_label('delete_page__custom_root_directory_message', '')
        else:
            displayer.update_status('delete_page__custom_root_directory', ERROR)
            displayer.update_label('delete_page__custom_root_directory_message', 'Unable to delete the customized Linux files.')
            is_error = True
    else:
        displayer.update_status('delete_page__custom_root_directory', OK)
        displayer.update_label('delete_page__custom_root_directory_message', 'Nothing to delete. These files not exist.')
    # Pause to allow the user to see the result.
    sleep(1.000)

    #
    # Delete the custom disk directory.
    #
    logger.log_value('Delete the custom ISO directory', model.project.custom_disk_directory)
    # displayer.update_label('delete_page__custom_disk_directory_message', model.project.custom_disk_directory)
    displayer.update_status('delete_page__custom_disk_directory', PROCESSING)
    sleep(1.000)
    if exists(model.project.custom_disk_directory):
        result, exitstatus, signalstatus = file_utilities.delete_directory(model.project.custom_disk_directory)
        if not signalstatus:
            displayer.update_status('delete_page__custom_disk_directory', OK)
            displayer.update_label('delete_page__custom_disk_directory_message', '')
        else:
            displayer.update_status('delete_page__custom_disk_directory', ERROR)
            displayer.update_label('delete_page__custom_disk_directory_message', 'Unable to delete the customized disk image files.')
            is_error = True
    else:
        displayer.update_status('delete_page__custom_disk_directory', OK)
        displayer.update_label('delete_page__custom_disk_directory_message', 'Nothing to delete. These files do not exist.')
    # Pause to allow the user to see the result.
    sleep(1.000)

    #
    # Delete the custom ISO checksum files and the custom ISO files.
    #
    check_button = model.builder.get_object('delete_page__custom_iso_and_checksum_check_button')
    is_active = check_button.get_active()

    logger.log_value('Delete the custom ISO checksum files and the custom ISO files?', is_active)
    if is_active:

        displayer.update_status('delete_page__custom_iso_and_checksum', PROCESSING)
        sleep(1.000)

        filepath_pattern = join(model.project.directory, '*.md5')
        iso_checksum_filepath_list = glob(filepath_pattern)

        filepath_pattern = join(model.project.directory, '*.iso')
        iso_filepath_list = glob(filepath_pattern)

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
            displayer.update_status('delete_page__custom_iso_and_checksum', ERROR)
        else:
            displayer.update_status('delete_page__custom_iso_and_checksum', OK)

    else:

        displayer.update_status('delete_page__custom_iso_and_checksum', OK)

    # Pause to allow the user to see the result.
    sleep(1.000)

    return is_error


def reset_model():

    # model.project.cubic_version = None
    # model.project.create_date = None
    # model.project.modify_date = None
    # model.project.directory = None
    # model.project.configuration_filepath = None
    # model.project.iso_mount_point = None
    # model.project.custom_root_directory = None
    # model.project.custom_disk_directory = None

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

    model.status.is_success_copy = False
    model.status.is_success_extract = False
    model.status.casper_directory = None
    model.status.iso_checksum = None
    model.status.iso_checksum_filename = None

    model.options.boot_configurations = None
