#!/usr/bin/python3

########################################################################
#                                                                      #
# directory_chooser.py                                                 #
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

name = 'directory_chooser'
callback = None

########################################################################
# Functions
########################################################################


def open(calback):

    displayer.set_sensitive('window', False)
    displayer.show_all(name)
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


def on_clicked__directory_chooser__cancel_button(widget):

    logger.log_title('Clicked directory chooser cancel button')
    close()


def on_clicked__directory_chooser__select_button(widget):

    logger.log_title('Clicked directory chooser select button')
    close()

    filepath = get_selected_filepath()
    logger.log_value('The selected directory is', filepath)
    callback(filepath)


def on_delete_event__directory_chooser(widget, event):

    logger.log_title('Delete directory chooser')
    close()
    return True
