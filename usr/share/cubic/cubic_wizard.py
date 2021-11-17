#!/usr/bin/python3

########################################################################
#                                                                      #
# cubic_wizard.py                                                      #
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

import os
if os.getuid() == 0:
    print(
        'Error. Cubic (Custom Ubuntu ISO Creator) is a graphical user'
        ' interface application and may not be run using sudo or as'
        ' root. See "man cubic" for more information.')
    print()
    exit()

from cubic.utilities import logger
logger.log_title('Cubic - Custom Ubuntu ISO Creator')

########################################################################
# Imports
########################################################################

import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk

import glob
import importlib
import mimetypes
import os
import traceback

from cubic import navigator
from cubic.utilities import constructor
from cubic.utilities import model

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
    # os.chdir(model.application.directory)

    # Add additional mime types.
    mimetypes.init()
    file_path = os.path.join(model.application.directory, 'assets', 'mime.types')
    mimetypes.types_map.update(mimetypes.read_mime_types(file_path))

    # Get the user's home directory.
    model.application.user_home = os.path.expanduser('~')

    # Get the running kernel version.
    model.application.cubic_version = constructor.get_package_version('cubic')
    model.application.kernel_version = constructor.get_kernel_version()

    # Load the user interface.
    file_path = os.path.join(model.application.directory, 'cubic_wizard.ui')
    model.builder = Gtk.Builder.new_from_file(file_path)
    # Connect the signals to handlers in the associated module.
    model.builder.connect_signals(navigator)

    #-------------------------------------------------------------------
    # Pages
    #-------------------------------------------------------------------

    logger.log_label('Setup pages')
    print()

    # Get the stack.
    pages = model.builder.get_object('pages')

    pattern = os.path.join(model.application.directory, 'cubic', 'pages', '*_page.ui')
    file_paths = sorted(glob.glob(pattern))
    for file_path in file_paths:

        # Get the module name.
        module_name = os.path.basename(file_path)[:-3]
        logger.log_value('Setup', module_name.replace('_', ' '))

        # Load the user interface.
        model.builder.add_from_file(file_path)

        # Load the module.
        module = importlib.import_module(f'cubic.pages.{module_name}')

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
    widget = model.builder.get_object('project_page__test_header_bar_button')
    header_bar.add(widget)

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

    # Finish page
    widget = model.builder.get_object('finish_page__test_header_bar_button')
    header_bar.add(widget)

    #-------------------------------------------------------------------
    # File Choosers
    #-------------------------------------------------------------------

    logger.log_label('Setup file choosers')

    pattern = os.path.join(model.application.directory, 'cubic', 'choosers', '*_chooser.ui')
    file_paths = sorted(glob.glob(pattern))
    for file_path in file_paths:

        print()

        # Get the module name.
        module_name = os.path.basename(file_path)[:-3]
        logger.log_value('Setup (ignore warnings)', module_name.replace('_', ' '))

        # Load the user interface.
        model.builder.add_from_file(file_path)

        # Load the module.
        module = importlib.import_module(f'cubic.choosers.{module_name}')

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
    logger.log_value('The trace back is', traceback.format_exc())
