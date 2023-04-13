"""substitutions Module."""

from .file_contents import FileContents
from .templated import Templated
from .unary import Unary
from .write_temp_file import WriteTempFile

__all__ = [
    'FileContents',
    'Templated',
    'Unary',
    'WriteTempFile'
]
