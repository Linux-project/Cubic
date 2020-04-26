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

import navigation

from utilities import display
from file_choosers import copy_file_chooser
from utilities import file_utilities
from utilities import iso_utilities
from utilities import logger
from utilities import model
from utilities import terminal_utilities

import gi
gi.require_version('Gdk', '3.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gdk
from gi.repository import Gtk

########################################################################
# Globals & Constants
########################################################################

name = 'terminal_page'

# Indicates if the virtual environment is running.
is_running = False

########################################################################
# Navigation Functions
########################################################################


def setup(action, old_page=None):

    if action == 'back':

        # The virtual environment will be started in enter().

        display.reset_buttons(
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

        display.set_visible('terminal_page__copy_button', True)
        display.set_sensitive('terminal_page__copy_button', False)

        return

    if action == 'cancel':

        # Do not assume the virtual environment is running.

        display.reset_buttons(
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

        display.set_visible('terminal_page__copy_button', True)
        display.set_sensitive('terminal_page__copy_button', is_running)

        return

    if action == 'copy':

        # Do not assume the virtual environment is running.

        display.reset_buttons(
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

        display.set_visible('terminal_page__copy_button', True)
        display.set_sensitive('terminal_page__copy_button', is_running)

        return

    elif action == 'next':

        # The virtual environment will be started in enter().

        display.reset_buttons(
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

        display.set_visible('terminal_page__copy_button', True)
        display.set_sensitive('terminal_page__copy_button', False)

        return

    elif action == 'next_terminal_page':

        # The virtual environment will be started in enter().

        display.reset_buttons(
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

        display.set_visible('terminal_page__copy_button', True)
        display.set_sensitive('terminal_page__copy_button', False)

        return

    else:

        return 'unknown'


def enter(action, old_page=None):

    if action == 'back':

        # Attempt to enter the virtual environment.
        terminal_utilities.enter_virtual_environment(update_status)

        return

    elif action == 'cancel':

        return

    elif action == 'copy':

        return

    elif action == 'next':

        # Attempt to enter the virtual environment.
        terminal_utilities.enter_virtual_environment(update_status)

        return

    elif action == 'next_terminal_page':

        # Attempt to enter the virtual environment.
        terminal_utilities.enter_virtual_environment(update_status)

        return

    else:

        return 'unknown'


def leave(action, new_page=None):

    if action == 'back':

        display.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        display.set_visible('terminal_page__copy_button', False)

        # The terminal continues running whenever the application
        # navigates away from the terminal page, so the pseudo terminal
        # process must be explicitly killed.
        terminal_utilities.exit_virtual_environment()

        return

    elif action == 'copy':

        display.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        display.set_visible('terminal_page__copy_button', False)

        return

    elif action == 'next':

        display.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        display.set_visible('terminal_page__copy_button', False)

        # The terminal continues running whenever the application
        # navigates away from the terminal page, so the pseudo terminal
        # process must be explicitly killed.
        terminal_utilities.exit_virtual_environment()

    elif action == 'quit':

        display.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        display.set_visible('terminal_page__copy_button', False)

        # The terminal continues running whenever the application
        # navigates away from the terminal page, so the pseudo terminal
        # process must be explicitly killed.
        terminal_utilities.exit_virtual_environment()

        return

    else:

        return 'unknown'


########################################################################
# File Chooser Functions
########################################################################


def selected_filepaths(filepaths):

    logger.log_value('Selected filepaths', filepaths)

    model.uris = filepaths

    # Go to the copy page.

    # The pseudo terminal process is not registered with the
    # process_utilities module. As a result, the terminal's process
    # is not terminated by the interrupt_navigation_thread() function
    # of the navigation module. This allows the terminal to continue
    # running while the application navigates away from the terminal
    # page. The pseudo terminal process must be explicitly killed by
    # executing the exit_virtual_environment() function of the
    # terminal_utilities module.
    navigation.handle_navigation('copy')


########################################################################
# Handler Functions
########################################################################


# TODO: This function is not used.
def on_terminal_page__terminal_child_exited(*args):
    """
    This function is not used.
    """

    print('on_terminal_page__terminal_child_exited')
    print('ARGS:', args)
    for arg in args:
        print('ARG: %s' % arg)


def on_clicked__terminal_page__copy_button(widget):

    logger.log_title('Clicked terminal page copy button')

    copy_file_chooser.open(selected_filepaths)


def on_drag_data_received__terminal_page(widget, drag_context, x, y, data, info, drag_time):

    # Skip if terminal is not running.
    if is_running:
        return

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
        terminal_utilities.send_text_to_terminal(text)
    else:
        model.uris = data.get_uris()

        # Go to the copy page.

        # The pseudo terminal process is not registered with the
        # process_utilities module. As a result, the terminal's process
        # is not terminated by the interrupt_navigation_thread() function
        # of the navigation module. This allows the terminal to continue
        # running while the application navigates away from the terminal
        # page. The pseudo terminal process must be explicitly killed by
        # executing the exit_virtual_environment() function of the
        # terminal_utilities module.
        navigation.handle_navigation('copy')


def on_button_press_event__terminal_page(widget, event):

    print('on_button_press_event__terminal_page')

    if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:

        logger.log_value('Mouse button 3 pressed for', 'terminal_page')

        terminal = model.builder.get_object('terminal_page__terminal')
        terminal_has_selection = terminal.get_has_selection()

        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

        # Menu Item 1: Select Text
        display.set_sensitive('terminal_page__select_all_menu_item', True)

        # Menu Item 2: Copy Test
        if (terminal_has_selection):
            display.set_sensitive('terminal_page__copy_text_menu_item', True)
        else:
            display.set_sensitive('terminal_page__copy_text_menu_item', False)

        # Menu Item 3: Paste Text
        clipboard_has_text = clipboard.wait_is_text_available()
        if (is_running and clipboard_has_text and not terminal_has_selection):
            display.set_sensitive('terminal_page__paste_text_menu_item', True)
        else:
            display.set_sensitive('terminal_page__paste_text_menu_item', False)

        # Menu Item 4: Paste Files
        clipboard_has_uris = clipboard.wait_is_uris_available()
        if (is_running and clipboard_has_uris and not terminal_has_selection):
            count = len(clipboard.wait_for_uris())
            label = 'Paste File' if count == 1 else 'Paste %s Files' % count
            display.update_menu_item('terminal_page__paste_file_menu_item', label)
            display.set_sensitive('terminal_page__paste_file_menu_item', True)
        else:
            label = 'Paste File(s)'
            display.update_menu_item('terminal_page__paste_file_menu_item', label)
            display.set_sensitive('terminal_page__paste_file_menu_item', False)

        menu = model.builder.get_object('terminal_page__menu')
        menu.popup(None, None, None, None, event.button, event.time)


def on_button_release_event__terminal_page__copy_text_menu_item(*args):

    print('on_button_release_event__terminal_page__copy_text_menu_item')

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

    print('on_button_release_event__terminal_page__paste_file_menu_item')

    clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
    model.uris = clipboard.wait_for_uris()

    # Go to the copy page.

    # The pseudo terminal process is not registered with the
    # process_utilities module. As a result, the terminal's process is
    # not terminated by the interrupt_navigation_thread() function of the
    # navigation module. This allows the terminal to continue running
    # while the application navigates away from the terminal page. The
    # pseudo terminal process must be explicitly killed by executing the
    # exit_virtual_environment() function of the terminal_utilities
    # module.
    navigation.handle_navigation('copy')


def on_button_release_event__terminal_page__paste_text_menu_item(*args):

    print('on_button_release_event__terminal_page__paste_text_menu_item')

    terminal = model.builder.get_object('terminal_page__terminal')
    terminal.paste_clipboard()


def on_button_release_event__terminal_page__select_all_menu_item(*args):

    print('on_button_release_event__terminal_page__select_all_menu_item')

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
    display.reset_buttons(is_back_sensitive=True, is_next_sensitive=status)
    display.set_sensitive('terminal_page__copy_button', status)

    # Display the status.
    if status:
        message = 'You are in the virtual environment.'
        display.update_status_image('terminal_page__status', display.OK)
        display.update_label('terminal_page__status_label', message)
        display.update_label('terminal_page__kernel_version_label', 'kernel ' + model.application.kernel_version)
    else:
        message = 'You are not in the virtual environment.'
        display.update_status_image('terminal_page__status', display.ERROR)
        display.update_label('terminal_page__status_label', message)
        display.update_label('terminal_page__kernel_version_label', '')

    logger.log_value('Notify virtual environment status message', message)
