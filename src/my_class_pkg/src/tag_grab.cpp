#include "tf2_ros/transform_listener.h"
#include "tf2_geometry_msgs/tf2_geometry_msgs.h"
#include "geometry_msgs/TransformStamped.h"
#include "geometry_msgs/PointStamped.h"
#include "upros_message/ArmPosition.h"
#include "upros_message/TagCommand.h"
#include "std_srvs/Empty.h"
#include <ros/ros.h>

int target_tag = 0;

// 延时函数
void sleep(double second)
{
    ros::Duration(second).sleep();
}

// 语音控制指令回调
void cmd_callback(const upros_message::TagCommand::ConstPtr &msg)
{
    target_tag = msg->target;
    std::cout << "Get Tag: " << target_tag << std::endl;
}

int main(int argc, char **argv)
{
    ros::init(argc, argv, "voice_grab");
    ros::NodeHandle nh;

    // 订阅语音控制指令
    ros::Subscriber cmd_sub = nh.subscribe("/voice_control", 10, cmd_callback);
    ros::Rate rate(10);

    // 等待获取目标 tag
    while (target_tag == 0)
    {
        rate.sleep();
        ros::spinOnce();
    }

    // 根据 tag 选择对应坐标系
    std::string tag_link;
    if (target_tag == 1)
    {
        tag_link = "tag_1";
    }
    else if (target_tag == 2)
    {
        tag_link = "tag_2";
    }

    // TF 坐标变换监听
    tf2_ros::Buffer buffer;
    tf2_ros::TransformListener listener(buffer);
    ROS_INFO("tf coordinate transforming....");

    // 获取 tag 到机械臂基坐标的变换
    geometry_msgs::TransformStamped tfs_1 =
        buffer.lookupTransform("arm_base_link", tag_link, ros::Time(0), ros::Duration(100));

    // 单位转换：ROS坐标系 → 机械臂坐标系
    int x = -static_cast<int>(tfs_1.transform.translation.y * 1000);
    int y = static_cast<int>(tfs_1.transform.translation.x * 1000) + 30;
    int z = static_cast<int>(tfs_1.transform.translation.z * 1000 + 40);

    // 机械臂服务客户端
    ros::ServiceClient arm_move_open_client =
        nh.serviceClient<upros_message::ArmPosition>("/upros_arm_control/arm_pos_service_open");
    ros::ServiceClient arm_move_close_client =
        nh.serviceClient<upros_message::ArmPosition>("/upros_arm_control/arm_pos_service_close");
    ros::ServiceClient arm_zero_client =
        nh.serviceClient<std_srvs::Empty>("/upros_arm_control/zero_service");
    ros::ServiceClient arm_grab_client =
        nh.serviceClient<std_srvs::Empty>("/upros_arm_control/grab_service");

    ROS_INFO("Target X: %d, Target Y: %d, Target Z: %d", x, y, z);

    // 发送移动指令
    upros_message::ArmPosition move_srv;
    move_srv.request.x = x;
    move_srv.request.y = y;
    move_srv.request.z = z;
    arm_move_open_client.call(move_srv);

    sleep(5.0);
    // 执行抓取
    std_srvs::Empty empty_srv;
    arm_grab_client.call(empty_srv);

    sleep(5.0);
    // 机械臂归零
    arm_zero_client.call(empty_srv);

    sleep(5.0);
    ros::spin();

    return 0;
}
