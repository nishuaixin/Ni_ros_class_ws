#include <ros/ros.h>
#include <actionlib/server/simple_action_server.h>
#include <my_class_pkg/MyActionAction.h>

class MyActionServer {
protected:
    ros::NodeHandle nh_;
    // 修正：as_ 变量名和类型之间加空格（规范写法）
    actionlib::SimpleActionServer<my_class_pkg::MyActionAction> as_;
    // 修正1：std::string 和 action_name_ 之间加空格
    std::string action_name_;
    my_class_pkg::MyActionFeedback feedback_;
    my_class_pkg::MyActionResult result_;

public:
    // 构造函数：初始化 Action 服务器
    MyActionServer(std::string name) :
        as_(nh_, name, boost::bind(&MyActionServer::executeCB, this, _1), false),
        action_name_(name) 
    {
        as_.start(); // 启动 Action 服务器
    }

    ~MyActionServer(void) {}

    // 核心回调函数：处理客户端的目标请求
    void executeCB(const my_class_pkg::MyActionGoalConstPtr& goal) {
        // 修正2：拼写错误 Rater→Rate，且声明变量名 r
        ros::Rate r(1); // 1Hz 循环频率
        bool success = true;

        // 模拟耗时任务（循环10次，每次进度+10%）
        for (int i = 1; i <= 10; i++) {
            // 检查是否被客户端取消
            if (as_.isPreemptRequested() || !ros::ok()) {
                ROS_INFO("%s: Preempted", action_name_.c_str());
                as_.setPreempted(); // 标记任务被取消
                success = false;
                break;
            }

            // 更新反馈（进度值）并发布
            feedback_.progress = i * 10;
            ROS_INFO("%s: Executing, progress = %.1f%%", action_name_.c_str(), feedback_.progress);
            as_.publishFeedback(feedback_);

            // 修正3：变量 r 已声明，可正常调用 sleep()
            r.sleep();
        }

        // 任务完成，发送最终结果
        if (success) {
            result_.success = true;
            ROS_INFO("%s: Succeeded", action_name_.c_str());
            as_.setSucceeded(result_); // 标记任务成功
        }
    }
};

int main(int argc, char** argv) {
    // 初始化 ROS 节点
    ros::init(argc, argv, "my_action_server");
    // 创建 Action 服务器实例（服务名：my_action）
    MyActionServer server("my_action");
    // 循环处理回调
    ros::spin();

    return 0;
}
