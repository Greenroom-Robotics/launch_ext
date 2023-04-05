"""Module for the UnarySubstitution substitution."""

from typing import Text

from launch.launch_context import LaunchContext
from launch.substitution import Substitution
from launch.conditional import Conditional
from launch.some_substitutions_type import SomeSubstitutionsType


class Unary(Substitution):
    """Substitution that returns one of two results depending on single conditional."""

    def __init__(self, *, conditional: Conditional, when_true: SomeSubstitutionsType, when_false: SomeSubstitutionsType) -> None:
        """Create a UnarySubstitution."""
        super().__init__()

        if not isinstance(conditional, Conditional):
            raise TypeError(
                "UnarySubstitution expected Conditional object got '{}' instead.".format(type(conditional))
            )

        self.__conditional = conditional
        self.__values = (when_false, when_true)

    def describe(self) -> Text:
        """Return a description of this substitution as a string."""
        return "'{} ? {} : {}'".format(self.__conditional, self.__values[1], self.__values[0])

    def perform(self, context: LaunchContext) -> Text:
        """Perform the substitution by returning the appropriate substitution."""

        from launch.utilities import perform_substitutions  # import here to avoid loop

        # False = 0, True = 1
        val = self.__values[self.__conditional.evaluate(context)]
        return perform_substitutions(context, val)
