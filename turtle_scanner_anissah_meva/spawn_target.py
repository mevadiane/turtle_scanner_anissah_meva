import rclpy
from rclpy.node import Node
from turtlesim.srv import Spawn
import random

class SpawnTarget(Node):
    def __init__(self):
        super().__init__('spawn_target')
        self.client = self.create_client(Spawn, "/spawn")

        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for spawn service')
            
        self.spawn_request()
    
    def spawn_request(self):
        request = Spawn.Request()

        self.target_x = random.uniform(1.0, 10.0)
        self.target_y = random.uniform(1.0, 10.0)
        request.x = self.target_x
        request.y = self.target_y
        request.theta = 0.0
        request.name = 'turtle_target'

        future = self.client.call_async(request)
        future.add_done_callback(self.spawn_callback)

    def spawn_callback(self, future):
        response = future.result()
        self.get_logger().info(
            f'Spawned "{response.name}" at x={self.target_x:.2f}, y={self.target_y:.2f}'
        )


def main(args=None):
	rclpy.init(args=args)
	node = SpawnTarget()
	rclpy.spin(node)
	rclpy.shutdown()

if __name__=="__main__":
	main()