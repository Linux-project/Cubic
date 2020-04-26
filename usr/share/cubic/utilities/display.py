#!/usr/bin/python3

########################################################################
#                                                                      #
# display.py                                                           #
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

from constants import OK, ERROR, OPTIONAL, BULLET, PROCESSING, BLANK
from constants import LIGHT_ICON_DIRECTORY, DARK_ICON_DIRECTORY
from utilities import logger
from utilities import model

import gi

gi.require_version('GLib', '2.0')
from gi.repository import GLib

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

try:
    gi.require_version('GtkSource', '4')
    logger.log_value('Using GtkSource version', '4')
except ValueError:
    gi.require_version('GtkSource', '3.0')
    logger.log_value('Using GtkSource version', '3.0')
from gi.repository import GtkSource

import os

########################################################################
# Constants
########################################################################

# Icons corresponding to status
icons = ['cubic-ok', 'cubic-error', 'cubic-optional', 'cubic-bullet', 'cubic-blank', 'cubic-blank']

########################################################################
# Functions
########################################################################


def idle_add(callback):

    GLib.idle_add(callback)


def connect_handler(connect_handler_callback):

    GLib.idle_add(connect_handler_callback)


def disconnect_handler(disconnect_handler_callback):

    GLib.idle_add(disconnect_handler_callback)


def get_icon_search_path():

    icon_theme = Gtk.IconTheme.get_default()
    icon_search_path = icon_theme.get_search_path()

    print('-----------------------------------------------------------')
    logger.log_value('The icon search path is', icon_search_path)
    print('-----------------------------------------------------------')

    return icon_search_path


def get_theme_variant(window):

    style_context = window.get_style_context()

    # Foreground

    foreground_red = style_context.get_color(Gtk.StateFlags.NORMAL).red
    foreground_green = style_context.get_color(Gtk.StateFlags.NORMAL).green
    foreground_blue = style_context.get_color(Gtk.StateFlags.NORMAL).blue

    # logger.log_value('foreground_red', foreground_red)
    # logger.log_value('foreground_green', foreground_green)
    # logger.log_value('foreground_blue', foreground_blue)

    foreground_average = (foreground_red + foreground_green + foreground_blue) / 256
    # logger.log_value('The average foreground color is', foreground_average)

    # Background

    background_red = style_context.get_background_color(Gtk.StateFlags.NORMAL).red
    background_green = style_context.get_background_color(Gtk.StateFlags.NORMAL).green
    background_blue = style_context.get_background_color(Gtk.StateFlags.NORMAL).blue

    # logger.log_value('background_red', background_red)
    # logger.log_value('background_green', background_green)
    # logger.log_value('background_blue', background_blue)

    background_average = (background_red + background_green + background_blue) / 256
    # logger.log_value('The average background color is', background_average)

    theme_variant = 'unknown'
    if (foreground_average > background_average):
        theme_variant = 'dark'
    else:
        theme_variant = 'light'

    return theme_variant


def update_icon_search_paths(theme_variant):

    # logger.log_value('Set the icon search paths for theme variant', theme_variant)

    light_icon_path = os.path.join(model.application.directory, LIGHT_ICON_DIRECTORY)
    dark_icon_path = os.path.join(model.application.directory, DARK_ICON_DIRECTORY)

    icon_theme = Gtk.IconTheme.get_default()
    search_paths = icon_theme.get_search_path()
    if theme_variant == 'light':
        if dark_icon_path in search_paths:
            logger.log_value('Remove the icon search path for', 'dark theme')
            search_paths.remove(dark_icon_path)
        if light_icon_path not in search_paths:
            logger.log_value('Add the icon search path for', 'light theme')
            search_paths.append(light_icon_path)
        GLib.idle_add(Gtk.IconTheme.set_search_path, icon_theme, search_paths)
        logger.log_value('The new icon search paths are', search_paths)
    elif theme_variant == 'dark':
        if light_icon_path in search_paths:
            logger.log_value('Remove the icon search path for', 'light theme')
            search_paths.remove(light_icon_path)
        if dark_icon_path not in search_paths:
            logger.log_value('Add the icon search path for', 'dark theme')
            search_paths.append(dark_icon_path)
        GLib.idle_add(Gtk.IconTheme.set_search_path, icon_theme, search_paths)
        logger.log_value('The new icon search paths are', search_paths)
    else:
        logger.log_value('Error. the theme variant is not supported', theme_variant)
        logger.log_value('The current icon search paths are', search_paths)


