#!/usr/bin/python3

########################################################################
#                                                                      #
# configuration.py                                                     #
#                                                                      #
# Copyright (C) 2020, 2022 PJ Singh <psingh.cubic@gmail.com>           #
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
"""
Cubic versions:

"Classic" 2019 Version:
  From: Release 2015.11-1  on 11/05/2015
  To:   Release 2020.02-62 on 02/01/2020

"Release" 2020 Version:
  From: Release 2020.04-1  on 04/26/2020
  To:   Release 2020.10-35 on 10/23/2020
  • Renamed the "General" section to "Project"
  • Added new options and renamed options

"Release" 2021 Version:
  From: Release 2020.12-36 on 12/19/2020
  To:   Release 2022.06-72 on 06/30/2022
  • Added the "iso_template option"
  • Renamed both "iso_filename" options to "iso_file_name"
  • Renamed "iso_checksum_filename" option to "iso_checksum_file_name"

"Release" 2022 Version:
  From: Release 2022.11-73 on 11/??/2022
  To:   Release 20??.??-?? on ??/??/20??
  • Added ~/.config/cubic/cubic.conf
"""

########################################################################
# References
########################################################################

# https://docs.python.org/3/library/configparser.html#configparser.ConfigParser.getboolean
# https://pypi.org/project/packaging/

########################################################################
# Imports
########################################################################

import configparser
import os

from abc import ABC, abstractmethod
from packaging import version

from cubic.constants import CUBIC_VERSION_2019, CUBIC_VERSION_2020, CUBIC_VERSION_2021, CUBIC_VERSION_2022
from cubic.utilities import constructor
from cubic.utilities import file_utilities
from cubic.utilities import logger
from cubic.utilities import model

########################################################################
# Global Variables & Constants
########################################################################

# N/A

########################################################################
# Configuration Class
########################################################################


