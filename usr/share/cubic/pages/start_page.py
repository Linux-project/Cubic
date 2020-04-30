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

from file_choosers import directory_chooser

from constants import NEW_CUBIC_VERSION
from utilities import configuration
from utilities import constructor
from utilities import displayer
from utilities import logger
from utilities import model

from os.path import isfile

########################################################################
# Globals & Constants
########################################################################

name = 'start_page'

########################################################################
# Navigation Functions
########################################################################


def setup(action, old_page=None):

    if action == 'open':

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

        model.project.cubic_version = None
        model.project.directory = None
        model.project.configuration_filepath = None
        model.project.iso_mount_point = None
        model.project.custom_root_directory = None
        model.project.custom_disk_directory = None

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

        return

    elif action == 'back':

        if model.project.cubic_version < NEW_CUBIC_VERSION:
            displayer.reset_buttons(
                back_button_label='❬Back',
                back_action='back',
                back_button_style=None,
                is_back_sensitive=False,
                is_back_visible=False,
                next_button_label='Next❭',
                next_action='migrate',
                next_button_style='suggested-action',
                is_next_sensitive=True,
                is_next_visible=True)
            # displayer.update_label('start_page__project_directory_message', 'This directory contains a legacy Cubic project.')
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

        return

    elif action == 'cancel':

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

        return

    else:

        return 'unknown'


def enter(action, old_page=None):

    if action == 'open':

        # TODO: FOR TESTING ONLY
        # test('/mnt/ram/Ubuntu-19.10')

        return

    elif action == 'back':

        return

    elif action == 'cancel':

        return

    else:

        return 'unknown'


def leave(action, new_page=None):

    if action == 'next':

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        # The following fields must be set before leaving this page:
        # 1. project.cubic_version
        #    - Should be updated to application.cubic_version when the
        #      configuration is saved.
        # 2. project.directory
        #    - Set in the selected_project_directory() function.
        # 3. project.configuration_filepath
        #    - Set in the selected_project_directory() function.
        # 4. project.iso_mount_point
        # 5. project.custom_root_directory
        # 6. project.custom_disk_directory

        model.project.iso_mount_point = constructor.construct_original_iso_mount_point(model.project.directory)
        model.project.custom_root_directory = constructor.construct_custom_root_directory(model.project.directory)
        model.project.custom_disk_directory = constructor.construct_custom_disk_directory(model.project.directory)

        return

    elif action == 'migrate':

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        # The following fields must be set before leaving this page:
        # 1. project.cubic_version
        #    - Should be updated to application.cubic_version when the
        #      configuration is saved.
        # 2. project.directory
        #    - Set in the selected_project_directory() function.
        # 3. project.configuration_filepath
        #    - Set in the selected_project_directory() function.
        # 4. project.iso_mount_point
        # 5. project.custom_root_directory
        # 6. project.custom_disk_directory

        model.project.iso_mount_point = constructor.construct_original_iso_mount_point(model.project.directory)
        model.project.custom_root_directory = constructor.construct_custom_root_directory(model.project.directory)
        model.project.custom_disk_directory = constructor.construct_custom_disk_directory(model.project.directory)

        return

    elif action == 'quit':

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        return

    else:

        return 'unknown'


########################################################################
# Handler Functions
########################################################################


def on_changed__start_page__project_directory_entry(widget):

    logger.log_label('Project directory changed')

    model.project.directory = widget.get_text()

    validate_page()


def on_clicked__start_page__project_directory_open_button(widget):

    logger.log_title('Clicked project directory page project directory file chooser open button')

    directory_chooser.open(selected_project_directory)

    # TODO: Remove
    # if model.project.cubic_version < model.application.cubic_version:
    #     displayer.update_label('start_page__project_directory_message', 'This project was created using an older version of Cubic.')


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
        model.project.configuration_filepath = constructor.construct_configuration_filepath(model.project.directory)
        if isfile(model.project.configuration_filepath):
            configuration.load()
            if model.project.cubic_version < NEW_CUBIC_VERSION:
                displayer.reset_buttons(
                    back_button_label='❬Back',
                    back_action='back',
                    back_button_style=None,
                    is_back_sensitive=False,
                    is_back_visible=False,
                    next_button_label='Next❭',
                    next_action='migrate',
                    next_button_style='suggested-action',
                    is_next_sensitive=True,
                    is_next_visible=True)
                displayer.update_label('start_page__project_directory_message', 'This directory contains a legacy Cubic project.')
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
                displayer.update_label('start_page__project_directory_message', 'This directory contains an existing Cubic project.')
        else:
            configuration.initialize()
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
            displayer.update_label('start_page__project_directory_message', 'A new cubic project will be created in this directory.')
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
