#!/usr/bin/python3

########################################################################
#                                                                      #
# iso_image_chooser.py                                                 #
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

import os
import traceback

from cubic.utilities import displayer
from cubic.utilities import logger
from cubic.utilities import model

########################################################################
# Global Variables & Constants
########################################################################

name = 'iso_image_chooser'
callback = None

########################################################################
# Functions
########################################################################


def open(calback, file_path=None):

    displayer.set_sensitive('window', False)
    if file_path:
        displayer.show_file_chooser(name, file_path)
    else:
        displayer.show_file_chooser(name, model.application.user_home)
    set_callback(calback)


def close():

    displayer.set_sensitive('window', False)
    displayer.hide(name)
    displayer.set_sensitive('window', True)


def set_callback(new_callback):

    global callback
    callback = new_callback


def get_selected_file_path():

    dialog = model.builder.get_object(name)
    file_path = dialog.get_filename()
    return file_path


def on_clicked__iso_image_chooser__cancel_button(widget):

    logger.log_title('Clicked ISO image chooser cancel button')
    close()


def on_clicked__iso_image_chooser__select_button(widget):

    logger.log_title('Clicked ISO image chooser select button')
    file_path = get_selected_file_path()
    try:
        os.path.isfile(file_path)
        close()
        logger.log_value('The selected file path is', file_path)
        callback(file_path)
    except TypeError as exception:
        logger.log_value('Error. The selected file path is', file_path)
        logger.log_value('The exception is', exception)
        logger.log_value('The trace back is', traceback.format_exc())
        file_path = None


def on_map__iso_image_chooser__header_bar(header_bar):

    is_visible = header_bar.is_visible()
    button_box = model.builder.get_object('iso_image_chooser__button_box')

    # Do not use GLib.idle_add because hiding the button_box must be
    # immediate.
    button_box.set_visible(not is_visible)


def on_delete_event__iso_image_chooser(widget, event):

    logger.log_title('Delete ISO image chooser')
    close()
    return True
