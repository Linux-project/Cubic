#!/usr/bin/python3

########################################################################
#                                                                      #
# constants.py                                                         #
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
# Constants
########################################################################

# Status
OK = 0
ERROR = 1
OPTIONAL = 2
BULLET = 3
PROCESSING = 4
BLANK = 5

NEW_CUBIC_VERSION = '2020.04'

ISO_MOUNT_POINT = 'source-disk'  # 'original-iso-mount'
CUSTOM_DISK_DIRECTORY = 'custom-disk'  # 'custom-live-iso'
CUSTOM_ROOT_DIRECTORY = 'custom-root'  # 'squashfs-root'

# DEFAULT_BOOT_CONFIGURATIONS_STRING = 'boot/grub/grub.cfg,boot/grub/loopback.cfg,isolinux/isolinux.cfg,isolinux/txt.cfg'
DEFAULT_BOOT_CONFIGURATIONS_STRING = 'boot/grub/grub.cfg,boot/grub/loopback.cfg,isolinux/txt.cfg'

ZOOM = 10
PERCENT_START = 0
PERCENT_STOP = 100
PROGRESS_START = PERCENT_START * ZOOM
PROGRESS_STOP = PERCENT_STOP * ZOOM
SLOW_INTERVAL = 0.5000 / ZOOM
FAST_INTERVAL = 0.0100 / ZOOM

NUMBERS_LOWER_CASE = ['no', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
NUMBERS_TITLE_CASE = ['No', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine']
NUMBERS_UPPER_CASE = ['NO', 'ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE']

########################################################################
# Font Colors
########################################################################

# TODO: Replace colors in other modules with these

# https://en.wikipedia.org/wiki/ANSI_escape_code
# https://stackoverflow.com/questions/4842424/list-of-ansi-color-escape-sequences
BOLD_RED = '\033[1;31m'
BOLD_GREEN = '\033[1;32m'
BOLD_BLUE = '\033[1;34m'
BOLD_YELLOW = '\033[1;33;1m'
BOLD_MAGENTA = '\033[1;35;1m'
BOLD_CYAN = '\033[1;36;1m'
NORMAL = '\033[0m'

# https://stackoverflow.com/questions/45065919/move-cursor-position-in-bash-at-specific-column
# http://www.termsys.demon.co.uk/vtansi.htm
# Cursor Backward		<ESC>[{COUNT}D
# Moves the cursor backward by COUNT columns; the default count is 1.
# NEW_LINE = '\033[50D\033[-1C\n'
NEW_LINE = '\033[99D\n'
