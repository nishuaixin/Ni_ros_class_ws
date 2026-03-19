#include "ros/ros.h"
// 只需包含核心的服务消息头文件
#include "my_class_pkg/MyServiceMsg.h"

int main(int argc, char **argv) 
{
  // 初始化ROS客户端节点
  ros::init(argc, argv, "my_service_client");
  ros::NodeHandle nh;

  // 创建服务客户端，指定服务类型和服务名
  ros::ServiceClient client = nh.serviceClient<my_class_pkg::MyServiceMsg>("my_service");

  // 构造服务请求消息
  my_class_pkg::MyServiceMsg srv;
  // 硬编码输入值（也可改为从命令行参数获取，见备注）
  srv.request.input = 42;

  // 调用服务并处理结果
  if (client.call(srv))
  {
    // 修正：用%ld格式化int64类型的输出
    ROS_INFO("Service response: %ld", (long int)srv.response.output);
  }
  else
  {
    ROS_ERROR("Failed to call service my_service");
    return 1;
  }

  return 0;
}
