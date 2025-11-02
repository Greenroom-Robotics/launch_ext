"""substitutions Module."""

from .templated import Templated
from .unary import Unary
from .write_temp_file import WriteTempFile
from .yaml_to_file import YAMLToFile
from .yaml_to_json import YamlToJson
from .xacro import Xacro
from .resolve_host import ResolveHost

# Alias for consistent naming
YamlToFile = YAMLToFile

__all__ = [
    'ROSLoggers',
    'Templated',
    'Unary',
    'WriteTempFile',
    'YAMLToFile',
    'YamlToFile',
    'YamlToJson',
    "Xacro",
    "ResolveHost"
]
