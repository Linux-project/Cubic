#!/usr/bin/python3

########################################################################
#                                                                      #
# displayer.py                                                         #
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
gi.require_version('GLib', '2.0')
gi.require_version('Gtk', '3.0')

try:
    gi.require_version('GtkSource', '4')
except ValueError:
    gi.require_version('GtkSource', '3.0')

# The following is necessary to avoid the error: "Gtk-ERROR **: failed
# to add UI: source_view.ui:39:1 Invalid object type 'GtkSourceView'"
from gi.repository.GtkSource import View

from gi.repository import Gio
from gi.repository import GLib
from gi.repository import Gtk
from gi.repository import GtkSource
from gi.repository import Pango

from constants import OK, ERROR, BULLET, PROCESSING
from utilities import logger
from utilities import model

logger.log_value('Using GtkSource version', GtkSource._version)

########################################################################
# Global Variables & Constants
########################################################################

# Status icons may be referenced using the constants:
# OK, ERROR, OPTIONAL, BULLET, PROCESSING, BLANK
icons = ['cubic-ok-symbolic', 'cubic-error-symbolic', 'cubic-optional-symbolic', 'cubic-bullet-symbolic', 'cubic-blank-symbolic', 'cubic-blank-symbolic']

# Get the system mono-spaced font.
settings = Gio.Settings.new('org.gnome.desktop.interface')
font_name = settings.get_string('monospace-font-name')
MONOSPACE_FONT = Pango.FontDescription(font_name)

# Get the source view language for ini files.
language_name = 'ini'
language_name_manager = GtkSource.LanguageManager()
SOURCE_LANGUAGE = language_name_manager.get_language(language_name)

# Get the source view style for Tango.
scheme_name = 'tango'
style_scheme_manager = GtkSource.StyleSchemeManager()
SOURCE_STYLE_SCHEME = style_scheme_manager.get_scheme(scheme_name)

# Transition Effects
SLIDE_NONE = Gtk.StackTransitionType.NONE
SLIDE_LEFT = Gtk.StackTransitionType.SLIDE_LEFT
SLIDE_RIGHT = Gtk.StackTransitionType.SLIDE_RIGHT

########################################################################
# General Functions
########################################################################


def idle_add(callback):
    """
    This is used on the Project page.
    The Console module calls GLib.idle_add() directly.
    """

    GLib.idle_add(callback)


########################################################################
# Page Functions
########################################################################


def main_quit():

    GLib.idle_add(Gtk.main_quit)


def transition(old_page, new_page, effect):
    """
    Transition the to a new page in the Gtk.Stack using the specified
    Gtk.StackTransitionType effect. All pages must have the 'visible'
    property set to True in the *.ui file.
    """

    if old_page != new_page:
        # Get the Gtk.Stack.
        pages = model.builder.get_object('pages')
        if old_page:
            # Print a message.
            logger.log_value('Hide old page', old_page.name.replace('_', ' '))
        if new_page:
            # Show the next page
            logger.log_value('Show new page', new_page.name.replace('_', ' '))
            GLib.idle_add(Gtk.Stack.set_visible_child_full, pages, new_page.name, effect)
    else:
        # Stay on the current page.
        logger.log_value('Stay on page', old_page.name.replace('_', ' '))


########################################################################
# Navigation Button Functions
########################################################################


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

    set_button('back_button', back_button_label, back_action, back_button_style, is_back_sensitive, is_back_visible)
    set_button('next_button', next_button_label, next_action, next_button_style, is_next_sensitive, is_next_visible)


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


########################################################################
# Container Functions
########################################################################


def attach(grid, widget, x, y, width, height):

    GLib.idle_add(Gtk.Grid.attach, grid, widget, x, y, width, height)


def add_named(stack, page, name):

    GLib.idle_add(Gtk.Stack.add_named, stack, page, name)


def set_visible_child(stack, page):

    GLib.idle_add(Gtk.Stack.set_visible_child, stack, page)


########################################################################
# Show / Hide Functions
########################################################################


def show(widget_name):

    widget = model.builder.get_object(widget_name)
    GLib.idle_add(Gtk.Widget.show, widget)


def hide(widget_name):

    widget = model.builder.get_object(widget_name)
    GLib.idle_add(Gtk.Widget.hide, widget)


def show_all(widget_name):

    widget = model.builder.get_object(widget_name)
    GLib.idle_add(Gtk.Widget.show_all, widget)


def set_visible(widget_name, is_visible):

    widget = model.builder.get_object(widget_name)
    GLib.idle_add(Gtk.Widget.set_visible, widget, is_visible)


