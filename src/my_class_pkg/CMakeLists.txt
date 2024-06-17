cmake_minimum_required(VERSION 3.0.2)
project(my_class_pkg)

# 编译选项（C++11 兼容 Noetic）
add_compile_options(-std=c++11)

# 查找依赖包
find_package(catkin REQUIRED COMPONENTS
  roscpp
  rospy
  std_msgs
  message_generation
  actionlib
  actionlib_msgs
  dynamic_reconfigure
  geometry_msgs
  tf2_ros
  move_base_msgs
)

# 动态参数配置文件生成规则
generate_dynamic_reconfigure_options(
  cfg/Tutorials.cfg
)

# 声明ROS消息/服务/动作
add_message_files(
  DIRECTORY msg          
  FILES MyMessage.msg    
)

add_action_files(
  DIRECTORY action
  FILES MyAction.action
)

add_service_files(
  DIRECTORY srv
  FILES MyServiceMsg.srv
)

# 生成消息/服务/动作（Noetic 正确写法）
generate_messages(
  DEPENDENCIES  
  std_msgs 
  actionlib_msgs 
  geometry_msgs
)

# catkin包配置（核心修正：删除错误的EXPORTED_TARGETS）
catkin_package(
  CATKIN_DEPENDS 
  roscpp 
  rospy 
  std_msgs 
  message_runtime  
  actionlib 
  actionlib_msgs
  dynamic_reconfigure
  geometry_msgs
  # 移除错误的 EXPORTED_TARGETS generate_messages
)

# 包含目录
include_directories(
  ${catkin_INCLUDE_DIRS}
)

# 1. 基础发布者/订阅者
add_executable(ros_publisher_node src/ros_publisher.cpp)
target_link_libraries(ros_publisher_node ${catkin_LIBRARIES})
# Noetic 正确的消息依赖目标：${PROJECT_NAME}_generate_messages
add_dependencies(ros_publisher_node ${PROJECT_NAME}_generate_messages ${catkin_EXPORTED_TARGETS})

add_executable(ros_subscriber_node src/ros_subscriber.cpp)
target_link_libraries(ros_subscriber_node ${catkin_LIBRARIES})
add_dependencies(ros_subscriber_node ${PROJECT_NAME}_generate_messages ${catkin_EXPORTED_TARGETS})

# 2. 自定义消息发布/订阅
add_executable(msg_publisher_node src/msg_publisher.cpp)
target_link_libraries(msg_publisher_node ${catkin_LIBRARIES})
add_dependencies(msg_publisher_node ${PROJECT_NAME}_generate_messages ${catkin_EXPORTED_TARGETS})

add_executable(msg_subscriber_node src/msg_subscriber.cpp) 
target_link_libraries(msg_subscriber_node ${catkin_LIBRARIES})
add_dependencies(msg_subscriber_node ${PROJECT_NAME}_generate_messages ${catkin_EXPORTED_TARGETS})

# 3. 服务端/客户端
add_executable(ros_server_node src/ros_server.cpp)
target_link_libraries(ros_server_node ${catkin_LIBRARIES})
add_dependencies(ros_server_node ${PROJECT_NAME}_generate_messages ${catkin_EXPORTED_TARGETS})

add_executable(ros_client_node src/ros_client.cpp)
target_link_libraries(ros_client_node ${catkin_LIBRARIES})
add_dependencies(ros_client_node ${PROJECT_NAME}_generate_messages ${catkin_EXPORTED_TARGETS})

# 4. 动作服务端/客户端
add_executable(ros_action_server src/ros_action_server.cpp)
target_link_libraries(ros_action_server ${catkin_LIBRARIES})
add_dependencies(ros_action_server ${PROJECT_NAME}_generate_messages ${catkin_EXPORTED_TARGETS})

add_executable(ros_action_client src/ros_action_client.cpp)
target_link_libraries(ros_action_client ${catkin_LIBRARIES})
add_dependencies(ros_action_client ${PROJECT_NAME}_generate_messages ${catkin_EXPORTED_TARGETS})

# 5. 传感器相关节点
add_executable(ros_bump_node src/ros_bump.cpp)
target_link_libraries(ros_bump_node ${catkin_LIBRARIES})

add_executable(bump_run_node src/bump_run.cpp)
target_link_libraries(bump_run_node ${catkin_LIBRARIES})

add_executable(ros_sonic_node src/ros_sonic.cpp)
target_link_libraries(ros_sonic_node ${catkin_LIBRARIES})

add_executable(tof_back_node src/tof_back.cpp)
target_link_libraries(tof_back_node ${catkin_LIBRARIES})

add_executable(ros_imu_node src/ros_imu.cpp)
target_link_libraries(ros_imu_node ${catkin_LIBRARIES})

add_executable(imu_180_node src/imu_180.cpp)
target_link_libraries(imu_180_node ${catkin_LIBRARIES})

add_executable(tag_grab_node src/tag_grab.cpp)
target_link_libraries(tag_grab_node ${catkin_LIBRARIES})

# 6. C++参数节点
add_executable(ros_param src/ros_param.cpp)
target_link_libraries(ros_param ${catkin_LIBRARIES})
add_dependencies(ros_param ${PROJECT_NAME}_generate_messages ${catkin_EXPORTED_TARGETS})

# 7. 动态参数节点（保留原有配置）
add_executable(dynamic_reconfigure_node src/dynamic_reconfigure.cpp)
add_dependencies(dynamic_reconfigure_node ${PROJECT_NAME}_gencfg ${PROJECT_NAME}_generate_messages)
target_link_libraries(dynamic_reconfigure_node ${catkin_LIBRARIES})

#############
## 安装 ##
#############
install(TARGETS 
  ros_publisher_node 
  ros_subscriber_node 
  msg_publisher_node
  msg_subscriber_node
  ros_server_node
  ros_client_node
  ros_action_server
  ros_action_client
  ros_bump_node
  bump_run_node
  ros_sonic_node
  tof_back_node
  ros_imu_node
  imu_180_node
  ros_param
  dynamic_reconfigure_node
  RUNTIME DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

# 安装消息/服务/动作文件
install(DIRECTORY msg/ srv/ action/ cfg/
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)

# 小乌龟速度动态调控节点
add_executable(ros_dynamic_speed_node src/ros_dynamic_speed.cpp)
add_dependencies(ros_dynamic_speed_node ${PROJECT_NAME}_gencfg)
target_link_libraries(ros_dynamic_speed_node ${catkin_LIBRARIES})
# C++日志节点编译规则
add_executable(ros_log src/ros_log.cpp)
target_link_libraries(ros_log ${catkin_LIBRARIES})
add_executable(ros_imu_rotate_node src/imu_rotate.cpp)
target_link_libraries(ros_imu_rotate_node ${catkin_LIBRARIES})
add_executable(ros_scan_node src/ros_scan.cpp)
target_link_libraries(ros_scan_node ${catkin_LIBRARIES})
add_executable(ros_avoid_node src/ros_avoid.cpp)
target_link_libraries(ros_avoid_node ${catkin_LIBRARIES})
add_executable(movebase_client_node src/movebase_client.cpp)
target_link_libraries(movebase_client_node ${catkin_LIBRARIES})
