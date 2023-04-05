"""Module for EnumCondition class."""

from typing import Text, Optional

from enum import Enum

from launch.condition import Condition
from launch.launch_context import LaunchContext
from launch.some_substitutions_type import SomeSubstitutionsType


def str_to_enum(enum_type: Enum, string: str) -> Optional[Enum]:
    """
    Convert a string to an enum.

    :param enum_type: The enum type to convert to.
    :param string: The string to convert.
    :return: The enum value.
    """
    for k, v in enum_type.__members__.items():
        if k.lower() == string.lower():
            return v
        
    return None


class EnumCondition(Condition):
    """
    Encapsulates a condition to check if it equals an enum to be evaluated when launching.
    """

    def __init__(self, substitute: SomeSubstitutionsType, check_enum_value: Enum) -> None:
        self.__substitute = substitute
        self._check_enum_value = check_enum_value
        super().__init__(predicate=self._predicate_func)

    def _predicate_func(self, context: LaunchContext) -> bool:
        enum_sub = str_to_enum(self._check_enum_value.__class__, self.__substitute.perform(context))
        return enum_sub == self._check_enum_value

    def describe(self) -> Text:
        """Return a description of this Condition."""
        return self.__repr__()
