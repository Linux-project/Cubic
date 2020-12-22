#!/usr/bin/python3

########################################################################
#                                                                      #
# terminal_page.py                                                     #
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

gi.require_version('Gdk', '3.0')
gi.require_version('Gtk', '3.0')

from gi.repository import Gdk
from gi.repository import Gio
from gi.repository import Gtk

import os
import re
import time

from constants import SLEEP_0250_MS
from file_choosers import copy_file_chooser
from navigator import handle_navigation
from utilities.displayer import MONOSPACE_FONT
from utilities import console
from utilities import displayer
from utilities import iso_utilities
from utilities import logger
from utilities import model
from utilities.processor import execute_synchronous

########################################################################
# Global Variables & Constants
########################################################################

name = 'terminal_page'

# Indicates if the virtual environment is running.
is_running = False

########################################################################
# Initialize
########################################################################

terminal = model.builder.get_object('terminal_page__terminal')

# Set Terminal Font
terminal.set_font(MONOSPACE_FONT)

# Set Terminal Colors
# TODO: Create and use displayer.get_terminal_colors() function.
schema_source = Gio.SettingsSchemaSource.get_default()
_, schemas = schema_source.list_schemas(True)
schemas = Gio.Settings.list_relocatable_schemas()
if 'org.gnome.Terminal.Legacy.Profile' in schemas:
    logger.log_value('Set terminal colors?', 'Yes')
    settings = Gio.Settings.new_with_path('org.gnome.Terminal.Legacy.Profile', '/org/gnome/terminal/legacy/')
    fg_rgb_color = None
    bg_rgb_color = None
    hex_palette = settings.get_value('palette')
    if not hex_palette:
        # Use custom foreground and background colors.
        fg_rgb_color = Gdk.RGBA()
        fg_rgb_color.parse('#e5e5e5')
        bg_rgb_color = Gdk.RGBA()
        bg_rgb_color.parse('#191919')
        hex_palette = [
            '#073642',
            '#DC322F',
            '#859900',
            '#B58900',
            '#268BD2',
            '#D33682',
            '#2AA198',
            '#EEE8D5',
            '#002B36',
            '#CB4B16',
            '#586E75',
            '#657B83',
            '#839496',
            '#6C71C4',
            '#93A1A1',
            '#FDF6E3'
        ]
    rgb_palette = []
    for hex_color in hex_palette:
        rgb_color = Gdk.RGBA()
        rgb_color.parse(hex_color)
        rgb_palette.append(rgb_color)
    terminal.set_colors(fg_rgb_color, bg_rgb_color, rgb_palette)
else:
    logger.log_value('Set terminal colors?', 'Skip')

# Allow Drag and Drop in the Terminal
flags = Gtk.DestDefaults.MOTION | Gtk.DestDefaults.HIGHLIGHT | Gtk.DestDefaults.DROP
# TODO: Change: Gtk.TargetFlags
#       See: https://lazka.github.io/pgi-docs/Gtk-3.0/structs/TargetEntry.html#methods
targets = [Gtk.TargetEntry.new('text/uri-list', 0, 80), Gtk.TargetEntry.new('text/plain', 0, 80)]
actions = Gdk.DragAction.COPY
terminal.drag_dest_set(flags, targets, actions)

########################################################################
# Navigation Functions
########################################################################


