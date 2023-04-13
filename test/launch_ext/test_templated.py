
from launch import LaunchContext
from launch_ext.substitutions import Templated
from launch.actions import SetLaunchConfiguration

def test_file_contents():
    lc = LaunchContext()

    SetLaunchConfiguration('test_sub', "world").visit(lc)

    sub = Templated(template="""hello $test_sub""")
    assert sub.perform(lc) == 'hello world'


    sub = Templated(template="""hello ${test_sub}s""")
    assert sub.perform(lc) == 'hello worlds'
