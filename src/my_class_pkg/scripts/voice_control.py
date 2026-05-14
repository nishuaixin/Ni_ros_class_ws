#!/usr/bin/env python3
from tokenizer import Tokenizer
import rospy
from upros_message.msg import TagCommand
from std_msgs.msg import String

class VoiceControlNode:
    def __init__(self):
        # 初始化ROS节点
        rospy.init_node('tokenizer_publisher')
        
        # 初始化意图分词器
        self.tokenizer = Tokenizer()
        
        # 发布器：发布语音解析后的控制指令
        self.tag_cmd_pub = rospy.Publisher(
            '/voice_control', 
            TagCommand,
            queue_size=10
        )
        
        # 订阅器：订阅语音识别结果
        self.talker_sub = rospy.Subscriber(
            '/speech/result', 
            String,
            self.speech_result_callback
        )

    def speech_result_callback(self, msg):
        """语音识别结果回调：解析指令并发布控制命令"""
        # 从语音指令中提取字符串
        user_input = msg.data
        
        # 文本预处理
        filtered_input = self.tokenizer.pre_process(user_input)
        
        # 提取意图 + 目标（指令组合）
        intent_string = self.tokenizer.extract_intent(filtered_input)
        
        # 只发布第一个解析出来的命令
        if intent_string:  # 增加非空判断，防止越界崩溃
            cmd = TagCommand()
            cmd.intent = intent_string[0]['intent']
            cmd.target = intent_string[0]['target']
            self.tag_cmd_pub.publish(cmd)
            
            # 可选：打印日志方便调试
            rospy.loginfo(f"发布控制指令: intent={cmd.intent}, target={cmd.target}")

if __name__ == "__main__":
    try:
        node = VoiceControlNode()
        rospy.spin()
    except KeyboardInterrupt:
        rospy.loginfo("\nCaught Ctrl + C. Exiting")

