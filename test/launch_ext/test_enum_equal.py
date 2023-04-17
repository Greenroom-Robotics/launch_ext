
from enum import Enum

from launch import LaunchContext
from launch.actions import SetLaunchConfiguration
from launch.substitutions import LaunchConfiguration

from launch_ext.conditions import EnumEqual

def test_enum_equal():

    class Mode(str, Enum):
        SIMULATOR = "simulator"
        HARDWARE = "hardware"
        STUBS = "stubs"

    lc = LaunchContext()
    SetLaunchConfiguration('mode', "simulator").visit(lc)

    cond = EnumEqual(LaunchConfiguration('mode'), Mode.SIMULATOR)
    assert cond.evaluate(lc) == True

    cond = EnumEqual(LaunchConfiguration('mode'), Mode.HARDWARE)
    assert cond.evaluate(lc) == False

    assert EnumEqual.enum_to_choices(Mode) == ['simulator', 'hardware', 'stubs']
