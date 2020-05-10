#!/usr/bin/python3

########################################################################
#                                                                      #
# packages_page.py                                                     #
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

from os.path import exists, join

from utilities import displayer
from utilities import iso_utilities
from utilities import logger
from utilities import model

########################################################################
# References
########################################################################

# N/A

########################################################################
# Globals & Constants
########################################################################

name = 'packages_page'

########################################################################
# Navigation Functions
########################################################################


def setup(action, old_page=None):

    if action == 'back':

        displayer.reset_buttons(
            back_button_label='❬Back',
            back_action='back',
            back_button_style=None,
            is_back_sensitive=True,
            is_back_visible=True,
            next_button_label='Next❭',
            next_action='next',
            next_button_style='suggested-action',
            is_next_sensitive=True,
            is_next_visible=True)

        displayer.set_visible('packages_page__header_bar_box', True)

        # TODO: Shouldn't we do this on the options page?

        # displayer.set_solid('packages_page__header_bar__box', True)
        # displayer.set_solid('options_page__header_bar__box', False)
        # displayer.set_solid('options_page__stack_switcher', False)
        # displayer.set_solid('stack_switcher', False)
        displayer.set_visible('stack_switcher', False)

        return

    elif action == 'next':

        displayer.reset_buttons(
            back_button_label='❬Back',
            back_action='back',
            back_button_style=None,
            is_back_sensitive=True,
            is_back_visible=True,
            next_button_label='Next❭',
            next_action='next',
            next_button_style='suggested-action',
            is_next_sensitive=True,
            is_next_visible=True)

        displayer.set_visible('packages_page__header_bar_box', True)

        # TODO: Shouldn't we do this on the options page?

        # displayer.set_solid('packages_page__header_bar__box', True)
        # displayer.set_solid('options_page__header_bar__box', False)
        # displayer.set_solid('options_page__stack_switcher', False)
        # displayer.set_solid('stack_switcher', False)
        displayer.set_visible('stack_switcher', False)

        # TODO: Remove these variables from the model, and add them to the Packages page.
        model.undo_index = 0
        model.undo_list = []

        displayer.set_sensitive('packages_page__redo_button', False)
        displayer.set_sensitive('packages_page__revert_button', False)
        displayer.set_sensitive('packages_page__undo_button', False)

        return

    else:

        return 'unknown'


def enter(action, old_page=None):

    if action == 'back':

        return

    elif action == 'next':

        return

    else:

        return 'unknown'


def leave(action, new_page=None):

    if action == 'back':

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        displayer.set_visible('packages_page__header_bar_box', False)

        return

    elif action == 'next':

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        displayer.set_visible('packages_page__header_bar_box', False)

        # Update filesystem.manifest-remove file.
        # Always save the filesystem.manifest-remove file, even if there are no
        # packages to remove. If the does not exist an empty file will be created.
        # This function will create the file if it does not exist.
        filename = 'filesystem.manifest-remove'
        removable_packages_list = create_typical_removable_packages_list()
        save_filesystem_manifest_remove_file(filename, removable_packages_list)

        # Update filesystem.manifest-minimal-remove file.
        filename = 'filesystem.manifest-minimal-remove'
        is_exists = is_exists_filesystem_manifest_remove(filename)
        removable_packages_list = create_minimal_removable_packages_list()
        # Save the filesystem.manifest-minimal-remove file if there are packages to
        # remove or if the file already exists. If the file does not exist, there
        # will not be any packages to remove. (In the future, if we may show the
        # minimal remove column even when the file does not exist).
        if is_exists or removable_packages_list:
            # This function will create the file if it does not exist.
            save_filesystem_manifest_remove_file(filename, removable_packages_list)

        # TODO: If either of the above fails, action should be 'error'
        #       and we should navigate to an error page.

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


