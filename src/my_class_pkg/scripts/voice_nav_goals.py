#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import rospy
import actionlib
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from std_msgs.msg import String
from geometry_msgs.msg import Quaternion
from math import sin, cos

class VoiceNavNode:
    def __init__(self):
        rospy.init_node('voice_nav_goals_node')
        
        # ------------- 你的两个固定点位 -------------
        self.goals = {
            "1": {
                "x": 2.516555,
                "y": -1.786569,
                "yaw": -0.154766,
                "name": "点位一"
            },
            "2": {
                "x": 1.163578,
                "y": -1.143194,
                "yaw": -0.073422,
                "name": "点位二"
            }
        }

        # 导航客户端
        self.client = actionlib.SimpleActionClient('move_base', MoveBaseAction)
        rospy.loginfo("等待 move_base 服务...")
        self.client.wait_for_server()
        rospy.loginfo("✅ 导航已就绪，等待语音指令")

        # 订阅语音识别结果
        rospy.Subscriber("/speech/result", String, self.speech_callback)
        
        # 语音播报发布
        self.talk_pub = rospy.Publisher("/talk", String, queue_size=1)

    # 欧拉角 yaw 转四元数（修复版，无tf2依赖）
    def yaw_to_quat(self, yaw):
        q = Quaternion()
        q.z = sin(yaw / 2.0)
        q.w = cos(yaw / 2.0)
        q.x = 0.0
        q.y = 0.0
        return q

    # 发送导航目标
    def send_goal(self, goal_id):
        if goal_id not in self.goals:
            self.speak("未找到该点位")
            return
        
        goal_info = self.goals[goal_id]
        x = goal_info["x"]
        y = goal_info["y"]
        yaw = goal_info["yaw"]
        name = goal_info["name"]

        rospy.loginfo(f"🚗 正在前往：{name}")
        self.speak(f"正在前往{name}")

        goal = MoveBaseGoal()
        goal.target_pose.header.frame_id = "map"
        goal.target_pose.header.stamp = rospy.Time.now()
        goal.target_pose.pose.position.x = x
        goal.target_pose.pose.position.y = y

        q = self.yaw_to_quat(yaw)
        goal.target_pose.pose.orientation = q

        self.client.send_goal(goal)
        self.client.wait_for_result()

        if self.client.get_state() == actionlib.SimpleGoalState.SUCCEEDED:
            rospy.loginfo(f"✅ 已到达：{name}")
            self.speak(f"已行驶到{name}")
        else:
            rospy.logerr(f"❌ 前往{name}失败")
            self.speak(f"前往{name}失败")

    # 语音识别回调：解析指令
    def speech_callback(self, msg):
        text = msg.data.strip()
        rospy.loginfo(f"🎤 识别到：{text}")

        if "目标点位一" in text or "点位一" in text:
            self.send_goal("2")
        elif "目标点位二" in text or "点位二" in text:
            self.send_goal("1")

    # 文字转语音播报
    def speak(self, content):
        self.talk_pub.publish(String(content))
        rospy.sleep(0.5)

if __name__ == '__main__':
    try:
        node = VoiceNavNode()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
