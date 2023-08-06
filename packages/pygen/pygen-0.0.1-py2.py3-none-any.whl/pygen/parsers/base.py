"""
The base parser.
"""


class BaseParser(object):
    @classmethod
    def register(cls):
        """
        Called when the class is first registerd.

        Typically used to register new mimetypes in the `mimetypes` module.
        """
