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
# https://docs.python.org/3/library/time.html#time.strftime

########################################################################
# Imports
########################################################################

import gi

gi.require_version('Gdk', '3.0')

from gi.repository import Gdk

import locale

########################################################################
# Memory / Storage Units
########################################################################

KIB = 1024**1  # 1 kibibytes (KiB) =          1024 bytes
MIB = 1024**2  # 1 mibibytes (MiB) =       1048576 bytes
GIB = 1024**3  # 1 gibibytes (GiB) =    1073741824 bytes
TIB = 1024**4  # 1 tebibytes (TiB) = 1099511627776 bytes

########################################################################
# Sleep Times
########################################################################

# Sleep in milliseconds.
SLEEP_0125_MS = 0.125
SLEEP_0250_MS = 0.250
SLEEP_0500_MS = 0.500
SLEEP_1000_MS = 1.000
SLEEP_1500_MS = 1.500

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

# TIME_STAMP_FORMAT = '%x %X'  # Locale appropriate date and time format.
TIME_STAMP_FORMAT = '%Y-%m-%d %H:%M'
TIME_STAMP_FORMAT_LONG_1 = '%A %B %d, %Y %I:%M %p'
TIME_STAMP_FORMAT_LONG_2 = '%A %B %d, %Y %I:%M'
TIME_STAMP_FORMAT_LONG_3 = '%A %B %d, %Y %H:%M'
TIME_STAMP_FORMAT_YYYYMMDD = '%Y%m%d'
VERSION_NUMBER_FORMAT = '%Y.%m.%d'

# Unicode "Hair Space" character used to precede percent ("%") symbols.
GAP = '\u200A'

########################################################################
# Application Versions
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

###############################################################
# File Sizes
###############################################################

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
IMAGE_FILE_NAME = 'partition-%s.img'
LOCK_FILE_NAME = '.#custom-root.lck'

# SQUASHFS_FILE_NAMES = [
#     'ubuntu-server-minimal.squashfs',
#     'ubuntu-server-minimal.ubuntu-server.installer.generic.squashfs',
#     'ubuntu-server-minimal.ubuntu-server.installer.squashfs',
#     'ubuntu-server-minimal.ubuntu-server.squashfs'
# ]
SQUASHFS_FILE_NAMES = ['filesystem.squashfs', 'ubuntu-server-minimal.squashfs']

EXTENSION_MANIFEST = 'manifest'
EXTENSION_MANIFEST_MINIMAL_REMOVE = 'manifest-minimal-remove'
EXTENSION_MANIFEST_REMOVE = 'manifest-remove'
EXTENSION_SIZE = 'size'
EXTENSION_SQUASHFS_GPG = 'squashfs.gpg'
EXTENSION_SQUASHFS = 'squashfs'

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

STAR = '★'
CUBIC_WIKI = 'cubic_wiki'
CUBIC_PAGE_HELP = 'cubic_page_help'
CUBIC_WEBSITE = 'cubic_website'
CUBIC_DONATE = 'cubic_donate'
CUBIC_SITES = [CUBIC_WEBSITE, CUBIC_WIKI, CUBIC_PAGE_HELP, CUBIC_DONATE]
CUBIC_URLS = '789C9D934B4EC330108659C0065A04DC010921A569917815D8501E12122252BBAF9CD424A64D6CC553010B240E9065381117C389C74DD8D5CECA0B7F5FE69FF17C6FFEFC6E6DD4DF57795474A365C8A2E93B0D25035A168709809043DF8F1924CBB017F1D40F9EBC31CBE2C4EBF707FEA8BA5F16DBC8B1392B8BE3B5205F5FEE6872C63352FD70B83EEBDFD58C07DC33554820394C058995E9D4C234AE382FA8B94ECAE25C7951736EA179D6A411899CBFD1081C44812651B40354C274809E6B07CF44098C6C46177495EECCA6DD3568C2D10FC88953B87B4DA2A80B344F59461668BAB0304D1045D5C14A1571F189BE1B17DF48F1CD14A920B9CB73083469820A12CDD5493A040D10353571018C67D2A1A6174DA2685F859394CEDA0DB37B5F35DEEED76EC839B47D9716BE5BC5B6657BEA7255A25435A3EECA42376A6833849866B4B5DD36437844D42CD22BCB984C1C16E9A106FF2DF789433AD434BBBDECFD01B809192B'