def setup(action, old_page=None):

    if action == 'back':

        # The virtual environment will be started in enter().

        displayer.reset_buttons(
            back_button_label='❬Back',
            back_action='back',
            back_button_style=None,
            is_back_sensitive=True,
            is_back_visible=True,
            next_button_label='Next❭',
            next_action='next',
            next_button_style=None,
            is_next_sensitive=False,
            is_next_visible=True)

        displayer.set_visible('terminal_page__copy_header_bar_button', True)
        displayer.set_sensitive('terminal_page__copy_header_bar_button', False)

        return

    if action == 'cancel':

        # Do not assume the virtual environment is running.

        displayer.reset_buttons(
            back_button_label='❬Back',
            back_action='back',
            back_button_style=None,
            is_back_sensitive=True,
            is_back_visible=True,
            next_button_label='Next❭',
            next_action='next',
            next_button_style=None,
            is_next_sensitive=is_running,
            is_next_visible=True)

        displayer.set_visible('terminal_page__copy_header_bar_button', True)
        displayer.set_sensitive('terminal_page__copy_header_bar_button', is_running)

        return

    if action == 'copy-into-terminal':

        # Do not assume the virtual environment is running.

        displayer.reset_buttons(
            back_button_label='❬Back',
            back_action='back',
            back_button_style=None,
            is_back_sensitive=True,
            is_back_visible=True,
            next_button_label='Next❭',
            next_action='next',
            next_button_style=None,
            is_next_sensitive=is_running,
            is_next_visible=True)

        displayer.set_visible('terminal_page__copy_header_bar_button', True)
        displayer.set_sensitive('terminal_page__copy_header_bar_button', is_running)

        return

    elif action == 'next':

        # The virtual environment will be started in enter().

        displayer.reset_buttons(
            back_button_label='❬Back',
            back_action='back',
            back_button_style=None,
            is_back_sensitive=True,
            is_back_visible=True,
            next_button_label='Next❭',
            next_action='next',
            next_button_style=None,
            is_next_sensitive=False,
            is_next_visible=True)

        displayer.set_visible('terminal_page__copy_header_bar_button', True)
        displayer.set_sensitive('terminal_page__copy_header_bar_button', False)

        return

    elif action == 'next-terminal':

        # The virtual environment will be started in enter().

        displayer.reset_buttons(
            back_button_label='❬Back',
            back_action='back',
            back_button_style=None,
            is_back_sensitive=True,
            is_back_visible=True,
            next_button_label='Next❭',
            next_action='next',
            next_button_style=None,
            is_next_sensitive=False,
            is_next_visible=True)

        displayer.set_visible('terminal_page__copy_header_bar_button', True)
        displayer.set_sensitive('terminal_page__copy_header_bar_button', False)

        return

    else:

        return 'unknown'


def enter(action, old_page=None):

    if action == 'back':

        # Attempt to enter the virtual environment.
        console.enter_virtual_environment(update_status)

        return

    elif action == 'cancel':

        return

    elif action == 'copy-into-terminal':

        return

    elif action == 'next':

        # Attempt to enter the virtual environment.
        console.enter_virtual_environment(update_status)

        # Update the release description.
        update_release_descriptions()

        return

    elif action == 'next-terminal':

        # Attempt to enter the virtual environment.
        console.enter_virtual_environment(update_status)

        # Update the release description.
        update_release_descriptions()

        return

    else:

        return 'unknown'


def update_release_descriptions():

    # logger.log_label('Update the release descriptions')

    description = '%s customized using Cubic on %s' % (model.custom.iso_volume_id, model.project.modify_date)

    file_path = os.path.join(model.project.custom_root_directory, 'etc', 'lsb-release')
    update_release_description(file_path, 'DISTRIB_DESCRIPTION', description)

    file_path = os.path.join(model.project.custom_root_directory, 'etc', 'os-release')
    update_release_description(file_path, 'PRETTY_NAME', description)

    file_path = os.path.join(model.project.custom_root_directory, 'usr', 'lib', 'os-release')
    update_release_description(file_path, 'PRETTY_NAME', description)


def update_release_description(file_path, key, value):

    logger.log_label('Update the release description')

    if not os.path.isfile(file_path):
        logger.log_value('The release description file does not exist', file_path)
    elif os.path.islink(file_path):
        logger.log_value('The release description file is is a symlink', file_path)
    else:
        logger.log_value('The release description file is', file_path)
        try:
            with open(file_path, 'r') as file:
                lines = file.read()
                match = re.search(r'%s=(.*)' % key, lines)
                if match:
                    logger.log_value('The current release description is', match.group(1))
                if model.update_release_description:
                    is_update_required = True
                    logger.log_value('Update the release description?', 'Yes')
                elif match and 'customized using Cubic on' in match.group(1):
                    is_update_required = True
                    logger.log_value('Update the release description?', 'Yes. The release description is automatically updated')
                else:
                    is_update_required = False
                    logger.log_value('Update the release description?', 'No. Keep custom release description')
                if is_update_required:
                    logger.log_value('The new release description is', value)
                    search_text = '%s.*' % key
                    replace_text = '%s=%s' % (key, value)
                    program = os.path.join(model.application.directory, 'commands', 'replace-text')
                    command = 'pkexec "%s" "%s" "%s" "%s"' % (program, search_text, replace_text, file_path)
                    result, exit_status, signal_status = execute_synchronous(command)
                    logger.log_value('The result is', result)
                    logger.log_value('The exit status, signal status is', '%s, %s' % (exit_status, signal_status))
        except Exception as exception:
            logger.log_value('Error. The release description could not be updated due to', exception)


