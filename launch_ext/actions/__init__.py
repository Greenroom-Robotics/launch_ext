"""actions Module."""

from .log_rotate import LogRotate
from .include_package_launch_file import IncludePackageLaunchFile
from .make_device_node import MakeDeviceNode, MakeDeviceNodeFromPath
from .write_file import WriteFile
from .set_launch_configuration_if_not_none import SetLaunchConfigurationIfNotNone
from .git_repo_info import LogRepoInfo, VerifyRepoCommit, VerifyRepoClean, SaveRepoDiff

__all__ = [
    'LogRotate',
    'IncludePackageLaunchFile'
    'WriteFile',
    'SetLaunchConfigurationIfNotNone',
    'ExecuteLocalExt',
    'ExecuteProcessExt',
    'MakeDeviceNode',
    'LogRepoInfo',
    'VerifyRepoCommit',
    'VerifyRepoClean',
    'SaveRepoDiff',
]

# hack city hack hack city

try:
    from .execute_local import ExecuteLocalExt
    from .execute_process import ExecuteProcessExt
    __all__.extend(['ExecuteLocalExt', 'ExecuteProcessExt'])
except ImportError:
    pass
