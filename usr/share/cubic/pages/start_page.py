#!/usr/bin/python3

########################################################################
#                                                                      #
# start_page.py                                                        #
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

from constants import CUBIC_VERSION_2020, CUBIC_VERSION_2021
from constants import OK, ERROR, EXCLUDED_FILESYSTEM_TYPES
from file_choosers import directory_chooser
from utilities import configuration
from utilities import constructor
from utilities import displayer
from utilities import file_utilities
from utilities import logger
from utilities import model

########################################################################
# Global Variables & Constants
########################################################################

name = 'start_page'

########################################################################
# Navigation Functions
########################################################################


def setup(action, old_page=None):

    if action == 'open':

        # Initialize button labels, actions, and styles.

        displayer.reset_buttons(
            back_button_label='❬Back',
            back_action='back',
            back_button_style=None,
            is_back_sensitive=False,
            is_back_visible=False,
            next_button_label='Next❭',
            next_action='next',
            next_button_style='suggested-action',
            is_next_sensitive=False,
            is_next_visible=True)

        display_version = constructor.get_major_minor_version(model.application.cubic_version)
        displayer.update_label('start_page__version_label', 'Version %s' % display_version)
        displayer.update_label('start_page__project_directory_message', 'Select a project directory.')

        return

    elif action == 'back':

        # Do not change button labels, actions, and styles.
        # The validate_page() function in the enter action will assign
        # the correct button labels, actions, and styles.

        displayer.reset_buttons(
            back_button_label=None,
            back_action=None,
            back_button_style=None,
            is_back_sensitive=False,
            is_back_visible=None,
            next_button_label=None,
            next_action=None,
            next_button_style=None,
            is_next_sensitive=None,
            is_next_visible=None)

        return

    elif action == 'cancel':

        # Do not change button labels, actions, and styles.

        displayer.reset_buttons(
            back_button_label=None,
            back_action=None,
            back_button_style=None,
            is_back_sensitive=False,
            is_back_visible=None,
            next_button_label=None,
            next_action=None,
            next_button_style=None,
            is_next_sensitive=None,
            is_next_visible=None)

        return

    else:

        return 'unknown'


def enter(action, old_page=None):

    if action == 'open':

        # TODO: FOR TESTING ONLY
        # test('/mnt/ram/Ubuntu')

        return

    elif action == 'back':

        validate_page()

        return

    elif action == 'cancel':

        return

    else:

        return 'unknown'


def leave(action, new_page=None):

    if action == 'next':

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        # The following fields must be set before leaving this page:
        #
        # 1. model.project.cubic_version
        #    - Loaded from an existing configuration, or set to
        #      model.application.cubic_version in the reset_model()
        #      function if the selected project directory changed.
        # 2. model.project.create_date
        #    - Loaded from an existing configuration, or set to current
        #      date in the reset_model() function if the selected
        #      project directory changed.
        # 3. model.project.directory
        #    - Set in the selected_project_directory() function.
        # 4. model.project.configuration_file_path
        #    - Set in the selected_project_directory() function.
        # 5. model.project.iso_mount_point
        # 6. model.project.custom_root_directory
        # 7. model.project.custom_disk_directory
        # 8. model.update_release_description

        # model.project.iso_mount_point = constructor.construct_original_iso_mount_point(model.project.directory)
        # model.project.custom_root_directory = constructor.construct_custom_root_directory(model.project.directory)
        # model.project.custom_disk_directory = constructor.construct_custom_disk_directory(model.project.directory)

        return

    elif action == 'migrate':

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        # The following fields must be set before leaving this page:
        #
        # 1. model.project.cubic_version
        #    - Loaded from an existing configuration, or set to
        #      model.application.cubic_version in the reset_model()
        #      function if the selected project directory changed.
        # 2. model.project.create_date
        #    - Loaded from an existing configuration, or set to current
        #      date in the reset_model() function if the selected
        #      project directory changed.
        # 3. model.project.directory
        #    - Set in the selected_project_directory() function.
        # 4. model.project.configuration_file_path
        #    - Set in the selected_project_directory() function.
        # 5. model.project.iso_mount_point
        # 6. model.project.custom_root_directory
        # 7. model.project.custom_disk_directory
        # 8. model.update_release_description

        # model.project.iso_mount_point = constructor.construct_original_iso_mount_point(model.project.directory)
        # model.project.custom_root_directory = constructor.construct_custom_root_directory(model.project.directory)
        # model.project.custom_disk_directory = constructor.construct_custom_disk_directory(model.project.directory)

        return

    elif action == 'quit':

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        return

    else:

        return 'unknown'


########################################################################
# Handler Functions
########################################################################


def on_clicked__start_page__project_directory_open_button(widget):

    logger.log_title('Clicked project directory page project directory file chooser open button')

    directory_chooser.open(selected_project_directory, model.project.directory)


def on_changed__start_page__project_directory_entry(widget):

    logger.log_label('Project directory changed')

    model.project.directory = widget.get_text()

    validate_page()


########################################################################
# Support Functions
########################################################################


def test(project_directory):

    logger.log_title('Clicked project directory page project directory file chooser open button')

    selected_project_directory(project_directory)


def selected_project_directory(directory):

    logger.log_label('Directory selected')
    logger.log_value('Directory', directory)

    displayer.update_entry('start_page__project_directory_entry', directory)


########################################################################
# Validation Functions
########################################################################


