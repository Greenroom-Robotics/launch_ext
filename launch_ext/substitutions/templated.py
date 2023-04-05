"""Module for the TemplateSubstitution substitution."""

from typing import Text

from string import Template

from launch.launch_context import LaunchContext
from launch.substitution import Substitution


class Templated(Substitution):
    """Substitution that wraps a single string text."""

    def __init__(self, *, template: Text) -> None:
        """Create a TemplateSubstitution."""
        super().__init__()

        if not isinstance(template, Text):
            raise TypeError(
                "TemplateSubstitution expected Text object got '{}' instead.".format(type(template))
            )

        self.__template = Template(template)

    @property
    def template(self) -> Template:
        """Getter for template."""
        return self.__template

    def describe(self) -> Text:
        """Return a description of this substitution as a string."""
        return "'{}'".format(self.template)

    def perform(self, context: LaunchContext) -> Text:
        """Perform the substitution by returning the string with values substituted."""
        return self.template.substitute(context.launch_configurations)