def on_clicked__packages_page__revert_button(widget):

    list_store = model.builder.get_object('packages_page__list_store')

    while model.undo_index > 0:

        model.undo_index -= 1

        row, column = model.undo_list[model.undo_index]

        displayer.select_tree_view_row('packages_page__treeview', row)
        # displayer.scroll_to_tree_view_row('packages_page__treeview', row)
        # sleep(0.250)

        # print(
        #     ' - Row: %s, Column: %s, Typical: %s, Minimal: %s, Previous: %s, Active: %s, Length: %s, Index: %s'
        #     % (
        #         row,
        #         column,
        #         list_store[row][0],
        #         list_store[row][1],
        #         list_store[row][2],
        #         list_store[row][3],
        #         len(model.undo_list),
        #         model.undo_index))

        if column == 0:
            list_store[row][0] = not list_store[row][0]
            # Even though the minimal check button column may not be visible (if
            # 'filesystem.manifest-minimal-remove' does not exist, still update
            # the list_store. It's a little inefficient, but does no harm.
            if list_store[row][0]:
                # Backup original minimal check button value
                list_store[row][2] = list_store[row][1]
                # Set minimal check button selected
                list_store[row][1] = True
                # Set minimal check button inactive
                list_store[row][3] = False
            else:
                # Restore original minimal check button value
                list_store[row][1] = list_store[row][2]
                # Set minimal check button active
                list_store[row][3] = True
        else:
            list_store[row][1] = not list_store[row][1]

    # if model.undo_index == 0:
    displayer.set_sensitive('packages_page__revert_button', False)
    displayer.set_sensitive('packages_page__undo_button', False)

    displayer.set_sensitive('packages_page__redo_button', True)

    # print(
    #     ' - Row: %s, Column: %s, Typical: %s, Minimal: %s, Previous: %s, Active: %s, Length: %s, Index: %s'
    #     % (
    #         row,
    #         column,
    #         list_store[row][0],
    #         list_store[row][1],
    #         list_store[row][2],
    #         list_store[row][3],
    #         len(model.undo_list),
    #         model.undo_index))


def on_clicked__packages_page__undo_button(widget):

    model.undo_index -= 1

    list_store = model.builder.get_object('packages_page__list_store')

    row, column = model.undo_list[model.undo_index]

    displayer.select_tree_view_row('packages_page__treeview', row)
    # displayer.scroll_to_tree_view_row('packages_page__treeview', row)
    # sleep(0.250)

    # print(
    #     ' - Row: %s, Column: %s, Typical: %s, Minimal: %s, Previous: %s, Active: %s, Length: %s, Index: %s'
    #     % (
    #         row,
    #         column,
    #         list_store[row][0],
    #         list_store[row][1],
    #         list_store[row][2],
    #         list_store[row][3],
    #         len(model.undo_list),
    #         model.undo_index))

    if column == 0:
        list_store[row][0] = not list_store[row][0]
        # Even though the minimal check button column may not be visible (if
        # 'filesystem.manifest-minimal-remove' does not exist, still update
        # the list_store. It's a little inefficient, but does no harm.
        if list_store[row][0]:
            # Backup original minimal check button value
            list_store[row][2] = list_store[row][1]
            # Set minimal check button selected
            list_store[row][1] = True
            # Set minimal check button inactive
            list_store[row][3] = False
        else:
            # Restore original minimal check button value
            list_store[row][1] = list_store[row][2]
            # Set minimal check button active
            list_store[row][3] = True
    else:
        list_store[row][1] = not list_store[row][1]

    if model.undo_index == 0:
        displayer.set_sensitive('packages_page__revert_button', False)
        displayer.set_sensitive('packages_page__undo_button', False)

    displayer.set_sensitive('packages_page__redo_button', True)

    # print(
    #     ' - Row: %s, Column: %s, Typical: %s, Minimal: %s, Previous: %s, Active: %s, Length: %s, Index: %s'
    #     % (
    #         row,
    #         column,
    #         list_store[row][0],
    #         list_store[row][1],
    #         list_store[row][2],
    #         list_store[row][3],
    #         len(model.undo_list),
    #         model.undo_index))


