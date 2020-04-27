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

from utilities import display
from utilities import file_utilities
from utilities import iso_utilities
from utilities import logger
from utilities import model

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import os
import re

########################################################################
# Globals & Constants
########################################################################

name = 'options_page'

########################################################################
# Navigation Functions
########################################################################


def setup(action, old_page=None):

    if action == 'back':

        display.reset_buttons(
            back_button_label='❬Back',
            back_action='back',
            back_button_style=None,
            is_back_sensitive=True,
            is_back_visible=True,
            next_button_label='Generate❭',
            next_action='generate',
            next_button_style='suggested-action',
            is_next_sensitive=True,
            is_next_visible=True)

        # display.set_visible('options_page__header_bar_preseed_box_1', True)
        # display.set_visible('options_page__header_bar_box_2', True)
        display.set_visible('title_label', False)
        display.set_visible('stack_switcher', True)

        # display.set_solid('packages_page__header_bar__box', False)
        # display.set_solid('options_page__header_bar__box', False)
        # # display.set_solid('options_page__stack_switcher', True)
        # # display.set_solid('stack_switcher', True)

        return

    elif action == 'next':

        display.reset_buttons(
            back_button_label='❬Back',
            back_action='back',
            back_button_style=None,
            is_back_sensitive=True,
            is_back_visible=True,
            next_button_label='Generate❭',
            next_action='generate',
            next_button_style='suggested-action',
            is_next_sensitive=True,
            is_next_visible=True)

        # display.set_visible('options_page__header_bar_preseed_box_1', True)
        # display.set_visible('options_page__header_bar_box_2', True)
        display.set_visible('title_label', False)
        display.set_visible('stack_switcher', True)

        # display.set_solid('packages_page__header_bar__box', False)
        # display.set_solid('options_page__header_bar__box', False)
        # # display.set_solid('options_page__stack_switcher', True)
        # display.set_solid('stack_switcher', True)

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

        display.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        # display.set_visible('options_page__header_bar_preseed_box_1', False)
        # display.set_visible('options_page__header_bar_box_2', False)
        display.set_visible('title_label', True)
        display.set_visible('stack_switcher', False)

        return

    elif action == 'generate':

        display.reset_buttons(is_back_sensitive=True, is_next_sensitive=False)

        # display.set_visible('options_page__header_bar_preseed_box_1', False)
        # display.set_visible('options_page__header_bar_box_2', False)
        display.set_visible('title_label', True)
        display.set_visible('stack_switcher', False)

        # Save preseed files.
        # TODO: Remove this line when 14.04 is no longer supported.
        # Bypass this functionality for Ubuntu 14.04.
        if model.builder.get_object('options_page__preseed_tab__stack'):
            logger.log_label('Save preseed files')
            save_stack_buffers('options_page__preseed_tab__stack')

        # Delete preseed files.
        if model.delete_list:
            logger.log_label('Delete preseed files')
            for filepath in model.delete_list:
                try:
                    logger.log_value('Delete file', filepath)
                    os.remove(filepath)
                except OSError as exception:
                    logger.log_value('Error deleting file', exception)
            model.delete_list = []

        # Save ISO boot configurations.
        # TODO: Remove this line when 14.04 is no longer supported.
        # Bypass this functionality for Ubuntu 14.04.
        if model.builder.get_object('options_page__boot_configuration_tab__stack'):
            logger.log_label('Save ISO boot configurations')
            save_stack_buffers('options_page__boot_configuration_tab__stack')
        else:
            # TODO: Add this function.
            update_and_save_boot_configurations()

        # TODO: If either of the above fails, action should be 'error'
        #       and we should navigate to an error page.

        display.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        return

    elif action == 'quit':

        display.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        # TODO: When the original ISO image is unmounted we leave the
        #       extract page, remove the following:
        if model.project.iso_mount_point:
            # Unmount the ISO image.
            if iso_utilities.is_mounted(model.project.iso_mount_point):
                iso_utilities.unmount(model.project.iso_mount_point)
            # Delete the mount point.
            file_utilities.delete_directory(model.project.iso_mount_point)

        return

    else:

        return 'unknown'


########################################################################
# Handler Functions
########################################################################


def on_clicked__options_page__boot_revert_button(widget):

    print('TBD:on_clicked__options_page__boot_revert_button')


def on_clicked__options_page__boot_undo_button(widget):

    print('TBD:on_clicked__options_page__boot_undo_button')


def on_clicked__options_page__boot_redo_button(widget):

    print('TBD:on_clicked__options_page__boot_redo_button')


def on_clicked__options_page__preseed_revert_button(widget):

    print('TBD:on_clicked__options_page__preseed_revert_button')


def on_clicked__options_page__preseed_undo_button(widget):

    print('TBD:on_clicked__options_page__preseed_undo_button')


def on_clicked__options_page__preseed_redo_button(widget):

    print('TBD:on_clicked__options_page__preseed_redo_button')


