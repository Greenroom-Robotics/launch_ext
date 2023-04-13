
from launch import LaunchContext
from launch_ext.substitutions import Templated
from launch.actions import SetLaunchConfiguration
from launch.substitutions import LaunchConfiguration

def test_file_contents():
    lc = LaunchContext()

    SetLaunchConfiguration('test_sub', "world").visit(lc)

    sub = Templated("""hello $test_sub""")
    assert sub.perform(lc) == 'hello world'

    sub = Templated("""hello ${test_sub}s""")
    assert sub.perform(lc) == 'hello worlds'

    SetLaunchConfiguration('test_temp', "this is a template in a sub hello $test_sub").visit(lc)
    assert Templated(LaunchConfiguration("test_temp")).perform(lc) == "this is a template in a sub hello world"
