#include <ros/ros.h>
#include <sensor_msgs/LaserScan.h>

void scanCallback(const sensor_msgs::LaserScan::ConstPtr &scan) {
    // 获取激光点的个数
    int num_points = (scan->angle_max - scan->angle_min) / scan->angle_increment;
    ROS_INFO_STREAM("Number of points: " << num_points);

    // 获取数组中第一个激光点的距离，代表着弧度中的 -pi
    float first_range = scan->ranges[0];
    ROS_INFO_STREAM("First range: " << first_range);

    // 获取数组中最后一个激光点的距离，代表着弧度中的 pi
    float last_range = scan->ranges[num_points - 1];
    ROS_INFO_STREAM("Last range: " << last_range);

    // 获取数组中间激光点的距离，代表着弧度中的 0
    float half_range = scan->ranges[num_points/2];
    ROS_INFO_STREAM("Half range: " << half_range );

    // 获取1/4激光点的距离，代表着弧度中的 -pi/2
    float left_range = scan->ranges[num_points/4];
    ROS_INFO_STREAM("Left range: " << left_range );

    // 获取3/4激光点的距离，代表着弧度中的 pi/2
    float right_range = scan->ranges[num_points / 4 * 3];
    ROS_INFO_STREAM("Right range: " << right_range );
}

int main(int argc, char **argv) {
    // 初始化ROS节点
    ros::init(argc, argv, "laser_scan_listener");
    // 创建节点句柄
    ros::NodeHandle n;
    // 订阅/scan话题
    ros::Subscriber sub = n.subscribe("/scan", 1000, scanCallback);
    // 循环等待回调函数
    ros::spin();
    return 0;
}

