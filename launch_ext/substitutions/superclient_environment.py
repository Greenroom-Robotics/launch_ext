import os

from launch.substitutions import LaunchConfiguration
from launch.substitution import Substitution
import launch.logging


class SuperclientEnvironment(Substitution):
    """Substitution that provides the FastDDS SuperClient profile path.

    Use this in a Node's environment parameter to configure SuperClient mode.
    """

    def __init__(self, fastdds_superclient_profile_path: str | None = None):
        """Initialize the SuperclientEnvironment substitution.

        Args:
            fastdds_superclient_profile_path (str | None): Path to the FastDDS SuperClient profile file.
                Will default to LaunchConfiguration("fastdds_profile_super_client")
        """
        self.profile_path = (
            fastdds_superclient_profile_path
            if fastdds_superclient_profile_path is not None
            else LaunchConfiguration("fastdds_profile_super_client")
        )
        self.logger = launch.logging.get_logger('launch.user.superclient_environment')

    def perform(self, context):
        """Return the profile path or empty string if EASY_MODE is set."""
        if os.getenv("ROS2_EASY_MODE"):
            self.logger.info("ROS2_EASY_MODE is set, skipping FastDDS SuperClient profile configuration.")
            return ""

        if isinstance(self.profile_path, Substitution):
            return self.profile_path.perform(context)
        return self.profile_path

    def describe(self):
        return f'SuperclientEnvironment(profile_path={self.profile_path})'


def superclient_environment(fastdds_superclient_profile_path: str | None = None) -> dict:
    """Returns environment dict for SuperClient nodes.

    Args:
        fastdds_superclient_profile_path: Optional custom path to profile file

    Returns:
        Dictionary with environment variables for superclient configuration

    Example:
        Node(
            package='my_pkg',
            executable='my_node',
            environment=superclient_environment()
        )
    """
    env_var = (
        "FASTDDS_DEFAULT_PROFILES_FILE"
        if os.environ.get("ROS_DISTRO") == "kilted"
        else "FASTRTPS_DEFAULT_PROFILES_FILE"
    )

    return {
        env_var: SuperclientEnvironment(fastdds_superclient_profile_path)
    }
