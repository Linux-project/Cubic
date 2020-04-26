#!/usr/bin/python3

########################################################################
#                                                                      #
# copy_file_chooser.py                                                 #
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

from utilities import display
from utilities import logger
from utilities import model

name = 'copy_file_chooser'
callback = None


def open(calback):

    print('OPEN!')
    display.set_sensitive('window', False)
    display.show_all(name)
    set_callback(calback)


def close():
    display.set_sensitive('window', False)
    display.hide(name)
    display.set_sensitive('window', True)


def set_callback(new_callback):
    global callback
    callback = new_callback


def get_selected_filepaths():
    dialog = model.builder.get_object(name)
    filepaths = dialog.get_filenames()
    return filepaths


def on_clicked__copy_file_chooser__cancel_button(widget):
    logger.log_title('Clicked directory file chooser cancel button')
    close()


def on_clicked__copy_file_chooser__select_button(widget):
    logger.log_title('Clicked copy file chooser select button')
    close()
    filepaths = get_selected_filepaths()
    logger.log_value('The selected filepaths are', filepaths)
    callback(filepaths)


def on_delete_event__copy_file_chooser(widget, event):
    logger.log_title('Delete copy file chooser')
    close()
    return True
