#!/usr/bin/python3

########################################################################
#                                                                      #
# configuration.py                                                     #
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

from constants import NEW_CUBIC_VERSION
from constants import DEFAULT_BOOT_CONFIGURATIONS_STRING
from utilities import logger
from utilities import model

import configparser

########################################################################
# Globals & Constants
########################################################################

config_parser = None

########################################################################
# Support Functions
########################################################################


def get_value(section, key, default=None):

    return config_parser.get(section, key, fallback=default)


def get_boolean(section, key, default=False):

    return config_parser.getboolean(section, key, fallback=default)


def save_value(section, key, value):

    # Set the section, key, and value.

    if not config_parser.has_section(section):
        config_parser.add_section(section)

    if type(value) is str:
        config_parser.set(section, key, value)
    elif type(value) is bool:
        config_parser.set(section, key, str(value))
    elif type(value) is tuple:
        config_parser.set(section, key, ','.join(value))
    elif type(value) is list:
        config_parser.set(section, key, ','.join(value))
    else:
        config_parser.set(section, key, value)

    # Write the configuration file.
    with open(model.project.configuration_filepath, 'w') as configuration_file:
        config_parser.write(configuration_file)


########################################################################
# Initialize Functions
########################################################################


def initialize():

    _initialize_2020_layout()


def _initialize_2019_layout():
    """
    This function is not used.
    """

    logger.log_value('Initialize configuration', '2019 Layout')

    global config_parser

    # Create a new configuration.
    config_parser = configparser.ConfigParser(allow_no_value=True)
    config_parser.optionxform = str

    # Create sections.
    config_parser.add_section('General')
    config_parser.add_section('Original')
    config_parser.add_section('Custom')
    config_parser.add_section('Status')
    config_parser.add_section('Options')


def _initialize_2020_layout():

    logger.log_value('Initialize configuration', '2020 Layout')

    global config_parser

    # Create a new configuration.
    config_parser = configparser.ConfigParser(allow_no_value=True)
    config_parser.optionxform = str

    # Create sections.
    config_parser.add_section('Project')
    config_parser.add_section('Original')
    config_parser.add_section('Custom')
    config_parser.add_section('Status')
    config_parser.add_section('Options')


########################################################################
# Load Functions
########################################################################


def load():

    logger.log_label('Load configuration')

    # Create a new configuration.
    global config_parser
    config_parser = configparser.ConfigParser(allow_no_value=True)
    config_parser.optionxform = str

    # Read the configuration file.
    config_parser.read(model.project.configuration_filepath)

    # Get Cubic the version.
    if config_parser.has_section('Project'):
        # Using newer Cubic version.
        model.project.cubic_version = config_parser.get('Project', 'cubic_version')
    elif config_parser.has_section('General'):
        # Using older Cubic version.
        model.project.cubic_version = config_parser.get('General', 'cubic_version')
    else:
        # TODO: Error
        pass

    # Load values from the configuration.
    # (Add new layouts here, based on the version).
    print('model.project.cubic_version = %s' % model.project.cubic_version)

    if model.project.cubic_version < NEW_CUBIC_VERSION:
        _load_from_2019_layout()
    else:
        _load_from_2020_layout()