def leave(action, new_page=None):

    if action == 'back':

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        displayer.set_visible('terminal_page__copy_header_bar_button', False)

        # The terminal continues running whenever the application
        # navigates away from the Terminal page, so the pseudo terminal
        # process must be explicitly killed.
        console.exit_virtual_environment()

        time.sleep(SLEEP_0250_MS)

        return

    elif action == 'copy-into-terminal':

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        displayer.set_visible('terminal_page__copy_header_bar_button', False)

        return

    elif action == 'next':

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        displayer.set_visible('terminal_page__copy_header_bar_button', False)

        # The terminal continues running whenever the application
        # navigates away from the Terminal page, so the pseudo terminal
        # process must be explicitly killed.
        console.exit_virtual_environment()

        time.sleep(SLEEP_0250_MS)

    elif action == 'quit':

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        displayer.set_visible('terminal_page__copy_header_bar_button', False)

        # The terminal continues running whenever the application
        # navigates away from the Terminal page, so the pseudo terminal
        # process must be explicitly killed.
        console.exit_virtual_environment()

        iso_utilities.unmount_iso_and_delete_mount_point(model.project.iso_mount_point)

        return

    else:

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        displayer.set_visible('terminal_page__copy_header_bar_button', False)

        # The terminal continues running whenever the application
        # navigates away from the Terminal page, so the pseudo terminal
        # process must be explicitly killed.
        console.exit_virtual_environment()

        iso_utilities.unmount_iso_and_delete_mount_point(model.project.iso_mount_point)

        return 'unknown'


########################################################################
# File Chooser Functions
########################################################################


def selected_uris(uris):

    model.selected_uris = uris
    logger.log_value('The selected uris are', model.selected_uris)

    model.current_directory = console.get_current_directory()
    logger.log_value('The current directory is', model.current_directory)

    # Go to the copy page.

    # The pseudo terminal process is not registered with the
    # processor module. As a result, the terminal's process
    # is not terminated by the interrupt_navigation_thread() function
    # of the navigator module. This allows the terminal to continue
    # running while the application navigates away from the terminal
    # page. The pseudo terminal process must be explicitly killed by
    # executing the exit_virtual_environment() function of the
    # console module.
    handle_navigation('copy-into-terminal')


########################################################################
# Handler Functions
########################################################################


# TODO: This function is not used.
def on_terminal_page__terminal_child_exited(*args):
    """
    This function is not used.
    """

    logger.log_title('On terminal page terminal child exited')
    logger.log_value('The arcuments are', args)
    for arg in args:
        logger.log_value('The argument is', arg)


def on_clicked__terminal_page__copy_header_bar_button(widget):

    logger.log_title('Clicked terminal page copy button')

    copy_file_chooser.open(selected_uris)


def on_drag_data_received__terminal_page(widget, drag_context, x, y, data, info, drag_time):

    # Skip if terminal is not running.
    if not is_running: return

    logger.log_value('Drag data received for', 'terminal_page')

    # Gtk.SelectionData
    # https://lazka.github.io/pgi-docs/#Gtk-3.0/classes/SelectionData.html

    # The data type is....................... text/uri-list
    # The data type is....................... text/plain
    atom = data.get_data_type()
    data_type = str(atom)
    logger.log_value('The data type is', data_type)

    text = data.get_text()

    if text is not None:
        console.send_text_to_terminal(text)
    else:
        model.selected_uris = data.get_uris()
        logger.log_value('The selected uris are', model.selected_uris)

        model.current_directory = console.get_current_directory()
        logger.log_value('The current directory is', model.current_directory)

        # Go to the copy page.

        # The pseudo terminal process is not registered with the
        # processor module. As a result, the terminal's process
        # is not terminated by the interrupt_navigation_thread() function
        # of the navigator module. This allows the terminal to continue
        # running while the application navigates away from the terminal
        # page. The pseudo terminal process must be explicitly killed by
        # executing the exit_virtual_environment() function of the
        # console module.
        handle_navigation('copy-into-terminal')


