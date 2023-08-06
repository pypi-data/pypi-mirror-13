# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Parsers
"""
import json
from zope import component
from zope.interface import Interface, implementer

class Parser(Interface):
    """
    Parser interface
    """

    def parsed(self, event):
        """
        Parse message
        """

@implementer(Parser)
class Json(object):
    """
    JSON event parser
    """
    def __init__(self):
        self.n = 0

    def parsed(self, event):
        """
        Create a Json object
        """
        self.event = event
        # self.n += 1
        # print(self.n, '->', event)
        try:
            return json.loads(event)
        except:
            return {'ERROR': event}

component.provideUtility(Json(), Parser, 'json')
