from launch.substitutions import (
    PathJoinSubstitution,
    FileContent,
)
from launch_ros.substitutions import FindPackageShare
from launch.action import Action
from launch.actions import OpaqueFunction
from launch.launch_context import LaunchContext
from launch_ros.actions import Node
import json
import launch.logging


def deep_merge(base: dict, override: dict) -> dict:
    """
    Recursively merge two dictionaries, with override values taking precedence.

    Args:
        base (dict): The base dictionary
        override (dict): The override dictionary whose values take precedence

    Returns:
        dict: A new dictionary with merged values
    """
    result = base.copy()

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # Recursively merge nested dictionaries
            result[key] = deep_merge(result[key], value)
        else:
            # For all other types (including lists), override completely replaces base
            result[key] = value

    return result


class ConfigureZenoh(Action):
    """
    Configure Zenoh middleware for ROS 2 nodes.
    
    This class sets up Zenoh middleware by creating configuration files for both
    the Zenoh router and Zenoh session. It can also optionally start a Zenoh router
    process based on the provided parameters.
    """

    def write_config_file(
        self, context: LaunchContext, file_name: str, overrides: dict, destination: str
    ) -> None:
        """
        Read a JSON config file, apply overrides, and write the result to a new location.
        
        This helper method reads a JSON configuration file from the package share directory,
        applies any overrides provided as a dictionary, and writes the resulting configuration
        to a new file in the /home/ros directory.
        
        Args:
            context (LaunchContext): The launch context
            file_name (str): Name of the configuration file to read and write
            overrides (dict, optional): Dictionary of settings to override in the config file.
                Defaults to {}.
                
        Returns:
            None
        """
        # Read the content of the template configuration file
        content = FileContent(
            PathJoinSubstitution([FindPackageShare("launch_ext"), "config", file_name])
        ).perform(context)

        # Parse the JSON content and apply overrides
        content_json = json.loads(content)
        content_json = deep_merge(content_json, overrides)

        # Write the modified configuration to the destination
        with open(destination, "w") as f:
            json.dump(content_json, f, indent=4)

        # Log the action
        launch.logging.get_logger("launch.user").info(f"Wrote file '{destination}'.")

        return None

    def __init__(
        self, 
        with_router: bool = False, 
        router_config: dict = {}, 
        session_config: dict = {}, 
        zenoh_router_config_path="/home/ros/zenoh_router_config.json", 
        zenoh_session_config_path="/home/ros/zenoh_session_config.json", 
        **kwargs
    ):
        """
        Initialize the ConfigureZenoh action.
        
        Args:
            with_router (bool): Whether to start a Zenoh router process
            router_config (dict): Configuration overrides for the Zenoh router
            session_config (dict): Configuration overrides for the Zenoh session
            zenoh_router_config_path (str, optional): Path where to write the Zenoh router config.
                Defaults to "/home/ros/zenoh_router_config.json"
            zenoh_session_config_path (str, optional): Path where to write the Zenoh session config.
                Defaults to "/home/ros/zenoh_session_config.json"
            **kwargs: Additional arguments passed to the parent Action class
        """
        super().__init__(**kwargs)

        # Define the Zenoh router node that will be conditionally launched
        zenoh_router = Node(
            name="zenoh_router",
            package="rmw_zenoh_cpp",
            executable="rmw_zenohd",
            output="both",
        )

        # Create the actions to write router and session configuration files
        write_zenoh_router_config = OpaqueFunction(
            function=self.write_config_file,
            kwargs={"file_name": "zenoh_router_config.json", "overrides": router_config, "destination": zenoh_router_config_path },
        )

        write_zenoh_session_config = OpaqueFunction(
            function=self.write_config_file,
            kwargs={"file_name": "zenoh_session_config.json", "overrides": session_config, "destination": zenoh_session_config_path },
        )

        # Collect the actions to be executed
        self.actions = [
            write_zenoh_router_config,
            write_zenoh_session_config,
        ]

        # Conditionally add the router node to the actions
        if with_router:
            self.actions.append(zenoh_router)

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