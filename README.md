## AVA Side — Installation

**Prerequisite:** ROS 2 Humble installed and sourced.

```bash
# 1. Clone the AVA workspace
git clone --branch main https://github.com/helenlu66/ava_nav_ros2_ws.git
cd ava_nav_ros2_ws

# 2. Pull all submodules
git submodule update --init --recursive
```

---

## AVA Side — Build & Launch

```bash
# Source in every new terminal
source /opt/ros/humble/setup.bash
source ~/ava_nav_ros2_ws/install/setup.bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export ROS_DOMAIN_ID=42
```

**Build**

```bash
cd ~/ava_nav_ros2_ws
colcon build --symlink-install
source install/setup.bash
```

**Terminal 1 — Start the AVA robot**

```bash
ros2 launch ava_bringup ava_bringup.launch.py
```

**Terminal 2 — Nav2 with the HRI main lab map**

```bash
ros2 launch nav2_bringup bringup_launch.py \
  map:=/path/to/hri_main_lab_map_3.yaml \
  use_sim_time:=false
```

**Terminal 3 — Nav2 demo delivery node**

```bash
ros2 launch nav2_demo nav2_demo.launch.py
```

---

Note that ![ava ros2 setup](src/ros_experiment_v2) is a private repo developed by the AVA team for the HRI lab. 

## Building the map
Refer to ![AVA README](AvaGen2-ROS2-Documentation/README.md) for how to build the map