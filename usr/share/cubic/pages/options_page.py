#!/usr/bin/python3

########################################################################
#                                                                      #
# options_page.py                                                      #
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

from os import makedirs, remove
from os.path import dirname, exists, join
from re import fullmatch

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

name = 'options_page'

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

        # TODO: Uncomment the following two lines when undo/redo
        #       functionality has been developed.
        # displayer.set_visible('options_page__header_bar_preseed_box_1', True)
        # displayer.set_visible('options_page__header_bar_box_2', True)

        displayer.set_visible('title_label', False)
        displayer.set_visible('stack_switcher', True)

        # displayer.set_solid('options_page__stack_switcher', True)
        # displayer.set_solid('stack_switcher', True)

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

        # TODO: Uncomment the following two lines when undo/redo
        #       functionality has been developed.
        # displayer.set_visible('options_page__header_bar_preseed_box_1', True)
        # displayer.set_visible('options_page__header_bar_box_2', True)

        displayer.set_visible('title_label', False)
        displayer.set_visible('stack_switcher', True)

        # displayer.set_solid('options_page__stack_switcher', True)
        # displayer.set_solid('stack_switcher', True)

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

        # TODO: Uncomment the following two lines when undo/redo
        #       functionality has been developed.
        # displayer.set_visible('options_page__header_bar_preseed_box_1', False)
        # displayer.set_visible('options_page__header_bar_box_2', False)

        displayer.set_visible('title_label', True)
        displayer.set_visible('stack_switcher', False)

        return

    elif action == 'next':

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        # TODO: Uncomment the following two lines when undo/redo
        #       functionality has been developed.
        # displayer.set_visible('options_page__header_bar_preseed_box_1', False)
        # displayer.set_visible('options_page__header_bar_box_2', False)

        displayer.set_visible('title_label', True)
        displayer.set_visible('stack_switcher', False)

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


def on_clicked__options_page__boot_revert_button(widget):

    # TODO
    print('TBD: on_clicked__options_page__boot_revert_button')


def on_clicked__options_page__boot_undo_button(widget):

    # TODO
    print('TBD: on_clicked__options_page__boot_undo_button')


def on_clicked__options_page__boot_redo_button(widget):

    # TODO
    print('TBD: on_clicked__options_page__boot_redo_button')


def on_clicked__options_page__preseed_revert_button(widget):

    # TODO
    print('TBD: on_clicked__options_page__preseed_revert_button')


def on_clicked__options_page__preseed_undo_button(widget):

    # TODO
    print('TBD: on_clicked__options_page__preseed_undo_button')


def on_clicked__options_page__preseed_redo_button(widget):

    print('TBD: on_clicked__options_page__preseed_redo_button')


def on_toggled__options_page__create_button(widget):

    on_toggled_create_or_delete_toggle_buttons('options_page__create_button')


def on_toggled__options_page__delete_button(widget):

    on_toggled_create_or_delete_toggle_buttons('options_page__delete_button')


def on_toggled_create_or_delete_toggle_buttons(toggle_button_name):

    options_page__create_button = model.builder.get_object('options_page__create_button')
    is_active_options_page__create_button = options_page__create_button.get_active()

    options_page__delete_button = model.builder.get_object('options_page__delete_button')
    is_active_options_page__delete_button = options_page__delete_button.get_active()

    if is_active_options_page__create_button and not is_active_options_page__delete_button:

        # Create
        displayer.set_visible('options_page__preseed_tab__stack', False)

        # Reset the name of the file to create and reset the error message.
        displayer.update_entry('options_page__preseed_tab__create_grid__entry', '')
        displayer.update_label('options_page__preseed_tab__create_grid__error_label', '')

        displayer.set_visible('options_page__preseed_tab__create_grid', True)
        displayer.set_visible('options_page__preseed_tab__delete_grid', False)

    elif not is_active_options_page__create_button and is_active_options_page__delete_button:

        # Delete
        displayer.set_visible('options_page__preseed_tab__stack', False)
        displayer.set_visible('options_page__preseed_tab__create_grid', False)

        # Get the name of the file to delete and reset the error message.
        stack = model.builder.get_object('options_page__preseed_tab__stack')
        scrolled_window = stack.get_visible_child()
        title = stack.child_get_property(scrolled_window, 'title')
        displayer.update_entry('options_page__preseed_tab__delete_grid__entry', title)
        displayer.update_label('options_page__preseed_tab__delete_grid__error_label', '')

        displayer.set_visible('options_page__preseed_tab__delete_grid', True)

    elif not is_active_options_page__create_button and not is_active_options_page__delete_button:

        # Edit
        displayer.set_visible('options_page__preseed_tab__stack', True)
        displayer.set_visible('options_page__preseed_tab__create_grid', False)
        displayer.set_visible('options_page__preseed_tab__delete_grid', False)

    elif toggle_button_name == 'options_page__create_button':

        # Create
        displayer.activate_toggle_button('options_page__create_button', True)
        displayer.activate_toggle_button('options_page__delete_button', False)

    elif toggle_button_name == 'options_page__delete_button':

        # Delete
        displayer.activate_toggle_button('options_page__create_button', False)
        displayer.activate_toggle_button('options_page__delete_button', True)

    else:

        print('NO MATCH')


