#!/usr/bin/python3

########################################################################
#                                                                      #
# test_1_page.py                                                       #
#                                                                      #
# Copyright (C) 2021 PJ Singh <psingh.cubic@gmail.com>                 #
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

from cubic.constants import BOLD_RED, NORMAL
from cubic.navigator import handle_navigation
from cubic.utilities import displayer
from cubic.utilities import emulator
from cubic.utilities import file_utilities
from cubic.utilities import iso_utilities
from cubic.utilities import logger
from cubic.utilities import model

########################################################################
# Global Variables & Constants
########################################################################

name = 'test_1_page'

########################################################################
# Navigation Functions
########################################################################


def setup(action, old_page=None):

    if action == 'test':

        displayer.update_label('test_1_page__banner_label', '\n')
        displayer.set_label_error('test_1_page__banner_label', False)
        displayer.update_entry('test_1_page__custom_iso_version_number_entry', model.generated.iso_version_number)
        displayer.update_entry('test_1_page__custom_iso_file_name_entry', model.generated.iso_file_name)
        displayer.update_entry('test_1_page__custom_iso_directory_entry', model.generated.iso_directory)
        displayer.update_entry('test_1_page__custom_iso_volume_id_entry', model.generated.iso_volume_id)
        displayer.update_entry('test_1_page__custom_iso_release_name_entry', model.generated.iso_release_name)
        displayer.update_entry('test_1_page__custom_iso_disk_name_entry', model.generated.iso_disk_name)
        displayer.update_entry('test_1_page__custom_iso_checksum_entry', model.generated.iso_checksum)
        displayer.update_entry('test_1_page__custom_iso_checksum_file_name_entry', model.generated.iso_checksum_file_name)
        '''
        displayer.reset_buttons(
            back_button_label='❬Back',
            back_action='cancel',
            back_button_style='suggested-action',
            is_back_sensitive=True,
            is_back_visible=True,
            next_button_label='Next❭',
            next_action='next',
            next_button_style=None,
            is_next_sensitive=False,
            is_next_visible=False)
        '''

        return

    else:

        logger.log_value('Error', BOLD_RED + 'Unknown action for setup' + NORMAL)

        return 'unknown'


def enter(action, old_page=None):

    if action == 'test':

        emulator.start_emulator(update_status)

        return

    else:

        logger.log_value('Error', BOLD_RED + 'Unknown action for enter' + NORMAL)

        return 'unknown'


def leave(action, new_page=None):

    if action == 'cancel':

        # Remove the status call back to prevent the navigation on
        # 'cancel' action from being invoked twice (by this function and
        # by the status call back function.
        emulator.remove_status_callback()

        displayer.update_label('test_1_page__banner_label', '\n')
        displayer.set_label_error('test_1_page__banner_label', False)

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        return

    elif action == 'quit':

        # Remove the status call back to prevent the navigation on
        # 'cancel' action from being invoked twice (by this function and
        # by the status call back function.
        emulator.remove_status_callback()

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        iso_utilities.unmount_iso_and_delete_mount_point(model.project.iso_mount_point)

        return

    else:

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        logger.log_value('Error', BOLD_RED + 'Unknown action for leave' + NORMAL)

        return 'unknown'


########################################################################
# Handler Functions
########################################################################


def on_clicked__test_1_page__custom_iso_file_name_open_button(widget):

    file_path = os.path.join(model.custom.iso_directory, model.custom.iso_file_name)
    if os.path.isfile(file_path):
        file_utilities.select_file_in_browser(file_path)
    else:
        file_utilities.open_directory_in_browser(model.custom.iso_directory)


def on_clicked__test_1_page__custom_iso_checksum_file_name_open_button(widget):

    file_path = os.path.join(model.custom.iso_directory, model.status.iso_checksum_file_name)
    if os.path.isfile(file_path):
        file_utilities.select_file_in_browser(file_path)
    else:
        file_utilities.open_directory_in_browser(model.custom.iso_directory)


########################################################################
# Support Functions
########################################################################


def update_status(status):
    """
    A callback function supplied by the client in order to be notified
    whenever the emulator starts or exits.

    Arguments:
    status : int
        emulator.EXITED, emulator.RUNNING, or emulator.ERROR
    """

    if status == emulator.EXITED:

        displayer.reset_buttons(
            back_button_label='❬Back',
            back_action='cancel',
            back_button_style='text-button',
            is_back_sensitive=True,
            is_back_visible=True,
            is_next_visible=False)

        handle_navigation('cancel')

    elif status == emulator.RUNNING:

        displayer.update_label('test_1_page__banner_label', 'Testing the generated disk image...')
        displayer.set_label_error('test_1_page__banner_label', False)

        displayer.reset_buttons(
            back_button_label='❬Stop',
            back_action='cancel',
            back_button_style='destructive-action',
            is_back_sensitive=True,
            is_back_visible=True,
            is_next_visible=False)

    elif status == emulator.ERROR:

        displayer.update_label('test_1_page__banner_label', 'Error. Unable to test the generated disk image.')
        displayer.set_label_error('test_1_page__banner_label', True)

        displayer.reset_buttons(
            back_button_label='❬Back',
            back_action='cancel',
            back_button_style='suggested-action',
            is_back_sensitive=True,
            is_back_visible=True,
            is_next_visible=False)

    else:

        pass
