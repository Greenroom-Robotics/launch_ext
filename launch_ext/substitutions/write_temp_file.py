"""Substitution for creating temporary files with content.

This module provides a substitution that writes content to a temporary file
and returns the file path, useful for passing configuration data to processes
that require file-based input.
"""

from typing import Text, List, BinaryIO
from tempfile import NamedTemporaryFile

from launch.launch_context import LaunchContext
from launch.substitution import Substitution
from launch.some_substitutions_type import SomeSubstitutionsType
from launch.utilities import normalize_to_list_of_substitutions
from launch.utilities import perform_substitutions


class WriteTempFile(Substitution):
    """Substitution that creates a temporary file with content and returns its path.

    This substitution is useful for creating temporary configuration files,
    parameter files, or any other content that needs to be written to disk
    for use by other processes during launch.

    Example:
        WriteTempFile("configuration content")
        WriteTempFile(["line 1\n", "line 2\n"])

    The temporary file is created with delete=False, so it persists until
    manually cleaned up or the system removes it.
    """

    def __init__(self, contents: SomeSubstitutionsType) -> None:
        """Initialize the WriteTempFile substitution.

        Args:
            contents: Content to write to the temporary file. Can be a string,
                     substitution, or list of strings/substitutions.
        """
        super().__init__()
        self.__contents = contents

    @property
    def contents(self) -> List[Substitution]:
        """Get the contents as a list of substitutions.

        Returns:
            List of substitution objects representing the file contents
        """
        return normalize_to_list_of_substitutions(self.__contents)

    def describe(self) -> Text:
        """Return a description of this substitution.

        Returns:
            String description of the substitution for debugging
        """
        contents_str = ' + '.join([sub.describe() for sub in self.contents])
        return 'WriteTempFile(contents={})'.format(contents_str)

    def write(self, handle: BinaryIO, context: LaunchContext) -> None:
        """Write the contents to a file handle.

        Args:
            handle: Binary file handle to write to
            context: Launch context for performing substitutions

        Returns:
            None
        """
        handle.write(perform_substitutions(context, self.contents).encode())

    def perform(self, context: LaunchContext) -> Text:
        """Create a temporary file with the content and return its path.

        Creates a named temporary file, writes the substituted content to it,
        and returns the file path. The file is not automatically deleted.

        Args:
            context: Launch context for performing substitutions

        Returns:
            Path to the created temporary file
        """
        temp_file = NamedTemporaryFile(delete=False)
        self.write(temp_file, context)
        temp_file.flush()
        return temp_file.name
