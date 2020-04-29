#!/usr/bin/python3

########################################################################
#                                                                      #
# finish_page.py                                                       #
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

from utilities import display
from utilities import file_utilities
from utilities import iso_utilities
from utilities import logger
from utilities import model

import os
from time import sleep

########################################################################
# Globals & Constants
########################################################################

name = 'finish_page'

########################################################################
# Navigation Functions
########################################################################


def setup(action, old_page=None):

    if action == 'finish':

        display.reset_buttons(
            back_button_label='❬Back',
            back_action='back',
            back_button_style=None,
            is_back_sensitive=False,
            is_back_visible=False,
            next_button_label='Close',
            next_action='close',
            next_button_style='suggested-action',
            is_next_sensitive=True,
            is_next_visible=True)

        display.update_entry('finish_page__custom_iso_version_number_entry', model.custom.iso_version_number)
        display.update_entry('finish_page__custom_iso_filename_entry', model.custom.iso_filename)
        display.update_entry('finish_page__custom_iso_directory_entry', model.custom.iso_directory)
        display.update_entry('finish_page__custom_iso_volume_id_entry', model.custom.iso_volume_id)
        display.update_entry('finish_page__custom_iso_release_name_entry', model.custom.iso_release_name)
        display.update_entry('finish_page__custom_iso_disk_name_entry', model.custom.iso_disk_name)
        display.update_entry('finish_page__custom_iso_checksum_entry', model.status.iso_checksum)
        display.update_entry('finish_page__custom_iso_checksum_filename_entry', model.status.iso_checksum_filename)

        display.update_status('finish_page__delete_project_files', BLANK)
        display.activate_check_button('finish_page__delete_project_files_check_button', False)

        return

    elif action == 'next':

        # TODO: FOR TESTING ONLY

        display.reset_buttons(
            back_button_label='❬Back',
            back_action='back',
            back_button_style=None,
            is_back_sensitive=False,
            is_back_visible=False,
            next_button_label='Close',
            next_action='close',
            next_button_style='suggested-action',
            is_next_sensitive=True,
            is_next_visible=True)

        display.update_entry('finish_page__custom_iso_version_number_entry', model.custom.iso_version_number)
        display.update_entry('finish_page__custom_iso_filename_entry', model.custom.iso_filename)
        display.update_entry('finish_page__custom_iso_directory_entry', model.custom.iso_directory)
        display.update_entry('finish_page__custom_iso_volume_id_entry', model.custom.iso_volume_id)
        display.update_entry('finish_page__custom_iso_release_name_entry', model.custom.iso_release_name)
        display.update_entry('finish_page__custom_iso_disk_name_entry', model.custom.iso_disk_name)
        display.update_entry('finish_page__custom_iso_checksum_entry', model.status.iso_checksum)
        display.update_entry('finish_page__custom_iso_checksum_filename_entry', model.status.iso_checksum_filename)

        display.update_status('finish_page__delete_project_files', BLANK)
        display.activate_check_button('finish_page__delete_project_files_check_button', False)

        return
    else:

        return 'unknown'


def enter(action, old_page=None):

    if action == 'finish':

        return

    elif action == 'next':

        # TODO: FOR TESTING ONLY

        return

    else:

        return 'unknown'


def leave(action, new_page=None):

    if action == 'close':

        display.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        display.set_sensitive('finish_page__delete_project_files_check_button', False)

        #
        # Unmount and delete the original ISO mount point.
        #
        is_error = unmount_original_iso()

        #
        # Delete project files.
        #
        check_button = model.builder.get_object('finish_page__delete_project_files_check_button')
        is_active = check_button.get_active()
        logger.log_value('Delete the project files?', is_active)
        if is_active:

            display.update_status('finish_page__delete_project_files', PROCESSING)

            # Pause.
            sleep(1.00)

            delete_project_files()

            display.update_status('finish_page__delete_project_files', OK)
            # Pause to allow the user to see the result.
            sleep(1.0)

        # TODO: Is it appropriate to quit here, or must this be done in
        #       navigation as a special case?
        #
        # display.main_quit()

        return

    elif action == 'quit':

        display.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        return

    else:

        return 'unknown'


