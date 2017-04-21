#!/usr/bin/env python
# -*- coding: utf-8 -*-

# utils.py by:
#    Agustin Zubiaga <aguz@sugarlabs.org>
#    Ignacio Rodríguez <ignacio@sugarlabs.org>
#    Alan Aguiar <alanjas@gmail.com>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os
import gtk
import urllib
import logging

from sugar.activity import activity
from sugar.bundle.activitybundle import ActivityBundle

# Paths
LIST_DOWNLOAD = "http://people.sugarlabs.org/ignacio/store.lst"
LIST_DOWNLOAD_MIRROR1 = "http://people.sugarlabs.org/aguz/store.lst"
LIST_DOWNLOAD_MIRROR2 = "http://www.fing.edu.uy/~aaguiar/files/store.lst"
LIST_PATH = os.path.join(activity.get_bundle_path(), 'store.lst')
ICONS_DIR = os.path.join(activity.get_activity_root(), 'data')
TMP_DIR = os.path.join(activity.get_activity_root(), "tmp")

downloading = False

# Logging
_logger = logging.getLogger('install-activity')
_logger.setLevel(logging.DEBUG)
logging.basicConfig()

from gettext import gettext as _


def get_logger():
    return _logger


def _know():
    _file = None
    try:
        _file = urllib.urlopen(LIST_DOWNLOAD)
    except:
        try:
            _file = urllib.urlopen(LIST_DOWNLOAD_MIRROR1)
        except:
            try:
                _file = urllib.urlopen(LIST_DOWNLOAD_MIRROR2)
            except:
                pass
    return _file


def update_list():
    """Download the latest list version"""
    global downloading
    try:
        downloading = True
        remote_file = _know()
        if remote_file is not None:
            _file = open(LIST_PATH, 'w')
            _file.write(remote_file.read())
            _file.close()
            remote_file.close()
    except:
        pass

    downloading = False


def get_store_list():
    """Returns the store list"""
    store_list = []
    try:
        f = open(LIST_PATH, 'r')
        e = True
        while e:
            line = f.readline()
            if not(line):
                e = False
            else:
                line = line.replace('\n', '')
                l = line.split('|')
                store_list.append(l)
    except:
        pass

    return store_list


def get_icon(activity_id):
    """Returns the icon of an specified activity"""
    store_list = get_store_list()
    activity_obj = store_list[activity_id]
    number = activity_obj[0]

    file_image = os.path.join(ICONS_DIR, "icon%s" % number)
    if not os.path.exists(file_image):
        url =\
      'http://activities.sugarlabs.org/en-US/sugar/images/addon_icon/' + number
        f, headers = urllib.urlretrieve(url, file_image)

    pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(file_image, 45, 45)

    return pixbuf


def download_activity(_id, row, progress_function):
    """Download (and install) an activity"""
    store_list = get_store_list()
    #print 'store', store_list
    activity_obj = store_list[_id]

    name = activity_obj[2]
    name = name.lower()
    name = name.replace(' ', '_')
    n = activity_obj[0]
    web = 'http://activities.sugarlabs.org/es-ES/sugar/downloads/latest/'
    web = web + n + '/addon-' + n + '-latest.xo'
    version = activity_obj[4]

    def progress_changed(block, block_size, total_size):
        downloaded = block * block_size
        progress = downloaded * 100 / total_size
        #print 'la ro', row
        progress_function(row, progress)

    xo = name + '-' + version + '.xo'
    #print 'alan', web, xo
    file_path = os.path.join(activity.get_activity_root(), "data", xo)

    _logger.info(_("Downloading activity (%s)") % name)
    urllib.urlretrieve(web,
                       file_path,
                       reporthook=progress_changed)

    _logger.info(_("Installing activity (%s)") % name)
    install_activity(file_path, row, progress_function)





def install_activity(xofile, row, progress_function):
    """Install an downloaded activity"""
    # Show "Installing..." message
    progress_function(row, 150)

    # Install the .xo
    try:
        bundle = ActivityBundle(xofile)
        bundle.install()
    except:
        print 'fallo install'

    # Remove the .xo
    os.remove(xofile)

    # Show "Installed..." message
    progress_function(row, 200)

    _logger.info(_("Activity installed!"))

