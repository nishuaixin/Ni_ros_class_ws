#include <ros/ros.h>
#include <sensor_msgs/LaserScan.h>
#include <geometry_msgs/Twist.h>

ros::Publisher cmdVelPub;
float firstRange, lastRange;

void scanCallback(const sensor_msgs::LaserScan::ConstPtr &scan)
{
    int num_points = (scan->angle_max - scan->angle_min) / scan->angle_increment;
    // 激光雷达数组中间的元素为最前方的激光雷达数据
    firstRange = scan->ranges[num_points/2];
    lastRange = scan->ranges[num_points/2 + 1];
    // 取2个数求平均值
    float meanRange = (firstRange + lastRange) / 2.0;
    ROS_INFO_STREAM("Mean range: " << meanRange);

    geometry_msgs::Twist cmdVelMsg;
    //前方距离小于2米停下
    if (meanRange <= 2.0)
    {
        cmdVelMsg.linear.x = 0.0;
    }
    //否则一直以0.3m/s前进
    else
    {
        cmdVelMsg.linear.x = 0.3;
    }
    cmdVelPub.publish(cmdVelMsg);
}

int main(int argc, char **argv)
{
    ros::init(argc, argv, "laser_scan_listener");
    ros::NodeHandle n;
    ros::Subscriber sub = n.subscribe("/scan", 1000, scanCallback);
    cmdVelPub = n.advertise<geometry_msgs::Twist>("/cmd_vel", 10);
    ros::spin();
    return 0;
}

