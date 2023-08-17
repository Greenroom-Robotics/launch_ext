"""Module for the ROSLogLevel substitution."""

from typing import Text, List

from launch.launch_context import LaunchContext
from launch.substitution import Substitution
from launch.some_substitutions_type import SomeSubstitutionsType
from launch.utilities import normalize_to_list_of_substitutions
from launch.utilities import perform_substitutions
from launch.substitutions.substitution_failure import SubstitutionFailure

def ROSLoggers(node_level: SomeSubstitutionsType = None, *args):
    out = []
    for a in args:
        if type(a) == dict:
            for k,v in a.items():
                out.append("--log-level")
                out.append(ROSLogLevel(v, name=k))

    if node_level is not None:
        out.append("--log-level")
        out.append(ROSLogLevel(v))
    return out

class ROSLogLevel(Substitution):
    """Substitution that contains the file contents of a file path."""

    def __init__(self, level: SomeSubstitutionsType, name: SomeSubstitutionsType = None, all_loggers:bool = False) -> None:
        """Create an ROSLogLevel substitution."""
        super().__init__()

        self.__node_name = None
        self.__node_level = normalize_to_list_of_substitutions(level)
        self.__all_loggers = all_loggers

        if not all_loggers and name is not None:
            self.__node_name = normalize_to_list_of_substitutions(name)
            # raise SubstitutionFailure(f"Cannot specify all loggers and specific log levels at the same time.")

    @property
    def level(self) -> Substitution:
        """Getter for path."""
        return self.__node_level

    def describe(self) -> Text:
        """Return a description of this substitution as a string."""
        return 'ROSLogLevel(level={})'.format(self.__node_level.describe())

    def perform(self, context: LaunchContext) -> Text:
        """Perform the substitution by obtaining the Node name from the context"""
        level = perform_substitutions(context, self.__node_level)

        try:
            if self.__node_name is not None:
                node_name = perform_substitutions(context, self.__node_name)
            else:
                node_name = context.get_locals_as_dict()['ros_specific_arguments']['name']
                _, node_name = node_name.split(":=")
        except KeyError:
            raise SubstitutionFailure(f"Invalid context for ROSLogLevel substitution.")

        if self.__all_loggers:
            return level
        else:
            return f"{node_name}:={level}"
