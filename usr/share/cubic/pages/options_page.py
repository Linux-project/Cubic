#!/usr/bin/python3

########################################################################
#                                                                      #
# options_page.py                                                      #
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

# TODO: Explicitly set model.options.boot_configurations to the default
#       value if it is None or empty (usually due to an exception).
# TODO: Set header widgets visible or hidden for all actions in the
#       start(), enter(), and leave() functions, and in all map and
#       unmap functions.

########################################################################
# References
########################################################################

# N/A

########################################################################
# Imports
########################################################################

import os

from pages.boot_tab import IsoBootTab
from pages.kernel_tab import IsoKernelTab
from pages.preseed_tab import PreseedTab
from utilities import configuration
from utilities import displayer
from utilities import iso_utilities
from utilities import logger
from utilities import model

########################################################################
# Global Variables & Constants
########################################################################

name = 'options_page'

kernel_tab = None
preseed_tab = None
boot_tab = None

########################################################################
# Navigation Functions
########################################################################


def setup(action, old_page=None):

    if action == 'back':

        displayer.reset_buttons(
            back_button_label='❬Back',
            back_action='back',
            back_button_style=None,
            is_back_sensitive=True,
            is_back_visible=True,
            next_button_label='Next❭',
            next_action='next',
            next_button_style='suggested-action',
            is_next_sensitive=True,
            is_next_visible=True)

        displayer.set_visible('title_label', False)
        displayer.set_visible('options_page__stack_switcher', True)

        return

    if action == 'cancel':

        # Do not assume the virtual environment is running.

        displayer.reset_buttons(
            back_button_label='❬Back',
            back_action='back',
            back_button_style=None,
            is_back_sensitive=True,
            is_back_visible=True,
            next_button_label='Next❭',
            next_action='next',
            next_button_style=None,
            is_next_sensitive=True,
            is_next_visible=True)

        displayer.set_visible('title_label', False)
        displayer.set_visible('options_page__stack_switcher', True)

        return

    if action == 'copy-preseed':

        # Do not assume the virtual environment is running.

        displayer.reset_buttons(
            back_button_label='❬Back',
            back_action='back',
            back_button_style=None,
            is_back_sensitive=True,
            is_back_visible=True,
            next_button_label='Next❭',
            next_action='next',
            next_button_style=None,
            is_next_sensitive=True,
            is_next_visible=True)

        displayer.set_visible('title_label', False)
        displayer.set_visible('options_page__stack_switcher', True)

        return

    if action == 'copy-boot-configuration':

        # Do not assume the virtual environment is running.

        displayer.reset_buttons(
            back_button_label='❬Back',
            back_action='back',
            back_button_style=None,
            is_back_sensitive=True,
            is_back_visible=True,
            next_button_label='Next❭',
            next_action='next',
            next_button_style=None,
            is_next_sensitive=True,
            is_next_visible=True)

        displayer.set_visible('title_label', False)
        displayer.set_visible('options_page__stack_switcher', True)

        return

    elif action == 'next':

        displayer.reset_buttons(
            back_button_label='❬Back',
            back_action='back',
            back_button_style=None,
            is_back_sensitive=True,
            is_back_visible=True,
            next_button_label='Next❭',
            next_action='next',
            next_button_style='suggested-action',
            is_next_sensitive=True,
            is_next_visible=True)

        displayer.set_visible('title_label', False)
        displayer.set_visible('options_page__stack_switcher', True)

        header_bar = model.builder.get_object('header_bar')

        global kernel_tab
        if not kernel_tab:

            # Load the user interface.
            model.builder.add_from_file('pages/kernel_tab.ui')
            grid = model.builder.get_object('options_page__kernel_tab__grid')
            scrolled_window = model.builder.get_object('kernel_tab__scrolled_window')
            displayer.attach(grid, scrolled_window, 0, 1, 1, 1)

            # Connect the signals to handlers in the associated module.
            kernel_tab = IsoKernelTab()

            # Add previously loaded widgets to the header bar.
            # box = model.builder.get_object('kernel_tab__header_box')
            # header_bar.add(box)
            # displayer.set_visible('kernel_tab__header_box', False)

        kernel_tab.create_linux_kernels_list()

        global preseed_tab
        if not preseed_tab:

            # Load the user interface.
            model.builder.add_from_file('pages/preseed_tab.ui')
            grid = model.builder.get_object('options_page__preseed_tab__grid')
            panes = model.builder.get_object('preseed_tab__panes')
            displayer.attach(grid, panes, 0, 1, 1, 1)

            # Connect the signals to handlers in the associated module.
            preseed_tab = PreseedTab()

            # Add previously loaded widgets to the header bar.
            box = model.builder.get_object('preseed_tab__header_box')
            header_bar.add(box)
            displayer.set_visible('preseed_tab__header_box', False)

        # If the preseed directory does not exist, create it.
        file_path = os.path.join(model.project.custom_disk_directory, 'preseed')
        # TODO: Use file_utilities.make_directory() or os.makedirs ?
        # file_utilities.make_directory(file_path)
        os.makedirs(file_path, exist_ok=True)
        preseed_tab.create_tree(['preseed'])

        global boot_tab
        if not boot_tab:

            # Load the user interface.
            model.builder.add_from_file('pages/boot_tab.ui')
            grid = model.builder.get_object('options_page__boot_tab__grid')
            panes = model.builder.get_object('boot_tab__panes')
            displayer.attach(grid, panes, 0, 1, 1, 1)

            # Connect the signals to handlers in the associated module.
            boot_tab = IsoBootTab()

            # Add previously loaded widgets to the header bar.
            box = model.builder.get_object('boot_tab__header_box')
            header_bar.add(box)
            displayer.set_visible('boot_tab__header_box', False)

        # Assume the boot/grub directory exists.
        boot_tab.create_tree(['boot/grub', 'isolinux'], model.options.boot_configurations)

        # Save the selected kernel in the model.
        model.selected_kernel_index = kernel_tab.selected_kernel_index

        # Update the boot configurations based on the selected kernel.
        update_boot_configurations(model.options.boot_configurations, model.kernel_details_list, model.selected_kernel_index)

        return

    else:

        return 'unknown'


