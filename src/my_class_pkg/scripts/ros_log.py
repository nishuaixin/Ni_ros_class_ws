#!/usr/bin/env python3
import rospy

if __name__ == '__main__':
    # 初始化ROS节点
    rospy.init_node('ros_logging_example_py')

    # 打印五级日志（DEBUG默认不显示）
    rospy.logdebug("This is a DEBUG message.（调试信息，开发阶段使用）")
    rospy.loginfo("This is an INFO message.（普通信息，提示系统状态）")
    rospy.logwarn("This is a WARNING message.（警告信息，潜在问题）")
    rospy.logerr("This is an ERROR message.（错误信息，需修复问题）")
    rospy.logfatal("This is a FATAL message.（致命错误，程序将终止）")

    # 运行ROS事件循环
    rospy.spin()

