"""
Scope manipulation.
"""

import re

from .exceptions import InvalidScope


class Scope(object):
    """
    Represents a scope.
    """
    @classmethod
    def from_string(cls, value):
        """
        Creates a `Scope` instance from a dotted path string.

        :param value: The dotted path string.
        :returns: A `Scope` instance if `value` is a valid path.
        """
        is_iterable = value.endswith('...')

        if is_iterable:
            value = value[:-3]

        if value:
            if not re.match('^[\w\d_-]+(\.[\w\d_-]+)*$', value):
                raise InvalidScope(value)

            scope = [
                int(x) if re.match('^\d+$', x) else x
                for x in value.split('.')
            ]
        else:
            scope = []

        return cls(scope=scope, is_iterable=is_iterable)

    def __init__(self, scope=None, is_iterable=False):
        """
        Creates a new scope.

        :param scope: A list of path components.
        :param is_iterable: A boolean flag that indicates whether the scope
            points to an iterable.
        """
        self.scope = list(scope or [])
        self.is_iterable = is_iterable

    def __eq__(self, other):
        if not isinstance(other, Scope):
            return NotImplemented

        return (other.scope == self.scope) and \
            (other.is_iterable == self.is_iterable)

    def __ne__(self, other):
        return not self == other

    def __str__(self):
        result = '.'.join(self.scope)

        if self.is_iterable:
            result += '...'

        return result

    def __repr__(self):
        args = []

        if self.scope:
            args.append(repr(self.scope))

        if self.is_iterable:
            args.append('is_iterable=%r' % self.is_iterable)

        return 'Scope(%s)' % ', '.join(args)

    def resolve(self, context):
        """
        Resolve the scope into the specified context.

        :params context: The context to resolve the scope into.
        :returns: The resolved context.
        """
        if self.scope:
            return Scope(scope=self.scope[1:]).resolve(context[self.scope[0]])
        else:
            return context