def reset_icon_search_paths():

    logger.log_label('Reset the icon search paths')

    light_icon_path = os.path.join(model.application.directory, LIGHT_ICON_DIRECTORY)
    dark_icon_path = os.path.join(model.application.directory, DARK_ICON_DIRECTORY)

    icon_theme = Gtk.IconTheme.get_default()
    search_paths = icon_theme.get_search_path()

    if light_icon_path in search_paths:
        logger.log_value('Remove the icon search path for', 'light theme')
        search_paths.remove(light_icon_path)

    if dark_icon_path in search_paths:
        logger.log_value('Remove the icon search path for', 'dark theme')
        search_paths.remove(dark_icon_path)

    GLib.idle_add(Gtk.IconTheme.set_search_path, icon_theme, search_paths)
    logger.log_value('The new icon search paths are', search_paths)


def print_icon_theme_search_path():
    icon_theme = Gtk.IconTheme.get_default()
    icon_theme_search_path = icon_theme.get_search_path()
    logger.log_value('The icon theme search path is', icon_theme_search_path)


def set_column_visible(widget_name, is_visible):
    widget = model.builder.get_object(widget_name)
    GLib.idle_add(Gtk.TreeViewColumn.set_visible, widget, is_visible)


def show(widget_name):
    widget = model.builder.get_object(widget_name)
    GLib.idle_add(Gtk.Widget.show, widget)


def hide(widget_name):
    widget = model.builder.get_object(widget_name)
    GLib.idle_add(Gtk.Widget.hide, widget)


# def hide_on_delete(widget_name):
#     widget = model.builder.get_object(widget_name)
#     GLib.idle_add(Gtk.Widget.hide_on_delete, widget)


def show_all(widget_name):
    widget = model.builder.get_object(widget_name)
    GLib.idle_add(Gtk.Widget.show_all, widget)


def set_visible(widget_name, is_visible):
    widget = model.builder.get_object(widget_name)
    GLib.idle_add(Gtk.Widget.set_visible, widget, is_visible)


def set_solid(widget_name, is_solid):
    print('SET SOLID %s %s' % (widget_name, is_solid))
    widget = model.builder.get_object(widget_name)
    GLib.idle_add(Gtk.Widget.set_opacity, widget, is_solid)
    # GLib.idle_add(Gtk.Widget.set_sensitive, widget, is_solid)


def set_sensitive(widget_name, is_sensitive):
    widget = model.builder.get_object(widget_name)
    GLib.idle_add(Gtk.Widget.set_sensitive, widget, is_sensitive)


def set_entry_error(widget_name, is_error):
    # logger.log_value('Set error for entry %s' % widget_name, is_error)
    entry = model.builder.get_object(widget_name)
    context = entry.get_style_context()
    if is_error:
        GLib.idle_add(Gtk.StyleContext.add_class, context, 'error')
    else:
        GLib.idle_add(Gtk.StyleContext.remove_class, context, 'error')


'''
def set_label_error(widget_name, is_error):
    # logger.log_value('Set name property to error is "%s" for label' % is_error, widget_name)
    label = model.builder.get_object(widget_name)
    name = label.get_name()
    # logger.log_value('The current name for the label is', name)
    if is_error:
        if name == 'normal':
            label.set_name('error')
            # GLib.idle_add(Gtk.Label.set_name, label, 'error')
        elif name == 'error':
            pass
        elif name == 'non-editable':
            label.set_name('non-editable-error')
            # GLib.idle_add(Gtk.Label.set_name, label, 'non-editable-error')
        elif name == 'non-editable-error':
            pass
        elif name == 'automatic':
            label.set_name('automatic-error')
            # GLib.idle_add(Gtk.Label.set_name, label, 'automatic-error')
        elif name == 'automatic-error':
            pass
        elif name == 'automatic-non-editable':
            label.set_name('automatic-non-editable-error')
            # GLib.idle_add(Gtk.Label.set_name, label, 'automatic-non-editable-error')
        elif name == 'automatic-non-editable-error':
            pass
        else:
            label.set_name('error')
            logger.log_value('Unable to set name property to indicate error is "%s" for label' % is_error, widget_name)
            logger.log_value('The previous name for the label was', name)
            logger.log_value('The new name for the label is', label.get_name())
    else:
        if name == 'normal':
            pass
        elif name == 'error':
            label.set_name('normal')
            # GLib.idle_add(Gtk.Label.set_name, label, 'normal')
        elif name == 'non-editable':
            pass
        elif name == 'non-editable-error':
            label.set_name('non-editable')
            # GLib.idle_add(Gtk.Label.set_name, label, 'non-editable')
        elif name == 'automatic':
            pass
        elif name == 'automatic-error':
            label.set_name('automatic')
            # GLib.idle_add(Gtk.Label.set_name, label, 'automatic')
        elif name == 'automatic-non-editable':
            pass
        elif name == 'automatic-non-editable-error':
            label.set_name('automatic-non-editable')
            # GLib.idle_add(Gtk.Label.set_name, label, 'automatic-non-editable')
        else:
            label.set_name('normal')
            logger.log_value('Unable to set name property to indicate error is "%s" for label' % is_error, widget_name)
            logger.log_value('The previous name for the label was', name)
            logger.log_value('The new name for the label is', label.get_name())
    # logger.log_value('The new name for the label is', label.get_name())
'''


