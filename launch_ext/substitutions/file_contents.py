"""Module for the FileContents substitution."""

from typing import Text, List

from pathlib import Path

from launch.launch_context import LaunchContext
from launch.substitution import Substitution
from launch.some_substitutions_type import SomeSubstitutionsType
from launch.utilities import normalize_to_list_of_substitutions
from launch.utilities import perform_substitutions
from launch.substitutions.substitution_failure import SubstitutionFailure


class FileContents(Substitution):
    """Substitution that contains the file contents of a file path."""

    def __init__(self, path: SomeSubstitutionsType) -> None:
        """Create an FileContents substitution."""
        super().__init__()
        self.__path = normalize_to_list_of_substitutions(path)

    @property
    def path(self) -> List[Substitution]:
        """Getter for path."""
        return self.__path

    def describe(self) -> Text:
        """Return a description of this substitution as a string."""
        path_str = ' + '.join([sub.describe() for sub in self.path])
        return 'FileContents(path={})'.format(path_str)

    def perform(self, context: LaunchContext) -> Text:
        """Perform the substitution by reading the contents of the file path."""
        path = Path(perform_substitutions(context, self.path))

        if not path.exists():
            raise SubstitutionFailure(f"Path '{path}' does not exist")

        if not path.is_file():
            raise SubstitutionFailure(f"'{path}' is not a file")

        return path.read_text()
