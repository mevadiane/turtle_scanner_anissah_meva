import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from geometry_msgs.msg import Twist
from std_msgs.msg import Bool
import math


class TurtleScanner(Node):
    def __init__(self):
        super().__init__('turtle_scanner')
        self.pose_scanner = None
        self.pose_target = None

        # Partie 2
        self.scan_sub = self.create_subscription(Pose, "/turtle1/pose", self.scan, 10)
        self.target_sub = self.create_subscription(Pose, "/turtle_target/pose", self.target, 10)

        # Partie 3
        self.get_logger().info('Node démarré — en attente des poses...')
        self.nb_lignes = 5
        self.y_start = 1.0
        self.y_step = 2.0
        self.x_min = 1.0
        self.x_max = 10.0
        self.linear_speed= 2.0
        self.angular_speed = 1.5
        self.waypoint_tolerance = 0.3
        self.Kp_ang = 8.0
        self.Kp_lin = 1.0

        self.current_waypoint = 0
        self.scan_done = False

        self.waypoints = self.generate_waypoints()
        self.get_logger().info(f'Waypoints générés : {self.waypoints}')
        self.cmd_pub= self.create_publisher(Twist, "/turtle1/cmd_vel", 10)
        self.timer = self.create_timer(1/20, self.scan_step)

        # Partie 4
        self.detection_radius = 1.5
        self.detected = False
        self.detected_pub = self.create_publisher(Bool, "/target_detected", 10)


    # Partie 2
    def scan(self, msg):
        self.pose_scanner = msg
        self.get_logger().info(
            f'Scanner — x={msg.x:.2f}, y={msg.y:.2f}, theta={msg.theta:.2f}'
        )

    def target(self, msg):
        self.pose_target = msg
        self.get_logger().info(
            f'Target  — x={msg.x:.2f}, y={msg.y:.2f}, theta={msg.theta:.2f}'
        )

    # Partie 3
    def generate_waypoints(self):
        waypoints = []
        for i in range(self.nb_lignes):
            y = self.y_start + i * self.y_step
            if i % 2 == 0:
                x = self.x_max
            else:
                x = self.x_min
            waypoints.append((x, y))
        return waypoints
    
    def compute_angle(self, A, B):
        return math.atan2(B[1] - A[1], B[0] - A[0])

    def compute_distance(self, A, B):
        return math.sqrt((B[0] - A[0])**2 + (B[1] - A[1])**2)

    def scan_step(self):
        if self.pose_scanner is None:
            return
        if self.scan_done:
            return

        

        # Partie 4
        if self.pose_target is not None and not self.detected:
            dist_target = self.compute_distance(
                (self.pose_scanner.x, self.pose_scanner.y),
                (self.pose_target.x, self.pose_target.y)
            )

            if dist_target < self.detection_radius:
                self.detected = True
                self.scan_done = True
                self.stop()

                msg = Bool()
                msg.data = True
                self.detected_pub.publish(msg)

                self.get_logger().info(
                    f'Cible détectée à ({self.pose_target.x:.2f}, {self.pose_target.y:.2f}) !'
                )
                return

        msg = Bool()
        msg.data = False
        self.detected_pub.publish(msg)

        if self.current_waypoint >= len(self.waypoints):
            self.stop()
            self.get_logger().info('Balayage terminé !')
            self.scan_done = True
            return

        A = (self.pose_scanner.x, self.pose_scanner.y)

        B = self.waypoints[self.current_waypoint]

        distance = self.compute_distance(A, B)

        if distance < self.waypoint_tolerance:
            self.get_logger().info(f'Waypoint {self.current_waypoint} atteint → suivant')
            self.current_waypoint += 1
            return

        theta_desired = self.compute_angle(A, B)
        error_angle = math.atan(math.tan((theta_desired - self.pose_scanner.theta) / 2))

        angular_vel = self.Kp_ang * error_angle
        linear_vel  = self.Kp_lin * distance

        linear_vel  = min(linear_vel,  self.linear_speed)
        angular_vel = max(min(angular_vel, self.angular_speed), -self.angular_speed)


        cmd = Twist()
        cmd.linear.x  = linear_vel
        cmd.angular.z = angular_vel
        self.cmd_pub.publish(cmd)

    def stop(self):
        cmd = Twist()
        cmd.linear.x  = 0.0
        cmd.angular.z = 0.0
        self.cmd_pub.publish(cmd)
        
def main(args=None):
	rclpy.init(args=args)
	node = TurtleScanner()
	rclpy.spin(node)
	rclpy.shutdown()

if __name__=="__main__":
	main()