#include "ros/ros.h"
#include "geometry_msgs/Twist.h"
#include "std_msgs/Int16MultiArray.h"

// 全局变量存储碰撞传感器数据
std_msgs::Int16MultiArray::ConstPtr g_bump_msg = nullptr;

// 碰撞传感器回调函数
void bumpCallback(const std_msgs::Int16MultiArray::ConstPtr& msg) {
    g_bump_msg = msg;
}

int main(int argc, char **argv) {
    // 初始化ROS节点
    ros::init(argc, argv, "bump_run");
    ros::NodeHandle nh;

    // 创建速度指令发布者（发布到/cmd_vel话题）
    ros::Publisher vel_pub = nh.advertise<geometry_msgs::Twist>("/cmd_vel", 10);
    // 创建碰撞传感器订阅者
    ros::Subscriber bump_sub = nh.subscribe("/robot/bump_sensor", 10, bumpCallback);

    // 初始化速度消息（默认前进）
    geometry_msgs::Twist vel_msg;
    vel_msg.linear.x = 0.3;  // 前进速度0.3m/s
    vel_msg.angular.z = 0;

    ros::Rate loop_rate(10);  // 10Hz循环
    int count = 0;            // 后退计数

    while (ros::ok()) {
        // 发布默认前进指令
        vel_pub.publish(vel_msg);
        ros::spinOnce();  // 处理回调

        // 检测碰撞（左前/正前/右前）
        if (g_bump_msg != nullptr) {
            if (g_bump_msg->data[0] == 1 || g_bump_msg->data[1] == 1 || g_bump_msg->data[2] == 1) {
                ROS_INFO("碰撞检测！开始后退");
                // 后退4秒（10Hz×40次）
                while (count < 40) {
                    vel_msg.linear.x = -0.1;  // 后退0.1m/s
                    vel_pub.publish(vel_msg);
                    count++;
                    loop_rate.sleep();
                }
                // 恢复前进
                count = 0;
                vel_msg.linear.x = 0.3;
                ROS_INFO("后退完成，恢复前进");
            }
        }
        loop_rate.sleep();
    }

    // 程序退出，停止机器人
    vel_msg.linear.x = 0;
    vel_pub.publish(vel_msg);
    return 0;
}