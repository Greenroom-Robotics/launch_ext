import os
import pathlib

from launch.actions import (
    ExecuteProcess,
    SetLaunchConfiguration,
    SetEnvironmentVariable,
)
from launch.substitutions import (
    PathJoinSubstitution,
    LaunchConfiguration,
)
from launch_ros.substitutions import FindPackageShare
from launch_ext.actions import WriteFile
from launch_ext.substitutions import (
    Xacro,
    ResolveHost,
    get_fastdds_default_profile_env_var,
)
from launch.action import Action
from launch.launch_context import LaunchContext
from launch.substitution import Substitution


class ResolveAndJoinInterfaces(Substitution):
    """Resolve each interface host and join with spaces."""

    def __init__(self, interfaces: list[str]):
        self.__interfaces = interfaces

    def perform(self, context):
        resolved = [ResolveHost(iface).perform(context) for iface in self.__interfaces]
        return " ".join(resolved)

    def describe(self):
        return f"ResolveAndJoinInterfaces({self.__interfaces})"


class ConfigureFastDDS(Action):
    """
    Configure Fast DDS middleware for ROS 2 nodes with support for different discovery protocols.

    This class sets up the Fast DDS configuration profile and optionally starts a Discovery Server
    process based on the provided parameters. It creates configuration XML files using Xacro
    templates and sets the appropriate environment variables to use these configurations.

    The class supports three discovery protocols:
    - SIMPLE: Direct peer-to-peer discovery (standard DDS discovery)
    - CLIENT: Discovery Server client mode (clients connect to a discovery server)
    - SUPER_CLIENT: Discovery Server super client mode (acts as both client and can distribute discovery info)
    """

    def __init__(
        self,
        with_discovery_server: bool = False,
        discovery_server_address: str = "0.0.0.0",
        discovery_server_ip: str = "0.0.0.0",
        allowed_interfaces: list[str] | None = None,
        simple_discovery: bool = True,
        fastdds_profile_path=None,
        fastdds_profile_super_client_path=None,
        **kwargs,
    ):
        """
        Initialize the ConfigureFastdds action.

        Args:
            with_discovery_server (bool): Whether to start a discovery server process
            discovery_server_address (str): Address for the discovery server to listen on
            discovery_server_ip (str): IP address where the discovery server can be reached by clients
            allowed_interfaces (list[str]): List of IP/host/interface addresses to allow. Empty means all.
            simple_discovery (bool): If True, use SIMPLE discovery protocol; otherwise use CLIENT/SUPER_CLIENT
            fastdds_profile_path (str, optional): Path where to write the main Fast DDS profile.
                Defaults to "~/fastdds_profile.xml"
            fastdds_profile_super_client_path (str, optional): Path where to write the super client profile.
                Defaults to "~/fastdds_profile_super_client.xml"
            **kwargs: Additional arguments passed to the parent Action class
        """
        super().__init__(**kwargs)
        if allowed_interfaces is None:
            allowed_interfaces = []
        resolved_interfaces = ResolveAndJoinInterfaces(allowed_interfaces)
        fastdds_profile_path = LaunchConfiguration(
            "fastdds_profile_path",
            default=fastdds_profile_path
            or f"{pathlib.Path.home()}/fastdds_profile.xml",
        )
        fastdds_profile_super_client_path = LaunchConfiguration(
            "fastdds_profile_super_client_path",
            default=fastdds_profile_super_client_path
            or f"{pathlib.Path.home()}/fastdds_profile_super_client.xml",
        )

        # Create the discovery server profile (SERVER mode with transport restrictions)
        fastdds_server_profile_path = LaunchConfiguration(
            "fastdds_server_profile_path",
            default=f"{pathlib.Path.home()}/fastdds_profile_server.xml",
        )
        write_fastdds_server_profile = WriteFile(
            Xacro(
                file_path=PathJoinSubstitution(
                    [
                        FindPackageShare("launch_ext"),
                        "config",
                        "fastdds_profile.xml.xacro",
                    ]
                ),
                mappings={
                    "discovery_server_ip": ResolveHost(discovery_server_ip),
                    "launch_log_dir": LaunchConfiguration("launch_log_dir"),
                    "allowed_interfaces": resolved_interfaces,
                    "discovery_protocol": "SERVER",
                    "ros_distro": os.environ.get("ROS_DISTRO", "jazzy"),
                },
            ),
            LaunchConfiguration("fastdds_server_profile"),
        )

        discovery_server = ExecuteProcess(
            name="discovery_server",
            cmd=[
                "fastdds",
                "discovery",
                "-x",
                LaunchConfiguration("fastdds_server_profile"),
            ],
            output={"stderr": ["screen", "log"], "both": ["own_log"]},
        )

        # Create the standard Fast DDS profile (CLIENT or SIMPLE mode)
        write_fastdds_profile = WriteFile(
            Xacro(
                file_path=PathJoinSubstitution(
                    [
                        FindPackageShare("launch_ext"),
                        "config",
                        "fastdds_profile.xml.xacro",
                    ]
                ),
                mappings={
                    "discovery_server_ip": ResolveHost(discovery_server_ip),
                    "launch_log_dir": LaunchConfiguration("launch_log_dir"),
                    "allowed_interfaces": resolved_interfaces,
                    "discovery_protocol": "SIMPLE" if simple_discovery else "CLIENT",
                    "ros_distro": os.environ.get("ROS_DISTRO", "jazzy"),
                },
            ),
            LaunchConfiguration("fastdds_profile"),
        )

        # Create the super client Fast DDS profile (SUPER_CLIENT mode)
        write_fastdds_profile_super_client = WriteFile(
            Xacro(
                file_path=PathJoinSubstitution(
                    [
                        FindPackageShare("launch_ext"),
                        "config",
                        "fastdds_profile.xml.xacro",
                    ]
                ),
                mappings={
                    "discovery_server_ip": ResolveHost(discovery_server_ip),
                    "launch_log_dir": LaunchConfiguration("launch_log_dir"),
                    "allowed_interfaces": resolved_interfaces,
                    "discovery_protocol": "SIMPLE"
                    if simple_discovery
                    else "SUPER_CLIENT",
                    "ros_distro": os.environ.get("ROS_DISTRO", "jazzy"),
                },
            ),
            LaunchConfiguration("fastdds_profile_super_client"),
        )

        # Collect all actions to be executed when this Action is executed
        self.actions = [
            # Set launch configurations for profile paths
            SetLaunchConfiguration("fastdds_profile", fastdds_profile_path),
            SetLaunchConfiguration(
                "fastdds_profile_super_client", fastdds_profile_super_client_path
            ),
            SetLaunchConfiguration(
                "fastdds_server_profile", fastdds_server_profile_path
            ),
            # Write the configuration files from templates
            write_fastdds_profile,
            write_fastdds_profile_super_client,
            write_fastdds_server_profile,
            # Configure environment to use the main profile
            SetEnvironmentVariable(
                get_fastdds_default_profile_env_var(),
                LaunchConfiguration("fastdds_profile"),
            ),
        ]

        if with_discovery_server:
            self.actions.append(discovery_server)

    def execute(self, context: LaunchContext) -> None:
        """
        Execute all configured actions in sequence.

        This method is called by the launch system when the action is executed.
        It iterates through all the actions created during initialization and
        executes them in order.

        Args:
            context (LaunchContext): The launch context

        Returns:
            None
        """
        for action in self.actions:
            action.execute(context)

        return None
