import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose

class TurtleScanner(Node):
    def __init__(self):
        super().__init__('set_way_point')
        self.pose_scanner = None
        self.pose_target = None
        self.scanner = self.create_subscription(Pose, "/turtle1/pose", self.scan, 10)
        self.target = self.create_subscription(Pose, "/turtle_target/pose", self.target, 10)

        self.get_logger().info('Node démarré — en attente des poses...')

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

        
def main(args=None):
	rclpy.init(args=args)
	node = TurtleScanner()
	rclpy.spin(node)
	rclpy.shutdown()

if __name__=="__main__":
	main()