#!/usr/bin/python3

########################################################################
#                                                                      #
# fields.py                                                            #
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

# https://docs.python.org/3/reference/datamodel.html

########################################################################
# Imports
########################################################################

from cubic.utilities import logger

########################################################################
# Global Variables & Constants
########################################################################

# N/A

########################################################################
# Classes
########################################################################


class Fields:

    def __init__(self, name):

        super().__setattr__('name', name.replace('_', ' '))

    def __setattr__(self, key, value):

        # Check if an additional parameter was supplied, and set is_log.
        if isinstance(value, tuple):
            value, is_log = value
        else:
            is_log = True

        if isinstance(value, str):
            value = str(value).strip()

        if value is None:
            value = ''

        if not hasattr(self, key):
            if is_log:
                display_key = key.replace('_', ' ')
                logger.log_value(f'Set {self.name} {display_key}', value)
            super().__setattr__(key, value)
        elif self.__getattribute__(key) != value:
            if is_log:
                display_key = key.replace('_', ' ')
                logger.log_value(f'Set {self.name} {display_key}', value)
            super().__setattr__(key, value)

    def __repr__(self):
        """
        Return the string representation of the underlying __dict__.
        """

        return str(self.__dict__)


class IsoField:
    """
    If appending a new field in IsoFields, update both references to the
    last field in the __setattr__() method. This ensures the validators
    are not invoked during the __init__() method. Currently the last
    field is "options_update_os_release".
    """

    def __init__(self, value, iso_fields):
        """
        Create a new IsoField object.
        value - Either a string that represents the name of the new
        IsoField, or an IsoField object that will be copied into the new
        IsoField object. If value is a string, the new IsoField object's
        values will be initialized to default values. If value is an
        existing IsoField object, then the new object will have the same
        name as the original object, and its values will be the same as
        the values of the original object.
        iso_fields - The IsoFields container for the new Isofield.
        """

        # Ensure self.__dict__ contains all required keys. This
        # simplifies, the __setattr__() implementation because checking
        # hasattr(self, key) becomes unnecessary when adding new keys.
        # Note that self.__setattr__() will not be invoked below, so
        # values will not be converted to displayable format when they
        # are stored. Python 3.7+ guarantees that dict will sort keys
        # using insertion order, so this is also useful for the
        # __repr__() method.
        super().__setattr__('name', None)
        super().__setattr__('value', None)
        super().__setattr__('is_valid', None)
        super().__setattr__('status', None)
        super().__setattr__('message', None)
        super().__setattr__('validator', None)
        super().__setattr__('iso_fields', None)

        # Ensure that self.__setattr__() is called, so that the values
        # are converted to displayable format, as necessary, before they
        # are stored.
        if isinstance(value, IsoField):
            # self.name = value.name
            super().__setattr__('name', value.name)
            # The iso_fields reference must be set prior to setting the
            # value or the validator. This is because the validate()
            # callback function, which is executed each time a new value
            # is set or when a new validator is set, requires this
            # parameter as an argument.
            self.iso_fields = iso_fields, False  # Reference to container object.
            self.value = value.value, False  # Converted to a string.
            self.is_valid = value.is_valid, False  # Converted to a boolean.
            self.status = value.status, False  # Converted to an integer.
            self.message = value.message, False  # Converted to a string.
            self.validator = value.validator, False
        elif isinstance(value, str):
            name = value.replace('_', ' ')
            # self.name = name
            super().__setattr__('name', name)
            self.iso_fields = iso_fields, False  # Reference to container object.
            self.value = None, False  # Converted to an empty string.
            self.is_valid = None, False  # Converted to False.
            self.status = None, False  # Converted to a 0.
            self.message = None, False  # Converted to an empty string.
            self.validator = None, False
        else:
            raise TypeError('Argument must be a string or IsoField')

    def __eq__(self, field):
        """
        Compare this object's value with another object's value.
        """

        if field:
            return self.value == field.value
        else:
            return False

    def __setattr__(self, key, value):
        """
        Set iso_fields, if they have changed, converting to displayable
        format, as necessary, before storing:
        - value is stored as a string or empty string if None
        - is_valid is stored as a boolean or False if None
        - status is stored as an integer or O if None
        - message is stored as a string or empty string if None
        - other iso_fields are stored as-is
        """

        # Check if an additional parameter was supplied, and set is_log.
        if isinstance(value, tuple):
            value, is_log = value
        else:
            is_log = True

        if key == 'name':
            if value:
                value = str(value).strip()
            if not value:
                value = ''
            if self.name != value:
                # if is_log:
                #     logger.log_value(f'Set {self.iso_fields.name} {self.name} {key}', value)
                super().__setattr__(key, value)
        elif key == 'value':
            if value:
                value = str(value).strip()
            if not value:
                value = ''
            if self.value != value:
                if is_log:
                    logger.log_value(f'Set {self.iso_fields.name} {self.name} {key}', value)
                super().__setattr__(key, value)
                # If a new value was set, validate it.
                # In order to ensure that the validator is not invoked
                # during IsoField.__init__() using an incomplete
                # IsoFields object, check if the last value,
                # options_update_os_release, has been assigned.
                if self.validator and self.iso_fields.options_update_os_release:
                    # If a validator is available, validate the fields.
                    is_valid, status, message = self.validator(self.iso_fields)
                    self.is_valid = is_valid
                    self.status = status
                    self.message = message
        elif key == 'is_valid':
            value = bool(value)
            if self.is_valid != value:
                if is_log:
                    logger.log_value(f'Is {self.iso_fields.name} {self.name} valid?', value)
                super().__setattr__(key, value)
        elif key == 'status':
            value = 0 if not value else int(value)
            if self.status != value:
                # if is_log:
                #     logger.log_value(f'Set {self.iso_fields.name} {self.name} {key}', value)
                super().__setattr__(key, value)
        elif key == 'message':
            if value:
                value = str(value).strip()
            if not value:
                value = ''
            if self.message != value:
                # if is_log:
                #     logger.log_value(f'Set {self.iso_fields.name} {self.name} {key}', value)
                super().__setattr__(key, value)
        elif key == 'validator':
            if self.validator != value:
                super().__setattr__(key, value)
                # If a new validator was set, validate the value.
                # In order to ensure that the validator is not invoked
                # during IsoField.__init__() using an incomplete
                # IsoFields object, check if the last value,
                # options_update_os_release, has been assigned.
                if self.validator and self.iso_fields.options_update_os_release:
                    # if is_log:
                    #     logger.log_value(f'Set {self.iso_fields.name} {self.name} {key}', value)
                    is_valid, status, message = self.validator(self.iso_fields)
                    self.is_valid = is_valid
                    self.status = status
                    self.message = message
        elif key == 'iso_fields':
            if self.iso_fields != value:
                # if is_log:
                #     logger.log_value(f'Set {self.iso_fields.name} {self.name} {key}', value)
                super().__setattr__(key, value)
        else:
            # TODO: Consider ignoring or raising an exception.
            if self.key != value:
                if is_log:
                    logger.log_value(f'Set {self.iso_fields.name} {self.name} {key}', value)
                super().__setattr__(key, value)

    def __repr__(self):
        """
        Return the string representation of the underlying __dict__.
        """

        return str(self.__dict__)