def _load_from_2020_layout():

    logger.log_value('Load configuration', '2020 Layout')

    # The following fields must be set prior to invoking this function:
    # 1. model.project.cubic_version
    # 2. model.project.directory

    # Project
    # model.project.cubic_version = get_value('Project', 'cubic_version')
    # model.project.directory = get_value('Project', 'directory')

    # Original
    model.original.iso_filename = get_value('Original', 'iso_filename')
    model.original.iso_directory = get_value('Original', 'iso_directory')
    model.original.iso_volume_id = get_value('Original', 'iso_volume_id')[:32]
    model.original.iso_release_name = get_value('Original', 'iso_release_name')
    model.original.iso_disk_name = get_value('Original', 'iso_disk_name')

    # Custom
    model.custom.iso_version_number = get_value('Custom', 'iso_version_number')
    model.custom.iso_filename = get_value('Custom', 'iso_filename')
    model.custom.iso_directory = get_value('Custom', 'iso_directory')
    model.custom.iso_volume_id = get_value('Custom', 'iso_volume_id')[:32]
    model.custom.iso_release_name = get_value('Custom', 'iso_release_name')
    model.custom.iso_disk_name = get_value('Custom', 'iso_disk_name')

    # Status
    model.status.is_success_copy = get_boolean('Status', 'is_success_copy', default=False)
    model.status.is_success_extract = get_boolean('Status', 'is_success_extract', default=False)
    model.status.casper_directory = get_value('Status', 'casper_directory', default=None)
    model.status.iso_checksum = get_value('Status', 'iso_checksum', default=None)
    model.status.iso_checksum_filename = get_value('Status', 'iso_checksum_filename', default=None)

    # Options
    boot_configurations_string = get_value('Options', 'boot_configurations', default=DEFAULT_BOOT_CONFIGURATIONS_STRING)
    model.options.boot_configurations = [boot_configuration.strip().strip('/') for boot_configuration in boot_configurations_string.split(',')]


def _load_from_2019_layout():

    logger.log_value('Load configuration', '2019 Layout')

    # The following fields must be set prior to invoking this function:
    # 1. model.project.cubic_version
    # 2. model.project.directory

    # General -> Project
    # model.project.cubic_version = get_value('General', 'cubic_version')
    # model.project.directory = get_value('General', 'project_directory')

    # Original
    model.original.iso_filename = get_value('Original', 'original_iso_image_filename')
    model.original.iso_directory = get_value('Original', 'original_iso_image_directory')
    model.original.iso_volume_id = get_value('Original', 'original_iso_image_volume_id')[:32]
    model.original.iso_release_name = get_value('Original', 'original_iso_image_release_name')
    model.original.iso_disk_name = get_value('Original', 'original_iso_image_disk_name')

    # Custom
    model.custom.iso_version_number = get_value('Custom', 'custom_iso_image_version_number')
    model.custom.iso_filename = get_value('Custom', 'custom_iso_image_filename')
    model.custom.iso_directory = get_value('Custom', 'custom_iso_image_directory')
    model.custom.iso_volume_id = get_value('Custom', 'custom_iso_image_volume_id')[:32]
    model.custom.iso_release_name = get_value('Custom', 'custom_iso_image_release_name')
    model.custom.iso_disk_name = get_value('Custom', 'custom_iso_image_disk_name')

    # Status
    model.status.is_success_copy = get_boolean('Status', 'is_success_copy_original_iso_files', default=False)
    model.status.is_success_extract = get_boolean('Status', 'is_success_extract_squashfs', default=False)
    # Not in the original 2019 layout.
    model.status.casper_directory = get_value('Status', 'casper_directory')
    # Not in the original 2019 layout.
    model.status.iso_checksum = get_value('Custom', 'custom_iso_image_checksum')
    # In the Custom section of the 2019 layout.
    model.status.iso_checksum_filename = get_value('Custom', 'custom_iso_image_md5_filename')

    # Options
    boot_configurations_string = get_value('Options', 'boot_configurations', default=DEFAULT_BOOT_CONFIGURATIONS_STRING)
    model.options.boot_configurations = [boot_configuration.strip().strip('/') for boot_configuration in boot_configurations_string.split(',')]


########################################################################
# Save Functions
########################################################################


def save():

    logger.log_label('Save configuration')

    if model.project.cubic_version < NEW_CUBIC_VERSION:
        model.project.cubic_version = model.application.cubic_version
        _initialize_2020_layout()
        _save_using_2020_layout()
    else:
        model.project.cubic_version = model.application.cubic_version
        _save_using_2020_layout()


