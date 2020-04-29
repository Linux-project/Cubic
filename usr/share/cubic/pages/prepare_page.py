#!/usr/bin/python3

########################################################################
#                                                                      #
# prepare_page.py                                                      #
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

from constants import OK, ERROR, OPTIONAL, BULLET, PROCESSING, BLANK
from utilities import display
from utilities import file_utilities
from utilities import iso_utilities
from utilities import logger
from utilities import model
from utilities import prepare_utilities

import glob
import os
from time import sleep

########################################################################
# Globals & Constants
########################################################################

name = 'prepare_page'

########################################################################
# Navigation Functions
########################################################################


def setup(action, old_page=None):

    if action == 'next':

        display.reset_buttons(
            back_button_label='❬Back',
            back_action='back',
            back_button_style=None,
            is_back_sensitive=True,
            is_back_visible=True,
            next_button_label='Next❭',
            next_action='next',
            next_button_style=None,
            is_next_sensitive=False,
            is_next_visible=True)

        display.update_status('prepare_page__installed_packages', BULLET)
        display.update_label('prepare_page__installed_packages_message', '...')

        display.update_status('prepare_page__package_manifest_1', BULLET)
        display.update_label('prepare_page__package_manifest_1_message', '...')

        display.update_status('prepare_page__package_manifest_2', BULLET)
        display.update_label('prepare_page__package_manifest_2_message', '...')

        display.update_status('prepare_page__save_package_manifest', BULLET)
        display.update_label('prepare_page__save_package_manifest_message', '...')

        display.update_status('prepare_page__iso_boot_kernels', BULLET)
        display.empty_box('prepare_page__iso_boot_kernels_box')
        display.update_label('prepare_page__iso_boot_kernels_message', '...')

        display.update_status('prepare_page__preseed_files', BULLET)
        display.update_label('prepare_page__preseed_files_message', '...')

        display.update_status('prepare_page__iso_boot_configurations', BULLET)
        display.update_label('prepare_page__iso_boot_configurations_message', '...')

        return

    else:

        return 'unknown'


def enter(action, old_page=None):

    if action == 'next':

        #
        # Package manifest
        #
        installed_packages_list = get_a_list_of_installed_packages()
        sleep(0.50)
        removable_packages_list_1 = prepare_typical_manifest(installed_packages_list)
        sleep(0.50)
        removable_packages_list_2 = prepare_minimal_manifest(installed_packages_list)
        sleep(0.50)
        package_details_list = save_package_manifest(installed_packages_list, removable_packages_list_1, removable_packages_list_2)
        sleep(0.50)

        #
        # Linux kernels
        #
        kernel_details_list = create_kernel_details_list()
        prepare_linux_kernels(kernel_details_list)
        sleep(0.50)

        #
        # Preseed
        #
        prepare_preseed()
        sleep(0.50)

        #
        # Boot configurations
        #
        prepare_boot_configuration(kernel_details_list)
        sleep(0.50)

        # TODO: Do not proceed to next page if error.

        sleep(1.00)

        return 'next'


def leave(action, new_page=None):

    if action == 'back':

        display.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        return

    elif action == 'next':

        display.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        return

    elif action == 'quit':

        display.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        # TODO: When the original ISO image is unmounted we leave the
        #       extract page, remove the following:
        if model.project.iso_mount_point:
            # Unmount the ISO image.
            if iso_utilities.is_mounted(model.project.iso_mount_point):
                iso_utilities.unmount(model.project.iso_mount_point)
            # Delete the mount point.
            file_utilities.delete_directory(model.project.iso_mount_point)

        return

    else:

        return 'unknown'


########################################################################
# Handler Functions
########################################################################


def on_size_allocate__prepare_page__iso_boot_kernels_view_port(widget, event, data=None):

    display.scroll_view_port_to_bottom('prepare_page__iso_boot_kernels_view_port')


########################################################################
# Support Functions
########################################################################

#-----------------------------------------------------------------------
# Package Manifest
#-----------------------------------------------------------------------


