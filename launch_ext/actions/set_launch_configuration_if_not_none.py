import launch
from launch.actions import SetLaunchConfiguration
from launch.some_substitutions_type import SomeSubstitutionsType


def SetLaunchConfigurationIfNotNone(name: str, value: SomeSubstitutionsType | None):
    """
    Set a launch configuration if the value is not None.
    """
    return (
        SetLaunchConfiguration(name, value)
        if value is not None
        else launch.LaunchDescriptionEntity()
    )
