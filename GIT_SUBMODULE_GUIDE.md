# Using nav2_demo_interfaces as a Git Submodule

This document shows how to use `nav2_demo_interfaces` as a shared git submodule in a second repo.

## Setup on Second Robot/Repo

Assuming your second repo is at `/path/to/second_repo`:

### 1. Add nav2_demo_interfaces as a submodule

```bash
cd /path/to/second_repo
git submodule add <url-to-nav2_demo_interfaces-repo> src/nav2_demo_interfaces
git commit -m "Add nav2_demo_interfaces as submodule"
```

Replace `<url-to-nav2_demo_interfaces-repo>` with:
- **Local path** (for testing): `file:///home/hrilab/ros2_ws/src/nav2_demo_interfaces`
- **GitHub/GitLab URL** (for production): `https://github.com/your-org/nav2_demo_interfaces.git`

### 2. Clone the second repo with submodule

When cloning a repo that has submodules:

```bash
git clone --recurse-submodules <url-to-second-repo>
# OR if you already cloned without submodules:
git submodule update --init --recursive
```

### 3. Build both packages

```bash
cd /path/to/second_repo
colcon build --packages-select nav2_demo_interfaces delivery_client_example
```

## Keeping Submodules in Sync

### Update to latest version in submodule

```bash
cd /path/to/second_repo/src/nav2_demo_interfaces
git pull origin main  # or master, depending on your branch
cd ../..
git add src/nav2_demo_interfaces
git commit -m "Update nav2_demo_interfaces submodule"
```

### Or from parent repo

```bash
cd /path/to/second_repo
git submodule update --remote src/nav2_demo_interfaces
git add src/nav2_demo_interfaces
git commit -m "Update nav2_demo_interfaces submodule"
```

## Current Status

`nav2_demo_interfaces` is now a standalone git repository at:
- **Local path**: `/home/hrilab/ros2_ws/src/nav2_demo_interfaces`
- **Git repo location**: `/home/hrilab/ros2_ws/src/nav2_demo_interfaces/.git/`

To push this to GitHub/GitLab for sharing:

```bash
cd /home/hrilab/ros2_ws/src/nav2_demo_interfaces
git remote add origin https://github.com/your-org/nav2_demo_interfaces.git
git push -u origin master
```

Then use that URL in step 1 above for the second repo.