def get_a_list_of_installed_packages():

    display.update_status('prepare_page__installed_packages', PROCESSING)
    sleep(0.50)

    # Get the list of installed packages.
    installed_packages_list = prepare_utilities.create_installed_packages_list()

    if installed_packages_list:
        display.update_status('prepare_page__installed_packages', OK)
        display.update_label('prepare_page__installed_packages_message', 'There are %d installed packages.' % len(installed_packages_list))
    else:
        display.update_status('prepare_page__installed_packages', ERROR)
        display.update_label('prepare_page__installed_packages_message', 'Error. Unable to identify the installed packages.')

    return installed_packages_list


def prepare_typical_manifest(installed_packages_list):

    # Create list of removable packages for a typical install.

    display.update_status('prepare_page__package_manifest_1', PROCESSING)
    sleep(0.50)

    filename = 'filesystem.manifest-remove'
    is_exists = is_exists_filesystem_manifest_remove(filename)
    removable_packages_list = prepare_utilities.get_removable_packages_list(filename) if is_exists else []
    if is_exists:
        display.update_status('prepare_page__package_manifest_1', OK)
        removable_packages_count = len(removable_packages_list)
        if removable_packages_count == 0:
            display.update_label('prepare_page__package_manifest_1_message', 'No packages are flagged for removal after a typical install.')
        elif removable_packages_count == 1:
            display.update_label('prepare_page__package_manifest_1_message', 'One package is flagged for removal after a typical install.')
        else:
            display.update_label('prepare_page__package_manifest_1_message', '%d packages are flagged for removal after a typical install.' % removable_packages_count)
    else:
        display.update_status('prepare_page__package_manifest_1', OK)
        display.update_label('prepare_page__package_manifest_1_message', 'This ISO does not have a list of packages to be removed after a typical install.')

    return removable_packages_list


def prepare_minimal_manifest(installed_packages_list):

    # Create list of removable packages for a minimal install.

    display.update_status('prepare_page__package_manifest_2', PROCESSING)
    sleep(0.50)

    filename = 'filesystem.manifest-minimal-remove'
    is_exists = is_exists_filesystem_manifest_remove(filename)
    removable_packages_list = prepare_utilities.get_removable_packages_list(filename) if is_exists else []
    if is_exists:
        display.update_status('prepare_page__package_manifest_2', OK)
        removable_packages_count = len(removable_packages_list)
        if removable_packages_count == 0:
            display.update_label('prepare_page__package_manifest_2_message', 'No packages are flagged for removal after a minimal install.')
        elif removable_packages_count == 1:
            display.update_label('prepare_page__package_manifest_2_message', 'One package is flagged for removal after a minimal install.')
        else:
            display.update_label('prepare_page__package_manifest_2_message', '%d packages are flagged for removal after a minimal install.' % removable_packages_count)
    else:
        display.update_status('prepare_page__package_manifest_2', OK)
        display.update_label('prepare_page__package_manifest_2_message', 'This ISO does not have a list of packages to be removed after a minimal install.')

    return removable_packages_list


def save_package_manifest(installed_packages_list, removable_packages_list_1, removable_packages_list_2):

    # TODO: We assume this file is created successfully. Should we catch an error and display a message?

    display.update_status('prepare_page__save_package_manifest', PROCESSING)
    sleep(0.50)

    # Save the filesystem manifest file.
    prepare_utilities.create_filesystem_manifest_file(installed_packages_list)

    # Create list of package details for typical and minimal installs.

    package_details_list = prepare_utilities.create_package_details_list(installed_packages_list, removable_packages_list_1, removable_packages_list_2)

    display.update_list_store('packages_page__list_store', package_details_list)

    if removable_packages_list_2:
        display.set_column_visible('packages_page__remove_2_treeviewcolumn', True)
    else:
        display.set_column_visible('packages_page__remove_2_treeviewcolumn', False)

    # TODO: This should be a part of the packages_page.
    model.undo_index = 0
    model.undo_list = []

    display.update_status('prepare_page__save_package_manifest', OK)
    display.update_label('prepare_page__save_package_manifest_message', 'Saved the package manifest file.')

    return package_details_list


#-----------------------------------------------------------------------
# Kernels
#-----------------------------------------------------------------------


