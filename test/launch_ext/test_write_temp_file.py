from pathlib import Path

from launch import LaunchContext
from launch.substitutions import PathJoinSubstitution
from launch_ext.substitutions import WriteTempFile
from launch.actions import SetLaunchConfiguration


def test_file_contents():
    lc = LaunchContext()
    SetLaunchConfiguration("test_sub", "world").visit(lc)

    sub = WriteTempFile("asdf")
    assert Path(sub.perform(lc)).read_text() == "asdf"
