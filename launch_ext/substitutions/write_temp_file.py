"""Module for the WriteTempFile substitution."""

from typing import Text, List, BinaryIO
from tempfile import NamedTemporaryFile

from launch.launch_context import LaunchContext
from launch.substitution import Substitution
from launch.some_substitutions_type import SomeSubstitutionsType
from launch.utilities import normalize_to_list_of_substitutions
from launch.utilities import perform_substitutions


class WriteTempFile(Substitution):
    """Substitution that writes the contents to a named temporary file and returns the file path."""

    def __init__(self, contents: SomeSubstitutionsType) -> None:
        """Create a WriteTempFile substitution."""
        super().__init__()
        self.__contents = contents

    @property
    def contents(self) -> List[Substitution]:
        """Getter for contents."""
        return normalize_to_list_of_substitutions(self.__contents)

    def describe(self) -> Text:
        """Return a description of this substitution as a string."""
        contents_str = ' + '.join([sub.describe() for sub in self.contents])
        return 'WriteTempFile(contents={})'.format(contents_str)

    def write(self, handle: BinaryIO, context: LaunchContext) -> None:
        handle.write(perform_substitutions(context, self.contents).encode())

    def perform(self, context: LaunchContext) -> Text:
        """Perform the substitution by writing the contents to a temporary file and returning the file path."""

        temp_file = NamedTemporaryFile(delete=False)
        self.write(temp_file, context)
        temp_file.flush()
        return temp_file.name
