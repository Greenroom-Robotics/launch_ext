from typing import Dict, Text
from launch.substitution import Substitution
from launch.launch_context import LaunchContext
from launch.some_substitutions_type import SomeSubstitutionsType
from launch.utilities import normalize_to_list_of_substitutions
from launch.utilities import perform_substitutions
import xacro


class Xacro(Substitution):
    """
    Substitution that processes a xacro file and returns the result as a string

    :param file_path: The path to the xacro file to process
    :param mappings: A dictionary of mappings to pass to xacro

    example:

      state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[
            {
                "robot_description": Xacro(
                    file_path=JoinLaunchSubstitutions(
                        [
                            FindPackageShare("my_robot_description"),
                            "urdf",
                            "my_robot.urdf.xacro",
                        ]
                    ),
                    mappings={
                        "thing_to_substitute": "substitution_value",
                        "another_thing_to_substitute": LaunchConfiguration("another_thing_to_substitute"),
                    },
                )
            }
        ],
    )
    """

    def __init__(
        self,
        file_path: SomeSubstitutionsType,
        mappings: Dict[str, SomeSubstitutionsType] = {},
        verbose: bool = False,
    ):
        """Create a TemplateSubstitution."""
        super().__init__()
        self.__file_path = normalize_to_list_of_substitutions(file_path)
        self.__mappings = {
            key: normalize_to_list_of_substitutions(value) for key, value in mappings.items()
        }
        self.__verbose = verbose

    def describe(self) -> str:
        """Return a description of this substitution as a string."""
        return f"Xacro: {self.__file_path}"

    def perform(self, context: LaunchContext) -> str:
        """Perform the substitution by returning the string with values substituted."""

        file_path = perform_substitutions(context, self.__file_path)
        mappings = {
            key: perform_substitutions(context, value) for key, value in self.__mappings.items()
        }

        if self.__verbose:
            print(f"xacro file_path: {file_path}")
            print(f"xacro mappings: {mappings}")
        document = xacro.process_file(file_path, mappings=mappings)
        document_string = document.toprettyxml(indent="  ")

        if self.__verbose:
            print(f"xacro result: {document_string}")
        return document_string
