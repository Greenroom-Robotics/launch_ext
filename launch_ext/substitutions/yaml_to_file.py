"""Module for the YAMLToFile substitution."""

from typing import Any, BinaryIO, Text
import yaml

from launch.launch_context import LaunchContext
from launch.substitution import Substitution
from launch.some_substitutions_type import SomeSubstitutionsType

from .write_temp_file import WriteTempFile


class YAMLToFile(WriteTempFile):
    """Substitution that writes the YAML contents to a named temporary file and returns the file path."""

    @property
    def contents(self) -> Any:
        """Getter for contents."""
        return self._WriteTempFile__contents

    def describe(self) -> Text:
        """Return a description of this substitution as a string."""
        contents_str = ' + '.join([sub.describe() for sub in super().contents])
        return 'YAMLToFile(contents={})'.format(contents_str)

    def write(self, handle: BinaryIO, context: LaunchContext) -> None:
        #pyyaml representer for Substitution objects
        def substitution_representer(dumper: yaml.Dumper, data: SomeSubstitutionsType):
            return dumper.represent_str(data.perform(context))

        yaml.add_multi_representer(Substitution, substitution_representer)
        yaml.dump(self.contents, handle, encoding='utf8')