class Configuration(ABC):
    """
    Abstract base class used to read and write a configuration file and
    map its contents to the model. Sections of the configuration file
    appear in the order that they are added. Keys in each section appear
    in the order that they are added.

    Derived classes must implement the following methods to map the
    configuration to the model:
    • _load_model(self) - Load the configuration into the model.
    • _save_model(self) - Copy the model into the configuration.
    """

    # ------------------------------------------------------------------
    # Initialize Methods
    # ------------------------------------------------------------------

    def __init__(self, file_path, *sections):
        """
        Create a configuration with the specified file path and
        sections.

        Arguments:
        self : Configuration
            A derived class of Configuration.
        file_path : str
            The file path of the configuration file.
        sections : list of str
            The sections to be added to the configuration file. Sections
            appear in the order that they are added.

        Returns:
        : Configuration
            An object of a derived class of Configuration.
        """

        # Store the file path.
        self.file_path = file_path

        # Create a new configuration parser.
        self.config_parser = configparser.ConfigParser(allow_no_value=True)
        # Make option names case sensitive.
        self.config_parser.optionxform = str

        # Add sections corresponding to the required layout.
        for section in sections:
            self.config_parser.add_section(section)

    def __repr__(self):
        """
        Get the string representation of this Configuration, which is
        the file path of the configuration file.

        Arguments:
        self : Configuration
            A derived class of Configuration.

        Returns:
        file_path : str
            The file path of the configuration file.
        """

        return self.file_path

    # ------------------------------------------------------------------
    # Load Methods
    # ------------------------------------------------------------------

    def load(self):
        """
        Load the contents of the configuration file into the model. This
        method invokes the _load_model() method of the derived class.

        Arguments:
        self : Configuration
            A derived class of Configuration.
        """

        # Read the configuration file.
        self.config_parser.read(self.file_path)

        # Load the model with values from the configuration.
        self._load_model()

        # Create a new configuration parser because the required layout
        # may be different from the previous layout. (The current
        # configuration parser may be discarded because the model has
        # already been loaded).
        self.config_parser = configparser.ConfigParser(allow_no_value=True)
        # Make option names case sensitive.
        self.config_parser.optionxform = str

    @abstractmethod
    def _load_model(self):
        """
        Load the contents of the configuration file into the model,
        mapping the sections, keys, and values to the the model. This
        method must be implemented in the derived class.

        Arguments:
        self : Configuration
            A derived class of Configuration.
        """

        raise NotImplementedError("Must override the _load_model() abstract method.")

    # ------------------------------------------------------------------
    # Save Methods
    # ------------------------------------------------------------------

    def save(self):
        """
        Write the contents of the mode to the configuration file. This
        method invokes the _save_model() method of the derived class to
        copy the model into the configuration before it is saved.

        Arguments:
        self : Configuration
            A derived class of Configuration.
        """

        # Create the parent directories if they do not exist.
        directory = os.path.dirname(self.file_path)
        file_utilities.make_directories(directory)

        # Copy model fields into the configuration.
        self._save_model()

        # Write the configuration file.
        with open(self.file_path, 'w') as file:
            self.config_parser.write(file)

    @abstractmethod
    def _save_model(self):
        """
        Map the model's sections, keys, and values to the the
        configuration. This method must be implemented in the derived
        class.

        Arguments:
        self : Configuration
            A derived class of Configuration.
        """

        raise NotImplementedError("Must override the _save_model() abstract method.")

    # ------------------------------------------------------------------
    # Get Value Methods
    # ------------------------------------------------------------------

    def get_value(self, section, key, default=None):
        """
        Get the value corresponding to the specified section and key in
        the configuration.

        Arguments:
        self : Configuration
            A derived class of Configuration.
        section : str
            The section in the configuration.
        key : str
            The key in the configuration.
        default : str
            The default value to return if the key is not found. The
            default is None.

        Returns:
        : str
            The value for the specified key and section in the
            configuration. None if the section or key does not exist.
        """

        return self.config_parser.get(section, key, fallback=default)

    def get_boolean(self, section, key, default=False):
        """
        Get the boolean value corresponding to the specified section and
        key in the configuration.

        Arguments:
        self : Configuration
            A derived class of Configuration.
        section : str
            The section in the configuration.
        key : str
            The key in the configuration.
        default : boolean
            The default value to return if the key is not found. The
            default is False.

        Returns:
        : boolean
            The boolean value for the specified key and section in the
            configuration.
            True if the value is '1', 'yes', 'true', or 'on'.
            False if the value is '0', 'no', 'false', or 'off'.
            False if the value is None or the empty string ''.
            False if the section or key does not exist.
        """

        try:
            # The values '1', 'yes', 'true', or 'on' will return True.
            # The values '0', 'no', 'false', or 'off' will return False.
            return self.config_parser.getboolean(section, key, fallback=default)
        except ValueError as exception:
            # Blank will return False.
            return False

    def get_list(self, section, key, default=[]):
        """
        Get the list of values corresponding to the specified section
        and key in the configuration.

        Arguments:
        self : Configuration
            A derived class of Configuration.
        section : str
            The section in the configuration.
        key : str
            The key in the configuration.
        default : list of str
            The default list to return if the key is not found. The
            default is an empty list.

        Returns:
        : list of str
            The list of strings for the specified key and section in the
            configuration.
        """

        values_string = self.config_parser.get(section, key, fallback=None)
        if not values_string or not values_string.strip(): return default

        # Convert a comma delimited string of values to a list of
        # values, removing leading and trailing spaces.
        values = []
        for value in values_string.split(','):
            value = value.strip()
            if value and value not in values:
                values.append(value)
        return values

    # ------------------------------------------------------------------
    # Set Value Methods
    # ------------------------------------------------------------------

    def set(self, section, key, value):
        """
        Set the value corresponding to the specified section and key in
        the configuration. If the section does not exist, it will be
        added. If the key does not exist, it will be added. Sections in
        the configuration file appear in the order that they are
        added, and keys in each section appear in the order that they
        are added.

        Arguments:
        self : Configuration
            A derived class of Configuration.
        section : str
            The section in the configuration. If the section does not
            exist, it will be added.
        key : str
            The key in the configuration. If the key does not exist, it
            will be added.
        value: str, bool, tuple, or list
            The value to set. All values are converted to strings. Lists
            and tuples are converted to comma delimited strings.
        """

        # If the section does not exist, add it.
        if not self.config_parser.has_section(section):
            self.config_parser.add_section(section)

        if type(value) is str:
            self.config_parser.set(section, key, value)
        elif type(value) is bool:
            self.config_parser.set(section, key, str(value))
        elif type(value) is tuple:
            self.config_parser.set(section, key, ', '.join(value))
        elif type(value) is list:
            self.config_parser.set(section, key, ', '.join(value))
        else:
            self.config_parser.set(section, key, value)


########################################################################
# Application Class
########################################################################


