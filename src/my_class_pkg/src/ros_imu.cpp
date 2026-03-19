#include <ros/ros.h>
#include <sensor_msgs/Imu.h>

void imu_callback(const sensor_msgs::Imu::ConstPtr& imu_msg) {
    // 获取加速度、角速度、姿态四元数数据
    geometry_msgs::Vector3 linear_acceleration = imu_msg->linear_acceleration;
    geometry_msgs::Vector3 angular_velocity = imu_msg->angular_velocity;
    geometry_msgs::Quaternion orientation = imu_msg->orientation;

    // 打印IMU全量数据
    ROS_INFO("Linear acceleration: x=%.2f, y=%.2f, z=%.2f m/s²", 
             linear_acceleration.x, linear_acceleration.y, linear_acceleration.z);
    ROS_INFO("Angular velocity: x=%.2f, y=%.2f, z=%.2f rad/s", 
             angular_velocity.x, angular_velocity.y, angular_velocity.z);
    ROS_INFO("Orientation: x=%.2f, y=%.2f, z=%.2f, w=%.2f", 
             orientation.x, orientation.y, orientation.z, orientation.w);
    ROS_INFO("----------------------------------------");
}

int main(int argc, char** argv) {
    // 初始化ROS节点
    ros::init(argc, argv, "imu_listener");
    ros::NodeHandle nh;

    // 订阅IMU传感器数据话题
    ros::Subscriber imu_sub = nh.subscribe<sensor_msgs::Imu>("/imu/data", 10, imu_callback);

    // 循环等待回调
    ros::spin();
    return 0;
}

