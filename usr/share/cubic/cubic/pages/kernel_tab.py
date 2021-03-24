#!/usr/bin/python3

########################################################################
#                                                                      #
# kernel_tab.py                                                        #
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

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk

from cubic.utilities import displayer
from cubic.utilities import logger
from cubic.utilities import model

########################################################################
# Global Variables & Constants
########################################################################

# N/A

########################################################################
# Kernel Tab Class
########################################################################


class KernelTab():

    def __init__(self):
        """
        Create a new KernelTab.
        This method is invoked using GLib.idle_add() from options_page.
        """

        logger.log_label('Initialize Kernel Tab')

        # Load the user interface and immediately connect the signals to
        # the handlers.
        model.builder.add_from_file('cubic/pages/kernel_tab.ui')
        model.builder.connect_signals({'on_toggled__kernel_tab__kernels_radio_button': self.on_toggled__kernel_tab__kernels_radio_button})

        # REFERENCE: https://whyareyoureadingthisurl.wordpress.com/2012/01/21/howto-pack-gtk-cellrenderers-vertically-in-a-gtk-treeview/
        column = model.builder.get_object('kernel_tab__tree_view_column_2')
        area = column.get_area()
        area.set_orientation(Gtk.Orientation.VERTICAL)

    def create_linux_kernels_list(self):

        # Python < 3.7 does not guarantee that the order of dictionary
        # elements is preserved when using the value() method. Therefore,
        # instead of simply using list(kernel_details.values()), it is
        # necessary to explicitly add each dictionary element to the new
        # list.
        #
        # https://bugs.launchpad.net/cubic/+bug/1860345
        # https://bugs.launchpad.net/cubic/+bug/1860682
        # https://stackoverflow.com/questions/1867861/how-to-keep-keys-values-in-same-order-as-declared
        #
        # displayer.update_list_store('kernel_tab__list_store', [list(kernel_details.values()) for kernel_details in model.kernel_details_list])

        # 0: version_name
        # 1: vmlinuz_file_name
        # 2: new_vmlinuz_file_name
        # 3: initrd_file_name
        # 4: new_initrd_file_name
        # 5: directory
        # 6: note
        # 7: is_selected

        kernel_details_list = []
        for index, kernel_details in enumerate(model.kernel_details_list):
            if kernel_details['is_selected']:
                self.selected_kernel_index = index
            # Convert kernel details dictionary into a list.
            kernel_details = [
                kernel_details['version_name'],
                kernel_details['vmlinuz_file_name'],
                kernel_details['new_vmlinuz_file_name'],
                kernel_details['initrd_file_name'],
                kernel_details['new_initrd_file_name'],
                kernel_details['directory'],
                kernel_details['note'],
                kernel_details['is_selected']
            ]
            kernel_details_list.append(kernel_details)
        displayer.update_list_store('kernel_tab__list_store', kernel_details_list)

    ####################################################################
    # Handlers
    ####################################################################

    def on_toggled__kernel_tab__kernels_radio_button(self, widget, row):
        """
        Record the selected kernel in model.kernel_details_list.
        """

        logger.log_label('Selected kernel')

        # TODO: Improve this. We should only use one list.

        # kernel_tab__list_store...
        # This is a list, so use indices to reference values.
        #
        # 0: version_name
        # 1: vmlinuz_file_name
        # 2: new_vmlinuz_file_name
        # 3: initrd_file_name
        # 4: new_initrd_file_name
        # 5: directory
        # 6: note
        # 7: is_selected

        # model.kernel_details_list...
        # This is a dictionary, so use keys to reference values.
        #
        # 0: version_integers
        # 1: version_name
        # 2: vmlinuz_file_name
        # 3: new_vmlinuz_file_name
        # 4: initrd_file_name
        # 5: new_initrd_file_name
        # 6: directory
        # 7: note
        # 8: is_selected

        list_store = model.builder.get_object('kernel_tab__list_store')

        # Unselect the previous kernel.
        list_store[self.selected_kernel_index][7] = False
        logger.log_value('The index of the previous selected kernel is', self.selected_kernel_index)

        # Select the new kernel and update the selected kernel index.
        self.selected_kernel_index = int(row)
        logger.log_value('The index of the selected kernel is', self.selected_kernel_index)
        list_store[self.selected_kernel_index][7] = True
