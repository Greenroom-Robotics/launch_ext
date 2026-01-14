"""Conditional substitution for ternary-like operations.

This module provides a substitution that evaluates a condition and returns
one of two possible values based on the result, similar to a ternary operator.
"""

from typing import Text

from launch.launch_context import LaunchContext
from launch.substitution import Substitution
from launch.condition import Condition
from launch.some_substitutions_type import SomeSubstitutionsType


class Unary(Substitution):
    """Conditional substitution that returns different values based on a condition.

    This substitution acts like a ternary operator (condition ? true_value : false_value),
    evaluating a condition and returning one of two possible substitution results.

    Example:
        Unary(
            conditional=IfCondition(LaunchConfiguration('debug')),
            when_true='debug_value',
            when_false='release_value'
        )
    """

    def __init__(
        self,
        *,
        conditional: Condition,
        when_true: SomeSubstitutionsType,
        when_false: SomeSubstitutionsType,
    ) -> None:
        """Initialize the Unary substitution.

        Args:
            conditional: Condition to evaluate
            when_true: Value to return when condition is True
            when_false: Value to return when condition is False

        Raises:
            TypeError: If conditional is not a Condition object
        """
        super().__init__()

        if not isinstance(conditional, Condition):
            raise TypeError(
                f"UnarySubstitution expected Conditional object got '{type(conditional)}' instead."
            )

        self.__conditional = conditional
        self.__values = (when_false, when_true)

    def describe(self) -> str:
        """Return a description of this substitution.

        Returns:
            String description in ternary operator format for debugging
        """
        return f"'{self.__conditional} ? {self.__values[1]} : {self.__values[0]}'"

    def perform(self, context: LaunchContext) -> str:
        """Evaluate the condition and return the appropriate value.

        Args:
            context: Launch context for evaluating conditions and substitutions

        Returns:
            String result of either when_true or when_false substitution
        """

        from launch.utilities import perform_substitutions  # import here to avoid loop

        # False = 0, True = 1
        val = self.__values[self.__conditional.evaluate(context)]
        return perform_substitutions(context, val)
