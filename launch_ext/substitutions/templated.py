"""Module for the TemplateSubstitution substitution."""

from typing import List, Text

from string import Template

from launch.launch_context import LaunchContext
from launch.substitution import Substitution
from launch.some_substitutions_type import SomeSubstitutionsType
from launch.utilities import normalize_to_list_of_substitutions
from launch.utilities import perform_substitutions

class Templated(Substitution):
    """Substitution that wraps a single string text."""

    def __init__(self, template: SomeSubstitutionsType) -> None:
        """Create a TemplateSubstitution."""
        super().__init__()

        self.__template = normalize_to_list_of_substitutions(template)

    @property
    def raw_template(self) -> List[Substitution]:
        """Getter for the raw template."""
        return self.__template

    def describe(self) -> Text:
        """Return a description of this substitution as a string."""
        return "'{}'".format(self.raw_template)

    def perform(self, context: LaunchContext) -> Text:
        """Perform the substitution by returning the string with values substituted."""

        temp = Template(perform_substitutions(context, self.raw_template))
        return temp.substitute(context.launch_configurations)
