import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from tf2_ros import TransformBroadcaster
from geometry_msgs.msg import TransformStamped
import numpy as np
import math

import sys

def quaternion_from_euler(ai, aj, ak):
    ai /= 2.0
    aj /= 2.0
    ak /= 2.0
    ci = math.cos(ai)
    si = math.sin(ai)
    cj = math.cos(aj)
    sj = math.sin(aj)
    ck = math.cos(ak)
    sk = math.sin(ak)
    cc = ci*ck
    cs = ci*sk
    sc = si*ck
    ss = si*sk

    q = np.empty((4, ))
    q[0] = cj*sc - sj*cs
    q[1] = cj*ss + sj*cc
    q[2] = cj*cs - sj*sc
    q[3] = cj*cc + sj*ss

    return q

class ackerman(Node): 
    def __init__(self):
        super().__init__("ackerman_node") 

        self.angulo = 0 #angulo de la rueda imaginaria
        self.t = 0.2 #ancho del auto
        self.d = 0.17 #largo del auto

        self.declare_parameter('left_wheel_steer_joint', 'left_wheel_steer_joint')
        self.left_wheel_steer_joint = self.get_parameter(
            'left_wheel_steer_joint').get_parameter_value().string_value

        # subscriptor
        # obj (msg_type,topic_name, callback_handler, buffer) 
        self.cmd_sub = self.create_subscription(Twist, '/cmd_vel', self.velocidad_joint, 1)

        # Initialize the transform broadcaster
        self.tf_broadcaster = TransformBroadcaster(self)

    def velocidad_joint(self, data):
        rotz = data.angular.z
        print('Rotz ' + str(rotz))
        if rotz > 0:
            self.angulo = 0.5
        elif rotz < 0:
            self.angulo = -0.5
        else:
            self.angulo = 0

        t = TransformStamped()

        # Read message content and assign it to
        # corresponding tf variables
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'base_link'
        t.child_frame_id = 'left_wheel_steer_joint'

        if self.angulo != 0:
            r = self.d/math.tan(self.angulo)
            anguloI = math.atan(self.d/(r - self.t/2))
            anguloD = math.atan(self.d/(r + self.t/2))
        else:
            anguloD = 0
            anguloI = 0
        print('AnguloI ' + str(anguloI))

        q = quaternion_from_euler(0, 0, math.pi/2)
        t.transform.rotation.x = q[0]
        t.transform.rotation.y = q[1]
        t.transform.rotation.z = q[2]
        t.transform.rotation.w = q[3]

        # Send the transformation
        self.tf_broadcaster.sendTransform(t)


def main(args=None):
    rclpy.init(args=args)
    node = ackerman() # Definicion del objeto "node"

    # ejecucion ciclica 
    rclpy.spin(node)
    # finalizacion
    rclpy.shutdown()

if __name__ == "__main__":
    main()