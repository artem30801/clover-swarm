#!/usr/bin/env python

# Demo Python node that periodically publishes a `Hello` string to `/test` topic.

import rospy
from std_msgs.msg import String

rospy.init_node('clover_app')

pub = rospy.Publisher('/swarm_test', String, queue_size=1)

r = rospy.Rate(5)

while not rospy.is_shutdown():
	pub.publish('Hello swarm')
	r.sleep()