class Application(Configuration):
    """
    Stores configuration values for Cubic that must persist across
    application restarts.
    • Load values from the configuration into the model.
    • Save values from the model into the configuration.

    Sections:
    • Application

    The following model fields are persisted when this configuration is
    saved:
    • model.application.cubic_version
      Updated in start_page.setup(), after creating the configuration
    • model.application.visited_sites
      Updated in navigator.on_clicked_*() functions
    • model.application.projects
      Updated in start_page.leave()
    • model.application.iso_directory
      Updated in project_page.selected_original_iso_file_path()
    """

    # ------------------------------------------------------------------
    # Initialize Methods
    # ------------------------------------------------------------------

    def __init__(self, file_path):
        """
        Create an Application configuration with the specified file path
        and the following sections:
        • Application

        Arguments:
        self : Configuration
            A derived class of Configuration.
        file_path : str
            The file path of the configuration file.
        """

        super().__init__(file_path, 'Application')

    # ------------------------------------------------------------------
    # Load Methods
    # ------------------------------------------------------------------

    def _load_model(self):
        """
        Load the contents of the configuration file into the application
        model using the appropriate layout.

        Arguments:
        self : Configuration
            A derived class of Configuration.
        """

        logger.log_label('Load application configuration')

        # Get the previous version.
        if not os.path.exists(self.file_path):
            previous_version = CUBIC_VERSION_2021
        else:
            previous_version = self.get_value('Application', 'cubic_version')
            previous_version = constructor.get_display_version(previous_version)

        # Load the model using the correct configuration file layout.
        previous_version = version.parse(previous_version)
        if previous_version < version.parse(CUBIC_VERSION_2022):
            self._load_model_2021_layout()
        else:
            self._load_model_2022_layout()

    def _load_model_2021_layout(self):
        """
        Load the application model from the 2021 configuration file
        layout.

        This method should only be called by the _load_model() method.

        Arguments:
        self : Configuration
            A derived class of Configuration.
        """

        logger.log_value('Load application configuration', '2021 layout from %s' % self.file_path)

        # Cubic version
        # The Cubic version should be set to the running version.
        # Not in the original 2021 layout.
        # model.application.cubic_version = CUBIC_VERSION_2021

        # Visited sites
        file_path = os.path.join(model.application.user_home, '.config', 'cubic', 'visited_sites.conf')
        # For the Cubic version '2022.11.73', ignore all visited sites.
        model.application.visited_sites = []
        # Delete this file because Cubic version '2022.11.73' does not
        # use it.
        file_utilities.delete_file(file_path)

        # Projects
        file_path = os.path.join(model.application.user_home, '.config', 'cubic', 'projects.conf')
        model.application.projects = file_utilities.read_lines(file_path)
        # Delete this file because Cubic version '2022.11.73' does not
        # use it.
        file_utilities.delete_file(file_path)

        # ISO file path
        model.application.iso_file_path = None

        # Configuration
        # model.application.configuration = self

    def _load_model_2022_layout(self):
        """
        Load the application model from the 2022 configuration file
        layout.

        This method should only be called by the _load_model() method.

        Arguments:
        self : Configuration
            A derived class of Configuration.
        """

        logger.log_value('Load application configuration', '2022 layout from %s' % self.file_path)

        # Read the configuration file.
        self.config_parser.read(self.file_path)

        # Cubic version
        # The Cubic version should be set to the running version.
        # model.application.cubic_version = self.get_value('Application', 'cubic_version')

        # Visited sites
        model.application.visited_sites = self.get_list('Application', 'visited_sites')

        # Projects
        model.application.projects = self.get_list('Application', 'projects')

        # ISO directory
        model.application.iso_file_path = self.get_value('Application', 'iso_file_path')

        # Configuration
        # model.application.configuration = self

    # ------------------------------------------------------------------
    # Save Methods
    # ------------------------------------------------------------------

    def _save_model(self):
        """
        This method should only be called by the save() method.

        Save the contents of the application model to the configuration
        file using the appropriate layout.

        Arguments:
        self : Configuration
            A derived class of Configuration.
        """

        logger.log_label('Save application configuration')

        # Save using the current layout.
        self._save_model_2022_layout()

    def _save_model_2022_layout(self):
        """
        Save the application model to the 2022 configuration file layout.

        This method should only be called by the _save_model() method.
        Be sure to specify the correct sections in the __init__()
        method.

        Arguments:
        self : Configuration
            A derived class of Configuration.
        """

        logger.log_value('Save application configuration', '2022 layout to %s' % self.file_path)

        # Save application values.
        self.set('Application', 'cubic_version', model.application.cubic_version)
        self.set('Application', 'visited_sites', model.application.visited_sites)
        self.set('Application', 'projects', model.application.projects)
        self.set('Application', 'iso_file_path', model.application.iso_file_path)


########################################################################
# Project Class
########################################################################


