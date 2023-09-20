import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
import math

class pidWF_node(Node): 
    def __init__(self):
        super().__init__("pidWF_node") 
        self.error_mio = 0.0
        self.lado = 0.0
        self.kp = 2.0
        self.kd = 2.1
        self.der = 0.0
        self.cd = 0.0
        self.cd2 = 0.0
        self.velocidad_angular = 0.5
        self.distancia_muy_segura = 0.6
        self.ranges = [0.0]

        # subscriptor obj
        # obj (msg_type,topic_name, callback_handler, buffer) 
        self.error_sub = self.create_subscription(Twist, '/error', self.error, 1)
        self.laser_sub = self.create_subscription(LaserScan, '/scan', self.scaner, 1)

        self.cmd_pub = self.create_publisher(Twist, '/cmd_pid', 10)

        self.timer_period = 0.5 # in [s]
        self.timer = self.create_timer(self.timer_period, self.velocidad)

    def error(self, data):
        self.error_mio = data.linear.x
        self.lado = data.linear.y
        self.der = data.linear.z #lo voy a usar para la derivada del error
        self.cd = data.angular.x
        self.cd2 = data.angular.y

    def scaner(self, data):
        self.ranges = data.ranges
    
    def velocidad(self): #el eje de giro z sale del piso
        vel = Twist()
        vel.linear.x = 0.4
        if(not math.isnan(self.error_mio) and not math.isinf(self.error_mio)):
            if(self.lado == 0.0):
                vel.angular.z = -(self.kp*self.error_mio + self.kd*self.der/self.timer_period)
            else:
                vel.angular.z = self.kp*self.error_mio + self.kd*self.der/self.timer_period

            # if(min(self.ranges) <= self.distancia_muy_segura and (self.ranges.index(min(self.ranges)) > 60 or self.ranges.index(min(self.ranges)) < 120)):
                
            #     if (self.cd <= self.cd2):
            #         vel.angular.z = self.velocidad_angular
            #     else:
            #         vel.angular.z = -self.velocidad_angular
        #self.get_logger().info('Recibo el error:'+ str(self.error_mio)+'\n\n\n')
        #self.get_logger().info('Vel angular:'+ str(vel.angular.z)+'\n\n\n')
        self.cmd_pub.publish(vel)

def main(args=None):
    rclpy.init(args=args)
    node = pidWF_node() # Definicion del objeto "node"

    # ejecucion ciclica 
    rclpy.spin(node)
    # finalizacion
    rclpy.shutdown()

if __name__ == "__main__":
    main()