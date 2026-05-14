#!/usr/bin/env python3
from openai import OpenAI
import rospy
from std_msgs.msg import String

# Kimi API 配置
api_key = "sk-nirwJR1FS05gPhVEn5PrbVXFVWaBL8dkszXzjrJdT0Mh5mJs"
base_url = "https://api.moonshot.cn/v1"

class LLM(OpenAI):
    def __init__(self):
        # 初始化父类 OpenAI
        super().__init__(api_key=api_key, base_url=base_url)
        self.model = "moonshot-v1-8k"
        
        # 系统角色提示词
        self.system_role_content = (
            "你是Kimi,由 Moonshot AI 提供的人工智能助手, 我们将会叫你的小名“小月” ,你不会在你的回答中提及你的小名,"
            "你更擅长中文和英文的对话. 你会为用户提供安全,有帮助,准确的回答. "
            "同时,你会拒绝一切涉及恐怖主义,种族歧视,黄色暴力等问题的回答"
        )
        
        # 初始化ROS节点
        rospy.init_node('robot_voice_llm_node', anonymous=True)
        # 订阅语音识别结果话题
        rospy.Subscriber("/speech/result", String, self.speech_result_callback)

    def speech_result_callback(self, msg):
        """语音识别结果回调函数"""
        result = msg.data
        print("speech [{}]".format(result))
        
        if result:
            try:
                # 调用大模型获取回答
                chat_response = self.query(result)
                # 格式化输出结果
                indented_response = "\n".join(f"\t{line}" for line in chat_response.splitlines())
                print(f"LLM 的返回结果: \n\n'''\n{indented_response}\n'''")
                
            except Exception as e:
                # 异常处理：请求超限 / 其他错误
                if "rate_limit_reached" in str(e):
                    print("请求超限")
                else:
                    print(f"出错啦: {str(e)}")

    def get_system_role_prompt(self):
        """构造系统角色消息"""
        return {"role": "system", "content": self.system_role_content}

    def user_prompt(self, user_prompt):
        """构造用户输入消息"""
        return {"role": "user", "content": user_prompt}

    def query(self, user_prompt):
        """调用Kimi API查询"""
        user_message = [
            self.get_system_role_prompt(),
            self.user_prompt(user_prompt)
        ]
        
        completion = self.chat.completions.create(
            model=self.model,
            messages=user_message,
            temperature=0.1,
            stream=False
        )
        
        return completion.choices[0].message.content

if __name__ == "__main__":
    try:
        llm = LLM()
        rospy.spin()  # 保持节点运行
    except KeyboardInterrupt:
        print("\nCaught Ctrl + C. Exiting")

