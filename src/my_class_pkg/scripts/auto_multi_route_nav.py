#!/usr/bin/env python3
import rospy
import sys
import time
import math
import actionlib
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from tf import transformations
from geometry_msgs.msg import Quaternion, PoseStamped
from std_msgs.msg import String
from apriltag_ros.msg import AprilTagDetectionArray

# ===================== 全局配置（你要的参数） =====================
# 到达容忍范围
XY_TOLERANCE = 0.05
YAW_TOLERANCE = 0.05

# 到达点附近后，卡住 10秒 才跳过
STUCK_TIMEOUT = 10.0  

# 识别目标Tag ID
TARGET_TAG_ID = 1

# 全局变量
tag1_detected = False
voice_pub = None
current_pose = None  # 实时位姿

# ===================== 实时获取机器人当前位姿（必须有） =====================
def pose_callback(msg):
    global current_pose
    current_pose = msg

# ===================== 语音播报函数 =====================
def say(text):
    global voice_pub
    msg = String()
    msg.data = text
    voice_pub.publish(msg)
    rospy.loginfo("[语音播报] " + text)
    rospy.sleep(2.0)

# ===================== AprilTag识别回调 =====================
def tag_callback(msg):
    global tag1_detected
    tag1_detected = False
    for detection in msg.detections:
        if detection.id[0] == TARGET_TAG_ID:
            tag1_detected = True
            break

# ===================== 计算欧拉角yaw =====================
def get_yaw_from_quaternion(quat):
    q = [quat.x, quat.y, quat.z, quat.w]
    roll, pitch, yaw = transformations.euler_from_quaternion(q)
    return yaw

# ===================== 核心：到达附近后卡住10秒才跳过 =====================
def go_point(x, y, yaw):
    client = actionlib.SimpleActionClient('move_base', MoveBaseAction)
    rospy.loginfo("等待 move_base 服务...")
    client.wait_for_server()

    goal = MoveBaseGoal()
    goal.target_pose.header.frame_id = "map"
    # ✅ 修复这里：rospy.Time.now() 而不是 rospy.now()
    goal.target_pose.header.stamp = rospy.Time.now()
    goal.target_pose.pose.position.x = x
    goal.target_pose.pose.position.y = y
    goal.target_pose.pose.position.z = 0.0

    q = transformations.quaternion_from_euler(0, 0, yaw)
    goal.target_pose.pose.orientation = Quaternion(*q)

    rospy.loginfo("前往点位：x=%.2f y=%.2f yaw=%.2f", x, y, yaw)
    client.send_goal(goal)

    # 计时变量
    near_start_time = None
    is_near = False

    while not rospy.is_shutdown():
        # 1. 导航成功完成 → 退出
        if client.get_state() == actionlib.GoalStatus.SUCCEEDED:
            rospy.loginfo("✅ 成功到达目标点")
            return True

        # 2. 没有获取到实时位姿 → 等待
        if current_pose is None:
            rospy.sleep(0.1)
            continue

        # 3. 计算当前与目标点的距离
        cx = current_pose.pose.position.x
        cy = current_pose.pose.position.y
        cyaw = get_yaw_from_quaternion(current_pose.pose.orientation)

        dist = math.hypot(cx - x, cy - y)
        yaw_err = abs(cyaw - yaw)

        # 4. 判断：是否已经到达目标点附近
        if dist < XY_TOLERANCE and yaw_err < YAW_TOLERANCE:
            if not is_near:
                rospy.loginfo("✅ 已到达点附近，开始计时卡住时间")
                is_near = True
                near_start_time = time.time()
            else:
                # 已经在附近，判断是否卡住超时
                if time.time() - near_start_time > STUCK_TIMEOUT:
                    rospy.logwarn(f"⏸️ 在点附近卡住超过{STUCK_TIMEOUT}秒，跳过该点")
                    client.cancel_goal()
                    return False
        else:
            # 不在附近 → 重置计时
            is_near = False
            near_start_time = None

        rospy.sleep(0.1)

    return False

# ===================== 路线定义 =====================
def go_common_prefix():
    go_point(1.97, 0.00, 0.00)
    go_point(2.44, -0.60, -1.50)

def go_route1():
    go_point(1.71, -0.68, -1.59)
    go_point(2.01, -4.27, 0.24)

def go_route2():
    go_point(1.10, -0.29, -2.88)
    go_point(0.27, -0.61, -1.47)
    go_point(0.30, -4.29, -1.61)
    go_point(1.72, -4.63, 0.16)
    go_point(2.83, -4.45, 1.64)

def go_common_suffix():
    go_point(2.33, -4.51, -2.88)
    go_point(1.76, -2.99, -3.10)
    go_point(0.53, -2.99, 2.73)
    go_point(-0.65, -2.59, 3.10)

# ===================== 主流程 =====================
if __name__ == '__main__':
    if len(sys.argv) < 2:
        rospy.logerr("请传入路线参数：0=路线一  1=路线二")
        sys.exit(1)

    route_mode = int(sys.argv[1])
    if route_mode not in [0, 1]:
        rospy.logerr("参数只能是 0 或 1")
        sys.exit(1)

    try:
        rospy.init_node('robot_multi_route_nav')
        
        # 订阅实时位姿
        rospy.Subscriber('/amcl_pose', PoseStamped, pose_callback)
        voice_pub = rospy.Publisher('/talk', String, queue_size=10)
        rospy.Subscriber('/tag_detections', AprilTagDetectionArray, tag_callback)
        rospy.sleep(1)

        say("任务开始，自主导航启动")

        # 公共前段
        go_common_prefix()

        # 目标点1
        say("前往第一个目标点")
        go_point(2.75, -1.80, -1.68)
        rospy.sleep(1.5)
        if tag1_detected:
            say("目标点一，成功识别AprilTag一号标签")
        else:
            say("目标点一，未识别到标签")

        # 选择路线
        if route_mode == 0:
            say("已选择路线一")
            go_route1()
        else:
            say("已选择路线二")
            go_route2()

        # 目标点2
        say("前往第二个目标点")
        go_point(2.73, -3.00, 1.80)
        rospy.sleep(1.5)
        if tag1_detected:
            say("目标点二，成功识别AprilTag一号标签")
        else:
            say("目标点二，未识别到标签")

        # 后段路径
        say("前往后续目标点")
        go_common_suffix()

        say("所有任务完成！")

    except rospy.ROSInterruptException:
        rospy.logerr("任务被中断")
     
