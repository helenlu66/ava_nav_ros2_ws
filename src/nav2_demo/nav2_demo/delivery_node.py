import math
import threading
from pathlib import Path

import rclpy
from ament_index_python.packages import get_package_share_directory
from action_msgs.msg import GoalStatus
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from interfaces.action import Delivery
from rclpy.action import ActionClient, ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
import yaml


def yaw_to_quaternion(yaw: float):
    half_yaw = yaw * 0.5
    return 0.0, 0.0, math.sin(half_yaw), math.cos(half_yaw)


class DeliveryNode(Node):
    def __init__(self):
        super().__init__('delivery_node')
        self.declare_parameter('loading_pose_file', 'loading_pose.yaml')
        self.declare_parameter('unloading_pose_file', 'unloading_pose.yaml')
        self.declare_parameter('frame_id', 'map')
        self.declare_parameter('delivery_action_name', 'deliver')
        self.declare_parameter('nav2_action_name', 'navigate_to_pose')
        self.declare_parameter('dry_run', False)

        self._callback_group = ReentrantCallbackGroup()

        loading_file = self.get_parameter('loading_pose_file').value
        unloading_file = self.get_parameter('unloading_pose_file').value
        self._dry_run = bool(self.get_parameter('dry_run').value)
        self._loading_pose = self._load_single_pose(loading_file)
        self._unloading_pose = self._load_single_pose(unloading_file)
        self._action_client = ActionClient(
            self,
            NavigateToPose,
            self.get_parameter('nav2_action_name').value,
            callback_group=self._callback_group,
        )
        self._delivery_action_server = ActionServer(
            self,
            Delivery,
            self.get_parameter('delivery_action_name').value,
            execute_callback=self._execute_callback,
            goal_callback=self._goal_callback,
            cancel_callback=self._cancel_callback,
            callback_group=self._callback_group,
        )

        self.get_logger().info(
            f"DeliveryNode ready, serving '{self.get_parameter('delivery_action_name').value}' "
            f"and forwarding to Nav2 action '{self.get_parameter('nav2_action_name').value}'."
        )
        self.get_logger().info(f"Dry-run mode: {self._dry_run}")
        self.get_logger().info(f"Loaded loading pose: {self._pose_to_log_string(self._loading_pose)}")
        self.get_logger().info(f"Loaded unloading pose: {self._pose_to_log_string(self._unloading_pose)}")

    def _load_single_pose(self, pose_file: str):
        path = Path(pose_file)
        if not path.is_absolute():
            path = Path(get_package_share_directory('nav2_demo')) / 'config' / pose_file

        with path.open('r', encoding='utf-8') as handle:
            data = yaml.safe_load(handle)
        return data

    def _pose_to_log_string(self, pose_data: dict) -> str:
        frame = pose_data.get('frame_id', self.get_parameter('frame_id').value)
        position = pose_data.get('position', {})
        orientation = pose_data.get('orientation', {})
        if 'yaw' in orientation:
            orientation_text = f"yaw={orientation['yaw']}"
        else:
            orientation_text = (
                f"x={orientation.get('x', 0.0)}, y={orientation.get('y', 0.0)}, "
                f"z={orientation.get('z', 0.0)}, w={orientation.get('w', 1.0)}"
            )
        return (
            f"frame={frame}, "
            f"x={position.get('x', 0.0)}, y={position.get('y', 0.0)}, z={position.get('z', 0.0)}, "
            f"orientation({orientation_text})"
        )

    def make_pose_stamped(self, pose_data: dict) -> PoseStamped:
        pose = PoseStamped()
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

    def _goal_callback(self, goal_request):
        target = goal_request.target.strip().lower()
        if target in ('loading', 'unloading'):
            return GoalResponse.ACCEPT
        self.get_logger().error("Rejecting unknown delivery target '%s'. Use 'loading' or 'unloading'." % target)
        return GoalResponse.REJECT

    def _cancel_callback(self, goal_handle):
        self.get_logger().info(f"Cancel request received for '{goal_handle.request.target}'.")
        return CancelResponse.ACCEPT

    def _publish_feedback(self, goal_handle, state: str):
        feedback = Delivery.Feedback()
        feedback.state = state
        goal_handle.publish_feedback(feedback)

    def _execute_callback(self, goal_handle):
        target = goal_handle.request.target.strip().lower()
        result = Delivery.Result()

        if target == 'loading':
            pose_data = self._loading_pose
        elif target == 'unloading':
            pose_data = self._unloading_pose
        else:
            result.success = False
            result.message = f"Unknown target '{target}'"
            goal_handle.abort()
            return result

        self.get_logger().info(f"Selected '{target}' pose: {self._pose_to_log_string(pose_data)}")

        if self._dry_run:
            self._publish_feedback(goal_handle, f"[dry-run] Loaded '{target}' pose and skipped Nav2 goal send")
            result.success = True
            result.message = f"[dry-run] '{target}' pose loaded and logged"
            goal_handle.succeed()
            return result

        if not self._action_client.wait_for_server(timeout_sec=10.0):
            self.get_logger().error('NavigateToPose action server is not available.')
            result.success = False
            result.message = 'NavigateToPose action server is not available.'
            goal_handle.abort()
            return result

        nav2_goal = NavigateToPose.Goal()
        nav2_goal.pose = self.make_pose_stamped(pose_data)

        done_event = threading.Event()
        outcome = {'success': False, 'message': 'Unknown error'}

        self._publish_feedback(goal_handle, f"Sending '{target}' goal to Nav2")
        send_future = self._action_client.send_goal_async(nav2_goal)

        def on_goal_response(future):
            nav2_goal_handle = future.result()
            if not nav2_goal_handle.accepted:
                outcome['success'] = False
                outcome['message'] = f"Nav2 rejected '{target}' goal"
                done_event.set()
                return

            self._publish_feedback(goal_handle, f"'{target}' goal accepted by Nav2")
            result_future = nav2_goal_handle.get_result_async()
            result_future.add_done_callback(on_nav2_result)

        def on_nav2_result(future):
            nav2_result = future.result()
            if nav2_result.status == GoalStatus.STATUS_SUCCEEDED:
                outcome['success'] = True
                outcome['message'] = f"Reached '{target}' successfully"
            else:
                outcome['success'] = False
                outcome['message'] = f"Nav2 finished '{target}' with status {nav2_result.status}"
            done_event.set()

        send_future.add_done_callback(on_goal_response)

        while rclpy.ok() and not done_event.wait(timeout=0.1):
            if goal_handle.is_cancel_requested:
                outcome['success'] = False
                outcome['message'] = f"'{target}' delivery canceled"
                goal_handle.canceled()
                result.success = outcome['success']
                result.message = outcome['message']
                return result

        result.success = outcome['success']
        result.message = outcome['message']
        if result.success:
            goal_handle.succeed()
        else:
            goal_handle.abort()
        return result


def main(args=None):
    rclpy.init(args=args)
    node = DeliveryNode()
    try:
        executor = MultiThreadedExecutor(num_threads=2)
        executor.add_node(node)
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
