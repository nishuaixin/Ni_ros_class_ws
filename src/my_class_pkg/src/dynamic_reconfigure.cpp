#include <ros/ros.h>
// 包含动态参数头文件（编译后自动生成）
#include <dynamic_reconfigure/server.h>
#include <my_class_pkg/TutorialsConfig.h>

// 动态参数回调函数：参数更新时自动执行
void callback(my_class_pkg::TutorialsConfig &config, uint32_t level)
{
   ROS_INFO("Reconfigure Request: %d %f %s %s %d",
           config.int_param, config.double_param,
           config.str_param.c_str(),
           config.bool_param?"True":"False",
           config.size);
}

int main(int argc, char **argv)
{
   ros::init(argc, argv, "dynamic_tutorials");
   // 创建动态参数服务端
   dynamic_reconfigure::Server<my_class_pkg::TutorialsConfig> server;
   dynamic_reconfigure::Server<my_class_pkg::TutorialsConfig>::CallbackType f;

   // 绑定回调函数
   f = boost::bind(&callback, _1, _2);
   server.setCallback(f);

   ROS_INFO("Spinning node");
   ros::spin();
   return 0;
}

