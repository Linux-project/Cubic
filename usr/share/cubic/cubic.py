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

########################################################################
# References
########################################################################

# N/A

########################################################################
# Initialize
########################################################################

# import warnings

import os
if os.getuid() == 0:
    print(
        'Error. Cubic (Custom Ubuntu ISO Creator) is a graphical user interface application and may not be run using sudo or as root. See "man cubic" for more information.'
    )
    print()
    exit()

from utilities import logger
logger.log_title('Cubic - Custom Ubuntu ISO Creator')

########################################################################
# Imports
########################################################################

import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk

import glob
import importlib
import os
import traceback

import navigator
from utilities import constructor
from utilities import model

########################################################################
# Global Variables & Constants
########################################################################

# N/A

########################################################################
# Main Application
########################################################################

# 1. Load the UI into the builder from the file.
# 2. Connect the signals to the module that has the handlers.

try:

    logger.log_title('Start Cubic')

    #-------------------------------------------------------------------
    # Initialize
    #-------------------------------------------------------------------

    # Real path is necessary here.
    model.application.directory = os.path.dirname(os.path.realpath(__file__))
    os.chdir(model.application.directory)

    model.application.user_home = os.path.expanduser(os.path.join('~', '*'))

    model.application.cubic_version = constructor.get_package_version('cubic')
    model.application.kernel_version = constructor.get_kernel_version()

    # Load the user interface.
    model.builder = Gtk.Builder.new_from_file('cubic.ui')
    # Connect the signals to handlers in the associated module.
    model.builder.connect_signals(navigator)

    #-------------------------------------------------------------------
    # Pages
    #-------------------------------------------------------------------

    logger.log_label('Setup pages')
    print()

    # Get the stack.
    pages = model.builder.get_object('pages')

    for file_name in sorted(glob.glob('pages/*_page.ui')):

        # Get the module name.
        module_name = file_name[6:-3]
        logger.log_value('Setup', module_name.replace('_', ' '))

        # Load the user interface.
        model.builder.add_from_file(file_name)

        # Load the module.
        module = importlib.import_module('pages.%s' % module_name)

        # Connect the signals to handlers in the associated module.
        model.builder.connect_signals(module)

        # Add page to stack.
        page = model.builder.get_object(module.name)
        pages.add_named(page, module.name)

    # Set the first page for the stack.
    page = model.builder.get_object('start_page')
    pages.set_visible_child(page)

    #-------------------------------------------------------------------
    # Header Bar
    #-------------------------------------------------------------------

    # Add previously loaded widgets to the header bar.

    # TODO: Can adding widgets to the header bar be moved to the individual pages?

    header_bar = model.builder.get_object('header_bar')

    # Project page
    widget = model.builder.get_object('project_page__delete_header_bar_button')
    header_bar.add(widget)

    widget = model.builder.get_object('project_page__header_bar_box')
    header_bar.add(widget)

    # Packages page
    widget = model.builder.get_object('packages_page__header_bar_box')
    header_bar.add(widget)

    # Options page
    options_page__stack_switcher = model.builder.get_object('options_page__stack_switcher')
    options_page__stack = model.builder.get_object('options_page__stack')
    options_page__stack_switcher.set_stack(options_page__stack)

    # Terminal page
    widget = model.builder.get_object('terminal_page__copy_header_bar_button')
    header_bar.add(widget)

    #-------------------------------------------------------------------
    # File Choosers
    #-------------------------------------------------------------------

    logger.log_label('Setup file choosers')

    for file_name in sorted(glob.glob('file_choosers/*_chooser.ui')):

        print()

        # Get the module name.
        module_name = file_name[14:-3]
        logger.log_value('Setup (ignore warnings)', module_name.replace('_', ' '))

        # Load the user interface.
        model.builder.add_from_file(file_name)

        # Load the module.
        module = importlib.import_module('file_choosers.%s' % module_name)

        # Connect the signals to handlers in the associated module.
        model.builder.connect_signals(module)

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
    logger.log_value('The tracek back is', traceback.format_exc())
