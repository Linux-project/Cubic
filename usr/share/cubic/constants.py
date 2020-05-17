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
# Application
########################################################################

NEW_CUBIC_VERSION = '2020.04'

ISO_MOUNT_POINT = 'source-disk'  # 'original-iso-mount'
CUSTOM_DISK_DIRECTORY = 'custom-disk'  # 'custom-live-iso'
CUSTOM_ROOT_DIRECTORY = 'custom-root'  # 'squashfs-root'

# The maximum ISO size is 8 Tera bytes.
MAXIMUM_ISO_SIZE_GIB = 8000.0
MAXIMUM_ISO_SIZE_BYTES = MAXIMUM_ISO_SIZE_GIB * 1073741824.0

########################################################################
# Status
########################################################################

OK = 0
ERROR = 1
OPTIONAL = 2
BULLET = 3
PROCESSING = 4
BLANK = 5

# DEFAULT_BOOT_CONFIGURATIONS_STRING = 'boot/grub/grub.cfg,boot/grub/loopback.cfg,isolinux/isolinux.cfg,isolinux/txt.cfg'
DEFAULT_BOOT_CONFIGURATIONS_STRING = 'boot/grub/grub.cfg,boot/grub/loopback.cfg,isolinux/txt.cfg'

NUMBERS_LOWER_CASE = ['no', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
NUMBERS_TITLE_CASE = ['No', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine']
NUMBERS_UPPER_CASE = ['NO', 'ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE']

########################################################################
# Progress
########################################################################

START_PERCENT = 0  # %
FINAL_PERCENT = 100  # %

# The number of seconds to delay before incrementing one percent.
DELAY_PER_PERCENT = 0.100  # seconds / percent

# The scale factor defines the "resolution" for each step in the
# progress. For example, a scale factor of 10 means that there are 1000
# steps to reach 100% (100% × 10 scale factor = 1000 steps); in other
# words, each progress step is 0.10% (1% ÷ 10 scale factor = 0.10%).
SCALE_FACTOR = 10

########################################################################
# TODO: DELETE THESE WHEN progress is replaced with progressor.
########################################################################

ZOOM = 10
PERCENT_START = 0
PERCENT_STOP = 100
PROGRESS_START = PERCENT_START * ZOOM
PROGRESS_STOP = PERCENT_STOP * ZOOM
SLOW_INTERVAL = 0.5000 / ZOOM
FAST_INTERVAL = 0.0100 / ZOOM

########################################################################
# Font Colors
########################################################################

# TODO: Replace colors in other modules with these

# https://en.wikipedia.org/wiki/ANSI_escape_code
# https://stackoverflow.com/questions/4842424/list-of-ansi-color-escape-sequences

RED = '\033[0;31m'
GREEN = '\033[0;32m'
BLUE = '\033[0;34m'
YELLOW = '\033[0;33m'
MAGENTA = '\033[0;35m'
CYAN = '\033[0;36m'

BOLD_RED = '\033[1;31m'
BOLD_GREEN = '\033[1;32m'
BOLD_BLUE = '\033[1;34m'
BOLD_YELLOW = '\033[1;33m'
BOLD_MAGENTA = '\033[1;35m'
BOLD_CYAN = '\033[1;36m'

NORMAL = '\033[0m'

# https://stackoverflow.com/questions/45065919/move-cursor-position-in-bash-at-specific-column
# http://www.termsys.demon.co.uk/vtansi.htm
# Cursor Backward		<ESC>[{COUNT}D
# Moves the cursor backward by COUNT columns; the default count is 1.
# NEW_LINE = '\033[50D\033[-1C\n'
NEW_LINE = '\033[99D\n'
