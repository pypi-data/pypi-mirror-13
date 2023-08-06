"""
A YAML file parser.
"""

from __future__ import absolute_import

import mimetypes
import yaml

from six import StringIO

from .base import BaseParser


class YamlParser(BaseParser):
    extensions = {'.yml', '.yaml'}
    mimetypes = {
        'application/yaml',
        'application/x-yaml',
        'application/vnd.yaml',
        'text/yaml',
        'text/x-yaml',
        'text/vnd.yaml',
    }

    @classmethod
    def register(cls):
        for mimetype in sorted(cls.mimetypes):
            for extension in sorted(cls.extensions):
                mimetypes.add_type(mimetype, extension)

    def load(self, file):
        return yaml.load(file)

    def loads(self, s):
        return yaml.load(StringIO(s))