def on_event__options_page__preseed_tab__stack_sidebar(widget, event):

    stack = model.builder.get_object('options_page__preseed_tab__stack')

    # Show or hide widgets, as necessary.

    scrolled_window = stack.get_visible_child()
    # scrolled_windows = stack.get_children()
    if scrolled_window:

        # Toggle buttons
        displayer.activate_toggle_button('options_page__create_button', False)
        displayer.activate_toggle_button('options_page__delete_button', False)

    else:

        # Toggle buttons
        displayer.activate_toggle_button('options_page__create_button', True)
        displayer.activate_toggle_button('options_page__delete_button', False)


def on_clicked__options_page__create_button(widget):

    # Get new item name.
    entry = model.builder.get_object('options_page__preseed_tab__create_grid__entry')
    filename = entry.get_text()

    # Validate filename.
    pattern = r'[a-zA-Z0-9][a-zA-Z0-9\.\-_]*[a-zA-Z0-9]'
    match = fullmatch(pattern, filename)

    if match:

        # New filename is valid.

        stack_name = 'options_page__preseed_tab__stack'
        stack = model.builder.get_object(stack_name)
        filepath = join(model.project.custom_disk_directory, 'preseed', filename)

        scrolled_window = stack.get_child_by_name(filepath)
        if scrolled_window:

            # Item already exists in the stack.

            logger.log_value('Item already exists in the stack', stack_name)
            title = stack.child_get_property(scrolled_window, 'title')
            logger.log_value('The title is', title)
            logger.log_value('The name (filepath) is', filepath)
            label = model.builder.get_object('options_page__preseed_tab__create_grid__error_label')
            label.set_text('Error. A file with this name already exists.')

        else:

            # Add a new item to the stack.

            logger.log_value('Add a new item to stack', stack_name)
            title = '/%s' % join('preseed', filename)
            logger.log_value('The title is', title)
            logger.log_value('The name (filepath) is', filepath)

            # Ensure the file is not flaged for deletion.
            if filepath in model.delete_list:
                model.delete_list.remove(filepath)

            # Add a new scrolled window to the stack.
            scrolled_window = displayer.add_source_view_to_stack(stack, title, filepath)

            # Show or hide widgets, as necessary.
            stack.set_visible_child(scrolled_window)

            # Toggle buttons

            displayer.activate_toggle_button('options_page__create_button', False)
            displayer.set_sensitive('options_page__create_button', True)

            displayer.activate_toggle_button('options_page__delete_button', False)
            displayer.set_sensitive('options_page__delete_button', True)

    else:

        # New filename is not valid.

        label = model.builder.get_object('options_page__preseed_tab__create_grid__error_label')
        label.set_text('Error. Invalid file name. Valid file names contain alpha-numeric characters, dashes, underscores, or periods.')


def on_clicked__options_page__delete_button(widget):

    stack_name = 'options_page__preseed_tab__stack'
    stack = model.builder.get_object(stack_name)

    scrolled_window = stack.get_visible_child()
    title = stack.child_get_property(scrolled_window, 'title')
    filepath = stack.child_get_property(scrolled_window, 'name')

    logger.log_value('Remove item from stack', stack_name)
    logger.log_value('The title is', title)
    logger.log_value('The name (filepath) is', filepath)

    # Only flag the file for deletion if it exits.
    if exists(filepath):
        model.delete_list.append(filepath)
    stack.remove(scrolled_window)

    # Show or hide widgets, as necessary.

    scrolled_window = stack.get_visible_child()
    # scrolled_windows = stack.get_children()

    if scrolled_window:

        # Toggle buttons

        displayer.activate_toggle_button('options_page__create_button', False)
        displayer.set_sensitive('options_page__create_button', True)

        displayer.activate_toggle_button('options_page__delete_button', False)
        displayer.set_sensitive('options_page__delete_button', True)

    else:

        # Toggle buttons

        displayer.activate_toggle_button('options_page__create_button', True)
        displayer.set_sensitive('options_page__create_button', False)

        displayer.activate_toggle_button('options_page__delete_button', False)
        displayer.set_sensitive('options_page__delete_button', False)


