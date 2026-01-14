"""Git repository information and verification actions.

This module provides launch actions for working with git repositories,
including logging repository information, verifying commits, and checking
repository cleanliness.
"""

from pathlib import Path
import git

import launch.logging
from launch.launch_context import LaunchContext
from launch.actions import OpaqueFunction
from launch.some_substitutions_type import SomeSubstitutionsType
from launch.utilities import normalize_to_list_of_substitutions, perform_substitutions


def get_repo_info(context: LaunchContext, path: SomeSubstitutionsType) -> None:
    """Get git repository information and log it.

    Logs the repository path, current branch, commit hash, and dirty status.

    Args:
        context: Launch context for performing substitutions
        path: Path to the git repository

    Returns:
        None
    """
    path = Path(perform_substitutions(context, path))
    try:
        repo = git.Repo(path, search_parent_directories=True)
        launch.logging.get_logger("launch.user").info(
            f"Repository Info | Path: {path.absolute()}, Branch: {repo.active_branch.name}, Commit: {repo.head.object.hexsha + (' (dirty)' if repo.is_dirty() else '')}"
        )
    except Exception as e:
        launch.logging.get_logger("launch.user").warn(
            f"Error getting git repo info at {path.absolute()}: {e}"
        )


def verify_repo_is_clean(
    context: LaunchContext, path: SomeSubstitutionsType, pass_on_failure: bool
) -> None:
    """Verify that the git repository has no uncommitted changes.

    Args:
        context: Launch context for performing substitutions
        path: Path to the git repository
        pass_on_failure: Whether to continue on failure or raise an exception

    Raises:
        RuntimeError: If the repository is dirty and pass_on_failure is False
        Exception: If repository access fails and pass_on_failure is False

    Returns:
        None
    """
    path = Path(perform_substitutions(context, path))
    try:
        repo = git.Repo(path, search_parent_directories=True)
        if repo.is_dirty():
            if pass_on_failure:
                launch.logging.get_logger("launch.user").warn(
                    f"Git repo at {path.absolute()} is dirty"
                )
            else:
                raise RuntimeError(f"Git repo at {path.absolute()} is dirty.")
        else:
            launch.logging.get_logger("launch.user").info(
                f"Git repo at {path.absolute()} is clean."
            )
    except Exception as e:
        launch.logging.get_logger("launch.user").warn(
            f"Error getting git repo info at {path.absolute()}: {e}"
        )
        if not pass_on_failure:
            raise e


def verify_repo_commit(
    context: LaunchContext,
    path: SomeSubstitutionsType,
    commit: SomeSubstitutionsType,
    pass_on_failure: bool,
) -> None:
    """Verify that the git repository is at the specified commit.

    Args:
        context: Launch context for performing substitutions
        path: Path to the git repository
        commit: Expected commit hash (full or abbreviated)
        pass_on_failure: Whether to continue on failure or raise an exception

    Raises:
        RuntimeError: If the repository is not at the specified commit and pass_on_failure is False
        Exception: If repository access fails and pass_on_failure is False

    Returns:
        None
    """
    path = Path(perform_substitutions(context, path))
    commit = perform_substitutions(context, commit)
    try:
        repo = git.Repo(path, search_parent_directories=True)
        if repo.head.object.hexsha != commit:
            if pass_on_failure:
                launch.logging.get_logger("launch.user").warn(
                    f"Git repo at {path.absolute()} is not at commit {commit}. Currently at {repo.head.object.hexsha}."
                )
            else:
                raise RuntimeError(f"Git repo at {path.absolute()} is not at commit {commit}.")
        else:
            launch.logging.get_logger("launch.user").info(
                f"Git repo at {path.absolute()} is at commit {commit}."
            )
    except Exception as e:
        launch.logging.get_logger("launch.user").warn(
            f"Error getting git repo info at {path.absolute()}: {e}"
        )
        if not pass_on_failure:
            raise e


def LogRepoInfo(path: SomeSubstitutionsType) -> OpaqueFunction:
    """Create an action that logs git repository information.

    Args:
        path: Path to the git repository

    Returns:
        OpaqueFunction that will log repository information when executed
    """
    path = normalize_to_list_of_substitutions(path)

    return OpaqueFunction(function=get_repo_info, kwargs={"path": path})


def VerifyRepoCommit(
    path: SomeSubstitutionsType, commit: SomeSubstitutionsType, pass_on_failure: bool = True
) -> OpaqueFunction:
    """Create an action that verifies a git repository is at a specific commit.

    Args:
        path: Path to the git repository
        commit: Expected commit hash to verify against
        pass_on_failure: Whether to continue on verification failure (default: True)

    Returns:
        OpaqueFunction that will verify the commit when executed
    """

    path = normalize_to_list_of_substitutions(path)
    commit = normalize_to_list_of_substitutions(commit)

    return OpaqueFunction(
        function=verify_repo_commit,
        kwargs={"path": path, "commit": commit, "pass_on_failure": pass_on_failure},
    )


def save_git_diff(
    context: LaunchContext,
    path: SomeSubstitutionsType,
    output_file: SomeSubstitutionsType,
    pass_on_failure: bool,
) -> None:
    """Save git diff output to a file.

    Args:
        context: Launch context for performing substitutions
        path: Path to the git repository
        output_file: File path where diff should be saved
        pass_on_failure: Whether to continue on failure or raise an exception

    Returns:
        None
    """
    path = Path(perform_substitutions(context, path))
    output_file = Path(perform_substitutions(context, output_file))
    try:
        repo = git.Repo(path, search_parent_directories=True)
        with open(output_file, "w") as f:
            f.write(repo.git.diff())
    except Exception as e:
        launch.logging.get_logger("launch.user").warn(
            f"Error getting git repo info at {path.absolute()}: {e}"
        )
        if not pass_on_failure:
            raise e


def SaveRepoDiff(
    path: SomeSubstitutionsType, output_file: SomeSubstitutionsType, pass_on_failure: bool = True
) -> OpaqueFunction:
    """Create an action that saves git repository diff to a file.

    Args:
        path: Path to the git repository
        output_file: File path where diff should be saved
        pass_on_failure: Whether to continue on failure (default: True)

    Returns:
        OpaqueFunction that will save the diff when executed
    """

    path = normalize_to_list_of_substitutions(path)
    output_file = normalize_to_list_of_substitutions(output_file)

    return OpaqueFunction(
        function=save_git_diff,
        kwargs={"path": path, "output_file": output_file, "pass_on_failure": pass_on_failure},
    )


def VerifyRepoClean(path: SomeSubstitutionsType, pass_on_failure: bool = True) -> OpaqueFunction:
    """Create an action that verifies a git repository has no uncommitted changes.

    Args:
        path: Path to the git repository
        pass_on_failure: Whether to continue on verification failure (default: True)

    Returns:
        OpaqueFunction that will verify repository cleanliness when executed
    """

    path = normalize_to_list_of_substitutions(path)

    return OpaqueFunction(
        function=verify_repo_is_clean, kwargs={"path": path, "pass_on_failure": pass_on_failure}
    )
