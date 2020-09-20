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

from os.path import isfile

from utilities import displayer
from utilities import logger
from utilities import model

########################################################################
# References
########################################################################

# N/A

########################################################################
# Globals & Constants
########################################################################

name = 'iso_image_chooser'
callback = None

########################################################################
# Functions
########################################################################


def open(calback, filepath=None):

    displayer.set_sensitive('window', False)
    if filepath:
        displayer.show_filechooser(name, filepath)
    else:
        displayer.show_filechooser(name, model.application.user_home)
    set_callback(calback)


def close():

    displayer.set_sensitive('window', False)
    displayer.hide(name)
    displayer.set_sensitive('window', True)


def set_callback(new_callback):

    global callback
    callback = new_callback


def get_selected_filepath():

    dialog = model.builder.get_object(name)
    filepath = dialog.get_filename()
    return filepath


def on_clicked__iso_image_chooser__cancel_button(widget):

    logger.log_title('Clicked ISO image chooser cancel button')
    close()


def on_clicked__iso_image_chooser__select_button(widget):

    logger.log_title('Clicked ISO image chooser select button')
    filepath = get_selected_filepath()
    try:
        isfile(filepath)
        close()
        logger.log_value('The selected filepath is', filepath)
        callback(filepath)
    except TypeError as exception:
        logger.log_value('Error. The selected filepath is', filepath)
        filepath = None


def on_delete_event__iso_image_chooser(widget, event):

    logger.log_title('Delete ISO image chooser')
    close()
    return True
