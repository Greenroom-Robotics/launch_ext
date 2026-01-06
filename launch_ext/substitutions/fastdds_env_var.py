import os
from launch.substitution import Substitution


class FastDDSEnvVar(Substitution):
    """Substitution that returns the appropriate FastDDS environment variable name.

    Returns "FASTDDS_DEFAULT_PROFILES_FILE" for ROS Kilted,
    "FASTRTPS_DEFAULT_PROFILES_FILE" for other distributions.
    """

    def perform(self, context):
        """Return the appropriate env var name based on ROS_DISTRO."""
        return (
            "FASTDDS_DEFAULT_PROFILES_FILE"
            if os.environ.get("ROS_DISTRO") == "kilted"
            else "FASTRTPS_DEFAULT_PROFILES_FILE"
        )

    def describe(self):
        return "FastDDSEnvVar()"


def get_fastdds_default_profile_env_var() -> str:
    """Get the appropriate FastDDS environment variable name.

    Returns:
        str: "FASTDDS_DEFAULT_PROFILES_FILE" for ROS Kilted,
             "FASTRTPS_DEFAULT_PROFILES_FILE" for other distributions.

    Example:
        env_var = get_fastdds_default_profile_env_var()
        os.environ[env_var] = "/path/to/profile.xml"
    """
    return (
        "FASTDDS_DEFAULT_PROFILES_FILE"
        if os.environ.get("ROS_DISTRO") == "kilted"
        else "FASTRTPS_DEFAULT_PROFILES_FILE"
    )
