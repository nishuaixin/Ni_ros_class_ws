#include <ros/ros.h>
#include <move_base_msgs/MoveBaseAction.h>
#include <actionlib/client/simple_action_client.h>
#include <tf2/LinearMath/Quaternion.h>

using namespace std;
typedef actionlib::SimpleActionClient<move_base_msgs::MoveBaseAction> MoveBaseClient;

int main(int argc, char **argv) {
    ros::init(argc, argv, "send_goals_node");
    MoveBaseClient ac("move_base", true);
    ac.waitForServer();

    // 目标点1
    move_base_msgs::MoveBaseGoal goal;
    goal.target_pose.header.frame_id = "map";
    goal.target_pose.pose.position.x = 1.0;
    goal.target_pose.pose.position.y = 0.0;
    goal.target_pose.pose.orientation.w = 1.0;

    ac.sendGoal(goal);
    ac.waitForResult();
    ROS_INFO("到达点1");

    // 回原点
    goal.target_pose.pose.position.x = 0;
    goal.target_pose.pose.position.y = 0;
    ac.sendGoal(goal);
    ac.waitForResult();
    ROS_INFO("回到起点");

    return 0;
}
