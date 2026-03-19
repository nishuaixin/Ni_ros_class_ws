#!/usr/bin/env python3
# 修正：import 后加空格，规范导入
import rospy
import actionlib
# 修正：单行完成导入，补全空格
from my_class_pkg.msg import MyActionAction, MyActionGoal, MyActionResult, MyActionFeedback

# 反馈回调函数（接收服务器的进度反馈）
# 修正：添加缩进（4个空格）
def feedback_cb(feedback):
    rospy.loginfo('Progress: {}%'.format(feedback.progress))

if __name__ == '__main__':  # 修正：补全空格
    # 初始化 ROS 客户端节点
    rospy.init_node('my_action_client')
    
    # 创建 Action 客户端（服务名：my_action，消息类型：MyActionAction）
    client = actionlib.SimpleActionClient('my_action', MyActionAction)
    
    # 等待 Action 服务器启动（阻塞直到服务器上线）
    rospy.loginfo('Waiting for action server...')
    client.wait_for_server()
    rospy.loginfo('Connected to action server!')

    # 创建动作目标（修正：移除不存在的 object_name 字段）
    goal = MyActionGoal()
    
    # 发送目标，并指定反馈回调函数
    rospy.loginfo('Sending goal...')
    client.send_goal(goal, feedback_cb=feedback_cb)
    
    # 等待任务完成（阻塞直到服务器返回结果）
    client.wait_for_result()

    # 获取并输出结果
    result = client.get_result()
    if result.success:
        rospy.loginfo('Action succeeded!')
    else:
        rospy.loginfo('Action failed!')