def set_solid(widget_name, is_solid):

    widget = model.builder.get_object(widget_name)
    GLib.idle_add(Gtk.Widget.set_opacity, widget, is_solid)


def set_opacity(widget_name, percent):

    widget = model.builder.get_object(widget_name)
    GLib.idle_add(Gtk.Widget.set_opacity, widget, percent / 100.0)


def set_sensitive(widget_name, is_sensitive):

    widget = model.builder.get_object(widget_name)
    GLib.idle_add(Gtk.Widget.set_sensitive, widget, is_sensitive)


########################################################################
# Label Functions
########################################################################


def update_label(label_name, text):

    # logger.log_value('Update label %s' % label_name, text)
    label = model.builder.get_object(label_name)
    GLib.idle_add(Gtk.Label.set_markup, label, text)


########################################################################
# Entry Functions
########################################################################


def update_entry(entry_name, text):

    # logger.log_value('Update entry %s' % entry_name, text)
    entry = model.builder.get_object(entry_name)
    GLib.idle_add(Gtk.Entry.set_text, entry, text)


def set_entry_error(widget_name, is_error):

    # logger.log_value('Set error for entry %s' % widget_name, is_error)
    entry = model.builder.get_object(widget_name)
    context = entry.get_style_context()
    if is_error:
        GLib.idle_add(Gtk.StyleContext.add_class, context, 'error')
    else:
        GLib.idle_add(Gtk.StyleContext.remove_class, context, 'error')


def set_entry_editable(widget_name, is_editable):

    # logger.log_value('Set name property to editable is "%s" for entry' % is_editable, widget_name)
    entry = model.builder.get_object(widget_name)
    # entry.set_editable(is_editable)
    GLib.idle_add(Gtk.Entry.set_editable, entry, is_editable)


########################################################################
# File Chooser Functions
########################################################################


def show_file_chooser(widget_name, file_path):

    file_chooser = model.builder.get_object(widget_name)
    GLib.idle_add(_show_file_chooser, file_chooser, file_path)


def _show_file_chooser(file_chooser, file_path):
    """
    Only invoke this function using GLib.idle_add().
    """

    # If the file does not exist, set_filename() will open the parent
    # directory and not select any file, but select_file_name() will
    # will open the parent directory and select the next file in the
    # list.
    file_chooser.set_filename(file_path)
    file_chooser.show_all()


########################################################################
# Status Functions
########################################################################


def update_status(prefix, status):
    """
    The proper naming convention must be used.
    Object ids must end in '_status' or '_spinner'.
    Object ids ending in '_status' are always images in the *.ui file.
    Object ids ending in '_spinner' are always spinners in the *.ui file.
    """

    # logger.log_value('Set status for entry %s_status' % prefix, status)

    # TODO: Use Gtk.Icontheme instead of Gtk.IconSize because Gtk.IconSize id deprecated.
    #       https://lazka.github.io/pgi-docs/Gtk-3.0/enums.html#Gtk.IconSize

    # Valid icon sizes are:
    #
    #   0 = Gtk.IconSize.INVALID
    #   1 = Gtk.IconSize.MENU
    #   2 = Gtk.IconSize.SMALL_TOOLBAR
    #   3 = Gtk.IconSize.LARGE_TOOLBAR
    #   4 = Gtk.IconSize.BUTTON
    #   5 = Gtk.IconSize.DND (Drag and Drop)
    #   6 = Gtk.IconSize.DIALOG

    image = model.builder.get_object('%s_status' % prefix)
    GLib.idle_add(Gtk.Image.set_from_icon_name, image, icons[status], Gtk.IconSize.BUTTON)
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


def update_status_image(name, status):
    """
    This is used on the Terminal page.
    """

    # TODO: Use Gtk.Icontheme instead of Gtk.IconSize because Gtk.IconSize id deprecated.
    #       https://lazka.github.io/pgi-docs/Gtk-3.0/enums.html#Gtk.IconSize

    image = model.builder.get_object(name)
    GLib.idle_add(Gtk.Image.set_from_icon_name, image, icons[status], Gtk.IconSize.BUTTON)


########################################################################
# Progress Bar Functions
########################################################################


def update_progress_bar_percent(progress_bar_name, percent):

    progress_bar = model.builder.get_object(progress_bar_name)
    GLib.idle_add(Gtk.ProgressBar.set_fraction, progress_bar, float(percent) / 100.00)


def update_progress_bar_text(progress_bar_name, text):

    progress_bar = model.builder.get_object(progress_bar_name)
    GLib.idle_add(Gtk.ProgressBar.set_text, progress_bar, text)


