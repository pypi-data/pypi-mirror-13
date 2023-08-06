"""
The target class.
"""

from itertools import product

from .target_template import TargetTemplate


class Target(object):
    """
    Represents a target.
    """
    def __init__(self, template_name, filename, scopes):
        """
        Initializes a new target.

        :param template_name: The name of the template to use for content
            generation.
        :param filename: The filename of the file to generate. Can contain
            Jinja2 template instructions.
        :param scopes: A dictionary of scopes indexed by their alias.
        """
        self.template_name = template_name
        self.filename = filename
        self.scopes = scopes

    def generate_scoped_contexts(self, context):
        """
        Generator that yields all the contexts from the specified context
        through the associated scopes.

        :param context: The root context.
        :yields: All the scoped contexts generated for this target.
        """
        if not self.scopes:
            yield context
        else:
            resolved_scopes = {
                alias: scope.resolve(context=context)
                for alias, scope in self.scopes.items()
            }

            axes_dimensions = list(zip(*[
                (alias, ctx)
                for alias, ctx in sorted(resolved_scopes.items())
                if self.scopes[alias].is_iterable
            ]))

            if axes_dimensions:
                axes, dimensions = axes_dimensions

                for dimension in product(*dimensions):
                    scoped_context = resolved_scopes.copy()
                    scoped_context.update(dict(zip(axes, dimension)))
                    yield scoped_context
            else:
                yield resolved_scopes

    def get_template(self, environment):
        """
        Get the associated target template loaded from the specified Jinja2
        environment.

        :param environment: The Jinja2 template environment.
        :returns: A `TargetTemplate` instance.
        """
        return TargetTemplate(
            template=environment.get_template(self.template_name),
            filename_template=environment.from_string(self.filename),
        )

    def generate(self, environment, context):
        """
        Generator that yields all the rendered pairs for the target, using the
        specified environment and context.

        :param environment: The Jinja2 template environment.
        :param context: The root context to use.
        :yields: Pairs of (filename, content) for the target.
        """
        target_template = self.get_template(environment)

        for scoped_context in self.generate_scoped_contexts(context):
            yield target_template.render(scoped_context)