def on_clicked__packages_page__redo_button(widget):

    list_store = model.builder.get_object('packages_page__list_store')

    row, column = model.undo_list[model.undo_index]

    displayer.select_tree_view_row('packages_page__treeview', row)
    # displayer.scroll_to_tree_view_row('packages_page__treeview', row)
    # sleep(0.250)

    # print(
    #     ' - Row: %s, Column: %s, Typical: %s, Minimal: %s, Previous: %s, Active: %s, Length: %s, Index: %s'
    #     % (
    #         row,
    #         column,
    #         list_store[row][0],
    #         list_store[row][1],
    #         list_store[row][2],
    #         list_store[row][3],
    #         len(model.undo_list),
    #         model.undo_index))

    if column == 0:
        list_store[row][0] = not list_store[row][0]
        # Even though the minimal check button column may not be visible (if
        # 'filesystem.manifest-minimal-remove' does not exist, still update
        # the list_store. It's a little inefficient, but does no harm.
        if list_store[row][0]:
            # Backup original minimal check button value
            list_store[row][2] = list_store[row][1]
            # Set minimal check button selected
            list_store[row][1] = True
            # Set minimal check button inactive
            list_store[row][3] = False
        else:
            # Restore original minimal check button value
            list_store[row][1] = list_store[row][2]
            # Set minimal check button active
            list_store[row][3] = True
    else:
        list_store[row][1] = not list_store[row][1]

    model.undo_index += 1

    if len(model.undo_list) == model.undo_index:
        displayer.set_sensitive('packages_page__redo_button', False)

    displayer.set_sensitive('packages_page__revert_button', True)
    displayer.set_sensitive('packages_page__undo_button', True)

    # print(
    #     ' - Row: %s, Column: %s, Typical: %s, Minimal: %s, Previous: %s, Active: %s, Length: %s, Index: %s'
    #     % (
    #         row,
    #         column,
    #         list_store[row][0],
    #         list_store[row][1],
    #         list_store[row][2],
    #         list_store[row][3],
    #         len(model.undo_list),
    #         model.undo_index))


def on_toggled__packages_page__remove_1_check_button(widget, row):

    list_store = model.builder.get_object('packages_page__list_store')

    # column = 0
    # print(
    #     ' - Row: %s, Column: %s, Typical: %s, Minimal: %s, Previous: %s, Active: %s, Length: %s, Index: %s'
    #     % (
    #         row,
    #         column,
    #         list_store[row][0],
    #         list_store[row][1],
    #         list_store[row][2],
    #         list_store[row][3],
    #         len(model.undo_list),
    #         model.undo_index))

    list_store[row][0] = not list_store[row][0]

    # Even though the minimal check button column may not be visible (if
    # 'filesystem.manifest-minimal-remove' does not exist, still update
    # the list_store. It's a little inefficient, but does no harm.
    if list_store[row][0]:
        # Backup original minimal check button value
        list_store[row][2] = list_store[row][1]
        # Set minimal check button selected
        list_store[row][1] = True
        # Set minimal check button inactive
        list_store[row][3] = False
    else:
        # Restore original minimal check button value
        list_store[row][1] = list_store[row][2]
        # Set minimal check button active
        list_store[row][3] = True

    if len(model.undo_list) > model.undo_index:
        # print(' - Insert at %s, value %s' % (model.undo_index, [row, 0]))
        model.undo_list[model.undo_index] = [row, 0]
    else:
        # print(
        #     ' - Append at %s, value %s' % (model.undo_index + 1,
        #                                    [row,
        #                                     0]))
        model.undo_list.append([row, 0])

    model.undo_index += 1

    displayer.set_sensitive('packages_page__revert_button', True)
    displayer.set_sensitive('packages_page__undo_button', True)
    displayer.set_sensitive('packages_page__redo_button', False)
    del model.undo_list[model.undo_index:]

    # print(
    #     ' - Row: %s, Column: %s, Typical: %s, Minimal: %s, Previous: %s, Active: %s, Length: %s, Index: %s'
    #     % (
    #         row,
    #         column,
    #         list_store[row][0],
    #         list_store[row][1],
    #         list_store[row][2],
    #         list_store[row][3],
    #         len(model.undo_list),
    #         model.undo_index))