def set_entry_editable(widget_name, is_editable):
    # logger.log_value('Set name property to editable is "%s" for entry' % is_editable, widget_name)
    entry = model.builder.get_object(widget_name)
    # entry.set_editable(is_editable)
    GLib.idle_add(Gtk.Entry.set_editable, entry, is_editable)


def show_spinner():
    grid = model.builder.get_object('pages')
    GLib.idle_add(Gtk.Grid.set_sensitive, grid, False)

    spinner = model.builder.get_object('window_spinner')
    GLib.idle_add(Gtk.Spinner.start, spinner)
    GLib.idle_add(Gtk.Spinner.set_visible, spinner, True)


def hide_spinner():
    spinner = model.builder.get_object('window_spinner')
    GLib.idle_add(Gtk.Spinner.set_visible, spinner, False)
    GLib.idle_add(Gtk.Spinner.stop, spinner)

    grid = model.builder.get_object('pages')
    GLib.idle_add(Gtk.Grid.set_sensitive, grid, True)


def update_label(label_name, text):
    # logger.log_value('Update label %s' % label_name, text)
    label = model.builder.get_object(label_name)
    GLib.idle_add(Gtk.Label.set_text, label, text)


def update_entry(entry_name, text):
    # logger.log_value('Update entry %s' % entry_name, text)
    entry = model.builder.get_object(entry_name)
    # entry.set_text(text)
    # GLib.idle_add(Gtk.Entry.set_text, entry, text, priority=GLib.PRIORITY_HIGH)
    GLib.idle_add(Gtk.Entry.set_text, entry, text)


def update_menu_item(menu_item_name, text):
    menu_item = model.builder.get_object(menu_item_name)
    GLib.idle_add(Gtk.MenuItem.set_label, menu_item, text)


def update_progressbar_percent(progressbar_name, percent):
    progressbar = model.builder.get_object(progressbar_name)
    GLib.idle_add(Gtk.ProgressBar.set_fraction, progressbar, float(percent) / 100.0)


def update_progressbar_text(progressbar_name, text):
    progressbar = model.builder.get_object(progressbar_name)
    GLib.idle_add(Gtk.ProgressBar.set_text, progressbar, text)


def activate_toggle_button(toggle_button_name, is_active):
    toggle_button = model.builder.get_object(toggle_button_name)
    GLib.idle_add(Gtk.ToggleButton.set_active, toggle_button, is_active)


def activate_radio_button(radio_button_name, is_active):
    radio_button = model.builder.get_object(radio_button_name)
    GLib.idle_add(Gtk.RadioButton.set_active, radio_button, is_active)


def activate_check_button(check_button_name, is_active):
    check_button = model.builder.get_object(check_button_name)
    GLib.idle_add(Gtk.CheckButton.set_active, check_button, is_active)


def insert_box_label(box_name, text, opacity):
    # Since label is not displayed, there is no need to call GLib.idle_add().
    label = Gtk.Label(text)
    label.set_halign(Gtk.Align.START)
    label.set_visible(True)
    label.set_opacity(opacity)

    box = model.builder.get_object(box_name)
    GLib.idle_add(Gtk.Box.add, box, label)


def scroll_view_port_to_bottom(view_port_name):
    view_port = model.builder.get_object(view_port_name)
    adjustment = view_port.get_vadjustment()
    amount = adjustment.get_upper() - adjustment.get_page_size()
    GLib.idle_add(Gtk.Adjustment.set_value, adjustment, amount)