def validate_page():

    if model.project.directory:
        if file_utilities.directory_is_writable(model.project.directory):
            file_system_type = file_utilities.get_file_system_type(model.project.directory)
            if file_system_type not in EXCLUDED_FILESYSTEM_TYPES:
                model.project.iso_mount_point = constructor.construct_original_iso_mount_point(model.project.directory)
                model.project.custom_root_directory = constructor.construct_custom_root_directory(model.project.directory)
                model.project.custom_disk_directory = constructor.construct_custom_disk_directory(model.project.directory)
                model.project.configuration_file_path = constructor.construct_configuration_file_path(model.project.directory)
                if os.path.isfile(model.project.configuration_file_path):
                    configuration.load()
                    model.update_release_description = bool(model.project.cubic_version < CUBIC_VERSION_2021)
                    if model.project.cubic_version < CUBIC_VERSION_2020:
                        displayer.reset_buttons(
                            back_button_label='❬Back',
                            back_action='back',
                            back_button_style=None,
                            is_back_sensitive=False,
                            is_back_visible=False,
                            next_button_label='Migrate❭',
                            next_action='migrate',
                            next_button_style='suggested-action',
                            is_next_sensitive=True,
                            is_next_visible=True)
                        displayer.update_label('start_page__project_directory_message', 'This directory contains a legacy Cubic project.')
                        displayer.set_entry_error('start_page__project_directory_entry', OK)
                    else:
                        displayer.reset_buttons(
                            back_button_label='❬Back',
                            back_action='back',
                            back_button_style=None,
                            is_back_sensitive=False,
                            is_back_visible=False,
                            next_button_label='Next❭',
                            next_action='next',
                            next_button_style='suggested-action',
                            is_next_sensitive=True,
                            is_next_visible=True)
                        # displayer.update_label('start_page__project_directory_message', 'This directory contains an existing Cubic project.')
                        # TODO: Remove the following if/else clause in a
                        #       future release because this code was
                        #       added to alleviate a configuration file
                        #       layout change. (12/19/2020)
                        if not model.status.iso_template and not os.path.isfile(os.path.join(model.original.iso_directory, model.original.iso_file_name)):
                            displayer.update_label(
                                'start_page__project_directory_message',
                                '<span size="medium" foreground="red">Warning. Cubic will require the original disk image to copy important files and may overwrite your changes to the disk boot configurations (%s) or preseed files. Before proceeding, make backups of these files located in %s.</span>'
                                % (', '.join(model.options.boot_configurations),
                                   model.project.custom_disk_directory))
                        else:
                            displayer.update_label('start_page__project_directory_message', 'This directory contains an existing Cubic project.')
                        displayer.set_entry_error('start_page__project_directory_entry', OK)
                else:
                    configuration.initialize()
                    reset_model()
                    model.update_release_description = True
                    displayer.reset_buttons(
                        back_button_label='❬Back',
                        back_action='back',
                        back_button_style=None,
                        is_back_sensitive=False,
                        is_back_visible=False,
                        next_button_label='Next❭',
                        next_action='next',
                        next_button_style='suggested-action',
                        is_next_sensitive=True,
                        is_next_visible=True)
                    displayer.update_label('start_page__project_directory_message', 'A new Cubic project will be created using this directory.')
                    displayer.set_entry_error('start_page__project_directory_entry', OK)
            else:
                displayer.reset_buttons(
                    back_button_label='❬Back',
                    back_action='back',
                    back_button_style=None,
                    is_back_sensitive=False,
                    is_back_visible=False,
                    next_button_label='Next❭',
                    next_action='next',
                    next_button_style='suggested-action',
                    is_next_sensitive=False,
                    is_next_visible=True)
                displayer.update_label(
                    'start_page__project_directory_message',
                    '<span foreground="red">Error. Cannot customize Linux on the %s file system.</span>' % file_system_type)
                displayer.set_entry_error('start_page__project_directory_entry', ERROR)
        else:
            displayer.reset_buttons(
                back_button_label='❬Back',
                back_action='back',
                back_button_style=None,
                is_back_sensitive=False,
                is_back_visible=False,
                next_button_label='Next❭',
                next_action='next',
                next_button_style='suggested-action',
                is_next_sensitive=False,
                is_next_visible=True)
            displayer.update_label('start_page__project_directory_message', '<span foreground="red">Error. Cannot access directory.</span>')
            displayer.set_entry_error('start_page__project_directory_entry', ERROR)
    else:
        displayer.reset_buttons(
            back_button_label='❬Back',
            back_action='back',
            back_button_style=None,
            is_back_sensitive=False,
            is_back_visible=False,
            next_button_label='Next❭',
            next_action='next',
            next_button_style='suggested-action',
            is_next_sensitive=False,
            is_next_visible=True)
        displayer.update_label('start_page__project_directory_message', 'Select a project directory.')
        displayer.set_entry_error('start_page__project_directory_entry', OK)


def reset_model():

    model.project.cubic_version = model.application.cubic_version
    model.project.create_date = constructor.get_current_time_stamp()
    model.project.modify_date = None
    # model.project.directory = None
    # model.project.configuration_file_path = None
    # model.project.iso_mount_point = None
    # model.project.custom_root_directory = None
    # model.project.custom_disk_directory = None

    model.original.iso_file_name = None
    model.original.iso_directory = None
    model.original.iso_volume_id = None
    model.original.iso_release_name = None
    model.original.iso_disk_name = None
    model.original.iso_release_notes_url = None

    model.custom.iso_version_number = None
    model.custom.iso_file_name = None
    model.custom.iso_directory = None
    model.custom.iso_volume_id = None
    model.custom.iso_release_name = None
    model.custom.iso_disk_name = None
    model.custom.iso_release_notes_url = None

    model.status.is_success_copy = False
    model.status.is_success_extract = False
    model.status.iso_template = None
    model.status.casper_directory = None
    model.status.iso_checksum = None
    model.status.iso_checksum_file_name = None

    model.options.boot_configurations = None
    model.options.compression = None
