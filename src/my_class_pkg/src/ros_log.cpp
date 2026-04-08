#include <ros/ros.h>

int main(int argc, char** argv) {
    // 初始化ROS节点
    ros::init(argc, argv, "ros_logging_example");
    // 创建节点句柄
    ros::NodeHandle nh;

    // 打印五级日志（DEBUG默认不显示，需开启调试模式）
    ROS_DEBUG("This is a DEBUG message.（调试信息，开发阶段使用）");
    ROS_INFO("This is an INFO message.（普通信息，提示系统状态）");
    ROS_WARN("This is a WARNING message.（警告信息，潜在问题）");
    ROS_ERROR("This is an ERROR message.（错误信息，需修复问题）");
    ROS_FATAL("This is a FATAL message.（致命错误，程序将终止）");

    // 运行ROS事件循环
    ros::spin();
    return 0;
}

