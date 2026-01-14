"""Module for the WriteFile action."""

from pathlib import Path
import launch.logging
from launch.actions import OpaqueFunction
from launch.launch_context import LaunchContext
from launch.some_substitutions_type import SomeSubstitutionsType


def write_file(
    context: LaunchContext,
    contents: SomeSubstitutionsType,
    dest_path: SomeSubstitutionsType,
    overwrite: bool = True,
):
    contents = context.perform_substitution(contents)
    dest_path = Path(context.perform_substitution(dest_path))

    if dest_path.exists() and not overwrite:
        launch.logging.get_logger("launch.user").warn(f"File {dest_path} exists, not overwriting")
        return

    dest_path.write_text(contents)
    launch.logging.get_logger("launch.user").info(f"Wrote file '{dest_path}'.")


def WriteFile(contents: SomeSubstitutionsType, dest_path: SomeSubstitutionsType) -> OpaqueFunction:
    """Action that writes a substitution to a file."""
    return OpaqueFunction(
        function=write_file,
        kwargs={
            "contents": contents,
            "dest_path": dest_path,
        },
    )
