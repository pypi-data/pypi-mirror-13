"""
Scope exceptions.
"""


class InvalidScope(ValueError):
    """
    An invalid scope was specified.
    """
    def __init__(self, scope):
        super(InvalidScope, self).__init__("Not a valid scope: %r" % scope)
        self.scope = scope


class NoParserError(RuntimeError):
    """
    No parser was found for a given filename.
    """

    def __init__(self, mimetype, mimetypes):
        super(NoParserError, self).__init__(
            "No parser found for type {mimetype!r}. Supported mimetypes are: "
            "{mimetypes}".format(
                mimetype=mimetype,
                mimetypes=', '.join(mimetypes),
            ),
        )
        self.mimetype = mimetype
        self.mimetypes = mimetypes
