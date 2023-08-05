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

    def parse(self, event):
        """
        Parse message
        """

@implementer(Parser)
class Json(object):
    """
    JSON event parser
    """

    def parse(self, event):
        """
        Create a Json object
        """
        self.event = event
        return json.loads(event)

component.provideUtility(Json(), Parser, 'json')
