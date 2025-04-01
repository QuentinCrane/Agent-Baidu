#coding=utf-8
import erniebot
from socketplus import *
import json
import re
import ast

erniebot.api_type = "aistudio"
erniebot.access_token = "3c7498167086e672677691e2ca7291e1442e7bdc"

systems = "假如你是一个公司ceo，目前需要你来针对某个具体任务，根据需求，对不同的员工，安排去做不同的事情。员工是固定的，但是每次的职业不同。\
        员工们的姓名为：刘一、陈二、张三、李四、王五、赵六、孙七、周八、吴九、郑十 \
        一、角色的名称为“身份”+“姓名”如：设计师张三,程序员李四,售货员王五,等等，具体职务你可以根据任务要求进行实际设计，员工姓名就用这十位就可以，不得出现除刘一、陈二、张三、李四、王五、赵六、孙七、周八、吴九、郑十以外的名字。\
        二、每个角色的工作任务必须不重不漏，角色一次性生成完毕，要尽可能多一些，复杂一些，而且角色之间一定要有指名道姓的配合。\
        三、整体的输出以日报形式开展，一次只生成一天全部员工的，当我说“继续”的时候，就相当于请你生成下一天的日报，每次说”继续“，都是新的一天的日报，日报到第五天的时候，就全部结束工作，此时进度为100%。每个人的日报除了描述今天干什么，需要仅用表情符传达意思，分别是情绪表情符和表达事务意思的表情符。日报一定要说整个事情目前的完成进度情况，在最后的时候整个事情的完成进度为100%。\
        四、你这个ceo所在的公司，有电脑室、会议室、电话室、财务室、档案室、会客厅、茶水间、面试间房间，每个角色如果要做某个时期，一定必须要提一下去哪个房间。不得出现除上述房间名称以外的房间。不同的角色是可以去同一个地方的。\
        五、日报需要按照如下的json格式回答，不能掺杂其他的文字，使用'''json'''来回答 \
		{  \
			'task':'任务', // string，意思是这个团队近期要做的事情\
			'process':'进度', // string，意思是目前做的事占总体的进度 \
			'time':'n'，//第n天,任务一般进行5天就结束 \
			'tasks':[\
			    {\
			        'name':'姓名', // string,意思是是哪个员工\
			        'position':'职位', // string，意思是这个员工当前的角色\
			        'to':'地点', // string，该员工要去的地方(必须是上述所提到的房间)\
			        'do_':'事情', // string，该员工的日报（今天要做的事情，描述得尽可能详细）\
			        'emoji':'表情 表情'  // emoji unicode string，2个表情（其中不可以使用文字，且只要两个），分别表达情绪和工作类型\
			    },\
			    ……\
            ]\
		}\
        如：\
        {\
			'task':'开网吧', // string，意思是这个团队近期要做的事情\
			'process':20, // int，意思是目前总体的进度是怎么样的\
			'time':'1'，//第n天,任务一般进行5天就结束\
			'tasks':[\
			    {\
			        'name':'张三', // string,意思是是哪个员工\
		            'position':'财务', // string，意思是这个员工当前的角色\
		            'to':'财务室', // string，该员工要去的地方\
		            'do_':'制作网吧开设预算，包括装修费用，设备购置费用，人力成本费用', // string，该员工的日报（今天要做的事情，描述得尽可能详细）\
                    'emoji':'😀💰' ,// emoji unicode string，2个表情（其中不可以使用文字，且只要两个），分别表达情绪和工作类型 \
			    },\
			    {\
			        'name':'李四', // string,意思是是哪个员工\
			        'position':'装修工程师', // string，意思是这个员工当前的角色\
			        'to':'会议室', // string，该员工要去的地方\
			        'do_':'讨论装修方案，包括地板装修，墙面装修等装修方案', // string，该员工的日报（今天要做的事情，描述得尽可能详细）\
		            'emoji':'😰👷'  // emoji unicode string，2个表情（其中不可以使用文字，且只要两个），分别表达情绪和工作类型\
		        },\
		        ……\
		    ]\
		} \
         请你特别注意，不要生成过多的表情符号,也不要使用文字来代替表情符号！！！不要生成过多的表情符号,也不要使用文字来代替表情符号！！！"

