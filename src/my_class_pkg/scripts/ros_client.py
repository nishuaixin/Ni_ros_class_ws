#!/usr/bin/env python3
import rospy
from my_class_pkg.srv import MyServiceMsg
rospy.init_node("my_service_client")
#等待my_service服务可用
rospy.wait_for_service("my_service")
#创建my_service服务的客户端
client = rospy.ServiceProxy("my_service",MyServiceMsg)
#发送请求消息并等待响应
try:
    resp=client.call(2)
    rospy.loginfo("Service response:%d",resp.output)
except rospy.ServiceException as e:
    rospy.logerr("Servicecall failed:%s",e)