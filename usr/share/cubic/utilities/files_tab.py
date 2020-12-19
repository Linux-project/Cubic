#!/usr/bin/python3

########################################################################
#                                                                      #
# files_tab.py                                                         #
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

import gi
import magic
import mimetypes
import os
import re
import shutil

gi.require_version('Gtk', '3.0')

from gi.repository import GLib

from file_choosers import copy_file_chooser
from navigator import handle_navigation
from utilities.files_tree import FilesTree
from utilities import logger
from utilities import model

########################################################################
# Global Variables & Constants
########################################################################

# TODO: Improve this pattern.
# FILE_NAME_PATTERN = r'[a-zA-Z0-9][a-zA-Z0-9\.\-_]*[a-zA-Z0-9]'
FILE_NAME_PATTERN = r'[a-zA-Z0-9]([a-zA-Z0-9\.\-_]*[a-zA-Z0-9])*'

FILE_NAME_EXISTS_MESSAGE = 'A file with this name already exists.'
INVALID_FILE_NAME_MESSAGE = 'Enter a valid file name containing alpha-numeric characters, dashes, underscores, or periods.'

########################################################################
# Cubic Tab Class
########################################################################


class FilesTab:

    def __init__(self):
        """
        Create a new FilesTab.
        """

        logger.log_label('Initialize Files Tab')

        self.files_tree = None

        # Note: do not use GLib.idle_add() to connect the signals.
        model.builder.connect_signals(
            {
                self.ON_CHANGED_CREATE_DIRECTORY_FILE_NAME_ENTRY: self.on_changed_create_directory_file_name_entry,
                self.ON_CHANGED_CREATE_FILE_FILE_NAME_ENTRY: self.on_changed_create_file_file_name_entry,
                self.ON_CHANGED_RENAME_DIRECTORY_TARGET_FILE_NAME_ENTRY: self.on_changed_rename_directory_target_file_name_entry,
                self.ON_CHANGED_RENAME_FILE_TARGET_FILE_NAME_ENTRY: self.on_changed_rename_file_target_file_name_entry,
                self.ON_CLICKED_CREATE_DIRECTORY_BUTTON: self.on_clicked_create_directory_button,
                self.ON_CLICKED_CREATE_FILE_BUTTON: self.on_clicked_create_file_button,
                self.ON_CLICKED_DELETE_DIRECTORY_BUTTON: self.on_clicked_delete_directory_button,
                self.ON_CLICKED_DELETE_FILE_BUTTON: self.on_clicked_delete_file_button,
                self.ON_CLICKED_RENAME_DIRECTORY_BUTTON: self.on_clicked_rename_directory_button,
                self.ON_CLICKED_RENAME_FILE_BUTTON: self.on_clicked_rename_file_button,
                self.ON_CLICKED_COPY_FILES_HEADER_BAR_BUTTON: self.on_clicked_copy_files_header_bar_button,
                self.ON_TOGGLED_CREATE_DIRECTORY_HEADER_BAR_BUTTON: self.on_toggled_create_directory_header_bar_button,
                self.ON_TOGGLED_CREATE_FILE_HEADER_BAR_BUTTON: self.on_toggled_create_file_header_bar_button,
                self.ON_TOGGLED_DELETE_DIRECTORY_HEADER_BAR_BUTTON: self.on_toggled_delete_directory_header_bar_button,
                self.ON_TOGGLED_DELETE_FILE_HEADER_BAR_BUTTON: self.on_toggled_delete_file_header_bar_button,
                self.ON_TOGGLED_RENAME_DIRECTORY_HEADER_BAR_BUTTON: self.on_toggled_rename_directory_header_bar_button,
                self.ON_TOGGLED_RENAME_FILE_HEADER_BAR_BUTTON: self.on_toggled_rename_file_header_bar_button,
                self.ON_TOGGLED_SHOW_ALL_FILES_HEADER_BAR_BUTTON: self.on_toggled_show_all_files_header_bar_button
            })

    def create_tree(self, root_file_paths, required_file_paths=None):

        GLib.idle_add(self._create_tree, root_file_paths, required_file_paths)

    def _create_tree(self, root_file_paths, required_file_paths):

        # Activate this show all files (filter) button only if there are
        # required file paths.
        button = model.builder.get_object(self.SHOW_ALL_FILES_HEADER_BAR_BUTTON)
        button.set_active(not bool(required_file_paths))

        self.files_tree = FilesTree(root_file_paths=root_file_paths, selection_changed=self.show_pane_for_file, required_file_paths=required_file_paths)

        # TODO: Should we save this? Could be used in FilesTab.show_pane_for_file()
        # Save the root_file paths.
        # self.root_file_paths = root_file_paths

        # Add the new tree view to the scrolled window.
        scrolled_window = model.builder.get_object(self.SCROLLED_WINDOW_1)
        # child = scrolled_window.get_child()
        # if child: scrolled_window.remove(child)
        scrolled_window.add(self.files_tree.tree_view)

    def remove_tree(self):

        GLib.idle_add(self._remove_tree)

    def _remove_tree(self):

        self.files_tree.remove_watches()
        scrolled_window = model.builder.get_object(self.SCROLLED_WINDOW_1)
        tree_view = scrolled_window.get_child()
        if tree_view: scrolled_window.remove(tree_view)
        self.files_tree = None

    ####################################################################
    # Header Bar Button Handlers
    ####################################################################

    #-------------------------------------------------------------------
    # Filter
    #-------------------------------------------------------------------

    def on_toggled_show_all_files_header_bar_button(self, button):

        GLib.idle_add(self.toggle_show_all_files_header_bar_button, button)

    def toggle_show_all_files_header_bar_button(self, button):

        is_show_all_files = button.get_active()
        self.files_tree.filter(is_show_all_files)

    #-------------------------------------------------------------------
    # Directory
    #-------------------------------------------------------------------

    def untoggle_directory_header_bar_buttons(self, selected_button=None):

        button = model.builder.get_object(self.CREATE_FILE_HEADER_BAR_BUTTON)
        button.handler_block_by_func(self.on_toggled_create_file_header_bar_button)
        button.set_active(button == selected_button)
        button.handler_unblock_by_func(self.on_toggled_create_file_header_bar_button)

        button = model.builder.get_object(self.CREATE_DIRECTORY_HEADER_BAR_BUTTON)
        button.handler_block_by_func(self.on_toggled_create_directory_header_bar_button)
        button.set_active(button == selected_button)
        button.handler_unblock_by_func(self.on_toggled_create_directory_header_bar_button)

        button = model.builder.get_object(self.RENAME_DIRECTORY_HEADER_BAR_BUTTON)
        button.handler_block_by_func(self.on_toggled_rename_directory_header_bar_button)
        button.set_active(button == selected_button)
        button.handler_unblock_by_func(self.on_toggled_rename_directory_header_bar_button)

        button = model.builder.get_object(self.DELETE_DIRECTORY_HEADER_BAR_BUTTON)
        button.handler_block_by_func(self.on_toggled_delete_directory_header_bar_button)
        button.set_active(button == selected_button)
        button.handler_unblock_by_func(self.on_toggled_delete_directory_header_bar_button)

    def on_clicked_copy_files_header_bar_button(self, button):

        GLib.idle_add(self.click_copy_files_header_bar_button, button)

    def click_copy_files_header_bar_button(self, button):

        self.untoggle_directory_header_bar_buttons(button)
        self.show_pane_for_selected_file()
        copy_file_chooser.open(self.selected_uris)

    def on_toggled_create_file_header_bar_button(self, button):

        GLib.idle_add(self.toggle_create_file_header_bar_button, button)

    def toggle_create_file_header_bar_button(self, button):

        is_active = button.get_active()
        if is_active:
            self.untoggle_directory_header_bar_buttons(button)
            self.show_pane_for_selected_create_file()
        else:
            self.show_pane_for_selected_file()

    def on_toggled_create_directory_header_bar_button(self, button):

        GLib.idle_add(self.toggle_create_directory_header_bar_button, button)

    def toggle_create_directory_header_bar_button(self, button):

        is_active = button.get_active()
        if is_active:
            self.untoggle_directory_header_bar_buttons(button)
            self.show_pane_for_selected_create_directory()
        else:
            self.show_pane_for_selected_file()

    def on_toggled_rename_directory_header_bar_button(self, button):

        GLib.idle_add(self.toggle_rename_directory_header_bar_button, button)

    def toggle_rename_directory_header_bar_button(self, button):

        is_active = button.get_active()
        if is_active:
            self.untoggle_directory_header_bar_buttons(button)
            self.show_pane_for_selected_rename_directory()
        else:
            self.show_pane_for_selected_file()

    def on_toggled_delete_directory_header_bar_button(self, button):

        GLib.idle_add(self.toggle_delete_directory_header_bar_button, button)

    def toggle_delete_directory_header_bar_button(self, button):

        is_active = button.get_active()
        if is_active:
            self.untoggle_directory_header_bar_buttons(button)
            self.show_pane_for_selected_delete_directory()
        else:
            self.show_pane_for_selected_file()

    #-------------------------------------------------------------------
    # File
    #-------------------------------------------------------------------

    def untoggle_file_header_bar_buttons(self, selected_button=None):

        button = model.builder.get_object(self.RENAME_FILE_HEADER_BAR_BUTTON)
        button.handler_block_by_func(self.on_toggled_rename_file_header_bar_button)
        button.set_active(button == selected_button)
        button.handler_unblock_by_func(self.on_toggled_rename_file_header_bar_button)

        button = model.builder.get_object(self.DELETE_FILE_HEADER_BAR_BUTTON)
        button.handler_block_by_func(self.on_toggled_delete_file_header_bar_button)
        button.set_active(button == selected_button)
        button.handler_unblock_by_func(self.on_toggled_delete_file_header_bar_button)

    def on_toggled_rename_file_header_bar_button(self, button):

        GLib.idle_add(self.toggle_rename_file_header_bar_button, button)

    def toggle_rename_file_header_bar_button(self, button):

        is_active = button.get_active()
        if is_active:
            self.untoggle_file_header_bar_buttons(button)
            self.show_pane_for_selected_rename_file()
        else:
            self.show_pane_for_selected_file()

    def on_toggled_delete_file_header_bar_button(self, button):

        GLib.idle_add(self.toggle_delete_file_header_bar_button, button)

    def toggle_delete_file_header_bar_button(self, button):

        is_active = button.get_active()
        if is_active:
            self.untoggle_file_header_bar_buttons(button)
            self.show_pane_for_selected_delete_file()
        else:
            self.show_pane_for_selected_file()

    ####################################################################
    # Pane Handlers
    ####################################################################

    #-------------------------------------------------------------------
    # Create File
    #-------------------------------------------------------------------

    def on_changed_create_file_file_name_entry(self, entry):

        GLib.idle_add(self.validate_create_file_file_name)

    def validate_create_file_file_name(self):

        # Get the file name.
        entry = model.builder.get_object(self.CREATE_FILE_FILE_NAME_ENTRY)
        file_name = entry.get_text()

        # Validate file name.
        is_valid = re.fullmatch(FILE_NAME_PATTERN, file_name)

        if is_valid:

            # Get the path for the file.
            label = model.builder.get_object(self.CREATE_FILE_FILE_PATH_LABEL)
            file_path = label.get_text()

            # Get the path for the new file.
            file_path = os.path.join(file_path, file_name)

            # Check if the file already exists.
            full_file_path = self.get_full_file_path(file_path)
            if os.path.exists(full_file_path):
                is_valid = False
                message = FILE_NAME_EXISTS_MESSAGE
            else:
                is_valid = True
                message = ''
        else:
            is_valid = False
            message = INVALID_FILE_NAME_MESSAGE

        button = model.builder.get_object(self.CREATE_FILE_BUTTON)
        button.set_sensitive(is_valid)

        label = model.builder.get_object(self.CREATE_FILE_MESSAGE)
        label.set_text(message)

    def on_clicked_create_file_button(self, button):

        GLib.idle_add(self.create_file)

    def create_file(self):

        # Get the path for the directory.
        label = model.builder.get_object(self.CREATE_FILE_FILE_PATH_LABEL)
        file_path = label.get_text()

        # Get the file name.
        entry = model.builder.get_object(self.CREATE_FILE_FILE_NAME_ENTRY)
        file_name = entry.get_text()

        # Get the path for the new file.
        file_path = os.path.join(file_path, file_name)

        # Create the new file.
        logger.log_value('Create file', file_path)
        full_file_path = self.get_full_file_path(file_path)
        with open(full_file_path, 'a'):
            pass

        # Set target_file_path to notify the the process_IN_CREATE()
        # function to select this file in the tree. After the tree
        # selection changes, the new file will be displayed in the file
        # pane and the header bar buttons will be reset by the
        # show_pane_for_file() callback function.
        self.files_tree.target_file_path = file_path

    #-------------------------------------------------------------------
    # Create Directory
    #-------------------------------------------------------------------

    def on_changed_create_directory_file_name_entry(self, entry):

        GLib.idle_add(self.validate_create_directory_file_name)

    def validate_create_directory_file_name(self):

        # Get the file name.
        entry = model.builder.get_object(self.CREATE_DIRECTORY_FILE_NAME_ENTRY)
        file_name = entry.get_text()

        # Validate file name.
        is_valid = re.fullmatch(FILE_NAME_PATTERN, file_name)

        if is_valid:

            # Get the path for the directory.
            label = model.builder.get_object(self.CREATE_DIRECTORY_FILE_PATH_LABEL)
            file_path = label.get_text()

            # Get the path for the new file.
            file_path = os.path.join(file_path, file_name)

            # Check if the file already exists.
            full_file_path = self.get_full_file_path(file_path)
            if os.path.exists(full_file_path):
                is_valid = False
                message = FILE_NAME_EXISTS_MESSAGE
            else:
                is_valid = True
                message = ''
        else:
            is_valid = False
            message = INVALID_FILE_NAME_MESSAGE

        button = model.builder.get_object(self.CREATE_DIRECTORY_BUTTON)
        button.set_sensitive(is_valid)

        label = model.builder.get_object(self.CREATE_DIRECTORY_MESSAGE)
        label.set_text(message)

    def on_clicked_create_directory_button(self, button):

        GLib.idle_add(self.create_directory)

    def create_directory(self):

        # Get the path for the directory.
        label = model.builder.get_object(self.CREATE_DIRECTORY_FILE_PATH_LABEL)
        file_path = label.get_text()

        # Get the file name.
        entry = model.builder.get_object(self.CREATE_DIRECTORY_FILE_NAME_ENTRY)
        file_name = entry.get_text()

        # Get the path for the new file.
        file_path = os.path.join(file_path, file_name)

        # Create the new file.
        logger.log_value('Create directory', file_path)
        full_file_path = self.get_full_file_path(file_path)
        os.makedirs(full_file_path, exist_ok=True)

        # Set target_file_path to notify the the process_IN_CREATE()
        # function to select this file in the tree. After the tree
        # selection changes, the new file will be displayed in the file
        # pane and the header bar buttons will be reset by the
        # show_pane_for_file() callback function.
        self.files_tree.target_file_path = file_path

    #-------------------------------------------------------------------
    # Rename Directory
    #-------------------------------------------------------------------

    def on_changed_rename_directory_target_file_name_entry(self, entry):

        GLib.idle_add(self.validate_rename_directory_file_name)

    def validate_rename_directory_file_name(self):

        # Get the file name.
        entry = model.builder.get_object(self.RENAME_DIRECTORY_TARGET_FILE_NAME_ENTRY)
        file_name = entry.get_text()

        # Validate file name.
        is_valid = re.fullmatch(FILE_NAME_PATTERN, file_name)

        if is_valid:

            # Get the path for the new file.
            label = model.builder.get_object(self.RENAME_DIRECTORY_FILE_PATH_LABEL)
            file_path = label.get_text()
            parent_directory_path, _ = os.path.split(file_path)
            file_path = os.path.join(parent_directory_path, file_name)

            # Check if the file already exists.
            full_file_path = self.get_full_file_path(file_path)
            if os.path.exists(full_file_path):
                is_valid = False
                message = FILE_NAME_EXISTS_MESSAGE
            else:
                is_valid = True
                message = ''
        else:
            is_valid = False
            message = INVALID_FILE_NAME_MESSAGE

        button = model.builder.get_object(self.RENAME_DIRECTORY_BUTTON)
        button.set_sensitive(is_valid)

        label = model.builder.get_object(self.RENAME_DIRECTORY_MESSAGE)
        label.set_text(message)

    def on_clicked_rename_directory_button(self, button):

        GLib.idle_add(self.rename_directory)

    def rename_directory(self):

        # Get the path for the original file.
        label = model.builder.get_object(self.RENAME_DIRECTORY_FILE_PATH_LABEL)
        source_file_path = label.get_text()

        # Get the path for the new file.
        parent_directory_path, _ = os.path.split(source_file_path)
        entry = model.builder.get_object(self.RENAME_DIRECTORY_TARGET_FILE_NAME_ENTRY)
        target_file_name = entry.get_text()
        target_file_path = os.path.join(parent_directory_path, target_file_name)

        # Update the required file paths. Assume the rename ill succeed.
        ### self.files_tree.update_required_file_paths(source_file_path, target_file_path)

        # Rename the file.
        logger.log_value('Rename directory', 'from %s to %s' % (source_file_path, target_file_path))
        full_source_file_path = self.get_full_file_path(source_file_path)
        full_target_file_path = self.get_full_file_path(target_file_path)
        os.rename(full_source_file_path, full_target_file_path)

        # Set target_file_path to notify the the process_IN_MOVED_TO()
        # function to select this file in the tree. After the tree
        # selection changes, the new file will be displayed in the file
        # pane and the header bar buttons will be reset by the
        # show_pane_for_file() callback function.
        self.files_tree.target_file_path = target_file_path

    #-------------------------------------------------------------------
    # Delete Directory
    #-------------------------------------------------------------------

    def on_clicked_delete_directory_button(self, button):

        GLib.idle_add(self.delete_directory)

    def delete_directory(self):

        # Get the path for the file.
        label = model.builder.get_object(self.DELETE_DIRECTORY_FILE_PATH_LABEL)
        file_path = label.get_text()

        # Delete the file.
        # TODO: What to do about FileNotFoundError error?
        logger.log_value('Delete directory', file_path)
        full_file_path = self.get_full_file_path(file_path)
        shutil.rmtree(full_file_path)

        # Set target_file_path to notify the the process_IN_DELETE()
        # function to select this file's parent directory in the tree.
        # After the tree selection changes, the new file will be
        # displayed in the file pane and the header bar buttons will be
        # reset by the change_tree_view_selection() function.
        self.files_tree.target_file_path = file_path

    #-------------------------------------------------------------------
    # Rename File
    #-------------------------------------------------------------------

    def on_changed_rename_file_target_file_name_entry(self, entry):

        GLib.idle_add(self.validate_rename_file_file_name)

    def validate_rename_file_file_name(self):

        # Get the file name.
        entry = model.builder.get_object(self.RENAME_FILE_TARGET_FILE_NAME_ENTRY)
        file_name = entry.get_text()

        # Validate file name.
        is_valid = re.fullmatch(FILE_NAME_PATTERN, file_name)

        if is_valid:

            # Get the path for the new file.
            label = model.builder.get_object(self.RENAME_FILE_FILE_PATH_LABEL)
            file_path = label.get_text()
            parent_directory_path, _ = os.path.split(file_path)
            file_path = os.path.join(parent_directory_path, file_name)

            # Check if the file already exists.
            full_file_path = self.get_full_file_path(file_path)
            if os.path.exists(full_file_path):
                is_valid = False
                message = FILE_NAME_EXISTS_MESSAGE
            else:
                is_valid = True
                message = ''
        else:
            is_valid = False
            message = INVALID_FILE_NAME_MESSAGE

        button = model.builder.get_object(self.RENAME_FILE_BUTTON)
        button.set_sensitive(is_valid)

        label = model.builder.get_object(self.RENAME_FILE_MESSAGE)
        label.set_text(message)

    def on_clicked_rename_file_button(self, button):

        GLib.idle_add(self.rename_file)

    def rename_file(self):

        # Get the path for the original file.
        label = model.builder.get_object(self.RENAME_FILE_FILE_PATH_LABEL)
        source_file_path = label.get_text()

        # Get the path for the new file.
        parent_directory_path, _ = os.path.split(source_file_path)
        entry = model.builder.get_object(self.RENAME_FILE_TARGET_FILE_NAME_ENTRY)
        target_file_name = entry.get_text()
        target_file_path = os.path.join(parent_directory_path, target_file_name)

        # Update the required file paths.
        # self.files_tree.update_required_file_paths(source_file_path, target_file_path)

        # Rename the file.
        logger.log_value('Rename file', 'from %s to %s' % (source_file_path, target_file_path))
        full_source_file_path = self.get_full_file_path(source_file_path)
        full_target_file_path = self.get_full_file_path(target_file_path)
        os.rename(full_source_file_path, full_target_file_path)

        # Set target_file_path to notify the the process_IN_MOVED_TO()
        # function to select this file in the tree. After the tree
        # selection changes, the new file will be displayed in the file
        # pane and the header bar buttons will be reset by the
        # show_pane_for_file() callback function.
        self.files_tree.target_file_path = target_file_path

    #-------------------------------------------------------------------
    # Delete File
    #-------------------------------------------------------------------

    def on_clicked_delete_file_button(self, button):

        GLib.idle_add(self.delete_file)

    def delete_file(self):

        # Get the path for the file.
        label = model.builder.get_object(self.DELETE_FILE_FILE_PATH_LABEL)
        file_path = label.get_text()

        # Delete the file.
        # TODO: What to do about FileNotFoundError error?
        logger.log_value('Delete directory', file_path)
        full_file_path = self.get_full_file_path(file_path)
        os.remove(full_file_path)

        # Set target_file_path to notify the the process_IN_DELETE()
        # function to select this file's parent directory in the tree.
        # After the tree selection changes, the new file will be
        # displayed in the file pane and the header bar buttons will be
        # reset by the change_tree_view_selection() function.
        self.files_tree.target_file_path = file_path

    ####################################################################
    # Show Pane Functions
    ####################################################################

    #-------------------------------------------------------------------
    # Contents
    #-------------------------------------------------------------------

    def show_pane_for_selected_file(self):

        if self.files_tree:
            file_name, file_path, file_data, mime_type = self.files_tree.get_selected()
            # logger.log_value('Show pane for selected file', file_path)
            self.show_pane_for_file(file_name, file_path, file_data, mime_type)
        else:
            logger.log_value('Warning. Unable to show pane for selected file', 'The tree is None')

    def show_pane_for_file(self, file_name, file_path, file_data, mime_type):
        """
        May be called by methods in this class or as a callback from
        FilesTree.
        """

        logger.log_value('Show pane for file', file_path)

        # Untoggle all header bar buttons.
        self.untoggle_directory_header_bar_buttons()
        self.untoggle_file_header_bar_buttons()

        # Hide the rename and delete buttons for the tree root(s).
        # TODO: What is the best way to determine is_root?
        #       Option 1: is_root = file_path in self.root_file_paths
        #       Option 2: files_tree.is_root()
        is_root = self.files_tree.is_root(file_path)

        self.set_visible(self.RENAME_DIRECTORY_HEADER_BAR_BUTTON, not is_root)
        self.set_visible(self.DELETE_DIRECTORY_HEADER_BAR_BUTTON, not is_root)

        # Show file data in the scrolled window.

        scrolled_window = model.builder.get_object(self.SCROLLED_WINDOW_2)

        # Remove the current child from the scrolled window.
        child = scrolled_window.get_child()
        if child: scrolled_window.remove(child)

        # Display the new child based on the type of file.
        if mime_type == 'directory':
            self.set_visible(self.DIRECTORY_HEADER_BOX, True)
            self.set_visible(self.FILE_HEADER_BOX, False)
            # Set the file name for the view port.
            label = model.builder.get_object(self.FOLDER_NAME)
            label.set_text(file_name)
            # The child is a view port.
            child = model.builder.get_object(self.FOLDER_VIEW_PORT)
        elif file_data == None:
            # File data is read by the FilesTree.change_tree_selection()
            # method. File data will be None if the file could not be
            # read.
            self.set_visible(self.DIRECTORY_HEADER_BOX, False)
            self.set_visible(self.FILE_HEADER_BOX, True)
            # Set the file name for the view port.
            label = model.builder.get_object(self.UNKNOWN_FILE_NAME)
            label.set_text(file_name)
            # The child is a view port.
            child = model.builder.get_object(self.UNKNOWN_VIEW_PORT)
        elif mime_type == 'text':
            self.set_visible(self.DIRECTORY_HEADER_BOX, False)
            self.set_visible(self.FILE_HEADER_BOX, True)
            # The child is a source view.
            child = file_data
        elif mime_type == 'image':
            self.set_visible(self.DIRECTORY_HEADER_BOX, False)
            self.set_visible(self.FILE_HEADER_BOX, True)
            # Set the image for the view port.
            image = model.builder.get_object(self.PICTURE_IMAGE)
            image.set_from_pixbuf(file_data)
            # The child is a view port.
            child = model.builder.get_object(self.PICTURE_VIEW_PORT)
        else:
            self.set_visible(self.DIRECTORY_HEADER_BOX, False)
            self.set_visible(self.FILE_HEADER_BOX, True)
            # Set the file name for the view port.
            label = model.builder.get_object(self.UNKNOWN_FILE_NAME)
            label.set_text(file_name)
            # The child is a view port.
            child = model.builder.get_object(self.UNKNOWN_VIEW_PORT)

        # Add the new child to the scrolled window.
        scrolled_window.add(child)

    #-------------------------------------------------------------------
    # Directory
    #-------------------------------------------------------------------

    def show_pane_for_selected_create_file(self):

        if self.files_tree:
            file_name, file_path, file_data, mime_type = self.files_tree.get_selected()
            # logger.log_value('Show pane for create file', file_path)
            self.show_pane_for_create_file(file_name, file_path, file_data, mime_type)
        else:
            logger.log_value('Warning. Unable to show pane for create file', 'The tree is None')

    def show_pane_for_create_file(self, file_name, file_path, file_data, mime_type):

        logger.log_value('Show pane for create file', file_path)

        scrolled_window = model.builder.get_object(self.SCROLLED_WINDOW_2)

        # Remove the current child from the scrolled window.
        child = scrolled_window.get_child()
        if child: scrolled_window.remove(child)

        # Display information.

        label = model.builder.get_object(self.CREATE_FILE_FILE_PATH_LABEL)
        # label.set_markup('<span font_family="monospace">%s</span>' % file_path)
        label.set_markup(file_path)

        # entry = model.builder.get_object(self.CREATE_FILE_FILE_NAME_ENTRY)
        # entry.set_text('')

        # label = model.builder.get_object(self.CREATE_FILE_MESSAGE)
        # label.set_text('')

        # button = model.builder.get_object(self.CREATE_FILE_BUTTON)
        # button.set_sensitive(False)

        # Explicitly validate the field because the changed signal will
        # not be generated.
        self.validate_create_file_file_name()

        # Add the new child to the scrolled window.
        view_port = model.builder.get_object(self.CREATE_FILE_VIEW_PORT)
        scrolled_window.add(view_port)

    def show_pane_for_selected_create_directory(self):

        if self.files_tree:
            file_name, file_path, file_data, mime_type = self.files_tree.get_selected()
            # logger.log_value('Show pane for create directory', file_path)
            self.show_pane_for_create_directory(file_name, file_path, file_data, mime_type)
        else:
            logger.log_value('Warning. Unable to show pane for create directory', 'The tree is None')

    def show_pane_for_create_directory(self, file_name, file_path, file_data, mime_type):

        logger.log_value('Show pane for create directory', file_path)

        scrolled_window = model.builder.get_object(self.SCROLLED_WINDOW_2)

        # Remove the current child from the scrolled window.
        child = scrolled_window.get_child()
        if child: scrolled_window.remove(child)

        # Display information.

        label = model.builder.get_object(self.CREATE_DIRECTORY_FILE_PATH_LABEL)
        # label.set_markup('<span font_family="monospace">%s</span>' % file_path)
        label.set_markup(file_path)

        # entry = model.builder.get_object(self.CREATE_DIRECTORY_FILE_NAME_ENTRY)
        # entry.set_text('')

        # label = model.builder.get_object(self.CREATE_DIRECTORY_MESSAGE)
        # label.set_text('')

        # button = model.builder.get_object(self.CREATE_DIRECTORY_BUTTON)
        # button.set_sensitive(False)

        # Explicitly validate the field because the changed signal will
        # not be generated.
        self.validate_create_directory_file_name()

        # Add the new child to the scrolled window.
        view_port = model.builder.get_object(self.CREATE_DIRECTORY_VIEW_PORT)
        scrolled_window.add(view_port)

    def show_pane_for_selected_rename_directory(self):

        if self.files_tree:
            file_name, file_path, file_data, mime_type = self.files_tree.get_selected()
            # logger.log_value('Show pane for rename directory', file_path)
            self.show_pane_for_rename_directory(file_name, file_path, file_data, mime_type)
        else:
            logger.log_value('Warning. Unable to show pane for rename directory', 'The tree is None')

    def show_pane_for_rename_directory(self, file_name, file_path, file_data, mime_type):

        logger.log_value('Show pane for rename directory', file_path)

        scrolled_window = model.builder.get_object(self.SCROLLED_WINDOW_2)

        # Remove the current child from the scrolled window.
        child = scrolled_window.get_child()
        if child: scrolled_window.remove(child)

        # Display information.

        label = model.builder.get_object(self.RENAME_DIRECTORY_FILE_PATH_LABEL)
        # label.set_markup('<span font_family="monospace">%s</span>' % file_path)
        label.set_markup(file_path)

        entry = model.builder.get_object(self.RENAME_DIRECTORY_SOURCE_FILE_NAME_ENTRY)
        entry.set_text(file_name)

        entry = model.builder.get_object(self.RENAME_DIRECTORY_TARGET_FILE_NAME_ENTRY)
        entry.set_text(file_name)

        label = model.builder.get_object(self.RENAME_DIRECTORY_MESSAGE)
        label.set_text('Enter a new name for the directory.')

        # button = model.builder.get_object(self.RENAME_DIRECTORY_BUTTON)
        # button.set_sensitive(False)

        # Add the new child to the scrolled window.
        view_port = model.builder.get_object(self.RENAME_DIRECTORY_VIEW_PORT)
        scrolled_window.add(view_port)

    def show_pane_for_selected_delete_directory(self):

        if self.files_tree:
            file_name, file_path, file_data, mime_type = self.files_tree.get_selected()
            # logger.log_value('Show pane for selected directory', file_path)
            self.show_pane_for_delete_directory(file_name, file_path, file_data, mime_type)
        else:
            logger.log_value('Warning. Unable to show pane for delete directory', 'The tree is None')

    def show_pane_for_delete_directory(self, file_name, file_path, file_data, mime_type):

        logger.log_value('Show pane for delete directory', file_path)

        scrolled_window = model.builder.get_object(self.SCROLLED_WINDOW_2)

        # Remove the current child from the scrolled window.
        child = scrolled_window.get_child()
        if child: scrolled_window.remove(child)

        # Display information.

        label = model.builder.get_object(self.DELETE_DIRECTORY_FILE_PATH_LABEL)
        # label.set_markup('<span font_family="monospace">%s</span>' % file_path)
        label.set_markup(file_path)

        entry = model.builder.get_object(self.DELETE_DIRECTORY_FILE_NAME_ENTRY)
        entry.set_text(file_name)

        label = model.builder.get_object(self.DELETE_DIRECTORY_MESSAGE)
        label.set_text('Warning. This directory will be permanently removed.')

        # button = model.builder.get_object(self.DELETE_DIRECTORY_BUTTON)
        # button.set_sensitive(False)

        # Add the new child to the scrolled window.
        view_port = model.builder.get_object(self.DELETE_DIRECTORY_VIEW_PORT)
        scrolled_window.add(view_port)

    #-------------------------------------------------------------------
    # File
    #-------------------------------------------------------------------

    def show_pane_for_selected_rename_file(self):

        if self.files_tree:
            file_name, file_path, file_data, mime_type = self.files_tree.get_selected()
            # logger.log_value('Show pane for rename file', file_path)
            self.show_pane_for_rename_file(file_name, file_path, file_data, mime_type)
        else:
            logger.log_value('Warning. Unable to show pane for rename file', 'The tree is None')

    def show_pane_for_rename_file(self, file_name, file_path, file_data, mime_type):

        logger.log_value('Show pane for rename file', file_path)

        scrolled_window = model.builder.get_object(self.SCROLLED_WINDOW_2)

        # Remove the current child from the scrolled window.
        child = scrolled_window.get_child()
        if child: scrolled_window.remove(child)

        # Display information.

        label = model.builder.get_object(self.RENAME_FILE_FILE_PATH_LABEL)
        label.set_text(file_path)

        entry = model.builder.get_object(self.RENAME_FILE_SOURCE_FILE_NAME_ENTRY)
        entry.set_text(file_name)

        entry = model.builder.get_object(self.RENAME_FILE_TARGET_FILE_NAME_ENTRY)
        entry.set_text(file_name)

        label = model.builder.get_object(self.RENAME_FILE_MESSAGE)
        label.set_text('Enter a new name for the file.')

        # button = model.builder.get_object(self.RENAME_FILE_BUTTON)
        # button.set_sensitive(False)

        # Add the new child to the scrolled window.
        view_port = model.builder.get_object(self.RENAME_FILE_VIEW_PORT)
        scrolled_window.add(view_port)

    def show_pane_for_selected_delete_file(self):

        if self.files_tree:
            file_name, file_path, file_data, mime_type = self.files_tree.get_selected()
            # logger.log_value('Show pane for delete file', file_path)
            self.show_pane_for_delete_file(file_name, file_path, file_data, mime_type)
        else:
            logger.log_value('Warning. Unable to show pane for delete file', 'The tree is None')

    def show_pane_for_delete_file(self, file_name, file_path, file_data, mime_type):

        logger.log_value('Show pane for delete file', file_path)

        scrolled_window = model.builder.get_object(self.SCROLLED_WINDOW_2)

        # Remove the current child from the scrolled window.
        child = scrolled_window.get_child()
        if child: scrolled_window.remove(child)

        # Display information.

        label = model.builder.get_object(self.DELETE_FILE_FILE_PATH_LABEL)
        label.set_text(file_path)

        entry = model.builder.get_object(self.DELETE_FILE_FILE_NAME_ENTRY)
        entry.set_text(file_name)

        label = model.builder.get_object(self.DELETE_FILE_MESSAGE)
        label.set_text('Warning. This file will be permanently removed.')

        # button = model.builder.get_object(self.DELETE_FILE_BUTTON)
        # button.set_sensitive(False)

        # Add the new child to the scrolled window.
        view_port = model.builder.get_object(self.DELETE_FILE_VIEW_PORT)
        scrolled_window.add(view_port)

    ####################################################################
    # File Chooser Functions
    ####################################################################

    def selected_uris(self, uris):

        model.selected_uris = uris
        logger.log_value('The selected uris are', model.selected_uris)

        model.current_directory = self.files_tree.get_selected()[1]
        logger.log_value('The current directory is', model.current_directory)

        # Go to the copy page.
        handle_navigation(self.COPY_ACTION)

    ####################################################################
    #
    ####################################################################

    def search_and_replace_in_files(self, file_paths, *search_replace_tuples):

        GLib.idle_add(self._search_and_replace_in_files, file_paths, search_replace_tuples)

    def _search_and_replace_in_files(self, file_paths, search_replace_tuples):
        """
        file_path             - a list of relative file paths
        search_replace_tuples - a list of tuples containing (search
                                text, replacement text)
        """

        # logger.log_label('Search and replace in files')

        for file_path in file_paths:
            self.files_tree.search_and_replace_in_file(file_path, search_replace_tuples)

    ####################################################################
    # Miscellaneous Functions
    ####################################################################

    def guess_mime_type(self, full_file_path):
        """
        Guess the mime type using the file extension. This is faster
        than reading the file, but may be inaccurate.

        Arguments:
        full_file_path - Full file path of the file.

        Returns:
        The mime type of the file.
        """

        if os.path.isdir(full_file_path):
            # https://specifications.freedesktop.org/shared-mime-info-spec/shared-mime-info-spec-latest.html#idm140625828597376
            # inode/directory
            mime_type = 'directory'
        else:
            mime_info = mimetypes.guess_type(full_file_path)[0]
            if mime_info:
                mime_type, mime_subtype = mime_info.split(os.path.sep)
                if mime_type == 'application' and mime_subtype == 'octet-stream' and os.path.getsize(full_file_path) == 1:
                    mime_type = 'text'
            else:
                mime_type = None

        return mime_type

    def read_mime_type(self, full_file_path):
        """
        Guess the mime type by reading the file. This is slower than
        using the file extension, but is more inaccurate.

        Arguments:
        full_file_path - Full file path of the file.

        Returns:
        The mime type of the file.
        """

        if os.path.isdir(full_file_path):
            # https://specifications.freedesktop.org/shared-mime-info-spec/shared-mime-info-spec-latest.html#idm140625828597376
            # inode/directory
            mime_type = 'directory'
        else:
            mime_info = magic.from_file(full_file_path, True)
            if mime_info:
                mime_type, mime_subtype = mime_info.split(os.path.sep)
                if mime_type == 'application' and mime_subtype == 'octet-stream' and os.path.getsize(full_file_path) == 1:
                    mime_type = 'text'
                elif mime_type == 'inode' and mime_subtype == 'x-empty':
                    mime_type = 'text'
            else:
                mime_type = None

        return mime_type

    def get_icon_name(self, mime_type):

        if mime_type == 'audo':
            icon_name = 'audio-x-generic'

        elif mime_type == 'directory':
            icon_name = 'folder-symbolic'

        elif mime_type == 'font':
            icon_name = 'font-x-generic'

        elif mime_type == 'image':
            icon_name = 'image-x-generic'

        elif mime_type == 'package':
            icon_name = 'package-x-generic'

        elif mime_type == 'text':
            icon_name = 'text-x-generic'

        elif mime_type == 'video':
            icon_name = 'video-x-generic'

        else:
            icon_name = 'application-x-executable'

        return icon_name

    def set_visible(self, widget_name, is_visible):

        widget = model.builder.get_object(widget_name)
        widget.set_visible(is_visible)

    def get_required_file_paths(self):
        """
        This method is used by options_page.
        """

        if self.files_tree:
            return self.files_tree.get_required_file_paths()
        else:
            return []

    def get_full_file_path(self, file_path):

        file_path = os.path.join(model.project.custom_disk_directory, file_path)

        return file_path

    def get_relative_file_path(self, file_path):

        file_path = os.path.relpath(file_path, model.project.custom_disk_directory)

        return file_path
