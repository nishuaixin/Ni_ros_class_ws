#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from openai import OpenAI
import rospy
from std_msgs.msg import String
import re
import time

API_KEY = "sk-nirwJR1FS05gPhVEn5PrbVXFVWaBL8dkszXzjrJdT0Mh5mJs"
BASE_URL = "https://api.moonshot.cn/v1"
MODEL = "moonshot-v1-8k"

class VoiceChatRobot:
    def __init__(self):
        self.client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
        self.history = [{"role": "system", "content": "回答简洁自然，只用中文，不要格式符号。"}]
        
        # 🔥 防卡死：加冷却，防止连续触发
        self.last_call_time = 0
        self.cooldown = 1.5  # 1.5秒内只响应一次

        rospy.init_node("voice_chat_robot", anonymous=True)
        self.sub1 = rospy.Subscriber("/speech/result", String, self.callback)
        self.tts_pub = rospy.Publisher("/talk", String, queue_size=10)

        rospy.loginfo("=====================================")
        rospy.loginfo("✅ 终极稳跑版：连续对话不卡死")
        rospy.loginfo("=====================================")

    # 清理文字，避免TTS报错
    def clean_text(self, text):
        text = re.sub(r'[*\n\rs:：]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def ask_llm(self, text):
        try:
            self.history.append({"role": "user", "content": text})
            resp = self.client.chat.completions.create(
                model=MODEL,
                messages=self.history,
                temperature=0.1
            )
            answer = resp.choices[0].message.content.strip()
            answer = self.clean_text(answer)
            self.history.append({"role": "assistant", "content": answer})
            
            # 限制历史长度，防止溢出
            if len(self.history) > 11:
                self.history = [self.history[0]] + self.history[-10:]
            return answer
        except Exception as e:
            return "我没听清，请再讲一次"

    # 🔥 核心：带防抖、防重复触发
    def callback(self, msg):
        now = time.time()
        if now - self.last_call_time < self.cooldown:
            return  # 冷却中，直接忽略
        
        user_text = msg.data.strip()
        if len(user_text) < 2:
            return  # 太短，忽略
        
        # 记录触发时间
        self.last_call_time = now

        rospy.loginfo(f"\n🗣️ 你：{user_text}")
        answer = self.ask_llm(user_text)
        rospy.loginfo(f"✅ AI：{answer}")
        self.tts_pub.publish(String(answer))

if __name__ == "__main__":
    try:
        robot = VoiceChatRobot()
        rospy.spin()
    except KeyboardInterrupt:
        rospy.loginfo("退出")
