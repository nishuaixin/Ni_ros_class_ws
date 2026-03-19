#include <ros/ros.h>
#include <geometry_msgs/Twist.h>
#include <sensor_msgs/Imu.h>
#include <cmath>  // 用于π值和数学计算

// 全局变量存储IMU z轴角速度（绕竖直轴旋转）
double current_angular_z = 0.0;

// IMU回调函数：获取z轴角速度
void imu_callback(const sensor_msgs::Imu::ConstPtr& imu_msg) {
    current_angular_z = imu_msg->angular_velocity.z;
    // 简化打印，仅输出z轴角速度（旋转核心）
    ROS_INFO_THROTTLE(1.0, "IMU Z angular velocity: %.3f rad/s", current_angular_z);
}

int main(int argc, char** argv) {
    ros::init(argc, argv, "rotate_180_with_imu");
    ros::NodeHandle nh;

    // 发布速度指令到机器人运动话题
    ros::Publisher vel_pub = nh.advertise<geometry_msgs::Twist>("/cmd_vel", 10);
    // 订阅IMU数据
    ros::Subscriber imu_sub = nh.subscribe<sensor_msgs::Imu>("/imu/data", 10, imu_callback);

    ros::Rate loop_rate(10); // 10Hz循环频率
    geometry_msgs::Twist vel_msg;
    // 初始化：原地旋转，线速度全为0
    vel_msg.linear.x = 0.0;
    vel_msg.linear.y = 0.0;
    vel_msg.linear.z = 0.0;
    vel_msg.angular.x = 0.0;
    vel_msg.angular.y = 0.0;

    // 旋转参数：180°=π弧度，角速度π/10 rad/s（约18°/s，旋转平稳）
    double rotate_speed = M_PI / 10;
    double target_angle = M_PI;    // 目标角度：π rad
    double elapsed_time = 0.0;     // 已旋转时间
    double dt = 1.0 / 10.0;        // 每次循环时间间隔（10Hz=0.1s）

    ROS_INFO("Start rotating 180 degrees...");
    // 自旋循环：未达到180°则持续旋转
    while (ros::ok() && elapsed_time * rotate_speed < target_angle) {
        vel_msg.angular.z = rotate_speed; // 逆时针旋转（负值为顺时针）
        vel_pub.publish(vel_msg);

        elapsed_time += dt; // 更新已旋转时间
        ros::spinOnce();    // 处理IMU回调
        loop_rate.sleep();  // 保持10Hz频率

        // 打印旋转进度（转换为角度，每秒1次，避免刷屏）
        ROS_INFO_THROTTLE(0.5, "Rotation Progress: %.1f° / 180°", 
                          (elapsed_time * rotate_speed) * 180 / M_PI);
    }

    // 旋转完成，停止机器人
    vel_msg.angular.z = 0.0;
    vel_pub.publish(vel_msg);
    ROS_INFO("180 degrees rotation completed!");

    // 保持节点运行，持续监听IMU数据
    ros::spin();
    return 0;
}

