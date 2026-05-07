from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    loading_pose_file = LaunchConfiguration('loading_pose_file')
    unloading_pose_file = LaunchConfiguration('unloading_pose_file')
    frame_id = LaunchConfiguration('frame_id')
    action_name = LaunchConfiguration('action_name')
    command_topic = LaunchConfiguration('command_topic')

    return LaunchDescription([
        DeclareLaunchArgument('loading_pose_file', default_value='loading_pose.yaml'),
        DeclareLaunchArgument('unloading_pose_file', default_value='unloading_pose.yaml'),
        DeclareLaunchArgument('frame_id', default_value='map'),
        DeclareLaunchArgument('action_name', default_value='navigate_to_pose'),
        DeclareLaunchArgument('command_topic', default_value='delivery_command'),
        Node(
            package='nav2_demo',
            executable='delivery_router',
            output='screen',
            parameters=[{
                'loading_pose_file': loading_pose_file,
                'unloading_pose_file': unloading_pose_file,
                'frame_id': frame_id,
                'action_name': action_name,
                'command_topic': command_topic,
            }],
        ),
    ])