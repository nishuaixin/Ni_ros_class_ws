#!/usr/bin/env python3
# 修正：import 后加空格，规范导入语句
import rospy
import actionlib
# 修正：单行完成导入，避免换行错误
from my_class_pkg.msg import MyActionAction, MyActionGoal, MyActionResult, MyActionFeedback

class MyActionServer(object):
    # 修正：函数名和括号间加空格，规范缩进
    def __init__(self, name):
        self._action_name = name
        # 初始化 Action 服务器（auto_start=False 手动启动）
        self._as = actionlib.SimpleActionServer(
            self._action_name, 
            MyActionAction,
            execute_cb=self.executeCB,
            auto_start=False
        )
        self._as.start()  # 启动 Action 服务器
        # 初始化反馈和结果消息
        self._feedback = MyActionFeedback()
        self._result = MyActionResult()

    # 核心回调函数：处理客户端的目标请求
    def executeCB(self, goal):
        r = rospy.Rate(1)  # 1Hz 循环频率
        success = True

        # 模拟耗时任务（循环10次，进度每次+10%）
        for i in range(1, 11):
            # 检查是否被客户端取消
            if self._as.is_preempt_requested():
                rospy.loginfo('{}: Preempted'.format(self._action_name))
                self._as.set_preempted()  # 标记任务被取消
                success = False
                break

            # 更新进度反馈并发布
            self._feedback.progress = i * 10
            rospy.loginfo(
                '{}: Executing, progress = {}%'.format(
                    self._action_name, 
                    self._feedback.progress
                )
            )
            self._as.publish_feedback(self._feedback)
            r.sleep()  # 按频率休眠

        # 任务完成，发送最终结果
        if success:
            self._result.success = True
            rospy.loginfo('{}: Succeeded'.format(self._action_name))
            self._as.set_succeeded(self._result)  # 标记任务成功

if __name__ == '__main__':
    # 初始化 ROS 节点
    rospy.init_node('my_action_server_py')
    # 创建 Action 服务器实例（服务名：my_action）
    server = MyActionServer('my_action')
    # 保持节点运行
    rospy.spin()
