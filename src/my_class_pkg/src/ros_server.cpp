#include "ros/ros.h"
// 只需包含核心的服务消息头文件，无需单独包含Request/Response
#include "my_class_pkg/MyServiceMsg.h"

// 服务回调函数：处理请求并返回响应
bool myServiceCallback(my_class_pkg::MyServiceMsgRequest& req, 
                       my_class_pkg::MyServiceMsgResponse& res)
{
  // 核心逻辑：输入值乘以2作为输出
  res.output = req.input * 2;
  
  // 修正：使用%ld匹配int64类型，避免格式化警告/错误
  ROS_INFO("Request: input = %ld, output = %ld", 
           (long int)req.input, (long int)res.output);
  return true;
}

int main(int argc, char** argv)
{
  // 初始化ROS节点
  ros::init(argc, argv, "my_service_node");
  // 创建节点句柄
  ros::NodeHandle nh;
  // 注册服务，指定服务名和回调函数
  ros::ServiceServer service = nh.advertiseService("my_service", myServiceCallback);
  
  ROS_INFO("Ready to receive service requests.");
  // 循环处理回调
  ros::spin();
  
  return 0;
}
