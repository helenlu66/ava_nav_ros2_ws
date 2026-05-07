import math
from pathlib import Path

import rclpy
from ament_index_python.packages import get_package_share_directory
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
from rclpy.node import Node
from std_msgs.msg import String
import yaml


def yaw_to_quaternion(yaw: float):
    half_yaw = yaw * 0.5
    return 0.0, 0.0, math.sin(half_yaw), math.cos(half_yaw)


class DeliveryRouter(Node):
    def __init__(self):
        super().__init__('delivery_router')
        self.declare_parameter('loading_pose_file', 'loading_pose.yaml')
        self.declare_parameter('unloading_pose_file', 'unloading_pose.yaml')
        self.declare_parameter('frame_id', 'map')
        self.declare_parameter('action_name', 'navigate_to_pose')
        self.declare_parameter('command_topic', 'delivery_command')

        loading_file = self.get_parameter('loading_pose_file').value
        unloading_file = self.get_parameter('unloading_pose_file').value
        self._loading_pose = self._load_single_pose(loading_file)
        self._unloading_pose = self._load_single_pose(unloading_file)
        self._action_client = ActionClient(self, NavigateToPose, self.get_parameter('action_name').value)

        topic = self.get_parameter('command_topic').value
        self.create_subscription(String, topic, self._command_cb, 10)
        self.get_logger().info(f"DeliveryRouter ready, listening on '{topic}' for 'loading' or 'unloading'.")

    def _load_single_pose(self, pose_file: str):
        path = Path(pose_file)
        if not path.is_absolute():
            path = Path(get_package_share_directory('nav2_demo')) / 'config' / pose_file

        with path.open('r', encoding='utf-8') as handle:
            data = yaml.safe_load(handle)
        return data

    def make_pose_stamped(self, pose_data: dict) -> PoseStamped:
        pose = PoseStamped()
        # use parameter frame_id unless pose overrides it
        frame = pose_data.get('frame_id', self.get_parameter('frame_id').value)
        pose.header.frame_id = frame
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.pose.position.x = float(pose_data['position']['x'])
        pose.pose.position.y = float(pose_data['position']['y'])
        pose.pose.position.z = float(pose_data['position'].get('z', 0.0))
        orientation = pose_data.get('orientation', {})
        if 'yaw' in orientation:
            qx, qy, qz, qw = yaw_to_quaternion(float(orientation['yaw']))
            pose.pose.orientation.x = qx
            pose.pose.orientation.y = qy
            pose.pose.orientation.z = qz
            pose.pose.orientation.w = qw
        else:
            pose.pose.orientation.x = float(orientation.get('x', 0.0))
            pose.pose.orientation.y = float(orientation.get('y', 0.0))
            pose.pose.orientation.z = float(orientation.get('z', 0.0))
            pose.pose.orientation.w = float(orientation.get('w', 1.0))
        return pose

    def _command_cb(self, msg: String):
        name = msg.data.strip()
        if not name:
            self.get_logger().warn('Received empty delivery command')
            return
        if name not in ('loading', 'unloading'):
            self.get_logger().error("Unknown pose name '%s'. Use 'loading' or 'unloading'" % name)
            return

        if not self._action_client.wait_for_server(timeout_sec=10.0):
            self.get_logger().error('NavigateToPose action server is not available.')
            return

        goal = NavigateToPose.Goal()
        if name == 'loading':
            pose_data = self._loading_pose
        else:
            pose_data = self._unloading_pose
        goal.pose = self.make_pose_stamped(pose_data)
        send_future = self._action_client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, send_future)
        goal_handle = send_future.result()
        if not goal_handle.accepted:
            self.get_logger().error(f"{name} goal was rejected.")
            return

        self.get_logger().info(f"{name} goal accepted, waiting for result...")
        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)
        result = result_future.result()
        status = result.status
        self.get_logger().info(f"{name} goal finished with status: {status}")


def main(args=None):
    rclpy.init(args=args)
    node = DeliveryRouter()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