def create_kernel_details_list():

    display.update_status('prepare_page__iso_boot_kernels', PROCESSING)
    sleep(0.50)

    # Get the list of linux kernels.
    # .../custom-root/boot/vmlinuz-*; initrd.img-*
    directory_1 = os.path.join(model.project.custom_root_directory, 'boot')

    # .../source-disk/casper/vmlinuz.efi; initrd.lz
    directory_2 = os.path.join(model.project.iso_mount_point, model.status.casper_directory)

    kernel_details_list = prepare_utilities.create_kernel_details_list(directory_1, directory_2)

    display.update_status('prepare_page__iso_boot_kernels', OK)
    display.update_label('prepare_page__iso_boot_kernels_message', 'Found %d valid ISO boot kernels.' % len(kernel_details_list))

    return kernel_details_list


def prepare_linux_kernels(kernel_details_list):

    if kernel_details_list:

        # TODO: See if this code can be replaced with elements in cubic.ui
        # REFERENCE: https://whyareyoureadingthisurl.wordpress.com/2012/01/21/howto-pack-gtk-cellrenderers-vertically-in-a-gtk-treeview/
        import gi
        gi.require_version('Gtk', '3.0')
        from gi.repository import Gtk
        column = model.builder.get_object('options_page__linux_kernels_tab__treeviewcolumn_2')
        area = column.get_area()
        area.set_orientation(Gtk.Orientation.VERTICAL)

        # Because Python < 3.7 does not guarantee that the order of
        # dictionary elements is preserved when using the value() method.
        # Instead of simply using list(kernel_details.values()), it is
        # necessary to explicitly add each dictionary element to the new
        # list.
        #
        # https://bugs.launchpad.net/cubic/+bug/1860345
        # https://bugs.launchpad.net/cubic/+bug/1860682
        # https://stackoverflow.com/questions/1867861/how-to-keep-keys-values-in-same-order-as-declared
        #
        # display.update_list_store(
        #     'options_page__linux_kernels_tab__list_store',
        #     [
        #         list(kernel_details.values())
        #         for kernel_details in kernel_details_list
        #     ])
        #
        # 0: version_name
        # 1: vmlinuz_filename
        # 2: new_vmlinuz_filename
        # 3: initrd_filename
        # 4: new_initrd_filename
        # 5: directory
        # 6: note
        # 7: is_selected
        # 8: is_remove
        display.update_list_store(
            'options_page__linux_kernels_tab__list_store',
            [
                [
                    kernel_details['version_name'],
                    kernel_details['vmlinuz_filename'],
                    kernel_details['new_vmlinuz_filename'],
                    kernel_details['initrd_filename'],
                    kernel_details['new_initrd_filename'],
                    kernel_details['directory'],
                    kernel_details['note'],
                    kernel_details['is_selected'],
                    kernel_details['is_remove']
                ] for kernel_details in kernel_details_list
            ])

        return False

    else:

        return True


#-----------------------------------------------------------------------
# Preseed
#-----------------------------------------------------------------------


def prepare_preseed():

    display.update_status('prepare_page__preseed_files', PROCESSING)
    sleep(0.50)

    stack_name = 'options_page__preseed_tab__stack'

    model.delete_list = []
    # TODO: Only read text files.
    search_filepath = os.path.join(model.project.custom_disk_directory, 'preseed', '*')
    filepaths = glob.glob(search_filepath)
    filepaths.sort()

    display.add_to_stack(stack_name, filepaths)

    if filepaths:

        # Stack create button
        display.set_sensitive('options_page__create_button', True)

        # Stack delete button
        display.set_sensitive('options_page__delete_button', True)

        # Stack
        display.set_visible('options_page__preseed_tab__stack', True)

        # Create box
        # display.update_entry('options_page__preseed_tab__create_grid__entry', '')
        # display.update_label('options_page__preseed_tab__create_grid__error_label', '')
        display.set_visible('options_page__preseed_tab__create_grid', False)

        # Delete box
        # display.update_entry('options_page__preseed_tab__delete_grid__entry', '')
        # display.update_label('options_page__preseed_tab__delete_grid__error_label', '')
        display.set_visible('options_page__preseed_tab__delete_grid', False)

        display.update_status('prepare_page__preseed_files', OK)
        if len(filepaths) == 1:
            display.update_label('prepare_page__preseed_files_message', 'Found one preseed file.')
        else:
            display.update_label('prepare_page__preseed_files_message', 'Found %d preseed files.' % len(filepaths))

        sleep(0.50)

        return False

    else:

        # Stack create button
        display.set_sensitive('options_page__create_button', True)

        # Stack delete button
        display.set_sensitive('options_page__delete_button', False)

        # Stack
        display.set_visible('options_page__preseed_tab__stack', False)

        # Create box
        display.update_entry('options_page__preseed_tab__create_grid__entry', '')
        display.update_label('options_page__preseed_tab__create_grid__error_label', '')
        display.set_visible('options_page__preseed_tab__create_grid', True)

        # Delete box
        # display.update_entry('options_page__preseed_tab__delete_grid__entry', '')
        # display.update_label('options_page__preseed_tab__delete_grid__error_label', '')
        display.set_visible('options_page__preseed_tab__delete_grid', False)

        display.update_status('prepare_page__preseed_files', display.OPTIONAL)
        display.update_label('prepare_page__preseed_files_message', 'Did not find any preseed files.')

        sleep(0.50)

        return False


