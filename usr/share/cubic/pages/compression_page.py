#!/usr/bin/python3

########################################################################
#                                                                      #
# compression_page.py                                                  #
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

from utilities import configuration
from utilities import displayer
from utilities import iso_utilities
from utilities import logger
from utilities import model

########################################################################
# References
########################################################################

# https://catchchallenger.first-world.info/wiki/Quick_Benchmark:_Gzip_vs_Bzip2_vs_LZMA_vs_XZ_vs_LZ4_vs_LZO#The_file_test_results
# http://www.ilsistemista.net/index.php/linux-a-unix/44-linux-compressors-comparison-on-centos-6-5-x86-64-lzo-vs-lz4-vs-gzip-vs-bzip2-vs-lzma.html?start=4
# https://fastcompression.blogspot.com/2015/01/zstd-stronger-compression-algorithm.html

########################################################################
# Globals & Constants
########################################################################

name = 'compression_page'

radio_buttons = {
    'lz4': 'compression_page__radio_button_1',
    'lzo': 'compression_page__radio_button_2',
    'gzip': 'compression_page__radio_button_3',
    'zstd': 'compression_page__radio_button_4',
    'lzma': 'compression_page__radio_button_5',
    'xz': 'compression_page__radio_button_6'
}

########################################################################
# Navigation Functions
########################################################################


def setup(action, old_page=None):

    if action == 'back':

        displayer.reset_buttons(
            back_button_label='❬Back',
            back_action='back',
            back_button_style=None,
            is_back_sensitive=True,
            is_back_visible=True,
            next_button_label='Generate❭',
            next_action='generate',
            next_button_style='suggested-action',
            is_next_sensitive=True,
            is_next_visible=True)

        return

    elif action == 'next':

        displayer.reset_buttons(
            back_button_label='❬Back',
            back_action='back',
            back_button_style=None,
            is_back_sensitive=True,
            is_back_visible=True,
            next_button_label='Generate❭',
            next_action='generate',
            next_button_style='suggested-action',
            is_next_sensitive=True,
            is_next_visible=True)

        print('*** SETUP NEXT: model.options.compression = %s' % model.options.compression)

        return

    else:

        return 'unknown'


def enter(action, old_page=None):

    if action == 'back':

        return

    elif action == 'next':

        # 1 = lz4
        # 2 = lzo
        # 3 = gzip
        # 4 = zstd
        # 5 = lzma
        # 6 = xz

        if not model.options.compression: model.options.compression = 'gzip'
        displayer.activate_radio_button(radio_buttons[model.options.compression], True)

        return

    else:

        return 'unknown'


def leave(action, new_page=None):

    if action == 'back':

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        configuration.save()

        return

    elif action == 'generate':

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        # logger.log_value('Selected compression', model.options.compression)

        configuration.save()

        return

    elif action == 'quit':

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        iso_utilities.unmount_iso_and_delete_mount_point(model.project.iso_mount_point)

        configuration.save()

        return

    else:

        displayer.reset_buttons(is_back_sensitive=False, is_next_sensitive=False)

        configuration.save()

        return 'unknown'


########################################################################
# Handler Functions
########################################################################


def on_toggled__compression_page__radio_button(toggle_button):

    # 1 = lz4
    # 2 = lzo
    # 3 = gzip
    # 4 = zstd
    # 5 = lzma
    # 6 = xz

    if toggle_button.get_active():
        model.options.compression = toggle_button.get_label()
        # logger.log_value('Selected compression', model.options.compression)


########################################################################
# Support Functions
########################################################################

# N/A
