#!/usr/bin/env python
# -*- coding: utf-8 -*-

# activity.py by:
#    Agustin Zubiaga <aguz@sugarlabs.org>
#    Ignacio Rodríguez <ignacio@sugarlabs.org>

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

import gtk
import gobject

gtk.gdk.threads_init()

from sugar import profile
from sugar.activity import activity
from sugar.activity.widgets import ActivityToolbarButton
from sugar.activity.widgets import StopButton
from sugar.graphics.toolbarbox import ToolbarBox
from sugar.graphics.radiotoolbutton import RadioToolButton
from sugar.graphics.icon import Icon
from sugar.graphics import iconentry

from gettext import gettext as _

from canvas import Canvas


class InstallActivity(activity.Activity):

    def __init__(self, handle):
        activity.Activity.__init__(self, handle)

        self.max_participants = 1

        # Canvas
        canvas = Canvas(self)
        self.set_canvas(canvas)

        self._download_list = canvas.gtk_list.download_list

        # Toolbars
        toolbarbox = ToolbarBox()

        activity_button = ActivityToolbarButton(self)
        toolbarbox.toolbar.insert(activity_button, 0)

        separator = gtk.SeparatorToolItem()
        separator.set_draw(False)
        separator.set_expand(False)
        toolbarbox.toolbar.insert(separator, -1)

        # Switch
        store_list = RadioToolButton()
        store_list.set_active(True)
        store_list.props.icon_name = 'view-list'
        store_list.connect("clicked", canvas.switch_to_list)
        store_list.set_tooltip(_("Show the search list"))
        toolbarbox.toolbar.insert(store_list, -1)

        downloads_list = RadioToolButton()
        downloads_list.connect("clicked", canvas.switch_to_downloads_list)
        downloads_list.set_tooltip(_("Show the downloads list"))
        downloads_list.props.group = store_list


        self.downloads_icon = DownloadsIcon()
        downloads_list.set_icon_widget(self.downloads_icon)

        toolbarbox.toolbar.insert(downloads_list, -1)

        self.store_list = store_list
        self.downloads_list = downloads_list

        separator = gtk.SeparatorToolItem()
        separator.set_draw(True)
        separator.set_expand(False)
        toolbarbox.toolbar.insert(separator, -1)

        # Search
        search_entry = iconentry.IconEntry()
        search_entry.set_size_request(gtk.gdk.screen_width() / 4, -1)
        search_entry.set_icon_from_name(
                        iconentry.ICON_ENTRY_PRIMARY, 'system-search')
        search_entry.connect('activate', canvas.gtk_list.search)
        search_entry.connect('activate', lambda w:
                                               canvas.switch_to_list(None))
        search_entry.add_clear_button()
        search_item = gtk.ToolItem()
        search_item.add(search_entry)
        toolbarbox.toolbar.insert(search_item, -1)

        separator = gtk.SeparatorToolItem()
        separator.set_draw(False)
        separator.set_expand(True)
        toolbarbox.toolbar.insert(separator, -1)

        stopbtn = StopButton(self)
        toolbarbox.toolbar.insert(stopbtn, -1)

        self.set_toolbar_box(toolbarbox)
        self.show_all()

        canvas.set_page(0)


class DownloadsIcon(Icon):

    def __init__(self):
        Icon.__init__(self, icon_name='downloads')

        self._profile_colors = profile.get_color()

        self._count = 0
        self._time_out = None

        self.set_normal()

        self.show()

    def set_normal(self):
        self.set_fill_color("#282828")
        self.set_stroke_color("#FFFFFF")
        self._state = "normal"

    def set_profile_colors(self):
        self.set_xo_color(self._profile_colors)
        self._state = "profile_colors"

    def animate(self):
        if not self._time_out:
            self._time_out = gobject.timeout_add(700, self._animate_timeout)

    def _animate_timeout(self):
        self._count += 1

        if self._state == "normal":
            self.set_profile_colors()

        else:
            self.set_normal()

        if self._count >= 6:
            self._count = 0

            gobject.source_remove(self._time_out)
            self._time_out = None

            return False

        else:
            return True
