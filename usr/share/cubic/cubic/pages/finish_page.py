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

########################################################################
# References
########################################################################

# N/A

########################################################################
# Imports
########################################################################

import os
import time

from cubic.constants import IMAGE_FILE_NAME, LOCK_FILE_NAME
from cubic.constants import OK, ERROR, OPTIONAL, BULLET, PROCESSING, BLANK
from cubic.constants import SLEEP_0500_MS, SLEEP_1500_MS
from cubic.utilities import displayer
from cubic.utilities import file_utilities
from cubic.utilities import iso_utilities
from cubic.utilities import logger
from cubic.utilities import model

########################################################################
# Global Variables & Constants
########################################################################

name = 'finish_page'

########################################################################
# Navigation Functions
########################################################################


def setup(action, old_page=None):

    if action == 'finish':

        displayer.reset_buttons(
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

        displayer.update_entry('finish_page__custom_iso_version_number_entry', model.custom.iso_version_number)
        displayer.update_entry('finish_page__custom_iso_file_name_entry', model.custom.iso_file_name)
        displayer.update_entry('finish_page__custom_iso_directory_entry', model.custom.iso_directory)
        displayer.update_entry('finish_page__custom_iso_volume_id_entry', model.custom.iso_volume_id)
        displayer.update_entry('finish_page__custom_iso_release_name_entry', model.custom.iso_release_name)
        displayer.update_entry('finish_page__custom_iso_disk_name_entry', model.custom.iso_disk_name)
        displayer.update_entry('finish_page__custom_iso_checksum_entry', model.status.iso_checksum)
        displayer.update_entry('finish_page__custom_iso_checksum_file_name_entry', model.status.iso_checksum_file_name)

        displayer.update_status('finish_page__delete_project_files', BLANK)
        displayer.activate_check_button('finish_page__delete_project_files_check_button', False)

        return

    elif action == 'next':

        # TODO: FOR TESTING ONLY

        displayer.reset_buttons(
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

        displayer.update_entry('finish_page__custom_iso_version_number_entry', model.custom.iso_version_number)
        displayer.update_entry('finish_page__custom_iso_file_name_entry', model.custom.iso_file_name)
        displayer.update_entry('finish_page__custom_iso_directory_entry', model.custom.iso_directory)
        displayer.update_entry('finish_page__custom_iso_volume_id_entry', model.custom.iso_volume_id)
        displayer.update_entry('finish_page__custom_iso_release_name_entry', model.custom.iso_release_name)
        displayer.update_entry('finish_page__custom_iso_disk_name_entry', model.custom.iso_disk_name)
        displayer.update_entry('finish_page__custom_iso_checksum_entry', model.status.iso_checksum)
        displayer.update_entry('finish_page__custom_iso_checksum_file_name_entry', model.status.iso_checksum_file_name)

        displayer.update_status('finish_page__delete_project_files', BLANK)
        displayer.activate_check_button('finish_page__delete_project_files_check_button', False)

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

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        displayer.set_sensitive('finish_page__delete_project_files_check_button', False)

        # The original disk is unmounted when leaving the Generate page,
        # so there is no need to unmount it here.
        # iso_utilities.unmount_iso_and_delete_mount_point(model.project.iso_mount_point)

        # Delete project files.

        check_button = model.builder.get_object('finish_page__delete_project_files_check_button')
        is_active = check_button.get_active()
        logger.log_value('Delete the project files?', is_active)
        if is_active:
            displayer.update_status('finish_page__delete_project_files', PROCESSING)
            time.sleep(SLEEP_0500_MS)
            delete_project_files()
            displayer.update_status('finish_page__delete_project_files', OK)
            # Pause to allow the user to see the result.
            time.sleep(SLEEP_1500_MS)

        return

    elif action == 'quit':

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        return

    else:

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        return 'unknown'


########################################################################
# Handler Functions
########################################################################


def on_clicked__finish_page__custom_iso_file_name_open_button(widget):

    file_path = os.path.join(model.custom.iso_directory, model.custom.iso_file_name)
    if os.path.isfile(file_path):
        file_utilities.select_file_in_browser(file_path)
    else:
        file_utilities.open_directory_in_browser(model.custom.iso_directory)


def on_clicked__finish_page__custom_iso_checksum_file_name_open_button(widget):

    file_path = os.path.join(model.custom.iso_directory, model.status.iso_checksum_file_name)
    if os.path.isfile(file_path):
        file_utilities.select_file_in_browser(file_path)
    else:
        file_utilities.open_directory_in_browser(model.custom.iso_directory)


########################################################################
# Support Functions
########################################################################


def unmount_original_iso():

    is_error = False

    #
    # Unmount and delete the original disk mount point.
    #
    logger.log_value('Unmount the original disk and delete the mount point', model.project.iso_mount_point)
    if os.path.exists(model.project.iso_mount_point):
        # Unmount the original disk image.
        result, exit_status, signal_status = iso_utilities.unmount(model.project.iso_mount_point)
        if not signal_status:
            # Delete the mount point.
            logger.log_value('Delete the original disk mount point', model.project.iso_mount_point)
            result, exit_status, signal_status = file_utilities.delete_directory(model.project.iso_mount_point)
            if not signal_status:
                logger.log_value('Deleted the original disk mount point', model.project.iso_mount_point)
                pass
            else:
                logger.log_value('Unable to delete the original disk mount point', model.project.iso_mount_point)
                is_error = True
        else:
            logger.log_value('Unable to unmount the original disk and delete the mount point', model.project.iso_mount_point)
            is_error = True
    else:
        logger.log_value('Skipping. The original disk mount point does not exist', model.project.iso_mount_point)

    return is_error


def delete_project_files():

    is_error = False

    #
    # Delete the configuration file
    #
    logger.log_value('Delete the configuration file', model.project.configuration_file_path)
    # time.sleep(SLEEP_1000_MS)
    if os.path.exists(model.project.configuration_file_path):
        result, exit_status, signal_status = file_utilities.delete_file(model.project.configuration_file_path)
        if not signal_status:
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
    # time.sleep(SLEEP_1000_MS)
    if os.path.exists(model.project.custom_root_directory):
        result, exit_status, signal_status = file_utilities.delete_path_as_root(model.project.custom_root_directory)
        if not signal_status:
            # OK
            pass
        else:
            is_error = True
    else:
        # Skip
        pass

    #
    # Delete the virtual environment lock file.
    #
    lock_file_path = os.path.join(model.project.directory, LOCK_FILE_NAME)
    logger.log_value('Delete the virtual environment lock file', lock_file_path)
    # time.sleep(SLEEP_1000_MS)
    if os.path.exists(lock_file_path):
        result, exit_status, signal_status = file_utilities.delete_path_as_root(lock_file_path)
        if not signal_status:
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
    logger.log_value('Delete the custom disk directory', model.project.custom_disk_directory)
    # time.sleep(SLEEP_1000_MS)
    if os.path.exists(model.project.custom_disk_directory):
        result, exit_status, signal_status = file_utilities.delete_directory(model.project.custom_disk_directory)
        if not signal_status:
            # OK
            pass
        else:
            is_error = True
    else:
        # Skip
        pass

    #
    # Delete the iso partition image files.
    #
    image_file_pattern = os.path.join(model.project.directory, IMAGE_FILE_NAME % '[1-9]')
    image_file_files = file_utilities.get_files_with_pattern(image_file_pattern)
    logger.log_value('Delete the iso partition image files', image_file_files)
    # time.sleep(SLEEP_1000_MS)

    if image_file_files:
        file_utilities.delete_files_with_pattern(image_file_pattern)
        # Check if all image files were deleted.
        image_file_files = file_utilities.get_files_with_pattern(image_file_pattern)
        if image_file_files:
            is_error = True
    else:
        # Skip
        pass

    return is_error


########################################################################
# Validation Functions
########################################################################


def validate_page():

    return True