def on_toggled__options_page__create_button(widget):

    print('on_toggled__options_page__create_button')

    on_toggled_create_or_delete_toggle_buttons('options_page__create_button')


def on_toggled__options_page__delete_button(widget):

    print('on_toggled__options_page__delete_button')

    on_toggled_create_or_delete_toggle_buttons('options_page__delete_button')


def on_toggled_create_or_delete_toggle_buttons(toggle_button_name):

    print('toggle button: %s' % toggle_button_name)
    print()

    options_page__create_button = model.builder.get_object('options_page__create_button')
    is_active_options_page__create_button = options_page__create_button.get_active()

    options_page__delete_button = model.builder.get_object('options_page__delete_button')
    is_active_options_page__delete_button = options_page__delete_button.get_active()

    if is_active_options_page__create_button and not is_active_options_page__delete_button:
        # Create
        display.set_visible('options_page__preseed_tab__stack', False)

        # Reset the name of the file to create and reset the error message.
        display.update_entry('options_page__preseed_tab__create_grid__entry', '')
        display.update_label('options_page__preseed_tab__create_grid__error_label', '')

        display.set_visible('options_page__preseed_tab__create_grid', True)
        display.set_visible('options_page__preseed_tab__delete_grid', False)

    elif not is_active_options_page__create_button and is_active_options_page__delete_button:
        # Delete
        display.set_visible('options_page__preseed_tab__stack', False)
        display.set_visible('options_page__preseed_tab__create_grid', False)

        # Get the name of the file to delete and reset the error message.
        stack = model.builder.get_object('options_page__preseed_tab__stack')
        scrolled_window = stack.get_visible_child()
        title = stack.child_get_property(scrolled_window, 'title')
        display.update_entry('options_page__preseed_tab__delete_grid__entry', title)
        display.update_label('options_page__preseed_tab__delete_grid__error_label', '')

        display.set_visible('options_page__preseed_tab__delete_grid', True)

    elif not is_active_options_page__create_button and not is_active_options_page__delete_button:
        # Edit
        display.set_visible('options_page__preseed_tab__stack', True)
        display.set_visible('options_page__preseed_tab__create_grid', False)
        display.set_visible('options_page__preseed_tab__delete_grid', False)
    elif toggle_button_name == 'options_page__create_button':
        # Create
        display.activate_toggle_button('options_page__create_button', True)
        display.activate_toggle_button('options_page__delete_button', False)
    elif toggle_button_name == 'options_page__delete_button':
        # Delete
        display.activate_toggle_button('options_page__create_button', False)
        display.activate_toggle_button('options_page__delete_button', True)
    else:
        print('NO MATCH')


def on_event__options_page__preseed_tab__stack_sidebar(widget, event):

    print('on_event__options_page__preseed_tab__stack_sidebar')

    stack = model.builder.get_object('options_page__preseed_tab__stack')

    # Show or hide widgets, as necessary.

    scrolled_window = stack.get_visible_child()
    # scrolled_windows = stack.get_children()
    if scrolled_window:

        # Toggle buttons
        display.activate_toggle_button('options_page__create_button', False)
        display.activate_toggle_button('options_page__delete_button', False)

    else:

        # Toggle buttons
        display.activate_toggle_button('options_page__create_button', True)
        display.activate_toggle_button('options_page__delete_button', False)


def on_clicked__options_page__create_button(widget):

    print('on_clicked__options_page__create_button')

    # Get new item name.
    entry = model.builder.get_object('options_page__preseed_tab__create_grid__entry')
    filename = entry.get_text()

    # Validate filename.
    pattern = r'[a-zA-Z0-9][a-zA-Z0-9\.\-_]*[a-zA-Z0-9]'
    match = re.fullmatch(pattern, filename)

    if match:

        # New filename is valid.

        stack_name = 'options_page__preseed_tab__stack'
        stack = model.builder.get_object(stack_name)
        filepath = os.path.join(model.project.custom_disk_directory, 'preseed', filename)

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
            title = '/%s' % os.path.join('preseed', filename)
            logger.log_value('The title is', title)
            logger.log_value('The name (filepath) is', filepath)

            # Create a new scrolled window.
            builder_temp = Gtk.Builder.new_from_file('scrolled_window.ui')
            scrolled_window = builder_temp.get_object('scrolled_window')

            # Ensure the file is not flaged for deletion.
            if filepath in model.delete_list:
                model.delete_list.remove(filepath)

            # Add the new scrolled window to the stack.
            stack.add_titled(scrolled_window, filepath, title)
            stack.set_visible_child(scrolled_window)

            # Show or hide widgets, as necessary.

            # Toggle buttons

            display.activate_toggle_button('options_page__create_button', False)
            display.set_sensitive('options_page__create_button', True)

            display.activate_toggle_button('options_page__delete_button', False)
            display.set_sensitive('options_page__delete_button', True)

    else:

        # New filename is not valid.

        label = model.builder.get_object('options_page__preseed_tab__create_grid__error_label')
        label.set_text('Error. Invalid file name. Valid file names contain alpha-numeric characters, dashes, underscores, or periods.')


