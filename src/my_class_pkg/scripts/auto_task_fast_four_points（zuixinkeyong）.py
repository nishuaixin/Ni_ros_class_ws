#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math

import actionlib
import rospy
from actionlib_msgs.msg import GoalStatus
from apriltag_ros.msg import AprilTagDetectionArray
from geometry_msgs.msg import PoseWithCovarianceStamped, Quaternion
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from std_msgs.msg import String
from tf import transformations


TAG_ID = 1


class FastFourPointsTask:
    def __init__(self):
        self.voice_pub = rospy.Publisher("/talk", String, queue_size=10)
        self.tag1_last_seen = rospy.Time(0)
        self.current_pose = None

        rospy.Subscriber("/tag_detections", AprilTagDetectionArray, self.tag_callback)
        rospy.Subscriber("/amcl_pose", PoseWithCovarianceStamped, self.pose_callback)

        self.client = actionlib.SimpleActionClient("move_base", MoveBaseAction)
        rospy.loginfo("等待 move_base action server...")
        self.client.wait_for_server()
        rospy.loginfo("move_base 已连接")

    def say(self, text, wait=0.5):
        msg = String()
        msg.data = text
        self.voice_pub.publish(msg)
        rospy.loginfo("[语音] %s", text)
        if wait > 0:
            rospy.sleep(wait)

    def tag_callback(self, msg):
        for detection in msg.detections:
            if detection.id and detection.id[0] == TAG_ID:
                self.tag1_last_seen = rospy.Time.now()
                return

    def pose_callback(self, msg):
        self.current_pose = msg.pose.pose

    @staticmethod
    def make_goal(x, y, yaw):
        goal = MoveBaseGoal()
        goal.target_pose.header.frame_id = "map"
        goal.target_pose.header.stamp = rospy.Time.now()
        goal.target_pose.pose.position.x = x
        goal.target_pose.pose.position.y = y
        goal.target_pose.pose.position.z = 0.0
        q = transformations.quaternion_from_euler(0, 0, yaw)
        goal.target_pose.pose.orientation = Quaternion(*q)
        return goal

    @staticmethod
    def normalize_angle(angle):
        return math.atan2(math.sin(angle), math.cos(angle))

    def pose_error(self, x, y, yaw):
        if self.current_pose is None:
            return None, None

        px = self.current_pose.position.x
        py = self.current_pose.position.y
        distance = math.hypot(px - x, py - y)

        q = self.current_pose.orientation
        _, _, current_yaw = transformations.euler_from_quaternion([q.x, q.y, q.z, q.w])
        yaw_error = abs(self.normalize_angle(current_yaw - yaw))
        return distance, yaw_error

    def is_near(self, x, y, yaw, xy_tol, yaw_tol):
        distance, yaw_error = self.pose_error(x, y, yaw)
        if distance is None:
            return False
        return distance <= xy_tol and yaw_error <= yaw_tol

    def go_point(self, name, x, y, yaw, xy_tol=0.25, yaw_tol=3.14, timeout=120.0):
        rospy.loginfo(
            "前往%s: x=%.2f y=%.2f yaw=%.2f xy_tol=%.2f yaw_tol=%.2f timeout=%.1f",
            name, x, y, yaw, xy_tol, yaw_tol, timeout
        )
        self.client.send_goal(self.make_goal(x, y, yaw))

        start = rospy.Time.now()
        near_since = None
        rate = rospy.Rate(10)

        while not rospy.is_shutdown():
            state = self.client.get_state()
            if state == GoalStatus.SUCCEEDED:
                rospy.loginfo("%s 已到达", name)
                return True

            if self.is_near(x, y, yaw, xy_tol, yaw_tol):
                if near_since is None:
                    near_since = rospy.Time.now()
                elif (rospy.Time.now() - near_since).to_sec() >= 1.0:
                    rospy.loginfo("%s 已进入允许范围，提前进入下一步", name)
                    self.client.cancel_goal()
                    rospy.sleep(0.2)
                    return True
            else:
                near_since = None

            if (rospy.Time.now() - start).to_sec() > timeout:
                rospy.logwarn("%s 导航超时，跳过该点", name)
                self.client.cancel_goal()
                rospy.sleep(0.2)
                return False

            rate.sleep()

        return False

    def rotate_at_point(self, name, x, y, yaw, timeout=40.0):
        rospy.loginfo("%s 到点后调整朝向 yaw=%.2f", name, yaw)
        return self.go_point(
            name + "调整朝向",
            x, y, yaw,
            xy_tol=0.35,
            yaw_tol=0.28,
            timeout=timeout
        )

    def detect_tag_and_say(self, point_name, detect_time=1.8):
        self.tag1_last_seen = rospy.Time(0)
        end_time = rospy.Time.now() + rospy.Duration(detect_time)
        rate = rospy.Rate(10)

        while not rospy.is_shutdown() and rospy.Time.now() < end_time:
            if (rospy.Time.now() - self.tag1_last_seen).to_sec() < 0.6:
                self.say("%s，成功识别到 AprilTag 一号码" % point_name)
                return True
            rate.sleep()

        self.say("%s，未识别到 AprilTag 一号码" % point_name)
        return False

    def run(self):
        rospy.sleep(1.0)
        self.say("任务开始，机器人将按高效模式前往目标点")

        self.say("正在前往第一个目标点", wait=0.2)
        self.go_point(
            "目标点一附近",
            2.75, -1.80, -0.60,
            xy_tol=0.22,
            yaw_tol=3.14,
            timeout=120.0
        )
        self.rotate_at_point("目标点一", 2.75, -1.80, -1.68, timeout=35.0)
        self.detect_tag_and_say("目标点一")

        self.say("正在前往第二个目标点", wait=0.2)
        self.go_point(
            "目标点二附近",
            2.73, -3.00, -1.57,
            xy_tol=0.25,
            yaw_tol=3.14,
            timeout=140.0
        )
        self.rotate_at_point("目标点二", 2.73, -3.00, 1.80, timeout=40.0)
        self.detect_tag_and_say("目标点二")

        self.say("正在前往第四个目标点", wait=0.2)
        self.go_point(
            "目标点四附近",
            -0.65, -2.59, 3.00,
            xy_tol=0.28,
            yaw_tol=3.14,
            timeout=160.0
        )
        self.rotate_at_point("目标点四", -0.65, -2.59, 3.10, timeout=40.0)

        self.say("已到达第四个目标点，全部任务完成")


if __name__ == "__main__":
    try:
        rospy.init_node("auto_fast_task_no_point3")
        FastFourPointsTask().run()
    except rospy.ROSInterruptException:
        rospy.logerr("程序中断")

