#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math
import os
import sys

import actionlib
import rospy
from actionlib_msgs.msg import GoalStatus
from apriltag_ros.msg import AprilTagDetectionArray
from geometry_msgs.msg import PoseWithCovarianceStamped, Quaternion, Twist
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from std_srvs.srv import Empty
from std_msgs.msg import String
from tf import transformations

try:
    from nav_msgs.srv import LoadMap
except ImportError:
    LoadMap = None


TAG_ID = 1
ROUTE2_MAP_PGM = "/home/bcsh/upros_class_code/src/upros_navigation/maps/my_lab2.pgm"
ROUTE2_MAP_YAML = os.path.splitext(ROUTE2_MAP_PGM)[0] + ".yaml"


def read_route_param():
    route = rospy.get_param("~route", rospy.get_param("/route", 1))

    for arg in sys.argv:
        if arg.startswith("route:=") or arg.startswith("_route:="):
            try:
                route = int(arg.split(":=", 1)[1])
            except ValueError:
                rospy.logwarn("路线参数格式错误，使用默认路线一: %s", arg)

    if route not in (1, 2):
        rospy.logwarn("路线参数只能是 1 或 2，当前为 %d，自动使用路线一", route)
        route = 1

    return route


class FastFourPointsTask:
    def __init__(self):
        self.voice_pub = rospy.Publisher("/talk", String, queue_size=10)
        self.cmd_vel_pub = rospy.Publisher("/cmd_vel", Twist, queue_size=10)
        self.tag1_last_seen = rospy.Time(0)
        self.current_pose = None
        self.route = read_route_param()

        rospy.Subscriber("/tag_detections", AprilTagDetectionArray, self.tag_callback)
        rospy.Subscriber("/amcl_pose", PoseWithCovarianceStamped, self.pose_callback)

        self.client = actionlib.SimpleActionClient("move_base", MoveBaseAction)
        rospy.loginfo("等待 move_base action server...")
        self.client.wait_for_server()
        rospy.loginfo("move_base 已连接")
        rospy.loginfo("当前选择路线: route=%d", self.route)
        if self.route == 2:
            self.switch_to_route2_map()

    def switch_to_route2_map(self):
        if LoadMap is None:
            rospy.logwarn("当前 ROS 环境没有 nav_msgs/LoadMap，无法在脚本中切换地图")
            return False

        if not os.path.exists(ROUTE2_MAP_YAML):
            rospy.logwarn("路线二地图 yaml 不存在: %s", ROUTE2_MAP_YAML)
            rospy.logwarn("map_server 需要加载 yaml，不是直接加载 pgm: %s", ROUTE2_MAP_PGM)
            return False

        try:
            rospy.loginfo("路线二：正在切换地图 %s", ROUTE2_MAP_YAML)
            rospy.wait_for_service("/change_map", timeout=5.0)
            change_map = rospy.ServiceProxy("/change_map", LoadMap)
            result = change_map(ROUTE2_MAP_YAML)
            rospy.loginfo("路线二地图切换完成: %s", result)
            self.clear_costmaps()
            rospy.sleep(1.0)
            return True
        except Exception as exc:
            rospy.logwarn("路线二地图自动切换失败: %s", exc)
            rospy.logwarn("请改用 roslaunch 加载路线二地图 yaml: %s", ROUTE2_MAP_YAML)
            return False

    def clear_costmaps(self):
        try:
            rospy.wait_for_service("/move_base/clear_costmaps", timeout=3.0)
            clear = rospy.ServiceProxy("/move_base/clear_costmaps", Empty)
            clear()
            rospy.loginfo("已清理 move_base costmaps")
        except Exception as exc:
            rospy.logwarn("清理 costmaps 失败，继续执行任务: %s", exc)

    def back_off(self, speed=-0.10, duration=1.2):
        rospy.logwarn("检测到卡住，后退 %.1f 秒后重新规划", duration)
        twist = Twist()
        twist.linear.x = speed
        rate = rospy.Rate(10)
        end_time = rospy.Time.now() + rospy.Duration(duration)

        while not rospy.is_shutdown() and rospy.Time.now() < end_time:
            self.cmd_vel_pub.publish(twist)
            rate.sleep()

        twist.linear.x = 0.0
        twist.angular.z = 0.0
        for _ in range(5):
            self.cmd_vel_pub.publish(twist)
            rospy.sleep(0.05)

    def recover_and_retry(self, name, x, y, yaw):
        rospy.logwarn("%s 执行脱困：取消目标、后退、清图、重新规划", name)
        self.client.cancel_goal()
        rospy.sleep(0.3)
        self.back_off()
        self.clear_costmaps()
        rospy.sleep(0.5)
        self.client.send_goal(self.make_goal(x, y, yaw))

    def say(self, text, wait=1.5):
        msg = String()
        msg.data = text
        self.voice_pub.publish(msg)
        rospy.loginfo("[语音] %s", text)
        rospy.sleep(7.0)

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

    def go_point(self, name, x, y, yaw, xy_tol=0.25, yaw_tol=3.14, timeout=120.0, retries=1):
        rospy.loginfo(
            "前往%s: x=%.2f y=%.2f yaw=%.2f xy_tol=%.2f yaw_tol=%.2f timeout=%.1f",
            name, x, y, yaw, xy_tol, yaw_tol, timeout
        )
        self.client.send_goal(self.make_goal(x, y, yaw))

        start = rospy.Time.now()
        near_since = None
        retry_count = 0
        last_distance, _ = self.pose_error(x, y, yaw)
        last_progress_time = rospy.Time.now()
        rate = rospy.Rate(10)

        while not rospy.is_shutdown():
            state = self.client.get_state()
            if state == GoalStatus.SUCCEEDED:
                rospy.loginfo("%s 已到达", name)
                return True

            if state in (GoalStatus.ABORTED, GoalStatus.REJECTED, GoalStatus.LOST):
                if retry_count < retries:
                    retry_count += 1
                    rospy.logwarn("%s 导航失败，清理 costmap 后第 %d 次重试", name, retry_count)
                    self.recover_and_retry(name, x, y, yaw)
                    near_since = None
                    start = rospy.Time.now()
                    last_distance, _ = self.pose_error(x, y, yaw)
                    last_progress_time = rospy.Time.now()
                    continue

                rospy.logwarn("%s 导航失败且重试次数已用完，进入下一步", name)
                return False

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

            current_distance, _ = self.pose_error(x, y, yaw)
            if current_distance is not None:
                if last_distance is None or current_distance < last_distance - 0.06:
                    last_distance = current_distance
                    last_progress_time = rospy.Time.now()
                elif (
                    current_distance > xy_tol + 0.10
                    and (rospy.Time.now() - last_progress_time).to_sec() > 8.0
                    and retry_count < retries
                ):
                    retry_count += 1
                    rospy.logwarn("%s 8 秒内没有明显靠近目标，执行第 %d 次脱困", name, retry_count)
                    self.recover_and_retry(name, x, y, yaw)
                    near_since = None
                    start = rospy.Time.now()
                    last_distance, _ = self.pose_error(x, y, yaw)
                    last_progress_time = rospy.Time.now()
                    continue

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

        # 先去目标点一前置途经点
        self.go_point(
            "目标点一前置途经点",
            1.93, -0.29, -0.21,
            xy_tol=0.30,
            yaw_tol=3.14,
            timeout=120.0
        )

        # 目标点一
        self.go_point(
            "目标点一附近",
            2.57, -1.41, -1.34,
            xy_tol=0.22,
            yaw_tol=3.14,
            timeout=120.0
        )
        self.rotate_at_point("目标点一", 2.57, -1.41, -1.34, timeout=35.0)
        self.detect_tag_and_say("目标点一")

        # 从目标点一出来 再次经过同一点
        self.go_point(
            "离开目标点一途经点",
            1.93, -0.29, -3.02,
            xy_tol=0.30,
            yaw_tol=3.14,
            timeout=120.0
        )

        # 路线2 修改后逻辑：删除原有3个点，新增指定点后直接前往目标点二途经点
        if self.route == 2:
	            # 新增你指定的路线2关键点
            self.go_point(
                "路线二新增中转点",
                0.53, -4.3, -1.28,
                xy_tol=0.35,
                yaw_tol=3.14,
                timeout=160.0,
                retries=2
            )

        # 前往目标点二途经点
        self.go_point(
            "前往目标点二途经点",
            2.10, -4.38, 0.09,
            xy_tol=0.30,
            yaw_tol=3.14,
            timeout=140.0
        )

        # 目标点二
        self.go_point(
            "目标点二附近",
            2.70, -3.06, 1.51,
            xy_tol=0.25,
            yaw_tol=3.14,
            timeout=140.0,
            retries=2
        )
        self.rotate_at_point("目标点二", 2.70, -3.06, 1.51, timeout=40.0)
        self.detect_tag_and_say("目标点二")

        # 离开目标点二后返回途经点
        self.go_point(
            "离开目标点二途经点",
            2.10, -4.38, 3.10,
            xy_tol=0.30,
            yaw_tol=3.14,
            timeout=140.0
        )

        # 目标点四
        self.go_point(
            "目标点四附近",
            -0.68, -2.44, 3,
            xy_tol=0.28,
            yaw_tol=3.14,
            timeout=160.0
        )
        self.rotate_at_point("目标点四", -0.68, -2.44, 2.24, timeout=40.0)


if __name__ == "__main__":
    try:
        rospy.init_node("auto_fast_task_no_point3")
        FastFourPointsTask().run()
    except rospy.ROSInterruptException:
        rospy.logerr("程序中断")
