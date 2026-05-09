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

## Repository Structure

```
ros2_ws/
├── src/                                              # ROS 2 package source code
│   ├── ros2_asus_xtion/                            # ASUS Xtion drivers [submodule]
│   ├── ava_description/                            # AVA robot URDF descriptions
│   ├── interfaces/                                 # ROS 2 custom message/service definitions
│   ├── nav2_demo/                                  # Nav2 demonstration package
│   ├── spm/                                        # Spatial Mapping package
│   ├── ros_experiment_v2/                          # Private AVA team development [submodule]
│   └── ros2_experiment_v2/                         # Additional experiment package [submodule]
│
├── AvaGen2-ROS2-Documentation/                     # AVA Gen2 documentation [submodule]
├── hri_main_lab_map_*.yaml                         # Map configuration files for navigation
├── hri_main_lab_map_*.pgm                          # Map occupancy grid images
└── README.md                                        # This file
```

**Submodules:**
- [ros2_asus_xtion](https://github.com/mgonzs13/ros2_asus_xtion) — ASUS Xtion sensor drivers
- [ros_experiment_v2](https://github.com/helenlu66/ros_experiment_v2) — Private AVA team development
- [AvaGen2-ROS2-Documentation](https://github.com/ogoudey/AvaGen2-ROS2-Documention) — Robot documentation

**Key Notes:**
- Map files (`*.yaml` and `*.pgm`) are used with Nav2 for autonomous navigation
- Use `git submodule update --init --recursive` to pull all submodules

---

## Building the Map

Refer to [AvaGen2-ROS2-Documentation/README.md](AvaGen2-ROS2-Documentation/README.md) for instructions on building maps.

---

Note that [src/ros_experiment_v2](src/ros_experiment_v2)  is a private repo developed by the AVA team for the HRI lab.