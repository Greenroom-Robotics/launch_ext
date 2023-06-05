"""Module for the LogRotate action."""

from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta
import shutil
import re

import launch.logging

from launch.actions import OpaqueFunction
from launch.launch_context import LaunchContext
from launch.some_substitutions_type import SomeSubstitutionsType

# example 2023-04-06-01-17-08-449019-88dae75e49cb-49
LOG_DIR_REGEX = re.compile(r'\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}-\d{6}-\w{12}-\w{16}-\d+')


def log_rotate(context: LaunchContext, root_log_dir: SomeSubstitutionsType, current_log_dir: Optional[SomeSubstitutionsType], max_age: Optional[timedelta], symlinks: bool=True):
    current_log_dir = Path(context.perform_substitution(current_log_dir))
    root_log_dir = Path(context.perform_substitution(root_log_dir)) if root_log_dir is not None else current_log_dir.parent

    if symlinks:
        # create a symlink to the latest log directory
        (root_log_dir / "latest").unlink(missing_ok=True)
        (root_log_dir / "latest").symlink_to(current_log_dir)
        launch.logging.get_logger('launch.user').info(f"Symlinked 'latest' log directory to {current_log_dir}")

    # clean the logs
    for d in root_log_dir.iterdir():
        if d.is_dir() and LOG_DIR_REGEX.match(d.name):
            age = datetime.fromtimestamp(d.stat().st_mtime) - datetime.datetime.now()
            if age > max_age:
                launch.logging.get_logger('launch.user').info(f"Deleting log directory {d}")
                # shutil.rmtree(d)


def LogRotate(current_log_dir: SomeSubstitutionsType, max_age: Optional[timedelta], root_log_dir: Optional[SomeSubstitutionsType]=None, symlinks: bool=True) -> OpaqueFunction:
    """Action that rotates the log directory when executed."""
    return OpaqueFunction(function=log_rotate, kwargs={
        'current_log_dir': current_log_dir,
        'max_age': max_age,
        'root_log_dir': root_log_dir,
        'symlinks': symlinks
    })
