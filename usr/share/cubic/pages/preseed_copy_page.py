#!/usr/bin/python3

########################################################################
#                                                                      #
# preseed_copy_page.py                                                 #
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
import urllib

from constants import FINAL_PERCENT
from utilities import constructor
from utilities import displayer
from utilities import iso_utilities
from utilities import logger
from utilities import model
from utilities.progressor import show_progress

########################################################################
# Global Variables & Constants
########################################################################

name = 'preseed_copy_page'

total_files = 0
file_number = 0

########################################################################
# Navigation Functions
########################################################################


def setup(action, old_page=None):

    if action == 'copy-preseed':

        # The selected uris and current directory are set in FilesTab.selected_uris() method.

        count = len(model.selected_uris)
        count_text = constructor.number_as_text(count)
        files_text = constructor.get_plural('file', 'files', count)
        # label = 'Copy %s %s to <span font_family="monospace">%s</span>...' % (count_text, files_text, model.current_directory)
        label = 'Copy %s %s to %s...' % (count_text, files_text, model.current_directory)

        # Create a file details list of files to be copied.
        file_details_list = create_file_details_list(model.selected_uris)

        displayer.update_label('preseed_copy_page__progress_label', label)
        displayer.update_progress_bar_text('preseed_copy_page__copy_files_progress_bar', None)
        displayer.update_progress_bar_percent('preseed_copy_page__copy_files_progress_bar', 0)
        displayer.update_list_store('preseed_copy_page__file_details__list_store', file_details_list)

        return

    else:

        return 'unknown'


def enter(action, old_page=None):

    if action == 'copy-preseed':

        displayer.reset_buttons(
            back_button_label='Cancel',
            back_action='cancel',
            back_button_style=None,
            is_back_sensitive=True,
            is_back_visible=True,
            next_button_label='Copy',
            next_action='copy-preseed',
            next_button_style='suggested-action',
            is_next_sensitive=True,
            is_next_visible=True)

        return

    else:

        return 'unknown'


def leave(action, new_page=None):

    if action == 'cancel':

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        return

    elif action == 'copy-preseed':

        displayer.reset_buttons(is_back_sensitive=True, is_next_sensitive=False)

        copy_files(model.current_directory, model.selected_uris)

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
        file_path = urllib.parse.unquote(urllib.parse.urlparse(uri).path)
        file_details_list.append([0, file_path])

    return file_details_list


########################################################################
# Copy Files Functions
########################################################################

# TODO: Move these functions to file_utilities.py


def copy_files(current_directory, uris):

    logger.log_label('Copy file(s)')

    global total_files
    total_files = len(uris)

    # It is necessary to strip the leading '/' from the current directory,
    # otherwise os.path.join() considers the current directory to be an absolute
    # path and discards the custom disk directory prefix: "If a component
    # is an absolute path, all previous components are thrown away and
    # os.path.joining continues from the absolute path component."
    # (See https://docs.python.org/3/library/os.path.html).
    target_directory = os.path.abspath(os.path.join(model.project.custom_disk_directory, current_directory.strip(os.path.sep)))

    logger.log_value('The current directory is', current_directory)
    logger.log_value('The custom disk directory is', model.project.custom_disk_directory)
    logger.log_value('The target directory is', target_directory)

    global file_number
    for file_number, uri in enumerate(uris):

        file_path = urllib.parse.unquote(urllib.parse.urlparse(uri).path)

        if total_files == 1:
            # label = 'Copying one file to <span font_family="monospace">%s</span>' % current_directory
            label = 'Copying one file to %s...' % current_directory
        else:
            # label = 'Copying file %s of %s to <span font_family="monospace">%s</span>' % (file_number + 1, total_files, current_directory)
            label = 'Copying file %s of %s to %s...' % (file_number + 1, total_files, current_directory)

        displayer.update_label('preseed_copy_page__progress_label', label)
        displayer.scroll_to_tree_view_row('preseed_copy_page__tree_view', file_number)
        displayer.select_tree_view_row('preseed_copy_page__tree_view', file_number)

        copy_file(file_path, file_number, target_directory, total_files)


def copy_file(file_path, file_number, directory, total_files):

    logger.log_label('Copy file number %s of %s' % (file_number + 1, total_files))

    logger.log_value('The file is', file_path)
    logger.log_value('The target directory is', directory)

    program = os.path.join(model.application.directory, 'commands', 'copy-path')
    command = 'pkexec "%s" "%s" "%s"' % (program, file_path, directory)

    # The progress callback function.
    def progress_callback(percent):
        global total_files
        global file_number
        total_percent = (FINAL_PERCENT * file_number + percent) / total_files
        displayer.update_progress_bar_percent('preseed_copy_page__copy_files_progress_bar', total_percent)
        displayer.update_list_store_progress_bar_percent('preseed_copy_page__file_details__list_store', file_number, percent)
        if total_percent % 10 == 0:
            logger.log_value('Completed', '%i%%' % total_percent)

    exception, message = show_progress(command, progress_callback)


########################################################################
# Validation Functions
########################################################################
