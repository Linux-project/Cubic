#!/usr/bin/python3

########################################################################
#                                                                      #
# cubic.py                                                             #
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

from os import getuid
if getuid() == 0:
    print('Error. Cubic (Custom Ubuntu ISO Creator) is a graphical user interface application and may not be run using sudo or as root. See "man cubic" for more information.')
    print()
    exit()

from utilities import logger
logger.log_title('Cubic - Custom Ubuntu ISO Creator')

import gi

gi.require_version('Gdk', '3.0')
gi.require_version('Gtk', '3.0')

from gi.repository import Gdk
from gi.repository import Gio
from gi.repository import Gtk
from gi.repository import Pango
from glob import glob
from os import chdir
from os.path import dirname, realpath
from traceback import format_exc

import navigator

from utilities import displayer
from utilities import model
from utilities import constructor
from file_choosers import directory_chooser
from file_choosers import iso_image_chooser
from file_choosers import copy_file_chooser

########################################################################
# References
########################################################################

# N/A

########################################################################
# Globals & Constants
########################################################################

# N/A

########################################################################
# Main Application
########################################################################

try:

    logger.log_title('Start Cubic')

    #-------------------------------------------------------------------
    # Initialize
    #-------------------------------------------------------------------

    # Real path is necessary here.
    model.application.directory = dirname(realpath(__file__))
    chdir(model.application.directory)

    model.application.cubic_version = constructor.get_package_version('cubic')
    model.application.kernel_version = constructor.get_kernel_version()

    model.builder = Gtk.Builder.new_from_file('cubic.ui')
    model.builder.connect_signals(navigator)

    #-------------------------------------------------------------------
    # File Choosers
    #-------------------------------------------------------------------

    # Workaround for Bug #1887219: Project directory selection not
    # working in Elementary OS.
    distribution = constructor.get_distribution()
    logger.log_value('Distribution', distribution)
    is_elementary_based = constructor.os_is_elementary_based()
    if is_elementary_based:
        logger.log_value('The OS is elementary based', 'Use elementary style file choosers')
        model.builder.add_from_file('file_choosers/directory_chooser.elementary.ui')
        model.builder.connect_signals(directory_chooser)
        model.builder.add_from_file('file_choosers/iso_image_chooser.elementary.ui')
        model.builder.connect_signals(iso_image_chooser)
        model.builder.add_from_file('file_choosers/copy_file_chooser.elementary.ui')
        model.builder.connect_signals(copy_file_chooser)
    else:
        model.builder.add_from_file('file_choosers/directory_chooser.ui')
        model.builder.connect_signals(directory_chooser)
        model.builder.add_from_file('file_choosers/iso_image_chooser.ui')
        model.builder.connect_signals(iso_image_chooser)
        model.builder.add_from_file('file_choosers/copy_file_chooser.ui')
        model.builder.connect_signals(copy_file_chooser)

    #-------------------------------------------------------------------
    # Pages
    #-------------------------------------------------------------------

    pages = model.builder.get_object('pages')

    for file in sorted(glob('pages/*_page.ui')):
        module_name = file[6:-3]
        logger.log_value('Setup', module_name.replace('_', ' '))
        module = navigator.get_page(module_name)
        # logger.log_value('.', module.name)
        model.builder.add_from_file(file)
        model.builder.connect_signals(module)
        page = model.builder.get_object(module.name)
        pages.attach(page, 0, 0, 1, 1)

    #-------------------------------------------------------------------
    # Header Bar
    #-------------------------------------------------------------------

    header_bar = model.builder.get_object('header_bar')

    # Title

    widget = model.builder.get_object('title_label')
    displayer.set_visible('title_label', True)  # TODO: Already set visible in cubic.ui; no need to do it here.

    # Project page

    widget = model.builder.get_object('project_page__delete_button')
    header_bar.add(widget)
    displayer.set_visible('project_page__delete_button', False)  # TODO: Set invisible in cubic.ui

    widget = model.builder.get_object('project_page__header_bar_box')
    header_bar.add(widget)
    displayer.set_visible('project_page__header_bar_box', False)  # TODO: Set invisible in project_page.ui

    # Packages page

    widget = model.builder.get_object('packages_page__header_bar_box')
    header_bar.add(widget)
    displayer.set_visible('packages_page__header_bar_box', False)  # TODO: Set invisible in packages_page.ui

    # Options page

    widget = model.builder.get_object('options_page__header_bar_boot_box')
    header_bar.add(widget)
    displayer.set_visible('options_page__header_bar_boot_box', False)  # TODO: Set invisible in cubic.ui

    stack_switcher = model.builder.get_object('stack_switcher')
    options_page__stack = model.builder.get_object('options_page__stack')
    stack_switcher.set_stack(options_page__stack)
    displayer.set_visible('stack_switcher', False)  # TODO: Set invisible in cubic.ui

    widget = model.builder.get_object('options_page__header_bar_preseed_box_1')
    header_bar.add(widget)
    displayer.set_visible('options_page__header_bar_preseed_box_1', False)  # TODO: Set invisible in cubic.ui

    widget = model.builder.get_object('options_page__header_bar_preseed_box_2')
    header_bar.add(widget)
    displayer.set_visible('options_page__header_bar_preseed_box_2', False)  # TODO: Set invisible in cubic.ui

    # Terminal page

    widget = model.builder.get_object('terminal_page__copy_button')
    header_bar.add(widget)
    displayer.set_visible('terminal_page__copy_button', False)  # TODO: Set invisible in cubic.ui

    #-------------------------------------------------------------------
    # Terminal
    #-------------------------------------------------------------------

    # Set Terminal Font

    terminal = model.builder.get_object('terminal_page__terminal')
    # terminal.reset(True, False)
    settings = Gio.Settings.new('org.gnome.desktop.interface')
    font_name = settings.get_string('monospace-font-name')
    font = Pango.FontDescription(font_name)
    terminal.set_font(font)

    # Set Terminal Colors

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

    #-------------------------------------------------------------------
    # Start the User Interface
    #-------------------------------------------------------------------

    # Show the window.
    window = model.builder.get_object('window')
    window.show()

    # Open the application.
    navigator.handle_navigation('open')

    # Start the Gtk main loop.
    Gtk.main()

except Exception as exception:
    logger.log_value('Exception', exception)
    logger.log_value('The tracekback is', format_exc())
