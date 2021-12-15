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

########################################################################
# References
########################################################################

# N/A

########################################################################
# Imports
########################################################################

from cubic.utilities.fields import Fields

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
application.projects = None
application.visited_sites = None

########################################################################
# Project
########################################################################

project = Fields('project')
project.cubic_version = None
project.create_date = None
project.modify_date = None
project.directory = None
project.configuration_file_path = None
project.iso_mount_point = None
project.custom_root_directory = None
project.custom_disk_directory = None

########################################################################
# Original
########################################################################

original = Fields('original')
original.iso_file_name = None
original.iso_directory = None
original.iso_volume_id = None
original.iso_release_name = None
original.iso_disk_name = None
original.iso_release_notes_url = None

########################################################################
# Custom
########################################################################

custom = Fields('custom')
custom.iso_version_number = None
custom.iso_file_name = None
custom.iso_directory = None
custom.iso_volume_id = None
custom.iso_release_name = None
custom.iso_disk_name = None
custom.iso_release_notes_url = None

########################################################################
# Status
########################################################################

status = Fields('status')
status.is_success_copy = None
status.is_success_extract = None
status.iso_template = None
status.casper_directory = None
status.squashfs_file_name = None
status.iso_checksum = None
status.iso_checksum_file_name = None

########################################################################
# Generated
########################################################################

generated = Fields('generated')
generated.iso_version_number = None
generated.iso_file_name = None
generated.iso_directory = None
generated.iso_volume_id = None
generated.iso_release_name = None
generated.iso_disk_name = None
generated.iso_release_notes_url = None
# generated.iso_checksum = None
# generated.iso_checksum_file_name = None

########################################################################
# Options
########################################################################

options = Fields('options')
options.update_os_release = None
options.boot_configurations = None
options.compression = None

########################################################################
# Page/Module Specific
########################################################################

#-----------------------------------------------------------------------
# Terminal page, Preseed tab, ISO Boot tab
#-----------------------------------------------------------------------

# Stores the current directory selected on the Terminal page, the
# Preseed tab, or the ISO Boot tab. This is the directory to copy files
# into.
current_directory = None

# Stores the uniform resource identifiers of files selected on the
# Terminal page, the Preseed tab, or the ISO Boot tab. These are the
# files to be copied.
selected_uris = None

#-----------------------------------------------------------------------
# Prepare page, Linux Kernels tab
#-----------------------------------------------------------------------

selected_kernel_index = None

# This is a list of kernel detail dictionaries.
kernel_details_list = None

#-----------------------------------------------------------------------
# Prepare page, Packages page
#-----------------------------------------------------------------------

package_details_list = None

#-----------------------------------------------------------------------
# Prepare page, Packages page, Options page
#-----------------------------------------------------------------------

ubiquity_version = None

#-----------------------------------------------------------------------
# Generate page, Finish page
#-----------------------------------------------------------------------

iso_file_size = None

#-----------------------------------------------------------------------
# Emulator, Test 1 page, Test 2 page
#-----------------------------------------------------------------------

emulator_memory = None
