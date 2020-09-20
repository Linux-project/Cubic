#!/usr/bin/python3

########################################################################
#                                                                      #
# copy_page.py                                                         #
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

from os.path import abspath, join
from urllib.parse import urlparse, unquote

from constants import PERCENT_STOP
from utilities.console import get_current_directory
from utilities import displayer
from utilities import iso_utilities
from utilities import logger
from utilities import model
from utilities.progressor import show_progress

########################################################################
# References
########################################################################

# N/A

########################################################################
# Globals & Constants
########################################################################

name = 'copy_page'

current_directory = None
total_files = 0
file_number = 0

########################################################################
# Navigation Functions
########################################################################


def setup(action, old_page=None):

    if action == 'copy':

        global current_directory
        # TODO: Truncate path current_directory so it only starts at root.
        current_directory = get_current_directory()

        total_files = len(model.uris)
        if total_files == 1:
            label = 'Copy one file to %s' % current_directory
        else:
            label = 'Copy %s files to %s' % (total_files, current_directory)

        # Create a file details list of files to be copied.
        file_details_list = create_file_details_list(model.uris)

        displayer.update_label('copy_page__progress_label', label)
        displayer.update_progress_bar_text('copy_page__copy_files_progress_bar', None)
        displayer.update_progress_bar_percent('copy_page__copy_files_progress_bar', 0)
        displayer.update_list_store('copy_page__file_details__list_store', file_details_list)

        return

    else:

        return 'unknown'


def enter(action, old_page=None):

    if action == 'copy':

        displayer.reset_buttons(
            back_button_label='Cancel',
            back_action='cancel',
            back_button_style=None,
            is_back_sensitive=True,
            is_back_visible=True,
            next_button_label='Copy',
            next_action='copy',
            next_button_style='suggested-action',
            is_next_sensitive=True,
            is_next_visible=True)

        return

    else:

        return 'unknown'


def leave(action, new_page=None):

    if action == 'cancel':

        # TODO: Make sure the next button is enabled (only if the virtual environment is active).
        #       This may need to be done on the termnal_page setup function for 'cancel' and for 'copy'.
        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        return

    elif action == 'copy':

        # TODO: Make sure the next button is enabled (only if the virtual environment is active).
        #       This may need to be done on the termnal_page setup function for 'cancel' and for 'copy'.
        displayer.reset_buttons(is_back_sensitive=True, is_next_sensitive=False)

        global current_directory
        copy_files(current_directory, model.uris)

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

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

########################################################################
# Support Functions
########################################################################


def create_file_details_list(uris):
    # logger.log_value('List files to copy')

    file_details_list = []

    for file_number, uri in enumerate(uris):
        filepath = unquote(urlparse(uri).path)
        file_details_list.append([0, filepath])

    return file_details_list


########################################################################
# Copy Files Functions
########################################################################

# TODO: Move these functions to file_utilities.py


def copy_files(current_directory, uris):

    logger.log_label('Copy file(s)')

    global total_files
    total_files = len(uris)

    # It is necessary to concatenate the custom root directory and
    # the current directory using "+" because join() discards
    # the current directory, which is considered an absolute path: "If a
    # component is an absolute path, all previous components are thrown
    # away and joining continues from the absolute path component."
    # (See https://docs.python.org/3/library/os.path.html).
    # TODO: consider using (a + '/' + b)
    target_directory = abspath(model.project.custom_root_directory + current_directory)

    logger.log_value('The current directory is', current_directory)
    logger.log_value('The custom root directory is', model.project.custom_root_directory)
    logger.log_value('The target directory is', target_directory)

    global file_number
    for file_number, uri in enumerate(uris):

        filepath = unquote(urlparse(uri).path)

        if total_files == 1:
            # label = 'Copying one file to %s' % relative_directory
            label = 'Copying one file to %s' % target_directory
        else:
            # label = 'Copying file %s of %s to %s' % (file_number + 1, total_files, relative_directory)
            label = 'Copying file %s of %s to %s' % (file_number + 1, total_files, target_directory)

        displayer.update_label('copy_page__progress_label', label)
        displayer.scroll_to_tree_view_row('copy_page__treeview', file_number)
        displayer.select_tree_view_row('copy_page__treeview', file_number)

        copy_file(filepath, file_number, target_directory, total_files)


def copy_file(filepath, file_number, directory, total_files):

    logger.log_label('Copy file number %s of %s' % (file_number + 1, total_files))

    logger.log_value('The file is', filepath)
    logger.log_value('The target directory is', directory)

    program = join(model.application.directory, 'commands', 'copy-path')
    command = 'pkexec "%s" "%s" "%s" "%s"' % (program, filepath, directory, 'root')

    # The progress callback function.
    def progress_callback(percent):
        global total_files
        global file_number
        total_percent = (PERCENT_STOP * file_number + percent) / total_files
        displayer.update_progress_bar_percent('copy_page__copy_files_progress_bar', total_percent)
        displayer.update_list_store_progress_bar_percent('copy_page__file_details__list_store', file_number, percent)
        if total_percent % 10 == 0:
            logger.log_value('Completed', '%i%%' % total_percent)

    exception, message = show_progress(command, progress_callback)


########################################################################
# Validation Functions
########################################################################
