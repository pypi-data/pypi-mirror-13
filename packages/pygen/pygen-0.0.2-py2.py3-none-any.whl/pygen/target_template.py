"""
Target template class.
"""

import os


class TargetTemplate(object):
    """
    A target template represents a file to produce from a context.
    """
    def __init__(
        self,
        template,
        filename_template,
    ):
        """
        Initializes a new target template.

        :param template: The Jinja2 template instance that will be the source
            for the generated content.
        :param filename_template: The Jinja2 template instance that will be the
            source for the generated file's name. It is up the the caller to
            ensure that the resulting string is a valid filename.
        """
        self.template = template
        self.filename_template = filename_template

    def render_content(self, context):
        """
        Renders the target's content from the specified context.

        :param context: A context dictionary.
        :returns: The content as a string.
        """
        return self.template.render(context)

    def render_filename(self, context):
        """
        Renders the target's filename from the specified context.

        :param context: A context dictionary.
        :returns: The resulting filename, normalized.
        """
        return os.path.normpath(self.filename_template.render(context))

    def render(self, context):
        """
        Render the target from the specified context.

        :param context: A context dictionary.
        :returns: A pair (filename, content).
        """
        return self.render_filename(context), self.render_content(context)