def empty_box(box_name):
    box = model.builder.get_object(box_name)
    for child in box.get_children():
        if isinstance(child, Gtk.Label):
            logger.log_value('Removing label', child.get_text())
        elif isinstance(child, Gtk.Button):
            logger.log_value('Removing button', child.get_label())
        else:
            logger.log_value('Removing unknown type', child)
        GLib.idle_add(Gtk.Box.remove, box, child)
        GLib.idle_add(Gtk.Widget.destroy, child)


def insert_listbox_row_label(listbox_name, row_number, text, additional_height=0):
    # Since label is not displayed, there is no need to call GLib.idle_add().
    label = Gtk.Label(text)
    label.set_halign(Gtk.Align.START)
    label.set_visible(True)
    preferred_height = label.get_preferred_height()[0]
    label.set_size_request(-1, preferred_height + additional_height)

    listbox = model.builder.get_object(listbox_name)
    GLib.idle_add(Gtk.ListBox.insert, listbox, label, row_number)


def insert_listbox_row_check_button(listbox_name, row_number, text, is_active, additional_height=0):
    # Since check button is not displayed, there is no need to call GLib.idle_add().
    check_button = Gtk.check_button(text)
    check_button.set_halign(Gtk.Align.START)
    check_button.set_visible(True)
    check_button.set_active(is_active)
    preferred_height = check_button.get_preferred_height()[0]
    check_button.set_size_request(-1, preferred_height + additional_height)

    listbox = model.builder.get_object(listbox_name)
    GLib.idle_add(Gtk.ListBox.insert, listbox, check_button, row_number)


def get_listbox_row_count(listbox_name):
    listbox = model.builder.get_object(listbox_name)
    return len(listbox.get_children())


def get_listbox_row_widget(listbox_name, row_number):
    listbox = model.builder.get_object(listbox_name)
    listbox_row = listbox.get_row_at_index(row_number)

    child = listbox_row.get_children()[0]

    return child


def scroll_to_tree_view_row(tree_view_name, row_number):

    tree_view = model.builder.get_object(tree_view_name)
    tree_path = Gtk.TreePath.new_from_string('%s' % row_number)
    GLib.idle_add(Gtk.TreeView.scroll_to_cell, tree_view, tree_path, None, True, 0.5, 0.0)


def select_tree_view_row(tree_view_name, row_number):

    tree_view = model.builder.get_object(tree_view_name)
    tree_path = Gtk.TreePath.new_from_string('%s' % row_number)
    GLib.idle_add(Gtk.TreeView.set_cursor, tree_view, tree_path, None, False)


# TODO: This function is not used.
def select_listbox_row(listbox_name, row_number):
    listbox = model.builder.get_object(listbox_name)
    listbox_row = listbox.get_row_at_index(row_number)

    GLib.idle_add(Gtk.ListBox.select_row, listbox, listbox_row)


def update_listbox_row_label(listbox_name, row_number, text):
    listbox = model.builder.get_object(listbox_name)
    listbox_row = listbox.get_row_at_index(row_number)
    label = listbox_row.get_children()[0]

    GLib.idle_add(Gtk.Label.set_text, label, text)


def empty_listbox(listbox_name):
    listbox = model.builder.get_object(listbox_name)
    for listbox_row in listbox.get_children():
        child = listbox_row.get_children()[0]
        if isinstance(child, Gtk.Label):
            logger.log_value('Removing label', child.get_text())
        elif isinstance(child, Gtk.Button):
            logger.log_value('Removing button', child.get_label())
        else:
            logger.log_value('Removing unknown type', child)
        GLib.idle_add(Gtk.ListBox.remove, listbox, listbox_row)
        GLib.idle_add(Gtk.Widget.destroy, listbox_row)


def update_liststore(liststore_name, data_list):
    liststore = model.builder.get_object(liststore_name)
    GLib.idle_add(_update_liststore_rows, liststore, data_list)


# This function is invoked using GLib.idle_add.
def _update_liststore_rows(liststore, data_list):
    liststore.clear()
    for number, data in enumerate(data_list):
        # logger.log_value('%i. Adding an item to the list' % (number+1), data)
        liststore.append(data)


def update_liststore_progressbar_percent(liststore_name, path, percent):
    liststore = model.builder.get_object(liststore_name)
    GLib.idle_add(_update_liststore_progressbar_percent, liststore, path, percent)