def enter(action, old_page=None):

    if action == 'back':

        return

    elif action == 'cancel':

        return

    elif action == 'copy-preseed':

        return

    elif action == 'copy-boot-configuration':

        return

    elif action == 'next':

        return

    else:

        return 'unknown'


def leave(action, new_page=None):

    if action == 'back':

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        displayer.set_visible('title_label', True)
        displayer.set_visible('options_page__stack_switcher', False)

        # displayer.set_visible('kernel_tab__header_box', False)
        displayer.set_visible('preseed_tab__header_box', False)
        displayer.set_visible('boot_tab__header_box', False)

        model.options.boot_configurations = boot_tab.get_required_file_paths()
        configuration.save()

        preseed_tab.remove_tree()
        boot_tab.remove_tree()

        return

    elif action == 'copy-preseed':

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        displayer.set_visible('title_label', True)
        displayer.set_visible('options_page__stack_switcher', False)

        model.options.boot_configurations = boot_tab.get_required_file_paths()
        configuration.save()

        return

    elif action == 'copy-boot-configuration':

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        displayer.set_visible('title_label', True)
        displayer.set_visible('options_page__stack_switcher', False)

        model.options.boot_configurations = boot_tab.get_required_file_paths()
        configuration.save()

        return

    elif action == 'next':

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        displayer.set_visible('title_label', True)
        displayer.set_visible('options_page__stack_switcher', False)

        # displayer.set_visible('kernel_tab__header_box', False)
        displayer.set_visible('preseed_tab__header_box', False)
        displayer.set_visible('boot_tab__header_box', False)

        model.options.boot_configurations = boot_tab.get_required_file_paths()
        configuration.save()

        return

    elif action == 'quit':

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        model.options.boot_configurations = boot_tab.get_required_file_paths()
        configuration.save()

        preseed_tab.remove_tree()
        boot_tab.remove_tree()

        iso_utilities.unmount_iso_and_delete_mount_point(model.project.iso_mount_point)

        return

    else:

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        iso_utilities.unmount_iso_and_delete_mount_point(model.project.iso_mount_point)

        model.options.boot_configurations = boot_tab.get_required_file_paths()
        configuration.save()

        return 'unknown'