def on_toggled__packages_page__remove_2_check_button(widget, row):

    list_store = model.builder.get_object('packages_page__list_store')

    # column = 1
    # print(
    #     ' - Row: %s, Column: %s, Typical: %s, Minimal: %s, Previous: %s, Active: %s, Length: %s, Index: %s'
    #     % (
    #         row,
    #         column,
    #         list_store[row][0],
    #         list_store[row][1],
    #         list_store[row][2],
    #         list_store[row][3],
    #         len(model.undo_list),
    #         model.undo_index))

    list_store[row][1] = not list_store[row][1]

    if len(model.undo_list) > model.undo_index:
        # print(' - Insert at %s, value %s' % (model.undo_index, [row, 1]))
        model.undo_list[model.undo_index] = [row, 1]
    else:
        # print(
        #     ' - Append at %s, value %s' % (model.undo_index + 1,
        #                                    [row,
        #                                     1]))
        model.undo_list.append([row, 1])

    model.undo_index += 1

    displayer.set_sensitive('packages_page__revert_button', True)
    displayer.set_sensitive('packages_page__undo_button', True)
    displayer.set_sensitive('packages_page__redo_button', False)
    del model.undo_list[model.undo_index:]

    # print(
    #     ' - Row: %s, Column: %s, Typical: %s, Minimal: %s, Previous: %s, Active: %s, Length: %s, Index: %s'
    #     % (
    #         row,
    #         column,
    #         list_store[row][0],
    #         list_store[row][1],
    #         list_store[row][2],
    #         list_store[row][3],
    #         len(model.undo_list),
    #         model.undo_index))


########################################################################
# Support Functions
########################################################################


# TODO: This function is needed on multiple pages. Consider refactoring.
#       - extract_page
#       - generate_page
#       - options_page
def is_exists_filesystem_manifest_remove(filename):

    # Check custom live iso directory
    filepath = join(model.project.custom_disk_directory, model.status.casper_directory, filename)

    is_exists = exists(filepath)
    if is_exists:
        logger.log_value('%s found in' % filename, join(model.project.custom_disk_directory, model.status.casper_directory))
        return True
    else:
        logger.log_value('%s not found in' % filename, join(model.project.custom_disk_directory, model.status.casper_directory))
        return False


# TODO: This function is needed on multiple pages. Consider refactoring.
#       - packages_page
#       - prepare_page
def create_typical_removable_packages_list():

    logger.log_label('Create typical removable packages list')

    listore_name = 'packages_page__list_store'
    logger.log_value('Get user selections from', listore_name)
    list_store = model.builder.get_object(listore_name)
    removable_packages_list = []
    item = list_store.get_iter_first()
    while item is not None:
        flag = list_store.get_value(item, 0)
        package_name = list_store.get_value(item, 4)
        if flag:
            removable_packages_list.append(package_name)
        item = list_store.iter_next(item)
    removable_packages_list
    logger.log_value('New number of packages to be removed', len(removable_packages_list))

    return removable_packages_list


# TODO: This function is needed on multiple pages. Consider refactoring.
#       - packages_page
#       - prepare_page
def create_minimal_removable_packages_list():

    logger.log_label('Create minimal removable packages list')

    listore_name = 'packages_page__list_store'
    logger.log_value('Get user selections from', listore_name)
    list_store = model.builder.get_object(listore_name)
    removable_packages_list = []
    item = list_store.get_iter_first()
    while item is not None:
        flag = list_store.get_value(item, 1) and list_store.get_value(item, 3)
        package_name = list_store.get_value(item, 4)
        if flag:
            removable_packages_list.append(package_name)
        item = list_store.iter_next(item)
    removable_packages_list
    logger.log_value('New number of packages to be removed', len(removable_packages_list))

    return removable_packages_list


# TODO: This function is needed on multiple pages. Consider refactoring.
#       - packages_page
#       - prepare_page
# TODO: This function is not used.
def create_removable_packages_list(listore_name, index):

    logger.log_label('Get removable packages list from user selections')
    logger.log_value('Get user selections from', listore_name)
    list_store = model.builder.get_object(listore_name)
    removable_packages_list = []
    item = list_store.get_iter_first()
    while item is not None:
        flag = list_store.get_value(item, index)
        package_name = list_store.get_value(item, 2)
        if flag:
            removable_packages_list.append(package_name)
        item = list_store.iter_next(item)
    removable_packages_list
    logger.log_value('New number of packages to be removed', len(removable_packages_list))

    return removable_packages_list


def save_filesystem_manifest_remove_file(filename, removable_packages_list):

    logger.log_label('Create new filesystem manifest remove file')

    filepath = join(model.project.custom_disk_directory, model.status.casper_directory, filename)
    logger.log_value('Write filesystem manifest remove file to', filepath)
    with open(filepath, 'w') as file:
        first_line = True
        for packages_name in removable_packages_list:
            if first_line:
                file.write('%s' % packages_name)
                first_line = False
            else:
                file.write('\n%s' % packages_name)
