import os

from launch.actions import SetLaunchConfiguration

from launch_ext.actions import ConfigureFastDDS, ConfigureZenoh, ConfigureFastDDSEasyMode


def configure_middleware(config):
    if config.discovery.type == "zenoh":
        return [
            SetLaunchConfiguration("fastdds_profile_super_client", ""),
            ConfigureZenoh(
                with_router=config.discovery.with_discovery_server,
            ),
        ]
    if config.discovery.type == "fastdds":
        return [
            ConfigureFastDDS(
                discovery_server_address="0.0.0.0",
                with_discovery_server=config.discovery.with_discovery_server,
                discovery_server_ip=config.discovery.discovery_server_ip,
                own_ip=config.discovery.own_ip,
                simple_discovery=False,
            ),
        ]

    if config.discovery.type == "easy":
        if os.getenv("ROS_DISTRO") == "jazzy":
            raise RuntimeError(
                "Fast DDS Easy Mode is not supported on ROS Jazzy, please use a supported discovery mode or ROS version.\n"
                "HINT: To specify your distro when building or launching set the ROS_DISTRO environment variable "
                "or use the --ros-distro argument when building lookout"
            )

        return [
            ConfigureFastDDSEasyMode(
                easy_mode_base_address=config.discovery.base_address,
            ),
        ]

    return [
        ConfigureFastDDS(
            discovery_server_address="0.0.0.0",
            with_discovery_server=False,
            discovery_server_ip="0.0.0.0",
            own_ip="0.0.0.0",
            simple_discovery=True,
        ),
    ]
