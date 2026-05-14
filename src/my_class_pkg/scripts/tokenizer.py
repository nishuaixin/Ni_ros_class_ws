#!/usr/bin/env python3
import jieba
import re
import rospy
from upros_message.msg import TagCommand

class Tokenizer:
    def __init__(self):
        print("Init Tokenizer!!!!")
        # 定义停用词表
        self.stopwords = set(['的', '是', '啊'])
        
        # 自定义模板
        self.json_template = {
            "intent": "",
            "target": -1
        }
        
        # 中文文字对应数字的字典
        self.chinese_to_arabic = {
            '零': 0,
            '一': 1,
            '二': 2,
            '三': 3,
            '四': 4,
            '五': 5,
            '六': 6,
            '七': 7,
            '八': 8,
            '九': 9,
            '十': 10,
            '百': 100,
            '千': 1000,
            '万': 10000,
            '亿': 100000000
        }
        
        # 水果中英文对照字典
        self.fruit_name_mapping = {
            '苹果': 'apple',
            '香蕉': 'banana',
            '橙子': 'orange',
            '橘子': 'orange',
            '草莓': 'strawberry',
            '西瓜': 'watermelon',
            '菠萝': 'pineapple',
        }

    # 通过字典从汉字中提取数字
    def chinese_to_arabic_number(self, chinese_num):
        total = 0
        r = 1
        for i in range(len(chinese_num) - 1, -1, -1):
            val = self.chinese_to_arabic[chinese_num[i]]
            if val == 10000 or val == 100000000:
                if r < val:
                    r *= val
                else:
                    r //= val
            else:
                total += r * val
        return total

    # 将代表数字的中文汉字替换成阿拉伯数字
    def replace_chinese_numbers(self, text):
        pattern = re.compile(r'零?[一二三四五六七八九十百千万亿]+')
        matches = pattern.findall(text)
        for match in matches:
            arabic_number = self.chinese_to_arabic_number(match)
            text = text.replace(match, str(arabic_number))
        return text

    # 命令字符串预处理
    def pre_process(self, text):
        # 去除空格
        text = re.sub(r'\s+', '', text)
        # 中文数字转阿拉伯数字
        text = self.replace_chinese_numbers(text)
        # 转小写
        text = text.lower()
        # 分词
        tokens = list(jieba.lcut(text))
        # 去除停用词
        filtered_tokens = [token for token in tokens if token not in self.stopwords]
        # 水果名替换
        for i, token in enumerate(filtered_tokens):
            if token in self.fruit_name_mapping:
                filtered_tokens[i] = self.fruit_name_mapping[token]
        return filtered_tokens

    # 从字符串命令中提取意图和 ID
    def extract_intent(self, tokens):
        intents = {
            'go_to': ['移动', '去', '前往'],
            'pick': ['抓取', '拿起', '抓', '拿', '取'],
            'release': ['放下', '放到', '放', '放置']
        }
        result = []
        i = 0
        while i < len(tokens):
            found = False
            for intent, triggers in intents.items():
                if tokens[i] in triggers:
                    # 寻找后面的数字
                    j = i + 1
                    while j < len(tokens) and not (tokens[j].isdigit() or tokens[j] == '号'):
                        j += 1
                    # 提取数字
                    target_index = -1
                    if j < len(tokens):
                        for k in range(j, len(tokens)):
                            if tokens[k].isdigit():
                                target_index = int(tokens[k])
                                break
                    # 构造结果
                    json_obj = self.json_template.copy()
                    json_obj['intent'] = intent
                    json_obj['target'] = target_index
                    result.append(json_obj)
                    i = j
                    found = True
                    break
            if not found:
                i += 1
        return result

    # 对外接口：从文本获取意图
    def get_intent_from_text(self, text):
        filtered_input = self.pre_process(text)
        intents = self.extract_intent(filtered_input)
        return intents

if __name__ == '__main__':
    tokenizer = Tokenizer()
    user_input = input("请输入指令: ")
    # 预处理 + 提取意图
    intent_result = tokenizer.get_intent_from_text(user_input)
    print("Output:", intent_result)