########################################################################
# Handler Functions
########################################################################


def on_clicked__finish_page__custom_iso_filename_open_button(widget):

    print('on_clicked__finish_page__custom_iso_filename_open_button')

    if os.path.isfile('/bin/nautilus'):
        filepath = os.path.join(model.custom.iso_directory, model.custom.iso_filename)
        if not os.path.isfile(filepath):
            filepath = model.custom.iso_directory
        command = 'nautilus %s &' % filepath
        os.system(command)
    else:
        command = 'xdg-open %s &' % model.custom.iso_directory
        os.system(command)


def on_clicked__finish_page__custom_iso_checksum_filename_open_button(widget):

    print('on_clicked__finish_page__custom_iso_checksum_filename_open_button')

    if os.path.isfile('/bin/nautilus'):
        filepath = os.path.join(model.custom.iso_directory, model.status.iso_checksum_filename)
        if not os.path.isfile(filepath):
            filepath = model.custom.iso_directory
        command = 'nautilus %s &' % filepath
        os.system(command)
    else:
        command = 'xdg-open %s &' % model.custom.iso_directory
        os.system(command)


########################################################################
# Support Functions
########################################################################


def unmount_original_iso():

    is_error = False

    #
    # Unmount and delete the original ISO mount point.
    #
    logger.log_value('Unmount the original ISO and delete the mount point', model.project.iso_mount_point)
    if os.path.exists(model.project.iso_mount_point):
        # Unmount the original ISO disk image.
        result, exitstatus, signalstatus = iso_utilities.unmount(model.project.iso_mount_point)
        if not signalstatus:
            # Delete the mount point.
            logger.log_value('Delete the original ISO mount point', model.project.iso_mount_point)
            result, exitstatus, signalstatus = file_utilities.delete_directory(model.project.iso_mount_point)
            if not signalstatus:
                logger.log_value('Successfully deleted the original ISO mount point', model.project.iso_mount_point)
                pass
            else:
                logger.log_value('Unable to delete the original ISO mount point', model.project.iso_mount_point)
                is_error = True
        else:
            logger.log_value('Unable to unmount the original ISO and delete the mount point', model.project.iso_mount_point)
            is_error = True
    else:
        logger.log_value('Skipping. The original ISO mount point does not exist', model.project.iso_mount_point)

    return is_error


def delete_project_files():

    is_error = False

    #
    # Delete the configuration file
    #
    logger.log_value('Delete the configuration file', model.project.configuration_filepath)
    sleep(1.00)
    if os.path.exists(model.project.configuration_filepath):
        result, exitstatus, signalstatus = file_utilities.delete_file(model.project.configuration_filepath)
        if not signalstatus:
            # OK
            pass
        else:
            is_error = True
    else:
        # Skip
        pass

    #
    # Delete the custom root directory.
    #
    logger.log_value('Delete the custom root directory', model.project.custom_root_directory)
    sleep(1.00)
    if os.path.exists(model.project.custom_root_directory):
        result, exitstatus, signalstatus = file_utilities.delete_path_as_root(model.project.custom_root_directory)
        if not signalstatus:
            # OK
            pass
        else:
            is_error = True
    else:
        # Skip
        pass

    #
    # Delete the custom disk directory.
    #
    logger.log_value('Delete the custom ISO directory', model.project.custom_disk_directory)
    sleep(1.00)
    if os.path.exists(model.project.custom_disk_directory):
        result, exitstatus, signalstatus = file_utilities.delete_directory(model.project.custom_disk_directory)
        if not signalstatus:
            # OK
            pass
        else:
            is_error = True
    else:
        # Skip
        pass

    # Reset the model.
    # TODO: Reset these as the files are deleted.

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


########################################################################
# Validation Functions
########################################################################


def validate_page():

    return True
