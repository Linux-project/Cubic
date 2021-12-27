#!/usr/bin/python3

########################################################################
#                                                                      #
# migrate_page.py                                                      #
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

import getpass
import os
import time

from cubic.constants import BOLD_RED, NORMAL
from cubic.constants import OK, ERROR, OPTIONAL, BULLET, PROCESSING, BLANK
from cubic.constants import SLEEP_1000_MS
from cubic.utilities import configuration
from cubic.utilities import constructor
from cubic.utilities import displayer
from cubic.utilities import file_utilities
from cubic.utilities import logger
from cubic.utilities import model
from cubic.utilities.processor import execute_synchronous

########################################################################
# Global Variables & Constants
########################################################################

name = 'migrate_page'
custom = None

OLD_CUSTOM_DISK_DIRECTORY = 'custom-live-iso'
OLD_CUSTOM_ROOT_DIRECTORY = 'squashfs-root'

########################################################################
# Navigation Functions
########################################################################


def setup(action, old_page=None):

    if action == 'migrate':

        display_version = constructor.get_major_minor_version(model.project.cubic_version)
        displayer.update_entry('migrate_page__project_cubic_version_entry', display_version)
        displayer.update_entry('migrate_page__project_directory_entry', model.project.directory)
        displayer.update_entry('migrate_page__custom_iso_version_number_entry', model.custom.iso_version_number)
        displayer.update_entry('migrate_page__custom_iso_volume_id_entry', model.custom.iso_volume_id)
        displayer.update_entry('migrate_page__custom_iso_release_name_entry', model.custom.iso_release_name)
        displayer.update_entry('migrate_page__custom_iso_disk_name_entry', model.custom.iso_disk_name)

        displayer.update_status('migrate_page__configuration', BULLET)
        displayer.update_label('migrate_page__configuration_message', '')

        displayer.update_status('migrate_page__custom_root', BULLET)
        displayer.update_label('migrate_page__custom_root_message', '')

        displayer.update_status('migrate_page__custom_disk', BULLET)
        displayer.update_label('migrate_page__custom_disk_message', '')

        displayer.reset_buttons(
            back_button_label='❬Cancel',
            back_action='back',
            back_button_style=None,
            is_back_sensitive=True,
            is_back_visible=True,
            next_button_label='Migrate❭',
            next_action='next',
            next_button_style='suggested-action',
            is_next_sensitive=True,
            is_next_visible=True)

        return

    elif action == 'error':

        # Handle the error from the leave() function.

        return

    else:

        logger.log_value('Error', f'{BOLD_RED}Unknown action for setup{NORMAL}')

        return 'unknown'


def enter(action, old_page=None):

    if action == 'migrate':

        return

    elif action == 'error':

        # Handle the error from the leave() function.

        return

    else:

        logger.log_value('Error', f'{BOLD_RED}Unknown action for enter{NORMAL}')

        return 'unknown'


def leave(action, new_page=None):

    if action == 'back':

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        return

    elif action == 'next':

        # The following fields must be set before leaving this page:
        #
        # 1. model.project.cubic_version
        #    - Set to model.application.cubic_version when the
        #      configuration is saved.
        # 2. model.project.create_date
        # 3. model.project.directory
        # 4. model.project.configuration_file_path
        # 5. model.project.iso_mount_point
        # 6. model.project.custom_root_directory
        # 7. model.project.custom_disk_directory

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        is_error = migrate_configuration()
        if is_error: return 'error'  # Stay on this page.

        is_error = migrate_custom_root()
        if is_error: return 'error'  # Stay on this page.

        is_error = migrate_custom_disk()
        if is_error: return 'error'  # Stay on this page.

        return

    elif action == 'quit':

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        return

    else:

        logger.log_value('Error', f'{BOLD_RED}Unknown action for leave{NORMAL}')

        return 'unknown'


########################################################################
# Handler Functions
########################################################################


def on_clicked__migrate_page__project_directory_open_button(widget):

    file_utilities.open_directory_in_browser(model.project.directory)


########################################################################
# Support Functions
########################################################################


