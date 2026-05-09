from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    loading_pose_file = LaunchConfiguration('loading_pose_file')
    unloading_pose_file = LaunchConfiguration('unloading_pose_file')
    frame_id = LaunchConfiguration('frame_id')
    delivery_action_name = LaunchConfiguration('delivery_action_name')
    nav2_action_name = LaunchConfiguration('nav2_action_name')
    dry_run = LaunchConfiguration('dry_run')
    fastdds_profiles_file = LaunchConfiguration('fastdds_profiles_file')

    return LaunchDescription([
        DeclareLaunchArgument('loading_pose_file', default_value='loading_pose.yaml'),
        DeclareLaunchArgument('unloading_pose_file', default_value='unloading_pose.yaml'),
        DeclareLaunchArgument('frame_id', default_value='map'),
        DeclareLaunchArgument('delivery_action_name', default_value='deliver'),
        DeclareLaunchArgument('nav2_action_name', default_value='navigate_to_pose'),
        DeclareLaunchArgument('dry_run', default_value='false'),
        DeclareLaunchArgument(
            'fastdds_profiles_file',
            default_value=PathJoinSubstitution([
                FindPackageShare('nav2_demo'),
                'config',
                'delivery_fastdds_peers.xml',
            ]),
        ),
        SetEnvironmentVariable('FASTDDS_DEFAULT_PROFILES_FILE', fastdds_profiles_file),
        SetEnvironmentVariable('FASTRTPS_DEFAULT_PROFILES_FILE', fastdds_profiles_file),
        SetEnvironmentVariable(
            'CYCLONEDDS_URI',
            '<CycloneDDS><Domain>'
            '<General><Interfaces><NetworkInterface name="wlp4s0"/></Interfaces></General>'
            '<Discovery><Peers><Peer address="192.168.0.220"/></Peers></Discovery>'
            '</Domain></CycloneDDS>',
        ),
        SetEnvironmentVariable('RMW_IMPLEMENTATION', 'rmw_cyclonedds_cpp'),
        SetEnvironmentVariable('ROS_DOMAIN_ID', '42'),
        Node(
            package='nav2_demo',
            executable='delivery_node',
            output='screen',
            parameters=[{
                'loading_pose_file': loading_pose_file,
                'unloading_pose_file': unloading_pose_file,
                'frame_id': frame_id,
                'delivery_action_name': delivery_action_name,
                'nav2_action_name': nav2_action_name,
                'dry_run': dry_run,
            }],
        ),
    ])
