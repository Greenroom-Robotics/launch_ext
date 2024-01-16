import time
from typing import Callable
from threading import Thread

import rclpy
from rclpy.node import Node
import osrf_pycommon.process_utils
from launch import LaunchService, LaunchDescription
from example_interfaces.srv import Trigger
from example_interfaces.srv._trigger import Trigger_Request, Trigger_Response

class SharedState:
    def __init__(self):
        self.launch_service = LaunchService()
        
class TriggerNode(Node):
    def __init__(
        self, 
        namespace: str, 
        node_name: str, 
        trigger_name: str, 
        shared_state: SharedState,
        sleep_time: float = 2.0
    ):
        super().__init__(node_name, namespace=namespace)
        self.shared_state = shared_state
        self.sleep_time = sleep_time
        self.srv = self.create_service(Trigger, 'restart', self.trigger_callback)
        self.get_logger().info(f"Enabling restart service - {namespace}/{trigger_name}")

    def trigger_callback(self, request: Trigger_Request, response: Trigger_Response):
        if self.shared_state.launch_service is not None:
            self.shared_state.launch_service.shutdown()
            
        time.sleep(self.sleep_time)
        response.success = True
        return response


def launch_with_restart_trigger(
    namespace: str,
    node_name: str,
    generate_launch_description: Callable[[], LaunchDescription],
    trigger_name="restart",
    sleep_time: float = 2.0
):
    """
    Launches a ROS description with a trigger service that can be used to restart the launch.
    
    
    ```python
    from launch_ext import launch_with_restart_trigger
    from gama_config.gama_vessel import read_vessel_config, Mode
    from .some_launch_description import generate_launch_description

    launch_with_restart_trigger(
        namespace=config.namespace_vessel,
        node_name="gama_bringup",
        trigger_name="restart",
        generate_launch_description=generate_launch_description
    )
    
    # This will make a `example_interfaces/srv/Trigger` service available at "/gama_bringup/restart"
    ```
    """
    rclpy.init()
    
    def run_ros(shared_state: SharedState):
        node = TriggerNode(
            namespace=namespace, 
            node_name=node_name, 
            trigger_name=trigger_name, 
            shared_state=shared_state,
            sleep_time=sleep_time
        )
        rclpy.spin(node)

    def run_launch(shared_state: SharedState):
        shared_state.launch_service = LaunchService()
        shared_state.launch_service.include_launch_description(generate_launch_description())
        shared_state.launch_service.run()
        
    shared_state = SharedState()
    run_ros_thread = Thread(target=run_ros, args=(shared_state,))
    run_ros_thread.start()
    run_launch(shared_state)