class Project(Configuration):
    """
    Stores configuration values for each Cubic project.
    • Load values from the configuration into the model.
    • Save values from the model into the configuration.

    Sections:
    • Project
    • Original
    • Custom
    • Status
    • Options
    """

    # ------------------------------------------------------------------
    # Initialize Methods
    # ------------------------------------------------------------------

    def __init__(self, file_path):
        """
        Create a Project configuration with the specified file path and
        the following sections:
        • Project
        • Original
        • Custom
        • Status
        • Options

        Arguments:
        self : Configuration
            A derived class of Configuration.
        file_path : str
            The file path of the configuration file.
        """

        super().__init__(file_path, 'Project', 'Original', 'Custom', 'Status', 'Options')

    # ------------------------------------------------------------------
    # Load Methods
    # ------------------------------------------------------------------

    def _load_model(self):
        """
        Load the contents of the configuration file into the project
        model using the appropriate layout.

        Arguments:
        self : Configuration
            A derived class of Configuration.
        """

        logger.log_label('Load project configuration')

        # Get the previous version.
        if self.config_parser.has_section('General'):
            # Configuration has 'General' section.
            previous_version = CUBIC_VERSION_2019
        else:
            # Configuration has 'Project' section.
            previous_version = self.get_value('Project', 'cubic_version')
            previous_version = constructor.get_display_version(previous_version)

        # Load the model using the correct configuration file layout.
        previous_version = version.parse(previous_version)
        if previous_version < version.parse(CUBIC_VERSION_2020):
            # Classic or 2019 layout.
            self._load_model_2019_layout()
        elif previous_version < version.parse(CUBIC_VERSION_2021):
            self._load_model_2020_layout()
        elif previous_version < version.parse(CUBIC_VERSION_2022):
            self._load_model_2021_layout()
        else:
            self._load_model_2022_layout()

    def _load_model_2019_layout(self):
        """
        Load the project model from the 2019 configuration file layout.

        This method should only be called by the _load_model() method.

        Arguments:
        self : Configuration
            A derived class of Configuration.
        """

        logger.log_value('Load project configuration', '2019 layout from %s' % self.file_path)

        # The following fields must be set prior to invoking this method:
        # 1. model.project.directory

        # General -> Project
        model.project.cubic_version = self.get_value('General', 'cubic_version')
        # Not in the original 2019 layout.
        model.project.create_date = constructor.get_file_time_stamp(self.file_path)
        # Not in the original 2019 layout.
        model.project.modify_date = model.project.create_date
        # model.project.directory = self.get_value('General', 'project_directory')
        # model.project.configuration = self

        # Original
        model.original.iso_file_name = self.get_value('Original', 'original_iso_image_filename')
        model.original.iso_directory = self.get_value('Original', 'original_iso_image_directory')
        model.original.iso_volume_id = self.get_value('Original', 'original_iso_image_volume_id')[:32]
        model.original.iso_release_name = self.get_value('Original', 'original_iso_image_release_name')
        model.original.iso_disk_name = self.get_value('Original', 'original_iso_image_disk_name')

        # Custom
        model.custom.iso_version_number = self.get_value('Custom', 'custom_iso_image_version_number')
        model.custom.iso_file_name = self.get_value('Custom', 'custom_iso_image_filename')
        model.custom.iso_directory = self.get_value('Custom', 'custom_iso_image_directory')
        model.custom.iso_volume_id = self.get_value('Custom', 'custom_iso_image_volume_id')[:32]
        model.custom.iso_release_name = self.get_value('Custom', 'custom_iso_image_release_name')
        model.custom.iso_disk_name = self.get_value('Custom', 'custom_iso_image_disk_name')

        # Status
        model.status.is_success_copy = self.get_boolean('Status', 'is_success_copy_original_iso_files', default=False)
        model.status.is_success_extract = self.get_boolean('Status', 'is_success_extract_squashfs', default=False)
        # Not in the original 2019 layout.
        model.status.iso_template = self.get_value('Status', 'iso_template', default=None)

        # Not in the original 2019 layout.
        model.status.squashfs_directory = self.get_value('Status', 'squashfs_directory', default=None)
        # Not in the original 2019 layout.
        model.status.squashfs_file_name = self.get_value('Status', 'squashfs_file_name', default=None)
        # Not in the original 2019 layout.
        model.status.casper_directory = self.get_value('Status', 'casper_directory', default=None)
        # Not in the original 2019 layout.
        model.status.iso_checksum = self.get_value('Custom', 'custom_iso_image_checksum', default=None)
        # In the Custom section of the 2019 layout.
        model.status.iso_checksum_file_name = self.get_value('Custom', 'custom_iso_image_md5_filename', default=None)

        # Options
        # Not in the original 2019 layout.
        model.options.update_os_release = self.get_boolean('Options', 'update_os_release', default=True)
        model.options.boot_configurations = self.get_list('Options', 'boot_configurations', default=None)
        # Not in the original 2019 layout.
        model.options.compression = self.get_value('Options', 'compression', default=None)

    def _load_model_2020_layout(self):
        """
        Load the project model from the 2020 configuration file layout.

        This method should only be called by the _load_model() method.

        Arguments:
        self : Configuration
            A derived class of Configuration.
        """

        logger.log_value('Load project configuration', '2020 layout from %s' % self.file_path)

        # The following fields must be set prior to invoking this method:
        # 1. model.project.directory

        # Project
        model.project.cubic_version = self.get_value('Project', 'cubic_version')
        model.project.create_date = self.get_value('Project', 'create_date')
        model.project.modify_date = self.get_value('Project', 'modify_date')
        # model.project.directory = self.get_value('Project', 'directory')
        # model.project.configuration = self

        # Original
        model.original.iso_file_name = self.get_value('Original', 'iso_filename')
        model.original.iso_directory = self.get_value('Original', 'iso_directory')
        model.original.iso_volume_id = self.get_value('Original', 'iso_volume_id')[:32]
        model.original.iso_release_name = self.get_value('Original', 'iso_release_name')
        model.original.iso_disk_name = self.get_value('Original', 'iso_disk_name')

        # Custom
        model.custom.iso_version_number = self.get_value('Custom', 'iso_version_number')
        model.custom.iso_file_name = self.get_value('Custom', 'iso_filename')
        model.custom.iso_directory = self.get_value('Custom', 'iso_directory')
        model.custom.iso_volume_id = self.get_value('Custom', 'iso_volume_id')[:32]
        model.custom.iso_release_name = self.get_value('Custom', 'iso_release_name')
        model.custom.iso_disk_name = self.get_value('Custom', 'iso_disk_name')

        # Status
        model.status.is_success_copy = self.get_boolean('Status', 'is_success_copy', default=False)
        model.status.is_success_extract = self.get_boolean('Status', 'is_success_extract', default=False)
        # Not in the original 2020 layout.
        model.status.iso_template = self.get_value('Status', 'iso_template', default=None)
        # Not in the original 2020 layout.
        model.status.squashfs_directory = self.get_value('Status', 'squashfs_directory', default=None)
        # Not in the original 2020 layout.
        model.status.squashfs_file_name = self.get_value('Status', 'squashfs_file_name', default=None)
        model.status.casper_directory = self.get_value('Status', 'casper_directory', default=None)
        model.status.iso_checksum = self.get_value('Status', 'iso_checksum', default=None)
        model.status.iso_checksum_file_name = self.get_value('Status', 'iso_checksum_filename', default=None)

        # Options
        # Not in the original 2020 layout.
        model.options.update_os_release = self.get_boolean('Options', 'update_os_release', default=True)
        model.options.boot_configurations = self.get_list('Options', 'boot_configurations', default=None)
        model.options.compression = self.get_value('Options', 'compression', default=None)

    def _load_model_2021_layout(self):
        """
        Load the project model from the 2021 configuration file layout.

        This method should only be called by the _load_model() method.

        Arguments:
        self : Configuration
            A derived class of Configuration.
        """

        logger.log_value('Load project configuration', '2021 layout from %s' % self.file_path)

        # The following fields must be set prior to invoking this method:
        # 1. model.project.directory

        # Project
        model.project.cubic_version = self.get_value('Project', 'cubic_version')
        model.project.create_date = self.get_value('Project', 'create_date')
        model.project.modify_date = self.get_value('Project', 'modify_date')
        # model.project.directory = self.get_value('Project', 'directory')
        # model.project.configuration = self

        # Original
        model.original.iso_file_name = self.get_value('Original', 'iso_file_name')
        model.original.iso_directory = self.get_value('Original', 'iso_directory')
        model.original.iso_volume_id = self.get_value('Original', 'iso_volume_id')[:32]
        model.original.iso_release_name = self.get_value('Original', 'iso_release_name')
        model.original.iso_disk_name = self.get_value('Original', 'iso_disk_name')

        # Custom
        model.custom.iso_version_number = self.get_value('Custom', 'iso_version_number')
        model.custom.iso_file_name = self.get_value('Custom', 'iso_file_name')
        model.custom.iso_directory = self.get_value('Custom', 'iso_directory')
        model.custom.iso_volume_id = self.get_value('Custom', 'iso_volume_id')[:32]
        model.custom.iso_release_name = self.get_value('Custom', 'iso_release_name')
        model.custom.iso_disk_name = self.get_value('Custom', 'iso_disk_name')

        # Status
        model.status.is_success_copy = self.get_boolean('Status', 'is_success_copy', default=False)
        model.status.is_success_extract = self.get_boolean('Status', 'is_success_extract', default=False)
        model.status.iso_template = self.get_value('Status', 'iso_template', default=None)
        # Not in the original 2021 layout.
        model.status.squashfs_directory = self.get_value('Status', 'squashfs_directory', default=None)
        # Not in the original 2021 layout.
        model.status.squashfs_file_name = self.get_value('Status', 'squashfs_file_name', default=None)
        model.status.casper_directory = self.get_value('Status', 'casper_directory', default=None)
        model.status.iso_checksum = self.get_value('Status', 'iso_checksum', default=None)
        model.status.iso_checksum_file_name = self.get_value('Status', 'iso_checksum_file_name', default=None)

        # Options
        # Not in the original 2021 layout.
        model.options.update_os_release = self.get_boolean('Options', 'update_os_release', default=True)
        model.options.boot_configurations = self.get_list('Options', 'boot_configurations', default=None)
        model.options.compression = self.get_value('Options', 'compression', default=None)

    def _load_model_2022_layout(self):
        """
        Load the project model from the 2022 configuration file layout.

        This method should only be called by the _load_model() method.

        Arguments:
        self : Configuration
            A derived class of Configuration.
        """

        logger.log_value('Load project configuration', '2022 layout from %s' % self.file_path)

        # The following fields must be set prior to invoking this method:
        # 1. model.project.directory

        # Project
        model.project.cubic_version = self.get_value('Project', 'cubic_version')
        model.project.create_date = self.get_value('Project', 'create_date')
        model.project.modify_date = self.get_value('Project', 'modify_date')
        # model.project.directory = self.get_value('Project', 'directory')
        # model.project.configuration = self

        # Original
        model.original.iso_file_name = self.get_value('Original', 'iso_file_name')
        model.original.iso_directory = self.get_value('Original', 'iso_directory')
        model.original.iso_volume_id = self.get_value('Original', 'iso_volume_id')[:32]
        model.original.iso_release_name = self.get_value('Original', 'iso_release_name')
        model.original.iso_disk_name = self.get_value('Original', 'iso_disk_name')

        # Custom
        model.custom.iso_version_number = self.get_value('Custom', 'iso_version_number')
        model.custom.iso_file_name = self.get_value('Custom', 'iso_file_name')
        model.custom.iso_directory = self.get_value('Custom', 'iso_directory')
        model.custom.iso_volume_id = self.get_value('Custom', 'iso_volume_id')[:32]
        model.custom.iso_release_name = self.get_value('Custom', 'iso_release_name')
        model.custom.iso_disk_name = self.get_value('Custom', 'iso_disk_name')

        # Status
        model.status.is_success_copy = self.get_boolean('Status', 'is_success_copy', default=False)
        model.status.is_success_extract = self.get_boolean('Status', 'is_success_extract', default=False)
        model.status.iso_template = self.get_value('Status', 'iso_template', default=None)
        # Not in the original 2022 layout.
        model.status.squashfs_directory = self.get_value('Status', 'squashfs_directory', default=None)
        model.status.squashfs_file_name = self.get_value('Status', 'squashfs_file_name', default=None)
        model.status.casper_directory = self.get_value('Status', 'casper_directory', default=None)
        model.status.iso_checksum = self.get_value('Status', 'iso_checksum', default=None)
        model.status.iso_checksum_file_name = self.get_value('Status', 'iso_checksum_file_name', default=None)

        # Options
        model.options.update_os_release = self.get_boolean('Options', 'update_os_release', default=True)
        model.options.boot_configurations = self.get_list('Options', 'boot_configurations', default=None)
        model.options.compression = self.get_value('Options', 'compression', default=None)

    # ------------------------------------------------------------------
    # Save Methods
    # ------------------------------------------------------------------

    def _save_model(self):
        """
        This method should only be called by the save() method.

        Save the contents of the application model to the configuration
        file using the appropriate layout.

        Arguments:
        self : Configuration
            A derived class of Configuration.
        """

        logger.log_label('Save project configuration')

        # Save using the current layout.
        self._save_model_2022_layout()

    def _save_model_2019_layout(self):
        """
        This method is not used.

        Save the project model to the 2019 configuration file layout.

        This method should only be called by the _save_model() method.
        Be sure to specify the correct sections in the __init__()
        method.

        Arguments:
        self : Configuration
            A derived class of Configuration.
        """

        logger.log_value('Save project configuration', '2019 layout to %s' % self.file_path)

        # Project
        self.set('General', 'cubic_version', model.application.cubic_version)
        self.set('General', 'project_directory', model.project.directory)

        # Original
        self.set('Original', 'original_iso_image_filename', model.original.iso_file_name)
        self.set('Original', 'original_iso_image_directory', model.original.iso_directory)
        self.set('Original', 'original_iso_image_volume_id', model.original.iso_volume_id)
        self.set('Original', 'original_iso_image_release_name', model.original.iso_release_name)
        self.set('Original', 'original_iso_image_disk_name', model.original.iso_disk_name)

        # Custom
        self.set('Custom', 'custom_iso_image_version_number', model.custom.iso_version_number)
        self.set('Custom', 'custom_iso_image_filename', model.custom.iso_file_name)
        self.set('Custom', 'custom_iso_image_directory', model.custom.iso_directory)
        self.set('Custom', 'custom_iso_image_volume_id', model.custom.iso_volume_id)
        self.set('Custom', 'custom_iso_image_release_name', model.custom.iso_release_name)
        self.set('Custom', 'custom_iso_image_disk_name', model.custom.iso_disk_name)

        # Status
        self.set('Status', 'is_success_copy', model.status.is_success_copy)
        self.set('Status', 'is_success_extract', model.status.is_success_extract)
        # Not in the original 2019 layout.
        self.set('Status', 'iso_template', model.status.iso_template)
        # Not in the original 2019 layout.
        self.set('Status', 'squashfs_directory', model.status.squashfs_directory)
        # Not in the original 2019 layout.
        self.set('Status', 'squashfs_file_name', model.status.squashfs_file_name)
        # Not in the original 2019 layout.
        self.set('Status', 'casper_directory', model.status.casper_directory)
        # Not in the original 2019 layout.
        self.set('Status', 'custom_iso_image_checksum', model.status.iso_checksum)
        # In the Custom section of the 2019 layout.
        self.set('Custom', 'custom_iso_image_md5_filename', model.status.iso_checksum_file_name)

        # Options
        # Not in the original 2019 layout.
        self.set('Options', 'update_os_release', model.options.update_os_release)
        self.set('Options', 'boot_configurations', model.options.boot_configurations)
        # Not in the original 2019 layout.
        self.set('Options', 'compression', model.options.compression)

    def _save_model_2020_layout(self):
        """
        This method is not used.

        Save the project model to the 2020 configuration file layout.

        This method should only be called by the _save_model() method.
        Be sure to specify the correct sections in the __init__()
        method.

        Arguments:
        self : Configuration
            A derived class of Configuration.
        """

        logger.log_value('Save project configuration', '2020 layout to %s' % self.file_path)

        # Project
        self.set('Project', 'cubic_version', model.application.cubic_version)
        self.set('Project', 'create_date', model.project.create_date)
        self.set('Project', 'modify_date', model.project.modify_date)
        self.set('Project', 'directory', model.project.directory)

        # Original
        self.set('Original', 'iso_filename', model.original.iso_file_name)
        self.set('Original', 'iso_directory', model.original.iso_directory)
        self.set('Original', 'iso_volume_id', model.original.iso_volume_id)
        self.set('Original', 'iso_release_name', model.original.iso_release_name)
        self.set('Original', 'iso_disk_name', model.original.iso_disk_name)

        # Custom
        self.set('Custom', 'iso_version_number', model.custom.iso_version_number)
        self.set('Custom', 'iso_filename', model.custom.iso_file_name)
        self.set('Custom', 'iso_directory', model.custom.iso_directory)
        self.set('Custom', 'iso_volume_id', model.custom.iso_volume_id)
        self.set('Custom', 'iso_release_name', model.custom.iso_release_name)
        self.set('Custom', 'iso_disk_name', model.custom.iso_disk_name)

        # Status
        self.set('Status', 'is_success_copy', model.status.is_success_copy)
        self.set('Status', 'is_success_extract', model.status.is_success_extract)
        # Not in the original 2020 layout.
        self.set('Status', 'iso_template', model.status.iso_template)
        # Not in the original 2020 layout.
        self.set('Status', 'squashfs_directory', model.status.squashfs_directory)
        # Not in the original 2020 layout.
        self.set('Status', 'squashfs_file_name', model.status.squashfs_file_name)
        self.set('Status', 'casper_directory', model.status.casper_directory)
        self.set('Status', 'iso_checksum', model.status.iso_checksum)
        self.set('Status', 'iso_checksum_filename', model.status.iso_checksum_file_name)

        # Options
        # Not in the original 2020 layout.
        self.set('Options', 'update_os_release', model.options.update_os_release)
        self.set('Options', 'boot_configurations', model.options.boot_configurations)
        self.set('Options', 'compression', model.options.compression)

    def _save_model_2021_layout(self):
        """
        This method is not used.

        Save the project model to the 2021 configuration file layout.

        This method should only be called by the _save_model() method.
        Be sure to specify the correct sections in the __init__()
        method.

        Arguments:
        self : Configuration
            A derived class of Configuration.
        """

        logger.log_value('Save project configuration', '2021 layout to %s' % self.file_path)

        # Project
        self.set('Project', 'cubic_version', model.application.cubic_version)
        self.set('Project', 'create_date', model.project.create_date)
        self.set('Project', 'modify_date', model.project.modify_date)
        self.set('Project', 'directory', model.project.directory)

        # Original
        self.set('Original', 'iso_file_name', model.original.iso_file_name)
        self.set('Original', 'iso_directory', model.original.iso_directory)
        self.set('Original', 'iso_volume_id', model.original.iso_volume_id)
        self.set('Original', 'iso_release_name', model.original.iso_release_name)
        self.set('Original', 'iso_disk_name', model.original.iso_disk_name)

        # Custom
        self.set('Custom', 'iso_version_number', model.custom.iso_version_number)
        self.set('Custom', 'iso_file_name', model.custom.iso_file_name)
        self.set('Custom', 'iso_directory', model.custom.iso_directory)
        self.set('Custom', 'iso_volume_id', model.custom.iso_volume_id)
        self.set('Custom', 'iso_release_name', model.custom.iso_release_name)
        self.set('Custom', 'iso_disk_name', model.custom.iso_disk_name)

        # Status
        self.set('Status', 'is_success_copy', model.status.is_success_copy)
        self.set('Status', 'is_success_extract', model.status.is_success_extract)
        self.set('Status', 'iso_template', model.status.iso_template)
        # Not in the original 2021 layout.
        self.set('Status', 'squashfs_directory', model.status.squashfs_directory)
        # Not in the original 2021 layout.
        self.set('Status', 'squashfs_file_name', model.status.squashfs_file_name)
        self.set('Status', 'casper_directory', model.status.casper_directory)
        self.set('Status', 'iso_checksum', model.status.iso_checksum)
        self.set('Status', 'iso_checksum_file_name', model.status.iso_checksum_file_name)

        # Options
        # Not in the original 2021 layout.
        self.set('Options', 'update_os_release', model.options.update_os_release)
        self.set('Options', 'boot_configurations', model.options.boot_configurations)
        self.set('Options', 'compression', model.options.compression)

    def _save_model_2022_layout(self):
        """
        Save the project model to the 2022 configuration file layout.

        This method should only be called by the _save_model() method.
        Be sure to specify the correct sections in the __init__()
        method.

        Arguments:
        self : Configuration
            A derived class of Configuration.
        """

        logger.log_value('Save project configuration', '2022 layout to %s' % self.file_path)

        # Project
        self.set('Project', 'cubic_version', model.application.cubic_version)
        self.set('Project', 'create_date', model.project.create_date)
        self.set('Project', 'modify_date', model.project.modify_date)
        self.set('Project', 'directory', model.project.directory)

        # Original
        self.set('Original', 'iso_file_name', model.original.iso_file_name)
        self.set('Original', 'iso_directory', model.original.iso_directory)
        self.set('Original', 'iso_volume_id', model.original.iso_volume_id)
        self.set('Original', 'iso_release_name', model.original.iso_release_name)
        self.set('Original', 'iso_disk_name', model.original.iso_disk_name)

        # Custom
        self.set('Custom', 'iso_version_number', model.custom.iso_version_number)
        self.set('Custom', 'iso_file_name', model.custom.iso_file_name)
        self.set('Custom', 'iso_directory', model.custom.iso_directory)
        self.set('Custom', 'iso_volume_id', model.custom.iso_volume_id)
        self.set('Custom', 'iso_release_name', model.custom.iso_release_name)
        self.set('Custom', 'iso_disk_name', model.custom.iso_disk_name)

        # Status
        self.set('Status', 'is_success_copy', model.status.is_success_copy)
        self.set('Status', 'is_success_extract', model.status.is_success_extract)
        self.set('Status', 'iso_template', model.status.iso_template)
        self.set('Status', 'squashfs_directory', model.status.squashfs_directory)
        self.set('Status', 'squashfs_file_name', model.status.squashfs_file_name)
        self.set('Status', 'casper_directory', model.status.casper_directory)
        self.set('Status', 'iso_checksum', model.status.iso_checksum)
        self.set('Status', 'iso_checksum_file_name', model.status.iso_checksum_file_name)

        # Options
        self.set('Options', 'update_os_release', model.options.update_os_release)
        self.set('Options', 'boot_configurations', model.options.boot_configurations)
        self.set('Options', 'compression', model.options.compression)