def migrate_configuration():
    """
    Migrate the configuration.
    """

    is_error = False

    logger.log_label('Migrate the configuration')
    logger.log_value('Update the configuration file to the current format', model.project.configuration_file_path)

    displayer.update_status('migrate_page__configuration', PROCESSING)
    time.sleep(SLEEP_1000_MS)

    try:
        configuration.save()
        logger.log_value('Migrated', model.project.configuration_file_path)
        displayer.update_status('migrate_page__configuration', OK)
        displayer.update_label('migrate_page__configuration_message', '')
    except Exception as exception:
        logger.log_value('Error. Unable to migrate', model.project.configuration_file_path)
        logger.log_value('The exception is', exception)
        displayer.update_status('migrate_page__configuration', ERROR)
        displayer.update_label('migrate_page__configuration_message', f'Error. Unable to migrate {model.project.configuration_file_path}.')
        is_error = True

    # Pause to allow the user to see the result.
    time.sleep(SLEEP_1000_MS)

    return is_error


def migrate_custom_root():
    """
    Migrate the customized Linux file system.
    """

    is_error = False

    # Create the custom root directory used by the old project structure.
    source_file_path = os.path.join(model.project.directory, OLD_CUSTOM_ROOT_DIRECTORY)

    # The custom root directory for the new project structure was set on
    # the start page.
    target_file_path = model.project.custom_root_directory

    logger.log_label('Migrate the customized Linux file system')
    logger.log_value('From', source_file_path)
    logger.log_value('To', target_file_path)

    displayer.update_status('migrate_page__custom_root', PROCESSING)
    time.sleep(SLEEP_1000_MS)

    if os.path.exists(source_file_path):

        program = os.path.join(model.application.directory, 'commands', 'move-path')
        command = ['pkexec', program, source_file_path, target_file_path]
        result, exit_status, signal_status = execute_synchronous(command)

        if not exit_status:
            logger.log_value('Migrated', source_file_path)
            displayer.update_status('migrate_page__custom_root', OK)
            displayer.update_label('migrate_page__custom_root_message', '')
        else:
            logger.log_value('Error. Unable to migrate', source_file_path)
            logger.log_value('The result is', result)
            displayer.update_status('migrate_page__custom_root', ERROR)
            displayer.update_label('migrate_page__custom_root_message', f'Error. Unable to migrate {source_file_path}.')
            is_error = True

    else:

        logger.log_value('Error. Unable to migrate because the source directory does not exist', source_file_path)
        displayer.update_status('migrate_page__custom_root', ERROR)
        displayer.update_label('migrate_page__custom_root_message', f'Error. Unable to migrate {source_file_path}.')
        is_error = True

    # Pause to allow the user to see the result.
    time.sleep(SLEEP_1000_MS)

    return is_error


def migrate_custom_disk():
    """
    Migrate the customized disk.
    """

    is_error = False

    # Create the custom disk directory used by the old project structure.
    source_file_path = os.path.join(model.project.directory, OLD_CUSTOM_DISK_DIRECTORY)

    # The custom disk directory for the new project structure was set on
    # the start page.
    target_file_path = model.project.custom_disk_directory

    # Get the current user to whom the ownership of the custom disk
    # directory will be recursively changed.
    user = getpass.getuser()

    logger.log_label('Migrate the customized disk')
    logger.log_value('From', source_file_path)
    logger.log_value('To', target_file_path)
    logger.log_value('User', user)

    displayer.update_status('migrate_page__custom_disk', PROCESSING)
    time.sleep(SLEEP_1000_MS)

    if os.path.exists(source_file_path):

        program = os.path.join(model.application.directory, 'commands', 'move-path')
        command = ['pkexec', program, source_file_path, target_file_path, user]
        result, exit_status, signal_status = execute_synchronous(command)

        if not exit_status:
            logger.log_value('Migrated', source_file_path)
            displayer.update_status('migrate_page__custom_disk', OK)
            displayer.update_label('migrate_page__custom_disk_message', '')
        else:
            logger.log_value('Error. Unable to migrate', source_file_path)
            logger.log_value('The result is', result)
            displayer.update_status('migrate_page__custom_disk', ERROR)
            displayer.update_label('migrate_page__custom_disk_message', f'Error. Unable to migrate {source_file_path}.')
            is_error = True

    else:

        logger.log_value('Error. Unable to migrate because the source directory does not exist', source_file_path)
        displayer.update_status('migrate_page__custom_disk', ERROR)
        displayer.update_label('migrate_page__custom_disk_message', f'Error. Unable to migrate {source_file_path}.')
        is_error = True

    # Pause to allow the user to see the result.
    time.sleep(SLEEP_1000_MS)

    return is_error
