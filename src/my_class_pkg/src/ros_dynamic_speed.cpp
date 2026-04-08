#include <ros/ros.h>
#include <dynamic_reconfigure/server.h>
#include <my_class_pkg/TutorialsConfig.h>
#include <geometry_msgs/Twist.h>

// 全局变量：存储机器人速度
double robot_speed = 0;

// 动态参数回调函数：更新速度
void callback(my_class_pkg::TutorialsConfig &config, uint32_t level)
{
    ROS_INFO("Reconfigure Request: %d %f %s %s %d",
            config.int_param, config.double_param,
            config.str_param.c_str(),
            config.bool_param?"True":"False",
            config.size);
    robot_speed = config.double_param; // 动态参数赋值给速度
}

int main(int argc, char **argv)
{
    ros::init(argc, argv, "dynamic_tutorials");
    ros::NodeHandle nh; // 修复原文档语法错误：ros::NodeHandle(nh) → ros::NodeHandle nh;

    // 创建动态参数服务端
    dynamic_reconfigure::Server<my_class_pkg::TutorialsConfig> server;
    dynamic_reconfigure::Server<my_class_pkg::TutorialsConfig>::CallbackType f;
    f = boost::bind(&callback, _1, _2);
    server.setCallback(f);

    // 创建发布者：发布速度指令到小乌龟话题/turtle1/cmd_vel
   // ros::Publisher cmd_pub_ = nh.advertise<geometry_msgs::Twist>("/turtle1/cmd_vel", 10);
    // 改为实体机器人话题
ros::Publisher cmd_pub_ = nh.advertise<geometry_msgs::Twist>("/cmd_vel", 10);
    ros::Rate rate(10); // 10Hz发布频率

    ROS_INFO("Spinning node");
    while(ros::ok())
    {
        geometry_msgs::Twist cmd_vel;
        cmd_vel.linear.x = robot_speed; // 线速度X方向为动态参数值
        cmd_vel.angular.z = 0; // 角速度为0，仅直线运动
        cmd_pub_.publish(cmd_vel); // 发布速度指令

        ros::spinOnce();
        rate.sleep();
    }
    return 0;
}