# This function is invoked using GLib.idle_add.
def _update_liststore_progressbar_percent(liststore, path, percent):
    liststore[path][0] = percent


def update_status_image(name, status):

    image = model.builder.get_object(name)

    # TODO: Use Gtk.Icontheme instead of Gtk.IconSize because Gtk.IconSize id deprecated.
    #       https://lazka.github.io/pgi-docs/Gtk-3.0/enums.html#Gtk.IconSize
    GLib.idle_add(Gtk.Image.set_from_icon_name, image, icons[status], Gtk.IconSize.BUTTON)


def update_status(prefix, status):
    """
    The proper naming convention must be used.
    Object ids must end in '_status' or '_spinner'.
    Object ids ending in '_status' are always images in the *.ui file.
    Object ids ending in '_spinner' are always spinners in the *.ui file.
    """

    # logger.log_value('Set status for entry %s_status' % prefix, status)

    image = model.builder.get_object('%s_status' % prefix)

    # TODO: Use Gtk.Icontheme instead of Gtk.IconSize because Gtk.IconSize id deprecated.
    #       https://lazka.github.io/pgi-docs/Gtk-3.0/enums.html#Gtk.IconSize
    # GLib.idle_add(Gtk.Image.set_from_icon_name, image, icons[status], Gtk.IconSize.BUTTON)
    # GLib.idle_add(Gtk.Image.set_from_icon_name, image, icons[status], Gtk.IconSize.LARGE_TOOLBAR)
    GLib.idle_add(Gtk.Image.set_from_icon_name, image, icons[status], 0)

    # GLib.idle_add(Gtk.Image.set_opacity, image, False)

    spinner = model.builder.get_object('%s_spinner' % prefix)
    if spinner:
        if status == PROCESSING:
            GLib.idle_add(Gtk.Spinner.set_visible, spinner, True)
            # GLib.idle_add(Gtk.Spinner.set_opacity, spinner, True)
            GLib.idle_add(Gtk.Spinner.start, spinner)
        else:
            GLib.idle_add(Gtk.Spinner.set_visible, spinner, False)
            # GLib.idle_add(Gtk.Spinner.set_opacity, spinner, False)
            GLib.idle_add(Gtk.Spinner.stop, spinner)


# Button styles: text-button, suggested-action, destructive-action
def reset_buttons(
    back_button_label=None,
    back_action=None,
    back_button_style=None,
    is_back_sensitive=None,
    is_back_visible=None,
    next_button_label=None,
    next_action=None,
    next_button_style=None,
    is_next_sensitive=None,
    is_next_visible=None):

    # 25C1 = ◁
    # 25B7 = ▷
    #
    # 25C3 = ◃ Back
    # 25B9 = ▹ Next
    #
    # 261C = ☜ Back
    # 261E = ☞ Next
    #
    # 276C = ❬ Back
    # 276D = ❭ Next
    #
    # 21E6 = ⇦ Back
    # 21E8 = ⇨ Next
    #
    # 2190 = ← Back
    # 2192 = → Next

    # TODO: Set style for next button with default value?
    set_button('back_button', back_button_label, back_action, back_button_style, is_back_sensitive, is_back_visible)
    set_button('next_button', next_button_label, next_action, next_button_style, is_next_sensitive, is_next_visible)


def update_check_button_label(name, label):

    check_button = model.builder.get_object(name)
    GLib.idle_add(Gtk.CheckButton.set_label, check_button, label)


def set_button(name, label, action, style, is_sensitive, is_visible):
    """
    Update the label if it is not None.
    Update the action if it is not None.
    Update the style if it is not None.
    Update is_sensitive if it is not None.
    Update is_visible if it is not None.
    """

    button = model.builder.get_object(name)

    if is_visible is not None:
        GLib.idle_add(Gtk.Button.set_visible, button, is_visible)
    if action is not None:
        button.action = action
    if label is not None:
        GLib.idle_add(Gtk.Button.set_label, button, label)
    if style is not None:
        update_button_style(name, style)
    if is_sensitive is not None:
        GLib.idle_add(Gtk.Button.set_sensitive, button, is_sensitive)


def set_button_3(name, label, action, style, is_sensitive, is_visible):

    button = model.builder.get_object(name)
    GLib.idle_add(Gtk.Button.set_visible, button, is_visible)
    if action: button.action = action
    if label: GLib.idle_add(Gtk.Button.set_label, button, label)
    if style: update_button_style(name, style)
    GLib.idle_add(Gtk.Button.set_sensitive, button, is_sensitive)
    # if is_sensitive: button.set_state_flags(Gtk.StateFlags.NORMAL, True)


