# Ni_ros_class_ws
ROS 实验一专属工作空间，包含 Service（服务）、Action（动作）等核心示例。

## 快速克隆（雨课堂提供此指令）
```bash
git clone git@github.com:nishuaixin/Ni_ros_class_ws.git ~/Ni_ros_class_ws
```

## 编译工程
```bash
cd ~/Ni_ros_class_ws
catkin_make
source devel/setup.bash
```

## 启动指令
### 1. Service 服务示例
- 启动服务端：`rosrun my_class_pkg ros_server_node`
- 启动客户端：`rosrun my_class_pkg ros_client_node`

### 2. Action 动作示例（Python 版）
- 启动服务器：`rosrun my_class_pkg ros_action_server.py`
- 启动客户端：`rosrun my_class_pkg ros_action_client.py`

### 3. 话题发布/订阅示例
- 启动发布者：`rosrun my_class_pkg msg_publisher_node`
- 启动订阅者：`rosrun my_class_pkg msg_subscriber_node`
