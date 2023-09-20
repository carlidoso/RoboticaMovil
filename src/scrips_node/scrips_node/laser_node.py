import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
import math

import sys

class laser_node(Node): 
    def __init__(self):
        super().__init__("laser_node") 

        self.ac = 0.1
        self.l = 0.1
        self.cd = 0.0
        self.cd_2 = 0.0 #el 2 es el de la izquierda los otros de la derecha
        self.theta = 0.0
        self.theta_2 = 0.0
        self.y = 0.0
        self.y_2 = 0.0
        self.anterior = 0.0
        self.anterior_2 = 0.0
        self.distancia_muro = 0.6

        # subscriptor obj
        # obj (msg_type,topic_name, callback_handler, buffer) 
        self.laser_sub = self.create_subscription(LaserScan, '/scan', self.scaner, 1)
        
        self.error_pub = self.create_publisher(Twist, '/error', 10)

        timer_period = 0.5 # in [s]
        self.timer = self.create_timer(timer_period, self.error)
    
    def scaner(self, data):
        ranges = data.ranges
        b = ranges[0]
        a = ranges[30]
        b_2 = ranges[179]
        a_2 = ranges[149]
        alfa = math.atan((a*math.cos(math.pi/6)-b)/(a*math.sin(math.pi/6)))
        alfa_2 = math.atan((a_2*math.cos(math.pi/6)-b_2)/(a_2*math.sin(math.pi/6)))
        ab = b*math.cos(alfa)
        ab_2 = b_2*math.cos(alfa_2)
        self.cd = ab + self.ac*math.sin(alfa)
        self.cd_2 = ab_2 + self.ac*math.sin(alfa_2)
        self.theta = -alfa
        self.theta_2 = -alfa_2
        self.y = self.distancia_muro - self.cd
        self.y_2 = self.distancia_muro - self.cd_2

    def error(self):
        error = Twist()
        # if(self.cd <= self.cd_2):
        #     error.linear.x = -(self.y + self.l*math.sin(self.theta))
        #     error.linear.y = 0.0 #con esto se si esta por derecha o izquierda, el cero es derecha
        #     error.linear.z = error.linear.x - self.anterior
        #     self.anterior = error.linear.x
        # else:
        #     error.linear.x = -(self.y_2 + self.l*math.sin(self.theta_2))
        #     error.linear.y = 1.0 #este es muro de izquierda
        #     error.linear.z = error.linear.x - self.anterior_2
        #     self.anterior_2 = error.linear.x
        error.linear.x = -(self.y + self.l*math.sin(self.theta))
        error.linear.y = 0.0 #con esto se si esta por derecha o izquierda, el cero es derecha
        error.linear.z = error.linear.x - self.anterior
        self.anterior = error.linear.x
        error.angular.x = self.cd
        error.angular.y = self.cd_2
        #self.get_logger().info('Envio el error:'+ str(error.position.x)+'\n\n\n')

        self.error_pub.publish(error)

def main(args=None):
    rclpy.init(args=args)
    node = laser_node() # Definicion del objeto "node"

    # ejecucion ciclica 
    rclpy.spin(node)
    # finalizacion
    rclpy.shutdown()

if __name__ == "__main__":
    main()