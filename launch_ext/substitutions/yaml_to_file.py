"""Substitution for writing data as YAML to temporary files.

This module provides a substitution that serializes data to YAML format
and writes it to a temporary file, returning the file path.
"""

from typing import Any, BinaryIO, Text
import yaml

from launch.launch_context import LaunchContext
from launch.substitution import Substitution
from launch.some_substitutions_type import SomeSubstitutionsType

from .write_temp_file import WriteTempFile


class YAMLToFile(WriteTempFile):
    """Substitution that serializes data to YAML and writes it to a temporary file.

    This substitution extends WriteTempFile to handle YAML serialization,
    allowing complex data structures to be written as YAML files for
    consumption by other processes.

    The substitution supports Substitution objects within the data structure,
    which are resolved during the YAML serialization process.

    Example:
        YAMLToFile({
            'config': {
                'mode': LaunchConfiguration('mode'),
                'debug': True
            }
        })
    """

    @property
    def contents(self) -> Any:
        """Get the contents to be serialized as YAML.

        Returns:
            The data structure to be serialized
        """
        return self._WriteTempFile__contents

    def describe(self) -> Text:
        """Return a description of this substitution.

        Note: Does not accurately represent the YAML contents due to Substitution limitations.

        Returns:
            String description of the substitution for debugging
        """
        contents_str = ' + '.join([sub.describe() for sub in super().contents])
        return 'YAMLToFile(contents={})'.format(contents_str)

    def write(self, handle: BinaryIO, context: LaunchContext) -> None:
        """Write the data as YAML to the file handle.

        This method configures a custom YAML representer to handle Substitution
        objects by evaluating them in the given context before serialization.

        Args:
            handle: Binary file handle to write to
            context: Launch context for performing substitutions

        Returns:
            None
        """
        dumper = yaml.Dumper

        def substitution_representer(dumper: yaml.Dumper, data: SomeSubstitutionsType):
            """PyYAML representer for Substitution objects.

            Args:
                dumper: YAML dumper instance
                data: Substitution object to represent

            Returns:
                YAML representation of the substitution result
            """
            return dumper.represent_str(data.perform(context))

        dumper.add_multi_representer(Substitution, substitution_representer)

        yaml.dump(self.contents, handle, Dumper=dumper, encoding='utf8')
