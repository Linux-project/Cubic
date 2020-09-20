#!/usr/bin/python3

########################################################################
#                                                                      #
# model.py                                                             #
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
# but WITHOUT ANY WARRANTY, without even the implied warranty of       #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the         #
# GNU General Public License for more details.                         #
#                                                                      #
# You should have received a copy of the GNU General Public License    #
# along with Cubic. If not, see <http://www.gnu.org/licenses/>.        #
#                                                                      #
########################################################################

from utilities.fields import Fields

########################################################################
# References
########################################################################

# N/A

########################################################################
# Application
########################################################################

builder = None
page = None

application = Fields('application')
application.directory = None
application.user_home = None
application.cubic_version = None
application.kernel_version = None

########################################################################
# Project
########################################################################

project = Fields('project')
project.cubic_version = None
project.create_date = None
project.modify_date = None
project.directory = None
project.configuration_filepath = None
project.iso_mount_point = None
project.custom_root_directory = None
project.custom_disk_directory = None

########################################################################
# Original
########################################################################

original = Fields('original')
original.iso_filename = None
original.iso_directory = None
original.iso_volume_id = None
original.iso_release_name = None
original.iso_disk_name = None

########################################################################
# Custom
########################################################################

custom = Fields('custom')
custom.iso_version_number = None
custom.iso_filename = None
custom.iso_directory = None
custom.iso_volume_id = None
custom.iso_release_name = None
custom.iso_disk_name = None

########################################################################
# Status
########################################################################

status = Fields('status')
status.is_success_copy = False
status.is_success_extract = False
status.casper_directory = None
status.iso_checksum = None
status.iso_checksum_filename = None

########################################################################
# Options
########################################################################

# TODO: Consider moving this to "Status"
options = Fields('options')
options.boot_configurations = None
options.compression = None

########################################################################
# Page Specific
########################################################################

# Terminal Page --> Copy Page
# Used to exchange information between the Terminal page and the Copy
# page. This value is initialized whenever files are dragged onto the
# terminal or whenever files are selected for copying from the Terminal
# page.
uris = None

# Prepare Page --> Options Page --> Generate Page
# Used to exchange information between the Prepare page, the Options
# page and the Generate page to indicate which preseed files should be
# deleted. This value is initialized to an empty list on the Prepare
# page, when a new preseed file list is created.
# TODO: Instead of initializing this value on the Prepare page, we could
#  set this to [] in the Options page's setup function on action 'next',
# since we are guaranteed that the preseed list is a new list, created
# on the Prepare page.
delete_list = None

########################################################################
# Page Help
########################################################################

help_urls = {
    'start_page': 'https://answers.launchpad.net/cubic/+faq/3232',
    'migrate_page': 'https://answers.launchpad.net/cubic/+faq/3230',
    'project_page': 'https://answers.launchpad.net/cubic/+faq/3229',
    'delete_page': 'https://answers.launchpad.net/cubic/+faq/3228',
    'extract_page': 'https://answers.launchpad.net/cubic/+faq/3227',
    'terminal_page': 'https://answers.launchpad.net/cubic/+faq/3226',
    'copy_page': 'https://answers.launchpad.net/cubic/+faq/3225',
    'prepare_page': 'https://answers.launchpad.net/cubic/+faq/3224',
    'packages_page': 'https://answers.launchpad.net/cubic/+faq/3223',
    'options_page': 'https://answers.launchpad.net/cubic/+faq/3222',
    'compression_page': 'https://answers.launchpad.net/cubic/+faq/3221',
    'generate_page': 'https://answers.launchpad.net/cubic/+faq/3220',
    'finish_page': 'https://answers.launchpad.net/cubic/+faq/3219'
}
