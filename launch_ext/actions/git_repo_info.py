"""Module for Git Repo based actions."""

from pathlib import Path
import git

import launch.logging
from launch.launch_context import LaunchContext
from launch.actions import OpaqueFunction
from launch.some_substitutions_type import SomeSubstitutionsType
from launch.utilities import normalize_to_list_of_substitutions, perform_substitutions


def get_repo_info(context: LaunchContext, path: SomeSubstitutionsType):
    """Get the git repo info and log it.

    Args:
        context (LaunchContext): LaunchContext
        path (SomeSubstitutionsType): Path to the git repo
    """
    path: Path = Path(perform_substitutions(context, path))
    repo = git.Repo(path, search_parent_directories=True)
    launch.logging.get_logger('launch.user').info(f"Repository Info | Path: {path.absolute()}, Branch: {repo.active_branch.name}, Commit: {repo.head.object.hexsha + (' (dirty)' if repo.is_dirty() else '')}")

def verify_repo_is_clean(context: LaunchContext, path: SomeSubstitutionsType, pass_on_failure: bool):
    """Verify that the git repo is clean.

    Args:
        context (LaunchContext): LaunchContext
        path (SomeSubstitutionsType): Path to the git repo
        pass_on_failure (bool): Whether to pass on failure or raise an exception

    Raises:
        RuntimeError: If the git repo is dirty and pass_on_failure is False
    """
    path: Path = Path(perform_substitutions(context, path))
    repo = git.Repo(path, search_parent_directories=True)
    if repo.is_dirty():
        if pass_on_failure:
            launch.logging.get_logger('launch.user').warn(f"Git repo at {path.absolute()} is dirty")
        else:
            raise RuntimeError(f"Git repo at {path.absolute()} is dirty.")

def verify_repo_commit(context: LaunchContext, path: SomeSubstitutionsType, commit: SomeSubstitutionsType, pass_on_failure: bool):
    """Verify that the git repo is at the specified commit.

    Args:
        context (LaunchContext): LaunchContext
        path (SomeSubstitutionsType): Path to the git repo
        commit (SomeSubstitutionsType): Commit to check for
        pass_on_failure (bool): Whether to pass on failure or raise an exception

    Raises:
        RuntimeError: If the git repo is not at the specified commit and pass_on_failure is False
    """
    path: Path = Path(perform_substitutions(context, path))
    commit: str = perform_substitutions(context, commit)
    repo = git.Repo(path, search_parent_directories=True)
    if repo.head.object.hexsha != commit:
        if pass_on_failure:
            launch.logging.get_logger('launch.user').warn(f"Git repo at {path.absolute()} is not at commit {commit}. Currently at {repo.head.object.hexsha}.")
        else:
            raise RuntimeError(f"Git repo at {path.absolute()} is not at commit {commit}.")

def LogRepoInfo(path: SomeSubstitutionsType) -> OpaqueFunction:
    """Action that logs the git repo info when executed.

    Args:
        path (SomeSubstitutionsType): Path to the git repo

    Returns:
        OpaqueFunction: OpaqueFunction
    """
    path = normalize_to_list_of_substitutions(path)

    return OpaqueFunction(function=get_repo_info, kwargs={'path': path})

def VerifyRepoCommit(path: SomeSubstitutionsType, commit: SomeSubstitutionsType, pass_on_failure: bool=True) -> OpaqueFunction:
    """Action that commits the git repo info when executed.

    Args:
        path (SomeSubstitutionsType): Path to the git repo
        commit (SomeSubstitutionsType): Commit to check for
        pass_on_failure (bool, optional): Whether or not to pass on error. Defaults to True.

    Returns:
        OpaqueFunction: _description_
    """
    
    path = normalize_to_list_of_substitutions(path)
    commit = normalize_to_list_of_substitutions(commit)

    return OpaqueFunction(function=verify_repo_commit, kwargs={'path': path, 'commit': commit, 'pass_on_failure': pass_on_failure})

def VerifyRepoClean(path: SomeSubstitutionsType, pass_on_failure: bool=True) -> OpaqueFunction:
    """Action that commits the git repo info when executed.

    Args:
        path (SomeSubstitutionsType): Path to the git repo
        pass_on_failure (bool, optional): Whether or not to pass on error. Defaults to True.

    Returns:
        OpaqueFunction: _description_
    """

    path = normalize_to_list_of_substitutions(path)

    return OpaqueFunction(function=verify_repo_is_clean, kwargs={'path': path, 'pass_on_failure': pass_on_failure})