class IsoFields:

    # TODO: Copy the name of the IsoField, if one is supplied.
    #       Use value instead of name and iso_fields. Then check value
    #       using isinstance(value, str).
    def __init__(self, name, iso_fields=None):

        super().__setattr__('name', name.replace('_', ' '))

        if iso_fields:
            super().__setattr__('iso_version_number', IsoField(iso_fields.iso_version_number, self))
            super().__setattr__('iso_file_name', IsoField(iso_fields.iso_file_name, self))
            super().__setattr__('iso_directory', IsoField(iso_fields.iso_directory, self))
            super().__setattr__('iso_volume_id', IsoField(iso_fields.iso_volume_id, self))
            super().__setattr__('iso_release_name', IsoField(iso_fields.iso_release_name, self))
            super().__setattr__('iso_disk_name', IsoField(iso_fields.iso_disk_name, self))
            super().__setattr__('iso_release_notes_url', IsoField(iso_fields.iso_release_notes_url, self))
            super().__setattr__('options_update_os_release', IsoField(iso_fields.options_update_os_release, self))
        else:
            super().__setattr__('iso_version_number', IsoField('iso_version_number', self))
            super().__setattr__('iso_file_name', IsoField('iso_file_name', self))
            super().__setattr__('iso_directory', IsoField('iso_directory', self))
            super().__setattr__('iso_volume_id', IsoField('iso_volume_id', self))
            super().__setattr__('iso_release_name', IsoField('iso_release_name', self))
            super().__setattr__('iso_disk_name', IsoField('iso_disk_name', self))
            super().__setattr__('iso_release_notes_url', IsoField('iso_release_notes_url', self))
            super().__setattr__('options_update_os_release', IsoField('options_update_os_release', self))

    def __eq__(self, iso_fields):
        """
        Return True if the value property of each Isofield of this
        object is equal to the value property of each corresponding
        Isofield of iso_fields. Otherwise, return False.
        - iso_version_number.value
        - iso_file_name.value
        - iso_directory.value
        - iso_volume_id.value
        - iso_release_name.value
        - iso_disk_name.value
        - iso_release_notes_url.value
        - options_update_os_release
        """

        return (
            iso_fields                                                               \
            and self.iso_version_number == iso_fields.iso_version_number             \
            and self.iso_file_name == iso_fields.iso_file_name                       \
            and self.iso_directory == iso_fields.iso_directory                       \
            and self.iso_volume_id == iso_fields.iso_volume_id                       \
            and self.iso_release_name == iso_fields.iso_release_name                 \
            and self.iso_disk_name == iso_fields.iso_disk_name                       \
            and self.iso_release_notes_url == iso_fields.iso_release_notes_url       \
            and self.options_update_os_release == iso_fields.options_update_os_release)

    def __getattr__(self, key):
        """
        Add attribute for is_valid.
        """

        if key == 'is_valid':
            return (
                self.iso_version_number.is_valid          \
                and self.iso_file_name.is_valid           \
                and self.iso_directory.is_valid           \
                and self.iso_volume_id.is_valid           \
                and self.iso_release_name.is_valid        \
                and self.iso_disk_name.is_valid           \
                and self.iso_release_notes_url.is_valid   \
                and self.options_update_os_release.is_valid)

    def __repr__(self):
        """
        Return the string representation of the internal dictionary.
        """

        return str(self.__dict__)


