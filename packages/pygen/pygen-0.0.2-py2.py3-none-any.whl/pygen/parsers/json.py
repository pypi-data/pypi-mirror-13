"""
A JSON file parser.
"""

from __future__ import absolute_import

import json
import mimetypes

from .base import BaseParser


class JsonParser(BaseParser):
    extensions = {'.json'}
    mimetypes = {
        'application/json',
        'text/json',
    }

    @classmethod
    def register(cls):
        for mimetype in sorted(cls.mimetypes):
            for extension in sorted(cls.extensions):
                mimetypes.add_type(mimetype, extension)

    def load(self, file):
        return json.load(file)

    def loads(self, s):
        return json.loads(s)