def _save_using_2019_layout():
    """
    This function is not used.
    """

    logger.log_value('Save configuration', '2019 Layout')

    # Project
    config_parser.set('General', 'cubic_version', model.project.cubic_version)
    config_parser.set('General', 'project_directory', model.project.directory)

    # Original
    config_parser.set('Original', 'original_iso_image_filename', model.original.iso_filename)
    config_parser.set('Original', 'original_iso_image_directory', model.original.iso_directory)
    config_parser.set('Original', 'original_iso_image_volume_id', model.original.iso_volume_id)
    config_parser.set('Original', 'original_iso_image_release_name', model.original.iso_release_name)
    config_parser.set('Original', 'original_iso_image_disk_name', model.original.iso_disk_name)

    # Custom
    config_parser.set('Custom', 'custom_iso_image_version_number', model.custom.iso_version_number)
    config_parser.set('Custom', 'custom_iso_image_filename', model.custom.iso_filename)
    config_parser.set('Custom', 'custom_iso_image_directory', model.custom.iso_directory)
    config_parser.set('Custom', 'custom_iso_image_volume_id', model.custom.iso_volume_id)
    config_parser.set('Custom', 'custom_iso_image_release_name', model.custom.iso_release_name)
    config_parser.set('Custom', 'custom_iso_image_disk_name', model.custom.iso_disk_name)

    # Status
    config_parser.set('Status', 'is_success_copy', str(bool(model.status.is_success_copy)))
    config_parser.set('Status', 'is_success_extract', str(bool(model.status.is_success_extract)))
    # Not in the original 2019 layout.
    config_parser.set('Status', 'casper_directory', str(model.status.casper_directory))
    # Not in the original 2019 layout.
    config_parser.set('Status', 'custom_iso_image_checksum', str(model.status.iso_checksum))
    # In the Custom section of the 2019 layout.
    config_parser.set('Custom', 'custom_iso_image_md5_filename', str(model.status.iso_checksum_filename))

    # Save options values.
    boot_configurations_string = ','.join(boot_configuration.strip(' /') for boot_configuration in model.options.boot_configurations)
    config_parser.set('Options', 'boot_configurations', boot_configurations_string)

    # Write the configuration file.
    with open(model.project.configuration_filepath, 'w') as configuration_file:
        config_parser.write(configuration_file)


def _save_using_2020_layout():
    """
    This function should only be called by the save() function.
    """

    logger.log_value('Save configuration', '2020 Layout')

    # Save project values.
    config_parser.set('Project', 'cubic_version', model.project.cubic_version)
    config_parser.set('Project', 'directory', model.project.directory)

    # Save original values.
    config_parser.set('Original', 'iso_filename', model.original.iso_filename)
    config_parser.set('Original', 'iso_directory', model.original.iso_directory)
    config_parser.set('Original', 'iso_volume_id', model.original.iso_volume_id)
    config_parser.set('Original', 'iso_release_name', model.original.iso_release_name)
    config_parser.set('Original', 'iso_disk_name', model.original.iso_disk_name)

    # Save custom values.
    config_parser.set('Custom', 'iso_version_number', model.custom.iso_version_number)
    config_parser.set('Custom', 'iso_filename', model.custom.iso_filename)
    config_parser.set('Custom', 'iso_directory', model.custom.iso_directory)
    config_parser.set('Custom', 'iso_volume_id', model.custom.iso_volume_id)
    config_parser.set('Custom', 'iso_release_name', model.custom.iso_release_name)
    config_parser.set('Custom', 'iso_disk_name', model.custom.iso_disk_name)

    # Save status values.
    config_parser.set('Status', 'is_success_copy', str(bool(model.status.is_success_copy)))
    config_parser.set('Status', 'is_success_extract', str(bool(model.status.is_success_extract)))
    config_parser.set('Status', 'casper_directory', str(model.status.casper_directory))
    config_parser.set('Status', 'iso_checksum', str(model.status.iso_checksum))
    config_parser.set('Status', 'iso_checksum_filename', str(model.status.iso_checksum_filename))

    # Save options values.
    boot_configurations_string = ','.join(boot_configuration.strip(' /') for boot_configuration in model.options.boot_configurations)
    config_parser.set('Options', 'boot_configurations', boot_configurations_string)

    # Write the configuration file.
    with open(model.project.configuration_filepath, 'w') as configuration_file:
        config_parser.write(configuration_file)
