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
# References
########################################################################

# https://docs.python.org/3/library/locale.html#locale.setlocale
# http://manpages.ubuntu.com/manpages/groovy/man1/xorrisofs.1.html

########################################################################
# Imports
########################################################################

import locale

########################################################################
# Localization
########################################################################

# This sets the locale for all categories to the user’s default setting
# (typically specified in the LANG environment variable). An empty
# string specifies the user's default settings. According to POSIX, a
# program which has not called setlocale(LC_ALL, '') runs using the
# portable 'C' locale. Calling setlocale(LC_ALL, '') lets it use the
# default locale as defined by the LANG variable.
locale.setlocale(locale.LC_ALL, '')

TIME_STAMP_FORMAT = '%c'
LONG_TIME_STAMP_FORMAT = '%A %B %d, %Y %I:%M %p'
VERSION_NUMBER_FORMAT = '%Y.%m.%d'

########################################################################
# Application
########################################################################

# Cubic release versions:
#
# "Classic" 2019 Version:
#   From: Release 2015.11-1  on 11/05/2015
#   To:   Release 2020.02-62 on 02/01/2020
#
# "Release" 2020 Version:
#   From: Release 2020.04-1  on 04/26/2020
#   To:   Release 2020.10-35 on 10/23/2020
#
# "Release" 2021 Version:
#   From: Release 2020.12-36 on 12/19/2020
#   To:   Release 20??.??-?? on ??/??/20??

# These values are initial release version numbers.
CUBIC_VERSION_2019 = '2015.11-1'  # Releases 2015.11-1 thru 2020.02-62
CUBIC_VERSION_2020 = '2020.04-1'  # Releases 2020.04-1 thru 2020.10-35
CUBIC_VERSION_2021 = '2020.12-36'  # Releases 2020.12-36 thru present

# Sleep in milliseconds.
SLEEP_0125_MS = 0.125
SLEEP_0250_MS = 0.250
SLEEP_0500_MS = 0.500
SLEEP_1000_MS = 1.000
SLEEP_1500_MS = 1.500

# Size measurements.
KIB = 1024**1  # 1 kibibytes (KiB) =          1024 bytes
MIB = 1024**2  # 1 mibibytes (MiB) =       1048576 bytes
GIB = 1024**3  # 1 gibibytes (GiB) =    1073741824 bytes
TIB = 1024**4  # 1 tebibytes (TiB) = 1099511627776 bytes

# Units for xorriso command: 1024, 1024k, 1024m, 1024g, 2048, 512.
MULTIPLES = {'k': KIB, 'm': MIB, 'g': GIB, 't': TIB, 's': 2048, 'd': 512}

# The maximum ISO size is 8 tebibytes.
MAXIMUM_DISK_SIZE_BYTES = 8 * TIB
MAXIMUM_DISK_SIZE_GIB = MAXIMUM_DISK_SIZE_BYTES / GIB

########################################################################
# File Names
########################################################################

ISO_MOUNT_POINT = 'source-disk'  # 'original-iso-mount'
CUSTOM_DISK_DIRECTORY = 'custom-disk'  # 'custom-live-iso'
CUSTOM_ROOT_DIRECTORY = 'custom-root'  # 'squashfs-root'

# Excluded file system types.
# ext, ext2, ext3, ext4, nfs, ntfs, vfat, zfs; FAT16, FAT32, and exFAT
EXCLUDED_FILESYSTEM_TYPES = ['FAT', 'FAT16', 'FAT32', 'NTFS', 'VFAT']

IMAGE_FILE_NAME = 'partition-%s.img'
LOCK_FILE_NAME = '.#custom-root.lck'

########################################################################
# Status
########################################################################

OK = 0
ERROR = 1
OPTIONAL = 2
BULLET = 3
PROCESSING = 4
BLANK = 5

# Ubuntu uses "isolinux/txt.cfg"; other distros use different files.
# - Fix for bug #1885464: Linux Mint uses "isolinux/isolinux.cfg."
# - Fix for bug #???????: Elementry uses "isolinux/live.cfg."
DEFAULT_BOOT_CONFIGURATIONS_STRING = 'boot/grub/grub.cfg,boot/grub/loopback.cfg,isolinux/txt.cfg'
### DEFAULT_BOOT_CONFIGURATIONS_STRING = 'boot/grub/grub.cfg,boot/grub/loopback.cfg,isolinux/live.cfg,isolinux/isolinux.cfg,isolinux/txt.cfg'

NUMBERS_LOWER_CASE = ['no', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
NUMBERS_TITLE_CASE = ['No', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine']
NUMBERS_UPPER_CASE = ['NO', 'ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE']

########################################################################
# Progress
########################################################################

# The scale factor defines the "resolution" for each step in the
# progress. For example, a scale factor of 10 means that there are 1000
# steps to reach 100% (100% × 10 scale factor = 1000 steps); in other
# words, each progress step is 0.10% (1% ÷ 10 scale factor = 0.10%).
SCALE_FACTOR = 10
START_PERCENT = 0  # %
FINAL_PERCENT = 100  # %

########################################################################
# Terminal & Font Colors
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
