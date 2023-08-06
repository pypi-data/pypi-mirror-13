"""
Index class.
"""

import os
import yaml

from jinja2 import (
    Environment,
    PrefixLoader,
    FileSystemLoader,
)
from voluptuous import (
    Required,
    Schema,
)

from .scope import Scope
from .target import Target


class Index(object):
    """
    An index is a collection of targets.
    """
    @classmethod
    def load(cls, cwd, stream):
        """
        Load an index from a stream.
        :param cwd: The current directory. Used to resolve relative template
            paths.
        :param stream: A file-object to use as the source for the index.
        :returns: An `Index` instance.
        """
        data = yaml.load(stream)
        schema = Schema({
            Required('template_paths', default={}): {str: str},
            Required('targets', default={}): {
                str: {
                    'template_name': str,
                    'filename': str,
                    Required('scopes', default={}): {
                        str: Scope.from_string
                    },
                },
            },
        })
        parsed_data = schema(data)

        template_paths = parsed_data['template_paths']

        if template_paths:
            loader = PrefixLoader({
                prefix: FileSystemLoader(os.path.join(cwd, path))
                for prefix, path in template_paths.items()
            })
        else:
            loader = FileSystemLoader(cwd)

        environment = Environment(
            loader=loader,
            keep_trailing_newline=True,
        )
        targets = {
            target_name: Target(**target)
            for target_name, target in parsed_data['targets'].items()
        }
        return cls(environment=environment, targets=targets)

    def __init__(self, environment, targets):
        """
        Initialize a new index.

        :param environment: The Jinja2 template environment.
        :param targets: A dictionary of targets indexed by their names.
        """
        self.environment = environment
        self.targets = targets

    def generate(self, context):
        """
        Generator that yields all the rendered pairs for the targets, using the
        specified context.

        :param context: The root context to use.
        :yields: Triplets of (target_name, filename, content) for the targets.

        .. note::
            Targets are picked in alphabetical order.
        """
        for target_name, target in sorted(self.targets.items()):
            for filename, content in target.generate(
                environment=self.environment,
                context=context,
            ):
                yield target_name, filename, content