class IsoFieldsHistory:

    def __init__(self):

        # The index of the currently selected item in the history.
        self.selected = -1

        # The history.
        self.history = []

    def reset(self):

        self.history.clear()
        self.selected = -1

    def clear(self, iso_fields):
        """
        Remove all subsequent values after the current value.
        """

        del self.history[self.selected + 1:]

    def insert(self, iso_fields):

        self.selected = self.selected + 1
        del self.history[self.selected:]
        new_iso_fields = IsoFields(iso_fields.name, iso_fields)
        self.history.append(new_iso_fields)

    def get_first(self):

        return self.history[0]

    def get(self, selected):

        return self.history[selected]

    def current(self):

        if self.selected > -1 and self.selected < len(self.history):
            iso_fields = self.history[self.selected]
            new_iso_fields = IsoFields(iso_fields.name, iso_fields)
            return new_iso_fields
        else:
            return None

    def previous(self):

        self.selected = self.selected - 1
        iso_fields = self.history[self.selected]
        new_iso_fields = IsoFields(iso_fields.name, iso_fields)
        return new_iso_fields

    def next(self):

        self.selected = self.selected + 1
        iso_fields = self.history[self.selected]
        new_iso_fields = IsoFields(iso_fields.name, iso_fields)
        return new_iso_fields

    def has_history(self):
        """
        Indicate of there is at least one item in the history.
        Args:
            self (IsoFieldsHistory): This object.

        Returns:
            (bool): True if there are one or more items in the history
                    to the left of the current item.
                    False if there are zero items in the history to the
                    left of the current item.
        """
        return len(self.history) > 0

    def has_undo(self):
        """
        Indicate of there is at least one item in the history to the
        "left" of the currently selected item.
        Args:
            self (IsoFieldsHistory): This object.

        Returns:
            (bool): True if there are one or more items in the history
                    to the left of the current item.
                    False if there are zero items in the history to the
                    left of the current item.
        """
        return self.selected > 0

    def has_redo(self):

        return self.selected < len(self.history) - 1

    def print_iso_fields(self, iso_fields, message):

        print()
        print('-' * 80)
        print(message)
        print(f'The self.selected index is "{self.selected}"')
        print(f'The id is "{id(iso_fields)}"')
        print('Custom ISO fields are...')
        print(iso_fields)
        print('Custom ISO fields is valid...')
        print(iso_fields.is_valid)
        print('-  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -')
        print(f'The custom ISO fields list has  "{len(self.history)}" items.')
        print(f'The custom ISO fields has undo? "{self.has_undo()}"')

        for i, c in enumerate(self.history):
            print(f'The self.selected item is "{i}"')
            print(f'The id is "{id(c)}"')
            print('The ISO fields are...')
            print(c)
            print()
        print('-' * 80)
        print()