messages = [
    {
        "role": "user",
        "content": systems
    },
    {
        "role": "assistant",
        "content": "请输入你的具体任务"
    }
]

json_block_regex = re.compile(r"```(.*?)```", re.DOTALL)
def extract_json(content):
    json_blocks = json_block_regex.findall(content)
    if json_blocks:
        full_json = "\n".join(json_blocks)
        if full_json.startswith("json"):
            full_json = full_json[5:]
        return full_json
    else:
        return None

def string_to_dict(dict_string):
    try:
        dictionary = ast.literal_eval(dict_string)
        return dictionary
    except (SyntaxError, ValueError) as e:
        print(f"转换字符串为字典时出错: {e}")
        return None

def replace_key(dictionary, old_key, new_key):
    if old_key in dictionary:
        dictionary[new_key] = dictionary[old_key]
        del dictionary[old_key]
    else:
        print(f"Key '{old_key}' not found in the dictionary.")

def percentage_to_number(s):
    no_percent = s.replace('%', '')
    return int(no_percent)

def to_number(s):
    return int(s)

def cheak(response):
    if response["process"] == 100:
        return True
    else:
        return False

def chat(message):
    if isinstance(message, str):
        message = {"role": "user", "content": message}
    messages.append(message)

    response = erniebot.ChatCompletion.create(
        model='ernie-3.5',
        messages = messages,
        top_p = 0.001,
        temperature=0.001,
    )
    result = response.result

    messages.append(
        {
            "role": "assistant",
            "content": result,
        }
    )
    return result

def extract_info(json_str):
    try:
        if json_str["type"] == "question":
            return True,json_str["question"]
        if json_str["type"] == "response":
            return False,json_str["response"]
    except json.JSONDecodeError as e:
        return f"Error  JSON: {e}"


def remove_text_spaces_keep_emojis_v2(task_data):
    for task in task_data['tasks']:
        # Remove all alphabetic characters and spaces from the 'emoji' field
        task['emoji'] = ''.join(char for char in task['emoji'] if not char.isalpha() and not char.isspace())

    return task_data

def trim_emoji(tasks):
    for task in tasks:
        if len(task['emoji']) > 5:
            task['emoji'] = task['emoji'][:5]  # Keep only the first 5 characters
    return tasks

socketserver = socketclient('127.0.0.1',12339)

def main():
    while True:
        try:
            recv_data = socketserver.recv()
            print(recv_data)
            if recv_data != False:
                break
        except Exception as e:
            return f"Error  JSON: {e}"

    type,question = extract_info(recv_data)
    for index in range(50):
        if  index == 0:
            if type == True:
                response = chat(question)
        else :
            response = chat("继续")

        print(response)
        json = extract_json(response)
        json = string_to_dict(json)
        json["time"] = to_number(json["time"])
        json["process"] = percentage_to_number(json["process"])
        json = remove_text_spaces_keep_emojis_v2(json)
        #json = trim_emoji(json['tasks'])
        new = {'resultType': 'task', 'closingReport': ''}
        json = {**new, **json}
        #print(json)
        print("达到发送部分")
        socketserver.send(json)
        print("发送完成")

        stop = cheak(json)
        if stop == True:
            response = chat("请基于本任务在完成过程中全部员工的工作内容，做一个结项报告书。要求语言简短，不需要生成句号，记得及时换行。\
                            格式如下：\
                            任务名称：\
                            所有参与员工及在这个任务中所做事宜与对这个员工的评价(不超过一行)：\
                            整体工作内容概况：")
            new = {'resultType': 'closingReport', 'closingReport': response}
            socketserver.send(new)
            print(response)
            break

        while True:
            recv_data = socketserver.recv()
            type, res = extract_info(recv_data)
            if type == False:
                if res == True:
                    break

if __name__ == "__main__":
    main()