########################################################################
# Button Functions
########################################################################


def activate_toggle_button(toggle_button_name, is_active):
    """
    This is used on the Options page.
    """

    toggle_button = model.builder.get_object(toggle_button_name)
    GLib.idle_add(Gtk.ToggleButton.set_active, toggle_button, is_active)


def activate_check_button(check_button_name, is_active):
    """
    This is used on the Delete page and Finish page.
    """

    check_button = model.builder.get_object(check_button_name)
    GLib.idle_add(Gtk.CheckButton.set_active, check_button, is_active)


def update_check_button_label(name, label):
    """
    This is used on the Delete page.
    """

    check_button = model.builder.get_object(name)
    GLib.idle_add(Gtk.CheckButton.set_label, check_button, label)


def activate_radio_button(radio_button_name, is_active):

    radio_button = model.builder.get_object(radio_button_name)
    GLib.idle_add(Gtk.RadioButton.set_active, radio_button, is_active)


########################################################################
# Menu Functions
########################################################################


def update_menu_item(menu_item_name, text):
    """
    This is used on the Terminal page.
    """

    menu_item = model.builder.get_object(menu_item_name)
    GLib.idle_add(Gtk.MenuItem.set_label, menu_item, text)


########################################################################
# Box Functions (Prepare page and Generate page)
########################################################################


def empty_box(box_name):

    box = model.builder.get_object(box_name)
    for child in box.get_children():
        # TODO: Do we need the logging here?
        if isinstance(child, Gtk.Label):
            logger.log_value('Removing label from box', child.get_text())
        elif isinstance(child, Gtk.Button):
            logger.log_value('Removing button from box', child.get_label())
        else:
            logger.log_value('Removing unknown type from box', child)
        GLib.idle_add(Gtk.Box.remove, box, child)
        GLib.idle_add(Gtk.Widget.destroy, child)


def insert_box_label(box_name, text, opacity):

    # Since label is not displayed, there is no need to call GLib.idle_add().
    label = Gtk.Label(text)
    label.set_halign(Gtk.Align.FILL)
    label.set_hexpand(False)
    label.set_xalign(0.00)
    label.set_visible(True)
    label.set_opacity(opacity)
    label.set_justify(Gtk.Justification.LEFT)
    label.set_line_wrap(True)
    # label.set_max_width_chars(0)

    box = model.builder.get_object(box_name)
    GLib.idle_add(Gtk.Box.add, box, label)


def scroll_view_port_to_bottom(view_port_name):

    view_port = model.builder.get_object(view_port_name)
    adjustment = view_port.get_vadjustment()
    amount = adjustment.get_upper() - adjustment.get_page_size()
    GLib.idle_add(Gtk.Adjustment.set_value, adjustment, amount)


########################################################################
# Tree View Functions
########################################################################


def set_column_visible(widget_name, is_visible):

    widget = model.builder.get_object(widget_name)
    GLib.idle_add(Gtk.TreeViewColumn.set_visible, widget, is_visible)


def scroll_to_tree_view_row(tree_view_name, row_number):

    tree_view = model.builder.get_object(tree_view_name)
    tree_path = Gtk.TreePath.new_from_string('%s' % row_number)
    GLib.idle_add(Gtk.TreeView.scroll_to_cell, tree_view, tree_path, None, True, 0.5, 0.0)


def select_tree_view_row(tree_view_name, row_number):

    tree_view = model.builder.get_object(tree_view_name)
    tree_path = Gtk.TreePath.new_from_string('%s' % row_number)
    GLib.idle_add(Gtk.TreeView.set_cursor, tree_view, tree_path, None, False)


########################################################################
# List Store Functions
########################################################################


def update_list_store(list_store_name, data_list):

    list_store = model.builder.get_object(list_store_name)
    GLib.idle_add(_update_list_store_rows, list_store, data_list)


def _update_list_store_rows(list_store, data_list):
    """
    Only invoke this function using GLib.idle_add().
    """

    list_store.clear()
    for number, data in enumerate(data_list):
        # logger.log_value('%i. Adding an item to the list' % (number + 1), data)
        list_store.append(data)


def update_list_store_progress_bar_percent(list_store_name, path, percent):

    list_store = model.builder.get_object(list_store_name)
    GLib.idle_add(_update_list_store_progress_bar_percent, list_store, path, percent)


def _update_list_store_progress_bar_percent(list_store, path, percent):
    """
    Only invoke this function using GLib.idle_add().
    """

    list_store[path][0] = percent
