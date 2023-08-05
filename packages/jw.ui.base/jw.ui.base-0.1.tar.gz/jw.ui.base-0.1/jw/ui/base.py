# Copyright 2016 Johnny Wezel
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

"""
Base (interface)
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()

from zope.interface import Interface, Attribute

class Ui(Interface):
    """
    An abstract user interface
    """

    running = Attribute('running', 'Boolean indicating run status')

    def setup(self, **kwargs):
        """
        Setup user interface

        :param kwargs: arguments for setup

        Expected to set up the user interface
        """

    def widgetClass(self, name):
        """
        Get widget class for name

        :param name: widget class symbolic named
        :type name: str

        Expected to return a widget class from a name, normally using package entry points
        """

    def run(self):
        """
        Run user interface

        Expected to maintain user interface update or to run the loop
        """

    def stop(self):
        """
        Stop user interface

        Expected to stop maintaining interface updating (stop threads/greenlets) or stop the loop
        """

    def update(self):
        """
        Update status of user interface

        Expected to update display and events
        """

    def minimizeAll(self):
        """
        Minimize all windows

        Expected to minimize all windows
        """

    def restoreAll(self):
        """
        Restore all minimized windows

        Expected to restore all minimized windows
        """

class DisplayControl(Interface):
    """
    Control for displaying categorized data

    A display control is expected to set up a categorizing widget, like a notebook or tree view. The widget should
    display one element per category. A category is just a particular element of a dict.

    Example: after receiving three messages having the values "internal", "external" and "auxiliary" in their `source`
    member, three tabs with the respective values should be displayed.

    The category (or 'topic') name is to be supplied to `__init__`() in the `topic` keyword argument
    """

    parent = Attribute('parent', 'Parent control')

    kwargs = Attribute('kwargs', 'Keyword arguments')

    def report(self, message, show=False):
        """
        Report event

        :param message: event
        :type message: dict
        :param show: whether to switch to element reported
        :type show: bool

        Expected to fill message data into user interface
        """

    def collectStatus(self):
        """
        Update control status

        Expected to put all widget status information in the dict provided by self.kwargs['status'] if non-null
        """