def set_button_2(name, label, action, style, is_sensitive, is_visible):

    button = model.builder.get_object(name)

    if label: GLib.idle_add(Gtk.Button.set_label, button, label)

    button.action = action

    if style: update_button_style(name, style)

    GLib.idle_add(Gtk.Button.set_sensitive, button, is_sensitive)

    GLib.idle_add(Gtk.Button.set_visible, button, is_visible)


def update_button_style(name, style):

    button = model.builder.get_object(name)
    context = button.get_style_context()

    if style != 'suggested-action':
        if context.has_class('suggested-action'):
            GLib.idle_add(Gtk.StyleContext.remove_class, context, 'suggested-action')
    elif style == 'suggested-action':
        if not context.has_class('suggested-action'):
            GLib.idle_add(Gtk.StyleContext.add_class, context, 'suggested-action')

    if style != 'destructive-action':
        if context.has_class('destructive-action'):
            GLib.idle_add(Gtk.StyleContext.remove_class, context, 'destructive-action')
    elif style == 'destructive-action':
        if not context.has_class('destructive-action'):
            GLib.idle_add(Gtk.StyleContext.add_class, context, 'destructive-action')

    # The default style, 'text-button', is never removed.
    # if style != 'text-button':
    #     if context.has_class('text-button'):
    #         GLib.idle_add(Gtk.StyleContext.remove_class, context, 'text-button')
    # elif style == 'text-button':
    #     if not context.has_class('text-button'):
    #         GLib.idle_add(Gtk.StyleContext.add_class, context, 'text-button')


def set_button_WORKING(name, label, action, style, is_sensitive, is_visible):

    button = model.builder.get_object(name)

    # Only change the label if a different label was supplied.
    if label and label != button.get_label():
        GLib.idle_add(Gtk.Button.set_label, button, label)

    # Only change the action if a different action was supplied.
    # if action and action != button.action:
    button.action = action

    # Only change the style if a different style was supplied.
    if style:
        update_button_style(name, style)

    # Only change the sensitivity if a different sensitivity was supplied.
    if is_sensitive != button.get_sensitive():
        GLib.idle_add(Gtk.Button.set_sensitive, button, is_sensitive)

    # Only change the visibility if a different visibility was supplied.
    if is_visible != button.get_visible():
        GLib.idle_add(Gtk.Button.set_visible, button, is_visible)


def update_button_style_WORKING(name, style):

    button = model.builder.get_object(name)
    context = button.get_style_context()

    if style != 'suggested-action':
        if context.has_class('suggested-action'):
            GLib.idle_add(Gtk.StyleContext.remove_class, context, 'suggested-action')
    elif style == 'suggested-action':
        if not context.has_class('suggested-action'):
            GLib.idle_add(Gtk.StyleContext.add_class, context, 'suggested-action')

    if style != 'destructive-action':
        if context.has_class('destructive-action'):
            GLib.idle_add(Gtk.StyleContext.remove_class, context, 'destructive-action')
    elif style == 'destructive-action':
        if not context.has_class('destructive-action'):
            GLib.idle_add(Gtk.StyleContext.add_class, context, 'destructive-action')

    # The default style, 'text-button', is never removed.
    # if style != 'text-button':
    #     if context.has_class('text-button'):
    #         GLib.idle_add(Gtk.StyleContext.remove_class, context, 'text-button')
    # elif style == 'text-button':
    #     if not context.has_class('text-button'):
    #         GLib.idle_add(Gtk.StyleContext.add_class, context, 'text-button')


def transition(old_page, new_page):

    if old_page != new_page:

        # Hide the current page.
        if old_page:
            logger.log_value('Hide old page', old_page.name.replace('_', ' '))
            grid = model.builder.get_object(old_page.name)
            GLib.idle_add(Gtk.Grid.set_visible, grid, False)

        # Show the next page
        if new_page:
            logger.log_value('Show new page', new_page.name.replace('_', ' '))
            grid = model.builder.get_object(new_page.name)
            GLib.idle_add(Gtk.Grid.set_visible, grid, True)

    else:

        # Stay on the current page.
        logger.log_value('Stay on page', old_page.name.replace('_', ' '))


