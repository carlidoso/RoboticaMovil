import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan

class stop_node(Node): 
    def __init__(self):
        super().__init__("stop_node") 
        self.ranges = [0.0]
        self.vel_ang_z = 0.0
        self.distancia_segura = 0.5
        self.cd = 0.0
        self.cd2 = 0.0
        self.velocidad_angular = 0.8

        # subscriptor obj
        # obj (msg_type,topic_name, callback_handler, buffer) 
        self.laser_sub = self.create_subscription(LaserScan, '/scan', self.scaner, 1)
        self.cmd_sub = self.create_subscription(Twist, '/cmd_vel', self.velocidad, 1)
        self.error_sub = self.create_subscription(Twist, '/error', self.error, 1)

        self.cmd_pub = self.create_publisher(Twist, '/cmd_parar', 10)

        timer_period = 0.5 # in [s]
        self.timer = self.create_timer(timer_period, self.parar)

    def scaner(self, data):
        self.ranges = data.ranges
        #self.get_logger().info('rango 1:'+ str(self.ranges[0])+'\n\n\n')
        #self.get_logger().info('rango 2:'+ str(self.ranges[179])+'\n\n\n')
    
    def velocidad(self, data):
        self.vel_ang_z = data.angular.z

    def error(self, data):
        self.cd = data.angular.x
        self.cd2 = data.angular.y

    def parar(self):
        vel = Twist()
        
        # if(min(self.ranges) <= self.distancia_segura):
        #     #self.get_logger().info('Min:'+ str(min(self.ranges))+'\n\n\n')
        #     vel.linear.x = -0.1
        #     #el siguiente if es para saber si esta por chocarse de frente, es decir, mira si la distancia esta muy pequeña en un rango de angulos que esta justo frente al robot
        #     if(self.vel_ang_z < 0.0 and (self.ranges.index(min(self.ranges)) < 60 or self.ranges.index(min(self.ranges)) > 120)):
        #         vel.angular.z = -self.velocidad_angular
        #     else:
        #         vel.angular.z = self.velocidad_angular
        #     #vel.angular.z = 1.0
        #     self.get_logger().info('Vel angular:'+ str(vel.angular.z)+'\n\n\n')
        #     self.cmd_pub.publish(vel)
        if(min(self.ranges) <= self.distancia_segura and (self.ranges.index(min(self.ranges)) > 50 or self.ranges.index(min(self.ranges)) < 120)):
            #if (self.cd <= self.cd2):
            vel.angular.z = self.velocidad_angular
            #else:
                #vel.angular.z = self.velocidad_angular
            vel.linear.x = -0.5
            #self.get_logger().info('Pa tra:'+ str(vel.linear.x)+'\n')
            #self.get_logger().info('Pa lado:'+ str(vel.angular.z)+'\n\n\n')
            self.cmd_pub.publish(vel)




def main(args=None):
    rclpy.init(args=args)
    node = stop_node() # Definicion del objeto "node"

    # ejecucion ciclica 
    rclpy.spin(node)
    # finalizacion
    rclpy.shutdown()

if __name__ == "__main__":
    main()