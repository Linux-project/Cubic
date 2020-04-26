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

from constants import OK, ERROR, OPTIONAL, BULLET, PROCESSING, BLANK

from utilities import configuration
from utilities import constructors
from utilities import display
from utilities import logger
from utilities import model
from utilities.process_utilities import execute_synchronous

import getpass
import os
from time import sleep

########################################################################
# Globals & Constants
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

        display.reset_buttons(
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

        display_version = constructors.get_major_minor_version(model.project.cubic_version)
        display.update_entry('migrate_page__project_cubic_version_entry', display_version)
        display.update_entry('migrate_page__project_directory_entry', model.project.directory)
        # display.update_entry('migrate_page__original_iso_filename_entry', model.original.iso_filename)
        display.update_entry('migrate_page__custom_iso_version_number_entry', model.custom.iso_version_number)
        display.update_entry('migrate_page__custom_iso_volume_id_entry', model.custom.iso_volume_id)
        display.update_entry('migrate_page__custom_iso_release_name_entry', model.custom.iso_release_name)
        display.update_entry('migrate_page__custom_iso_disk_name_entry', model.custom.iso_disk_name)

        display.update_status('migrate_page__configuration', BULLET)
        display.update_label('migrate_page__configuration_message', '')

        display.update_status('migrate_page__custom_root', BULLET)
        display.update_label('migrate_page__custom_root_message', '')

        display.update_status('migrate_page__custom_disk', BULLET)
        display.update_label('migrate_page__custom_disk_message', '')

        return

    else:

        return 'unknown'


def enter(action, old_page=None):

    if action == 'migrate':

        return

    else:

        return 'unknown'


def leave(action, new_page=None):

    if action == 'back':

        display.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        return

    elif action == 'next':

        display.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        is_error = migrate_configuration()
        if is_error: return 'error'

        is_error = migrate_custom_root()
        if is_error: return 'error'

        is_error = migrate_custom_disk()
        if is_error: return 'error'

        return

    elif action == 'quit':

        display.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        return

    else:

        return 'unknown'


########################################################################
# Handler Functions
########################################################################


def on_clicked__migrate_page__project_directory_open_button(widget):

    print('on_clicked__migrate_page__project_directory_open_button')

    command = 'xdg-open %s &' % model.project.directory
    os.system(command)


########################################################################
# Support Functions
########################################################################


def migrate_configuration():
    """
    Migrate the configuration.
    """

    is_error = False

    logger.log_label('Migrate the configuration')
    logger.log_value('Update the configuration file to the current format', model.project.configuration_filepath)

    display.update_status('migrate_page__configuration', PROCESSING)
    sleep(1.00)

    try:
        configuration.save()
        logger.log_value('Migrated', model.project.configuration_filepath)
        display.update_status('migrate_page__configuration', OK)
        display.update_label('migrate_page__configuration_message', '')
    except Exception as exception:
        logger.log_value('Error. Unable to migrate', model.project.configuration_filepath)
        logger.log_value('The exception is', exception)
        display.update_status('migrate_page__configuration', ERROR)
        display.update_label('migrate_page__configuration_message', 'Error. Unable to migrate %s.' % model.project.configuration_filepath)
        is_error = True

    # Pause to allow the user to see the result.
    sleep(1.00)

    return is_error


def migrate_custom_root():
    """
    Migrate the customized Linux file system.
    """

    is_error = False

    # Create the custom root directory used by the old project structure.
    source_path = os.path.join(model.project.directory, OLD_CUSTOM_ROOT_DIRECTORY)

    # The custom root directory for the new project structure was set on
    # the start page.
    target_path = model.project.custom_root_directory

    logger.log_label('Migrate the customized Linux file system')
    logger.log_value('From', source_path)
    logger.log_value('To', target_path)

    display.update_status('migrate_page__custom_root', PROCESSING)
    sleep(1.00)

    if os.path.exists(source_path):

        program = os.path.join(model.application.directory, 'commands', 'migrate-directory')
        command = 'pkexec "%s" "%s" "%s"' % (program, source_path, target_path)
        result, exitstatus, signalstatus = execute_synchronous(command)

        if not exitstatus:
            logger.log_value('Migrated', source_path)
            display.update_status('migrate_page__custom_root', OK)
            display.update_label('migrate_page__custom_root_message', '')
        else:
            logger.log_value('Error. Unable to migrate', source_path)
            logger.log_value('The result is', result)
            display.update_status('migrate_page__custom_root', ERROR)
            display.update_label('migrate_page__custom_root_message', 'Error. Unable to migrate %s.' % source_path)
            is_error = True

    else:

        logger.log_value('Error. Unable to migrate because the source directory does not exist', source_path)
        display.update_status('migrate_page__custom_root', ERROR)
        display.update_label('migrate_page__custom_root_message', 'Error. Unable to migrate %s.' % source_path)
        is_error = True

    # Pause to allow the user to see the result.
    sleep(1.00)

    return is_error


def migrate_custom_disk():
    """
    Migrate the customized disk.
    """

    is_error = False

    # Create the custom disk directory used by the old project structure.
    source_path = os.path.join(model.project.directory, OLD_CUSTOM_DISK_DIRECTORY)

    # The custom disk directory for the new project structure was set on
    # the start page.
    target_path = model.project.custom_disk_directory

    # Get the current user to whom the ownership of the custom disk
    # directory will be recursively changed.
    user = getpass.getuser()

    logger.log_label('Migrate the customized disk')
    logger.log_value('From', source_path)
    logger.log_value('To', target_path)
    logger.log_value('User', user)

    display.update_status('migrate_page__custom_disk', PROCESSING)
    sleep(1.00)

    if os.path.exists(source_path):

        program = os.path.join(model.application.directory, 'commands', 'migrate-directory')
        command = 'pkexec "%s" "%s" "%s" "%s"' % (program, source_path, target_path, user)
        result, exitstatus, signalstatus = execute_synchronous(command)

        if not exitstatus:
            logger.log_value('Migrated', source_path)
            display.update_status('migrate_page__custom_disk', OK)
            display.update_label('migrate_page__custom_disk_message', '')
        else:
            logger.log_value('Error. Unable to migrate', source_path)
            logger.log_value('The result is', result)
            display.update_status('migrate_page__custom_disk', ERROR)
            display.update_label('migrate_page__custom_disk_message', 'Error. Unable to migrate %s.' % source_path)
            is_error = True

    else:

        logger.log_value('Error. Unable to migrate because the source directory does not exist', source_path)
        display.update_status('migrate_page__custom_disk', ERROR)
        display.update_label('migrate_page__custom_disk_message', 'Error. Unable to migrate %s.' % source_path)
        is_error = True

    # Pause to allow the user to see the result.
    sleep(1.00)

    return is_error
