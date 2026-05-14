#!/usr/bin/env python3
import rospy
import actionlib
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from tf import transformations
from geometry_msgs.msg import Quaternion
from std_msgs.msg import String
from apriltag_ros.msg import AprilTagDetectionArray

# -------------------------- 全局变量 --------------------------
tag1_detected = False
voice_pub = None

# -------------------------- 语音播报 --------------------------
def say(text):
    global voice_pub
    msg = String()
    msg.data = text
    voice_pub.publish(msg)
    rospy.loginfo("[语音] " + text)
    rospy.sleep(2.5)

# -------------------------- AprilTag识别 --------------------------
def tag_callback(msg):
    global tag1_detected
    tag1_detected = False
    for detection in msg.detections:
        if detection.id[0] == 1:
            tag1_detected = True
            break

# -------------------------- 发送导航目标点 --------------------------
def go_point(x, y, yaw):
    client = actionlib.SimpleActionClient('move_base', MoveBaseAction)
    rospy.loginfo("等待 move_base...")
    client.wait_for_server()

    goal = MoveBaseGoal()
    goal.target_pose.header.frame_id = "map"
    goal.target_pose.header.stamp = rospy.Time.now()

    # 位置
    goal.target_pose.pose.position.x = x
    goal.target_pose.pose.position.y = y
    goal.target_pose.pose.position.z = 0.0

    # 姿态 yaw -> 四元数
    q = transformations.quaternion_from_euler(0, 0, yaw)
    goal.target_pose.pose.orientation = Quaternion(*q)

    rospy.loginfo("前往目标点：x=%.2f y=%.2f yaw=%.2f" % (x, y, yaw))
    client.send_goal(goal)
    client.wait_for_result()
    rospy.loginfo("已到达目标点")

# -------------------------- 主流程 --------------------------
if __name__ == '__main__':
    try:
        rospy.init_node('auto_four_points_task')

        # 语音播报发布（话题：/talk）
        voice_pub = rospy.Publisher('/talk', String, queue_size=10)
        rospy.sleep(1)

        # 订阅AprilTag检测（话题：/tag_detections）
        rospy.Subscriber('/tag_detections', AprilTagDetectionArray, tag_callback)
        rospy.sleep(1)

        say("任务开始，机器人将自动前往四个目标点")

        # ===================== 目标点1 =====================
        say("正在前往第一个目标点")
        go_point(2.75, -1.8, 1.68)
        rospy.sleep(2)
        if tag1_detected:
            say("目标点一，成功识别AprilTag一号标签")
        else:
            say("目标点一，未识别到AprilTag一号标签")

        # ===================== 目标点2 =====================
        say("正在前往第二个目标点")
        go_point(2.73, -3.0, 1.80)
        rospy.sleep(2)
        if tag1_detected:
            say("目标点二，成功识别AprilTag一号标签")
        else:
            say("目标点二，未识别到AprilTag一号标签")

        # ===================== 目标点3 =====================
        say("正在前往第三个目标点")
        go_point(1.76, -2.99, -3.1)
        say("已到达第三个目标点")

        # ===================== 目标点4 =====================
        say("正在前往第四个目标点")
        go_point(-0.65, -2.59, 3.1)
        say("已到达第四个目标点，全部任务完成")

    except rospy.ROSInterruptException:
        rospy.logerr("程序中断")
