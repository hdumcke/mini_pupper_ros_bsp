import os
import yaml
from ament_index_python.packages import get_package_share_directory
import rclpy
from rclpy.node import Node

from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

class ServoDemo(Node):

    def __init__(self):
        super().__init__('test_servos')
        # Parameters
        self.dt = 0.1 # dt (seconds) for trajectory interpolation
        self.interval = 1.0 # Time interval (seconds) between every trajectory point
        self.init_positions = [-0.06148125231266022, 0.8319007754325867, -1.552734613418579, 0.06214146316051483, 0.8321430683135986, -1.553170919418335, -0.062141433358192444, 0.8321430683135986, -1.553170919418335, 0.06214146316051483, 0.8321430683135986, -1.553170919418335]

        # ROS 2 related assets
        self.pub_trajectories = self.create_publisher(JointTrajectory, "/joint_group_effort_controller/joint_trajectory", 10)
        self.timer = self.create_timer(self.dt, self.timer_callback)
        # Initialize trajectory messages
        self.traj_msg = JointTrajectory()
        self.traj_msg.points.append(JointTrajectoryPoint())

        # Read servos positions from yaml file
        # The reason why I don't use ROS 2 Parameters is similar to this issue:
        # https://github.com/ros2/ros2/issues/1380
        yaml_file_path = os.path.join(get_package_share_directory('test_api'), 'config', 'servo_test.yaml')
        with open(yaml_file_path) as f:
            self.position_data = yaml.load(f, Loader=yaml.FullLoader)['positions']
        # self.get_logger().info("Read servo positions: "f"{self.position_data}") # Debug

        # Initialize and interpolate position list
        self.position_list = []
        self.position_list_index = 0

        position_num = len(self.position_data)
        if(position_num == 0):
            self.position_list = [self.init_positions]
            self.position_list_max = 0
        elif(position_num == 1):
            self.position_list = [self.position_data[0]]
            self.position_list_max = 0
        else:
            self.position_list_max = position_num * (1.0 / self.dt - 1)
            # Every point given by yaml
            for i in range(position_num - 1):
                servo_trajs = []
                # Every servo
                for j in range(12):
                    single_servo_traj = []
                    # Linear Interpolation, y = kx + b
                    start = self.position_data[i][j]
                    end = self.position_data[i+1][j]
                    b = start
                    k = (end - start) / self.interval
                    for t in range(int(1.0 / self.dt - 1)):
                        single_servo_traj.append(k * t * self.dt + b)
                    servo_trajs.append(single_servo_traj)
                # Every timestamp
                for j in range(int(1.0 / self.dt - 1)):
                    position_list = []
                    # Every servo
                    for t in range(12):
                        position_list.append(servo_trajs[t][j])
                    self.position_list.append(position_list)

            servo_trajs = []
            # Every servo
            for j in range(12):
                single_servo_traj = []
                # Linear Interpolation, y = kx + b
                start = self.position_data[-1][j]
                end = self.position_data[0][j]
                b = start
                k = (end - start) / self.interval
                for t in range(int(self.interval / self.dt - 1)):
                    single_servo_traj.append(k * t * self.dt + b)
                servo_trajs.append(single_servo_traj)
            # Every timestamp
            for j in range(int(self.interval / self.dt - 1)):
                position_list = []
                # Every servo
                for t in range(12):
                    position_list.append(servo_trajs[t][j])
                self.position_list.append(position_list)

    def timer_callback(self):
        self.traj_msg.points[0].positions = self.position_list[self.position_list_index]
        self.pub_trajectories.publish(self.traj_msg)

        # update index
        self.position_list_index += 1
        self.position_list_index = int(self.position_list_index % self.position_list_max)


def main(args=None):
    rclpy.init(args=args)

    demo = ServoDemo()

    rclpy.spin(demo)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    demo.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