def on_clicked__options_page__delete_button(widget):

    print('on_clicked__options_page__delete_button')

    stack_name = 'options_page__preseed_tab__stack'
    stack = model.builder.get_object(stack_name)

    scrolled_window = stack.get_visible_child()
    title = stack.child_get_property(scrolled_window, 'title')
    filepath = stack.child_get_property(scrolled_window, 'name')

    logger.log_value('Remove item from stack', stack_name)
    logger.log_value('The title is', title)
    logger.log_value('The name (filepath) is', filepath)

    # Only flag the file for deletion if it exits.
    if os.path.exists(filepath):
        model.delete_list.append(filepath)
    stack.remove(scrolled_window)

    # Show or hide widgets, as necessary.

    scrolled_window = stack.get_visible_child()
    # scrolled_windows = stack.get_children()

    if scrolled_window:

        # Toggle buttons

        display.activate_toggle_button('options_page__create_button', False)
        display.set_sensitive('options_page__create_button', True)

        display.activate_toggle_button('options_page__delete_button', False)
        display.set_sensitive('options_page__delete_button', True)

    else:

        # Toggle buttons

        display.activate_toggle_button('options_page__create_button', True)
        display.set_sensitive('options_page__create_button', False)

        display.activate_toggle_button('options_page__delete_button', False)
        display.set_sensitive('options_page__delete_button', False)


def on_toggled__options_page__kernels_radio_button(widget, row):
    print('on_toggled__options_page__kernels_radio_button')

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
    # 8: is_remove
    liststore = model.builder.get_object('options_page__linux_kernels_tab__liststore')

    # Select clicked row, and unselect other rows.
    for number, item in enumerate(liststore):
        liststore[number][7] = (number == selected_index)

    # Search and replace text.
    stack_name = 'options_page__boot_configuration_tab__stack'

    # The contents of the boot configurations files is also replaced in
    # transitions._transition__from__project_page__to__unsquashfs_page()
    # and utilities.update_and_save_boot_configurations().

    # search_text_1 = r'/vmlinuz\S*'
    # replacement_text_1 = '/%s' % liststore[selected_index][2]
    search_text_1 = r'(linux.*)vmlinuz\S*'
    replacement_text_1 = r'\1%s' % liststore[selected_index][2]

    search_text_2 = r'(kernel.*)vmlinuz\S*'
    replacement_text_2 = r'\1%s' % liststore[selected_index][2]

    # search_text_3 = r'/initrd\S*'
    # replacement_text_3 = '/%s' % liststore[selected_index][4]
    search_text_3 = r'(initrd.*)initrd\S*'
    replacement_text_3 = r'\1%s' % liststore[selected_index][4]

    # Note: This won't work if boot appears between linux and vmlinuz.
    search_text_4 = r'(linux.*vmlinuz\S*\s*)(?!.*boot=)'
    replacement_text_4 = r'\1boot=casper '

    search_text_5 = r'(append\s*)(?!.*boot=)'
    replacement_text_5 = r'\1boot=casper '

    display.replace_text_in_stack_buffer(
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


def on_options_page__stack_switcher_set_focus_child(*args):
    print('on_options_page__stack_switcher_set_focus_child')
    print('There are %s args' % len(args))
    for arg in args:
        print('arg = %s' % arg)


def on_map__options_page__preseed_tab(*args):

    display.set_visible('options_page__header_bar_preseed_box_1', True)
    display.set_visible('options_page__header_bar_preseed_box_2', True)


def on_unmap__options_page__preseed_tab(*args):

    display.set_visible('options_page__header_bar_preseed_box_1', False)
    display.set_visible('options_page__header_bar_preseed_box_2', False)


def on_map__options_page__boot_configuration_tab(*args):

    display.set_visible('options_page__header_bar_boot_box', True)


def on_unmap__options_page__boot_configuration_tab(*args):

    display.set_visible('options_page__header_bar_boot_box', False)


########################################################################
# Support Functions
########################################################################


def save_stack_buffers(stack_name):

    stack = model.builder.get_object(stack_name)
    scrolled_windows = stack.get_children()

    for scrolled_window in scrolled_windows:

        filepath = stack.child_get_property(scrolled_window, 'name')
        title = stack.child_get_property(scrolled_window, 'title')

        logger.log_value('Write file', filepath)

        # Get the updated text.
        source_view = scrolled_window.get_child()
        source_buffer = source_view.get_buffer()
        start_iter = source_buffer.get_start_iter()
        end_iter = source_buffer.get_end_iter()
        data = source_buffer.get_text(start_iter, end_iter, True)

        # Create the parent directories (/preseed, /boot/grub, /isolinux, etc.)
        # if they do not exist.
        directory = os.path.dirname(filepath)
        os.makedirs(directory, exist_ok=True)

        # Write the file.
        with open(filepath, 'w') as file:
            file.write(data)
        # file.flush()
