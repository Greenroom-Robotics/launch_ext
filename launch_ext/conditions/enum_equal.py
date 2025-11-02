"""Condition for comparing substitution values against enum values.

This module provides a condition class that enables comparison of substitution
results with enumeration values, supporting case-insensitive string matching.
"""

from typing import List, Text, Optional

from enum import Enum

from launch.condition import Condition
from launch.launch_context import LaunchContext
from launch.some_substitutions_type import SomeSubstitutionsType


def str_to_enum(enum_type: Enum, string: str) -> Optional[Enum]:
    """Convert a string to an enum value using case-insensitive matching.

    Args:
        enum_type: The enum class to search within
        string: The string value to match against enum names

    Returns:
        The matching enum value if found, None otherwise
    """
    for k, v in enum_type.__members__.items():
        if k.lower() == string.lower():
            return v
        
    return None


class EnumEqual(Condition):
    """Condition that checks if a substitution value equals a specific enum value.

    This condition performs case-insensitive comparison between the result of
    a substitution and an enum value, making it useful for comparing launch
    configuration parameters against predefined enum constants.

    Example:
        from enum import Enum

        class Mode(Enum):
            DEBUG = "debug"
            RELEASE = "release"

        EnumEqual(LaunchConfiguration('build_mode'), Mode.DEBUG)
    """

    def __init__(self, substitute: SomeSubstitutionsType, check_enum_value: Enum) -> None:
        """Initialize the EnumEqual condition.

        Args:
            substitute: Substitution whose result will be compared
            check_enum_value: Enum value to compare against
        """
        self.__substitute = substitute
        self._check_enum_value = check_enum_value
        super().__init__(predicate=self._predicate_func)

    def _predicate_func(self, context: LaunchContext) -> bool:
        """Evaluate the condition by comparing substitution result with enum value.

        Args:
            context: Launch context for performing substitutions

        Returns:
            True if the substitution result matches the enum value, False otherwise
        """
        enum_sub = str_to_enum(self._check_enum_value.__class__, self.__substitute.perform(context))
        return enum_sub == self._check_enum_value

    def describe(self) -> Text:
        """Return a description of this condition.

        Returns:
            String description of the condition for debugging
        """
        return self.__repr__()

    @staticmethod
    def enum_to_choices(enum_type: Enum) -> List[str]:
        """Convert an enum type to a list of lowercase choice strings.

        Useful for generating choice lists for command-line arguments or
        documentation purposes.

        Args:
            enum_type: The enum class to extract choices from

        Returns:
            List of lowercase enum member names
        """
        return [k.lower() for k, v in enum_type.__members__.items()]