########################################################################
# Handler Functions
########################################################################


def on_map__options_page__kernel_tab(*args):

    logger.log_label('Show Options page, Kernel tab')
    # displayer.set_visible('kernel_tab__header_box', True)

    # displayer.set_visible('kernel_tab__header_box', False)
    displayer.set_visible('preseed_tab__header_box', False)
    displayer.set_visible('boot_tab__header_box', False)


def on_unmap__options_page__kernel_tab(*args):

    logger.log_value('Leave', 'Options page Kernel tab')
    # displayer.set_visible('kernel_tab__header_box', False)

    # Update the boot configurations if the selected kernel has changed.
    if kernel_tab.selected_kernel_index != model.selected_kernel_index:

        # Save the selected kernel in the model.
        model.selected_kernel_index = kernel_tab.selected_kernel_index

        # Update the boot configurations based on the selected kernel.
        update_boot_configurations(model.options.boot_configurations, model.kernel_details_list, model.selected_kernel_index)


def on_map__options_page__preseed_tab(*args):

    logger.log_label('Show Options page, Preseed tab')

    # displayer.set_visible('kernel_tab__header_box', False)
    displayer.set_visible('preseed_tab__header_box', True)
    displayer.set_visible('boot_tab__header_box', False)


def on_unmap__options_page__preseed_tab(*args):

    logger.log_value('Leave', 'Options page Preseed tab')

    displayer.set_visible('preseed_tab__header_box', False)


def on_map__options_page__boot_tab(*args):

    logger.log_label('Show Options page, Boot tab')

    # displayer.set_visible('kernel_tab__header_box', False)
    displayer.set_visible('preseed_tab__header_box', False)
    displayer.set_visible('boot_tab__header_box', True)


def on_unmap__options_page__boot_tab(*args):

    logger.log_value('Leave', 'Options page Boot tab')

    displayer.set_visible('boot_tab__header_box', False)


########################################################################
# Support Functions
########################################################################


def update_boot_configurations(file_paths, kernel_details_list, selected_index):
    """
    Update the boot configuration files, replacing references to vmlinuz
    and initrd with the correct file names based on the currently
    selected kernel.

    The contents of the boot configurations files is also replaced in
    kernel_tab.on_toggled__kernel_tab__kernels_radio_button().
    """

    logger.log_label('Update boot configurations')

    logger.log_value('The selected kernel is index number', selected_index)

    # Remove all existing boot=casper; this will be added below.
    search_text_1 = r'\s*boot=casper\s*'
    replacement_text_1 = r' '

    # Handle files like /boot/grub/grub.cfg and /boot/grub/loopback.cfg
    # that have /casper/vmlinuz and boot=casper on the same line.

    # linux + /casper/vmlinuz + boot=casper
    search_text_2 = r'^(\s*linux\s+.*)/%s\S*/vmlinuz\S*' % model.status.casper_directory
    replacement_text_2 = r'\1/%s/%s boot=casper' % (model.status.casper_directory, kernel_details_list[selected_index]['new_vmlinuz_file_name'])

    # Handle files like /isolinux/txt.cfg
    # that have /casper/vmlinuz and boot=casper on separate lines.

    # kernel + /casper/vmlinuz
    search_text_3 = r'^(\s*kernel\s+.*)/%s\S*/vmlinuz\S*' % model.status.casper_directory
    replacement_text_3 = r'\1/%s/%s' % (model.status.casper_directory, kernel_details_list[selected_index]['new_vmlinuz_file_name'])

    # append + boot=casper
    search_text_4 = r'(^\s*append\s+)(.*)'
    replacement_text_4 = r'\1boot=casper \2'

    # initrd
    search_text_5 = r'%s\S*/initrd\S*' % model.status.casper_directory
    replacement_text_5 = r'%s/%s' % (model.status.casper_directory, kernel_details_list[selected_index]['new_initrd_file_name'])

    # Search and replace text.
    boot_tab.search_and_replace_in_files(
        file_paths,
        (search_text_1,
         replacement_text_1),
        (search_text_2,
         replacement_text_2),
        (search_text_3,
         replacement_text_3),
        (search_text_4,
         replacement_text_4),
        (search_text_5,
         replacement_text_5))