def show_page(page):

    # Show the next page
    logger.log_value('Show new page', page.name.replace('_', ' '))
    grid = model.builder.get_object(page.name)
    GLib.idle_add(Gtk.Grid.set_visible, grid, True)


def add_to_stack(stack_name, filepaths, *search_replace_tuples):
    GLib.idle_add(_add_to_stack, stack_name, filepaths, *search_replace_tuples)


# This function is invoked using GLib.idle_add.
# The argument *search_replace_tuples is an optional list of tuples.
# Each tuple must contain a search_text and a replacement_text.
def _add_to_stack(stack_name, filepaths, *search_replace_tuples):

    stack = model.builder.get_object(stack_name)

    # TODO: Remove this line when 14.04 is no longer supported.
    # Bypass this functionality for Ubuntu 14.04.
    # Thsis is necessary because Gtk 3.10 in Ubuntu 14.04 does not support
    # Gtk.Stack or Gtk.StackSidebar.
    if not stack:
        return

    # Remove all items from the stack.
    logger.log_value('Remove all items from the stack', stack_name)
    scrolled_windows = stack.get_children()
    for scrolled_window in scrolled_windows:
        stack.remove(scrolled_window)

    # Prepate search settings.
    search_settings = GtkSource.SearchSettings()
    search_settings.set_regex_enabled(True)
    search_settings.set_wrap_around(True)

    # Add new items to the stack.
    logger.log_value('Add new items to stack', stack_name)
    for filepath in filepaths:

        title = '/%s' % os.path.relpath(filepath, model.project.custom_disk_directory)

        if os.path.exists(filepath):
            logger.log_value('Add %s from filepath' % title, filepath)

            # Create a new scrolled window.
            builder_temp = Gtk.Builder.new_from_file('scrolled_window.ui')
            scrolled_window = builder_temp.get_object('scrolled_window')

            # Get the source buffer.
            source_view = scrolled_window.get_child()
            source_buffer = source_view.get_buffer()

            # Read the file, and add it to the source buffer.
            with open(filepath, 'r') as file:
                data = file.read()
                source_buffer.set_text(data)

            # Add the new scrolled window to the stack.
            stack.add_titled(scrolled_window, filepath, title)

            # Optionally replace text.
            for search_replace_tuple in search_replace_tuples:
                search_text, replacement_text = search_replace_tuple
                logger.log_value('Search and replace', '%s ⊳ %s' % (search_text, replacement_text))
                search_settings.set_search_text(search_text)
                search_context = GtkSource.SearchContext.new(source_buffer, search_settings)
                replacement_count = search_context.replace_all(replacement_text, -1)
                logger.log_value('Number of matches', replacement_count)
        else:
            logger.log_value('Skip adding %s because the file does not exist' % title, filepath)


# This function blocks and does not use GLib.idle_add.
# The argument *search_replace_tuples is an optional list of tuples.
# Each tuple must contain a search_text and a replacement_text.
def replace_text_in_stack_buffer(stack_name, *search_replace_tuples):

    stack = model.builder.get_object(stack_name)

    # TODO: Remove this line when 14.04 is no longer supported.
    # Bypass this functionality for Ubuntu 14.04.
    # Thsis is necessary because Gtk 3.10 in Ubuntu 14.04 does not support
    # Gtk.Stack or Gtk.StackSidebar.
    if not stack:
        return

    logger.log_value('Searh and replace in stack', stack_name)

    # Prepate search settings.
    search_settings = GtkSource.SearchSettings()
    search_settings.set_regex_enabled(True)
    search_settings.set_wrap_around(True)

    scrolled_windows = stack.get_children()
    for scrolled_window in scrolled_windows:

        source_view = scrolled_window.get_child()
        source_buffer = source_view.get_buffer()

        total_replacement_count = 0
        for search_replace_tuple in search_replace_tuples:
            search_text, replacement_text = search_replace_tuple
            logger.log_value('Search and replace', '%s ⊳ %s' % (search_text, replacement_text))
            search_settings.set_search_text(search_text)
            search_context = GtkSource.SearchContext.new(source_buffer, search_settings)
            replacement_count = search_context.replace_all(replacement_text, -1)
            logger.log_value('Number of matches', replacement_count)
            total_replacement_count += replacement_count

    return total_replacement_count


def main_quit():

    # Reset icon search paths.
    reset_icon_search_paths()

    GLib.idle_add(Gtk.main_quit)