def on_button_press_event__terminal_page(widget, event):

    if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:

        logger.log_value('Mouse button 3 pressed for', 'terminal_page')

        terminal = model.builder.get_object('terminal_page__terminal')
        terminal_has_selection = terminal.get_has_selection()

        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

        # Menu Item 1: Select Text
        displayer.set_sensitive('terminal_page__select_all_menu_item', True)

        # Menu Item 2: Copy Test
        if (terminal_has_selection):
            displayer.set_sensitive('terminal_page__copy_text_menu_item', True)
        else:
            displayer.set_sensitive('terminal_page__copy_text_menu_item', False)

        # Menu Item 3: Paste Text
        clipboard_has_text = clipboard.wait_is_text_available()
        if (is_running and clipboard_has_text and not terminal_has_selection):
            displayer.set_sensitive('terminal_page__paste_text_menu_item', True)
        else:
            displayer.set_sensitive('terminal_page__paste_text_menu_item', False)

        # Menu Item 4: Paste Files
        clipboard_has_uris = clipboard.wait_is_uris_available()
        if (is_running and clipboard_has_uris and not terminal_has_selection):
            count = len(clipboard.wait_for_uris())
            label = 'Paste File' if count == 1 else 'Paste %s Files' % count
            displayer.update_menu_item('terminal_page__paste_file_menu_item', label)
            displayer.set_sensitive('terminal_page__paste_file_menu_item', True)
        else:
            label = 'Paste File(s)'
            displayer.update_menu_item('terminal_page__paste_file_menu_item', label)
            displayer.set_sensitive('terminal_page__paste_file_menu_item', False)

        menu = model.builder.get_object('terminal_page__menu')
        menu.popup(None, None, None, None, event.button, event.time)


def on_button_release_event__terminal_page__copy_text_menu_item(*args):

    terminal = model.builder.get_object('terminal_page__terminal')
    terminal.copy_clipboard()

    # TODO: Remove Vte 2.90.

    # https://lazka.github.io/pgi-docs/#Vte-2.90/classes/Terminal.html
    # https://lazka.github.io/pgi-docs/#Vte-2.91/classes/Terminal.html
    try:
        terminal.unselect_all
    except AttributeError:
        # Vte 2.90 only...
        # Ubuntu 14.04 uses libvte-2.90
        terminal.select_none()
    else:
        # Vte 2.91 only...
        # Ubuntu 15.04 uses libvte-2.91
        terminal.unselect_all()


def on_button_release_event__terminal_page__paste_file_menu_item(*args):

    clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
    model.selected_uris = clipboard.wait_for_uris()

    # Go to the copy page.

    # The pseudo terminal process is not registered with the
    # processor module. As a result, the terminal's process
    # is not terminated by the interrupt_navigation_thread() function
    # of the navigator module. This allows the terminal to continue
    # running while the application navigates away from the terminal
    # page. The pseudo terminal process must be explicitly killed by
    # executing the exit_virtual_environment() function of the
    # console module.

    handle_navigation('copy-into-terminal')


def on_button_release_event__terminal_page__paste_text_menu_item(*args):

    terminal = model.builder.get_object('terminal_page__terminal')
    terminal.paste_clipboard()


def on_button_release_event__terminal_page__select_all_menu_item(*args):

    terminal = model.builder.get_object('terminal_page__terminal')
    terminal.select_all()


########################################################################
# Support Functions
########################################################################


def update_status(status):
    """
    A callback function supplied by the client in order to be notified
    whenever the virtual environment starts or exits. This function must
    take a boolean status as the only argument. The function
    terminal.watch_child(process_id) is not used because it only sends a
    child-exited signal when the pseudo terminal exits, but it does not
    notify when the virtual environment has started successfully.
    """

    # Save the status so it can be used by the navigation actions.
    global is_running
    is_running = status

    # Reset buttons based on status.
    displayer.reset_buttons(is_back_sensitive=True, is_next_sensitive=status)
    displayer.set_sensitive('terminal_page__copy_header_bar_button', status)

    # Display the status.
    if status:
        message = 'You are in the virtual environment.'
        displayer.update_status_image('terminal_page__status', displayer.OK)
        displayer.update_label('terminal_page__status_label', message)
        displayer.update_label('terminal_page__kernel_version_label', 'kernel ' + model.application.kernel_version)
    else:
        message = 'You are not in the virtual environment.'
        displayer.update_status_image('terminal_page__status', displayer.ERROR)
        displayer.update_label('terminal_page__status_label', message)
        displayer.update_label('terminal_page__kernel_version_label', '')

    logger.log_value('Virtual environment status message', message)
