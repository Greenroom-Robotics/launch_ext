"""Module for the LogRotate action."""

from pathlib import Path
from typing import List, Optional
from datetime import datetime, timedelta
import shutil
import re

import launch.logging
from launch.actions import OpaqueFunction
from launch.launch_context import LaunchContext
from launch.some_substitutions_type import SomeSubstitutionsType
from launch.utilities import normalize_to_list_of_substitutions, perform_substitutions

# log dir is in this kind of format: 2023-04-06-01-17-08-449019-hostname-49
LOG_DIR_REGEX = re.compile(r"\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}-\d{6}-\w+-\d+")


def log_rotate(
    context: LaunchContext,
    logging_dir: SomeSubstitutionsType,
    max_age: timedelta,
    skip_directories: List[SomeSubstitutionsType],
    dry_run: bool,
):
    logging_dir = Path(perform_substitutions(context, logging_dir))
    skip_directories = [perform_substitutions(context, d) for d in skip_directories]

    # clean the root log directory
    for d in logging_dir.iterdir():
        if d.name in skip_directories or str(d) in skip_directories:
            continue

        if d.is_dir() and LOG_DIR_REGEX.match(d.name):
            age = datetime.now() - datetime.fromtimestamp(d.stat().st_mtime)
            if age > max_age:
                launch.logging.get_logger("launch.user").info(
                    f"Log Rotate: Deleting log directory {d}"
                )
                if not dry_run:
                    shutil.rmtree(d)


def LogRotate(
    max_age: timedelta,
    logging_dir: Optional[SomeSubstitutionsType] = None,
    skip_directories: Optional[List[SomeSubstitutionsType]] = None,
    dry_run: bool = False,
) -> OpaqueFunction:
    """Action that rotates the log directory when executed."""

    logging_dir = launch.logging._get_logging_directory() if logging_dir is None else logging_dir

    if logging_dir is not None:
        logging_dir = normalize_to_list_of_substitutions(logging_dir)

    if skip_directories is not None:
        skip_directories = normalize_to_list_of_substitutions(skip_directories)

    return OpaqueFunction(
        function=log_rotate,
        kwargs={
            "max_age": max_age,
            "logging_dir": logging_dir,
            "skip_directories": skip_directories if skip_directories is not None else [],
            "dry_run": dry_run,
        },
    )
