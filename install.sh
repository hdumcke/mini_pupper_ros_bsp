#!/bin/bash

# check Ubuntu version
source /etc/os-release

if [[ $UBUNTU_CODENAME != 'jammy' ]]
then
    echo "Ubuntu 22.04.1 LTS (Jammy Jellyfish) is required"
    echo "You are using $VERSION"
    exit 1
fi

### Get directory where this script is installed
BASEDIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

### Install ROS2
cd ~
git clone https://github.com/Tiryoh/ros2_setup_scripts_ubuntu.git
./ros2_setup_scripts_ubuntu/run.sh

source /opt/ros/humble/setup.bash
mkdir -p ~/mini_pupper_ws/src
cd ~/mini_pupper_ws/src
git clone https://github.com/mangdangroboticsclub/mini_pupper_ros_bsp

cd ~/mini_pupper_ws
rosdep update && rosdep install --from-path src --ignore-src -y --skip-keys microxrcedds_agent --skip-keys micro_ros_agent
sudo pip install setuptools==58.2.0 # suppress colcon build warning
colcon build --executor sequential --symlink-install

# Install mini_pupper_driver
cd ~/mini_pupper_ros_bsp/services
sudo ln -s $(realpath .)/mini_pupper_driver.service /etc/systemd/system/

# Install Joystick
cd ~/mini_pupper_ros_bsp/services
sudo ln -s $(realpath .)/joystick.service /etc/systemd/system/
sudo ln -s $(realpath .)/restart_joy.service /etc/systemd/system/

# Install Lidar
source /opt/ros/humble/setup.bash
mkdir -p ~/lidar_ws/src
cd ~/lidar_ws
git clone https://github.com/ldrobotSensorTeam/ldlidar_stl_ros2.git src/ldlidar
colcon build
cd ~/mini_pupper_ros_bsp/services
sudo ln -s $(realpath .)/lidar.service /etc/systemd/system/

# Install IMU
if [[ "$1" == "v2" ]]
then
cd ~/mini_pupper_ros_bsp/services
sudo ln -s $(realpath .)/imu.service /etc/systemd/system/
sudo apt install -y ros-humble-imu-tools
fi

# Install Camera
sudo adduser ubuntu input
sudo pip install ds4drv
~/mini_pupper_bsp/RPiCamera/install.sh
cd ~/mini_pupper_ros_bsp/services
sudo ln -s $(realpath .)/v4l2_camera.service /etc/systemd/system/
sudo apt install -y ros-humble-v4l2-camera ros-humble-image-transport-plugins
mkdir -p ~/.ros/camera_info/
# copy defaultcamera calibration file. This should be replaced by a camera spefici calibration file
cp $BASEDIR/ros2/mmal_service_16.1.yaml ~/.ros/camera_info/


# Cyclon DDS
sudo apt install -y ros-humble-rmw-cyclonedds-cpp
echo 'export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp' >> ~/.bashrc

# enable services
sudo systemctl daemon-reload
sudo systemctl enable mini_pupper_driver
sudo systemctl enable joystick
sudo systemctl enable restart_joy
sudo systemctl enable lidar
sudo systemctl enable imu
sudo systemctl enable v4l2_camera