#-----------------------------------------------------------------------
# Boot Configurations
#-----------------------------------------------------------------------


def prepare_boot_configuration(kernel_details_list):

    display.update_status('prepare_page__iso_boot_configurations', PROCESSING)
    sleep(0.50)

    if kernel_details_list:

        filepaths = []
        for boot_configuration in model.options.boot_configurations:
            filepath = os.path.join(model.project.custom_disk_directory, boot_configuration)
            filepaths.append(filepath)

        # Get the selected kernel.
        for selected_index, kernel_details in enumerate(kernel_details_list):
            if kernel_details['is_selected']: break
        else: selected_index = 0
        logger.log_value('The selected kernel is index number', selected_index)

        # Add files to the stack, and search and replace text.
        stack_name = 'options_page__boot_configuration_tab__stack'

        # The contents of the boot configurations files is also replaced in
        # handlers.on_toggled__options_page__linux_kernels_tab__radio_button()
        # and utilities.update_and_save_boot_configurations().

        # search_text_1 = r'/vmlinuz\S*'
        # replacement_text_1 = '/%s' % kernel_details_list[selected_index]['new_vmlinuz_filename']
        search_text_1 = r'(linux.*)vmlinuz\S*'
        replacement_text_1 = r'\1%s' % kernel_details_list[selected_index]['new_vmlinuz_filename']

        search_text_2 = r'(kernel.*)vmlinuz\S*'
        replacement_text_2 = r'\1%s' % kernel_details_list[selected_index]['new_vmlinuz_filename']

        # search_text_3 = r'/initrd\S*'
        # replacement_text_3 = '/%s' % kernel_details_list[selected_index]['new_initrd_filename']
        search_text_3 = r'(initrd.*)initrd\S*'
        replacement_text_3 = r'\1%s' % kernel_details_list[selected_index]['new_initrd_filename']

        # Note: This won't work if boot appears between linux and vmlinuz.
        search_text_4 = r'(linux.*vmlinuz\S*\s*)(?!.*boot=)'
        replacement_text_4 = r'\1boot=casper '

        search_text_5 = r'(append\s*)(?!.*boot=)'
        replacement_text_5 = r'\1boot=casper '

        display.add_to_stack(
            stack_name,
            filepaths,
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

        # TODO: better way to check for errors.

        display.update_status('prepare_page__iso_boot_configurations', OK)
        if len(filepaths) == 1:
            display.update_label('prepare_page__iso_boot_configurations_message', 'Found one ISO boot configuration file.')
        else:
            display.update_label('prepare_page__iso_boot_configurations_message', 'Found %d ISO boot configuration files.' % len(filepaths))

        return False

    else:

        display.update_status('prepare_page__iso_boot_configurations', ERROR)
        display.update_label('prepare_page__iso_boot_configurations_message', 'Error. Did not find any ISO boot configuration files.')

        return True


# TODO: This function is needed on multiple pages. Consider refactoring.
#       - extract_page
#       - generate_page
#       - options_page
def is_exists_filesystem_manifest_remove(filename):

    # Check custom live iso directory
    filepath = os.path.join(model.project.custom_disk_directory, model.status.casper_directory, filename)

    is_exists = os.path.exists(filepath)
    if is_exists:
        logger.log_value('%s found in' % filename, os.path.join(model.project.custom_disk_directory, model.status.casper_directory))
        return True
    else:
        logger.log_value('%s not found in' % filename, os.path.join(model.project.custom_disk_directory, model.status.casper_directory))
        return False
