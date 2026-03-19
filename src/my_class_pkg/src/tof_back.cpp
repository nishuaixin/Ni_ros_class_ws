#include <ros/ros.h>
#include <geometry_msgs/Twist.h>
#include <sensor_msgs/Range.h>

// 全局变量存储前TOF传感器距离，解决回调与主循环数据共享
double tof_distance = 1.0;

// 前TOF传感器回调函数（话题/ul/sensor2，与超声前传感器通用）
void rangeCallback2(const sensor_msgs::Range::ConstPtr& msg){
    ROS_INFO("TOF Front Distance: %f m", msg->range);
    tof_distance = msg->range;
}

int main(int argc,char **argv)
{
    ros::init(argc,argv,"tof_back");
    ros::NodeHandle nh;

    // 发布速度指令到机器人运动话题
    ros::Publisher pub = nh.advertise<geometry_msgs::Twist>("/cmd_vel", 10);
    // 订阅前TOF传感器数据（替换为/us/tof2即为纯TOF话题）
    ros::Subscriber sub_2 = nh.subscribe<sensor_msgs::Range>("/ul/sensor2", 10, rangeCallback2);

    ros::Rate loop_rate(10); // 10Hz循环频率
    geometry_msgs::Twist vel_msg;
    // 初始化前进速度：0.1m/s，无旋转
    vel_msg.linear.x = 0.1;
    vel_msg.linear.y = 0;
    vel_msg.linear.z = 0;
    vel_msg.angular.x = 0;
    vel_msg.angular.y = 0;
    vel_msg.angular.z = 0;  

    int count = 0;
    while(ros::ok())
    {
        pub.publish(vel_msg);
        ros::spinOnce();

        // 距离<0.4m且>0m触发避障（排除初始无效值）
        if(tof_distance < 0.4 && tof_distance > 0.0)
        {
            ROS_INFO("Obstacle detected! Backing up...");
            // 后退4秒（10Hz×40次）
            while(ros::ok() && count<40)
            {
                vel_msg.linear.x = -0.1;
                pub.publish(vel_msg);
                ros::spinOnce();
                loop_rate.sleep();
                count++;
            }
            // 重置计数，恢复前进
            count = 0;
            vel_msg.linear.x = 0.1;
            ROS_INFO("Back up done, resume moving forward!");
        }
        loop_rate.sleep();
    }

    // 程序退出，停止机器人
    vel_msg.linear.x = 0.0;
    pub.publish(vel_msg);
    return 0;
}