def on_toggled__options_page__kernels_radio_button_ORIGINAL(widget, row):

    selected_index = int(row)
    logger.log_value('The selected kernel is item number', selected_index)

    # 0: version_name
    # 1: vmlinuz_filename
    # 2: new_vmlinuz_filename
    # 3: initrd_filename
    # 4: new_initrd_filename
    # 5: directory
    # 6: note
    # 7: is_selected

    list_store = model.builder.get_object('options_page__linux_kernels_tab__list_store')

    # Select clicked row, and unselect other rows.
    for number, item in enumerate(list_store):
        list_store[number][7] = (number == selected_index)

    # Search and replace text.
    stack_name = 'options_page__boot_configuration_tab__stack'

    # search_text_1 = r'/vmlinuz\S*'
    # replacement_text_1 = '/%s' % list_store[selected_index][2]
    search_text_1 = r'(linux.*)vmlinuz\S*'
    replacement_text_1 = r'\1%s' % list_store[selected_index][2]

    search_text_2 = r'(kernel.*)vmlinuz\S*'
    replacement_text_2 = r'\1%s' % list_store[selected_index][2]

    # search_text_3 = r'/initrd\S*'
    # replacement_text_3 = '/%s' % list_store[selected_index][4]
    search_text_3 = r'(initrd.*)initrd\S*'
    replacement_text_3 = r'\1%s' % list_store[selected_index][4]

    # Note: This won't work if boot appears between linux and vmlinuz.
    search_text_4 = r'(linux.*vmlinuz\S*\s*)(?!.*boot=)'
    replacement_text_4 = r'\1boot=casper '

    search_text_5 = r'(append\s*)(?!.*boot=)'
    replacement_text_5 = r'\1boot=casper '

    displayer.replace_text_in_stack_buffer(
        stack_name,
        (search_text_1,
         replacement_text_1),
        (search_text_2,
         replacement_text_2),
        (search_text_3,
         replacement_text_3),
        (search_text_4,
         replacement_text_4),
        (search_text_5,
         replacement_text_5))


def on_toggled__options_page__kernels_radio_button(widget, row):

    # The contents of the boot configurations files is also replaced in
    # prepare_page.prepare_boot_configurations().

    # 0: version_name
    # 1: vmlinuz_filename
    # 2: new_vmlinuz_filename
    # 3: initrd_filename
    # 4: new_initrd_filename
    # 5: directory
    # 6: note
    # 7: is_selected

    list_store = model.builder.get_object('options_page__linux_kernels_tab__list_store')

    selected_index = int(row)
    # Select clicked row, and unselect other rows.
    for number, item in enumerate(list_store):
        list_store[number][7] = (number == selected_index)

    logger.log_value('The selected kernel is index number', selected_index)

    # vmlinuz & boot=casper
    # search_text_1 = r'\s+boot\s*=\s*casper'
    search_text_1 = r' boot=casper'
    replacement_text_1 = r''
    search_text_2 = r'%s/vmlinuz\S*' % model.status.casper_directory
    replacement_text_2 = r'%s/%s boot=casper' % (model.status.casper_directory, list_store[selected_index][2])

    # initrd
    search_text_3 = r'%s/initrd\S*' % model.status.casper_directory
    replacement_text_3 = r'%s/%s' % (model.status.casper_directory, list_store[selected_index][4])

    # Search and replace text.
    stack_name = 'options_page__boot_configuration_tab__stack'
    displayer.replace_text_in_stack_buffer(stack_name, (search_text_1, replacement_text_1), (search_text_2, replacement_text_2), (search_text_3, replacement_text_3))


def on_map__options_page__preseed_tab(*args):

    displayer.set_visible('options_page__header_bar_preseed_box_1', True)

    # TODO: Do not show the revert, undo, and redo buttons until they
    # are implemented.
    # displayer.set_visible('options_page__header_bar_preseed_box_2', True)
    displayer.set_visible('options_page__header_bar_preseed_box_2', False)


def on_unmap__options_page__preseed_tab(*args):

    displayer.set_visible('options_page__header_bar_preseed_box_1', False)
    displayer.set_visible('options_page__header_bar_preseed_box_2', False)


def on_map__options_page__boot_configuration_tab(*args):

    # TODO: Do not show the revert, undo, and redo buttons until they
    # are implemented.
    # displayer.set_visible('options_page__header_bar_boot_box', True)
    displayer.set_visible('options_page__header_bar_boot_box', False)


def on_unmap__options_page__boot_configuration_tab(*args):

    displayer.set_visible('options_page__header_bar_boot_box', False)
