cmake_minimum_required(VERSION 3.0.2)
project(my_class_pkg)

# 编译选项（C++11 兼容 Noetic）
add_compile_options(-std=c++11)

# 查找依赖包（核心：必须包含 message_generation）
find_package(catkin REQUIRED COMPONENTS
  roscpp
  rospy
  std_msgs
  message_generation
  actionlib
  actionlib_msgs
)

################################################
## 声明ROS消息/服务/动作 ##
################################################
# 声明.msg文件（路径：msg/MyMessage.msg）
add_message_files(
  DIRECTORY msg          # 指定.msg文件所在目录（若.msg在根目录则删除此行）
  FILES MyMessage.msg    # 你的自定义消息文件名
)

add_action_files(
  DIRECTORY action
  FILES MyAction.action
)

add_service_files(
  DIRECTORY srv
  FILES MyServiceMsg.srv
)
# 生成消息（依赖std_msgs，若.msg无依赖可删除）
generate_messages(
  DEPENDENCIES  actionlib_msgs
  std_msgs
)

###################################
## catkin包配置（Noetic 兼容版） ##
###################################
catkin_package(
  # INCLUDE_DIRS include       # 若有自定义头文件目录需打开
  # LIBRARIES my_class_pkg     # 若有自定义库需打开
  CATKIN_DEPENDS roscpp rospy std_msgs message_runtime  actionlib actionlib_msgs  # 补全运行依赖
  # 移除不兼容的 EXPORTED_TARGETS generate_messages_cpp
)

###########
## 编译 ##
###########
# 包含目录
include_directories(
  # include                   # 若有自定义头文件目录需打开
  ${catkin_INCLUDE_DIRS}
)

# 1. 基础发布者节点
add_executable(ros_publisher_node src/ros_publisher.cpp)
target_link_libraries(ros_publisher_node ${catkin_LIBRARIES})
# 关键：添加消息生成依赖（Noetic 正确写法）
add_dependencies(ros_publisher_node ${${PROJECT_NAME}_EXPORTED_TARGETS} ${catkin_EXPORTED_TARGETS})

# 2. 基础订阅者节点
add_executable(ros_subscriber_node src/ros_subscriber.cpp)
target_link_libraries(ros_subscriber_node ${catkin_LIBRARIES})
add_dependencies(ros_subscriber_node ${${PROJECT_NAME}_EXPORTED_TARGETS} ${catkin_EXPORTED_TARGETS})

# 3. 自定义消息发布者节点（核心）
add_executable(msg_publisher_node src/msg_publisher.cpp)
target_link_libraries(msg_publisher_node ${catkin_LIBRARIES})
add_executable(msg_subscriber_node src/msg_subscriber.cpp) 
target_link_libraries(msg_subscriber_node ${catkin_LIBRARIES})

add_executable(ros_server_node src/ros_server.cpp)
target_link_libraries(ros_server_node ${catkin_LIBRARIES})
add_executable(ros_client_node src/ros_client.cpp)
target_link_libraries(ros_client_node ${catkin_LIBRARIES})

add_executable(ros_action_server src/ros_action_server.cpp)
target_link_libraries(ros_action_server ${catkin_LIBRARIES})
add_executable(ros_action_client src/ros_action_client.cpp)
target_link_libraries(ros_action_client ${catkin_LIBRARIES})

# 关键：确保节点编译依赖消息生成（Noetic 必加）
add_dependencies(msg_publisher_node ${${PROJECT_NAME}_EXPORTED_TARGETS} ${catkin_EXPORTED_TARGETS})

#############
## 安装（可选） ##
#############
install(TARGETS ros_publisher_node ros_subscriber_node msg_publisher_node
  RUNTIME DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

# 可选：安装.msg文件到share目录（兜底方案，确保rostopic能识别）
install(DIRECTORY msg/
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/msg
)