########################################################################
# File System Types
########################################################################

# Local file system types:
# • btrfs is reported as btrfs
# • exfat is reported as exfat (or fuseblk?)
# • ext2  is reported as ext2
# • ext3  is reported as ext3
# • ext4  is reported as ext4
# • fat12 is reported as vfat (?)
# • fat16 is reported as vfat
# • fat32 is reported as vfat
# • ntfs  is reported as fuseblk
# • swap  is reported as devtmpfs
# • xfs   is reported as xfs
# • zfs   is reported as zfs

# Remote file system types:
# • fuse.gvfsd-fuse
# • fuse.sshfs

# Map Linux file system types to display names.
# For completeness, this dictionary includes file system types that are
# not reported by `df --print-type` (i.e. fat12, fat16, fat32, ntfs).
FILE_SYSTEM_TYPES = {
    'btrfs': 'btrfs',
    'exfat': 'exFAT',
    'ext2': 'ext2',
    'ext3': 'ext3',
    'ext4': 'ext4',
    'fat12': 'FAT12',
    'fat16': 'FAT16',
    'fat32': 'FAT32',
    'ntfs': 'NTFS',
    'fuseblk': 'NTFS',
    'vfat': 'FAT',
    'xfs': 'XFS',
    'zfs': 'ZFS',
    'fuse.gvfsd-fuse': 'remote',
    'fuse.sshfs': 'remote'
}

# For completeness, this list includes file system types that are
# not reported by `df --print-type` (i.e. fat12, fat16, fat32, ntfs).
EXCLUDED_FILE_SYSTEM_TYPES = ['exfat', 'fat12', 'fat16', 'fat32', 'fuseblk', 'ntfs', 'vfat', 'fuse.gvfsd-fuse', 'fuse.sshfs']

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
# Terminal Font Colors & Console Codes
########################################################################

# TODO: Replace colors in other modules with these.

# https://en.wikipedia.org/wiki/ANSI_escape_code
# https://stackoverflow.com/questions/4842424/list-of-ansi-color-escape-sequences

RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[0;33m'
BLUE = '\033[0;34m'
MAGENTA = '\033[0;35m'
CYAN = '\033[0;36m'
# GRAY = '\033[0;90m'

BOLD_RED = '\033[1;31m'
BOLD_GREEN = '\033[1;32m'
BOLD_YELLOW = '\033[1;33m'
BOLD_BLUE = '\033[1;34m'
BOLD_MAGENTA = '\033[1;35m'
BOLD_CYAN = '\033[1;36m'
# BOLD_GRAY = '\033[1;90m'

NORMAL = '\033[0m'

# https://stackoverflow.com/questions/45065919/move-cursor-position-in-bash-at-specific-column
# http://www.termsys.demon.co.uk/vtansi.htm
# Cursor Backward		<ESC>[{COUNT}D
# Moves the cursor backward by COUNT columns; the default count is 1.
# NEW_LINE = '\033[50D\033[-1C\n'
NEW_LINE = '\033[99D\n'

########################################################################
# Control Keys
########################################################################

CONTROL_SHIFT_KEYS_1 = (Gdk.ModifierType.SHIFT_MASK | Gdk.ModifierType.CONTROL_MASK)
CONTROL_SHIFT_KEYS_2 = (Gdk.ModifierType.SHIFT_MASK | Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.MODIFIER_RESERVED_25_MASK)

########################################################################
# Emulator
########################################################################

# Allocate memory to the emulator in increments of 256 MiB.
MEMORY_INCREMENT = 256 * MIB

# The minimum system memory to reserve after allocating memory to the
# emulator.
MIN_RESERVE_MEMORY = 1 * 512 * MIB  # Bytes (512 MiB, 0.5 GiB)

# The minimum available memory to reserve while testing.
MIN_AVAILABLE_MEMORY = 3 * 512 * MIB  # Bytes (1536 MiB, 1.5 GiB)
MIN_AVAILABLE_MEMORY_MIB = MIN_AVAILABLE_MEMORY / MIB
MIN_AVAILABLE_MEMORY_GIB = MIN_AVAILABLE_MEMORY / GIB
