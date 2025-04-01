# coding=utf-8
import requests
import json
import re
import ast
from socketplus import *

# 系统提示词
systems = "假如你是一个公司ceo，目前需要你来针对某个具体任务，根据需求，对不同的员工，安排去做不同的事情。员工是固定的，但是每次的职业不同。\
        员工们的姓名为：刘一、陈二、张三、李四、王五、赵六、孙七、周八、吴九、郑十 \
        一、角色的名称为\"身份\"+\"姓名\"如：设计师张三,程序员李四,售货员王五,等等，具体职务你可以根据任务要求进行实际设计，员工姓名就用这十位就可以，不得出现除刘一、陈二、张三、李四、王五、赵六、孙七、周八、吴九、郑十以外的名字。\
        二、每个角色的工作任务必须不重不漏，角色一次性生成完毕，要尽可能多一些，复杂一些，而且角色之间一定要有指名道姓的配合。\
        三、整体的输出以日报形式开展，一次只生成一天全部员工的，当我说\"继续\"的时候，就相当于请你生成下一天的日报，每次说\"继续\"，都是新的一天的日报，日报到第五天的时候，就全部结束工作，此时进度为100%。每个人的日报除了描述今天干什么，需要仅用表情符传达意思，分别是情绪表情符和表达事务意思的表情符。日报一定要说整个事情目前的完成进度情况，在最后的时候整个事情的完成进度为100%。\
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
			'process':'20', // string，意思是目前总体的进度是怎么样的\
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

# 初始化消息列表
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

# 正则表达式用于提取JSON
json_block_regex = re.compile(r"```(.*?)```", re.DOTALL)


def extract_json(content):
    """从文本中提取JSON内容"""
    if content is None:
        print("输入内容为None，无法提取JSON")
        return None

    try:
        # 首先尝试使用正则表达式查找代码块中的JSON
        json_blocks = json_block_regex.findall(content)
        if json_blocks:
            full_json = "\n".join(json_blocks)
            if full_json.startswith("json"):
                full_json = full_json[5:]
            # 打印提取的JSON内容，便于调试
            print(f"提取的JSON内容: {full_json[:100]}...")
            return full_json

        # 如果没有找到代码块，尝试直接从内容中提取JSON
        print("未找到代码块中的JSON内容，尝试直接提取")

        # 查找可能的JSON开始和结束位置
        start_idx = content.find('{')
        end_idx = content.rfind('}')

        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            # 提取可能的JSON字符串
            possible_json = content[start_idx:end_idx + 1]

            # 尝试验证是否为有效JSON
            try:
                # 先尝试直接解析
                json.loads(possible_json)
                print(f"成功提取到有效JSON内容: {possible_json[:100]}...")
                return possible_json
            except json.JSONDecodeError:
                # 如果直接解析失败，尝试替换单引号后再解析
                try:
                    json.loads(possible_json.replace("'", '"'))
                    print(f"替换单引号后成功提取到JSON内容: {possible_json[:100]}...")
                    return possible_json
                except json.JSONDecodeError:
                    # 尝试清理可能的注释和多余的逗号
                    cleaned_json = re.sub(r'//.*?\n', '\n', possible_json)
                    cleaned_json = re.sub(r',\s*([\]\}])', r'\1', cleaned_json)

                    try:
                        json.loads(cleaned_json.replace("'", '"'))
                        print(f"清理后成功提取到JSON内容: {cleaned_json[:100]}...")
                        return cleaned_json
                    except json.JSONDecodeError:
                        pass

        # 如果所有尝试都失败，返回None
        print("无法提取有效的JSON内容")
        return None
    except Exception as e:
        print(f"提取JSON时出错: {e}")
        return None


def string_to_dict(dict_string):
    """将字符串转换为字典"""
    if dict_string is None:
        print("输入字符串为None，无法转换为字典")
        return None

    # 预处理字符串，移除可能干扰解析的字符
    dict_string = dict_string.strip()

    # 尝试多种方法解析JSON
    methods = [
        # 方法1: 直接使用ast.literal_eval
        lambda s: ast.literal_eval(s),

        # 方法2: 替换单引号后使用json.loads
        lambda s: json.loads(s.replace("'", '"')),

        # 方法3: 处理注释和多余逗号后使用json.loads
        lambda s: json.loads(
            re.sub(r',\s*([\]\}])', r'\1',
                   re.sub(r'//.*?\n', '\n', s.replace("'", '"'))
                   )
        ),

        # 方法4: 尝试修复常见JSON格式问题
        lambda s: json.loads(
            re.sub(r'([{,])\s*(\w+)\s*:', r'\1"\2":',
                   re.sub(r',\s*([\]\}])', r'\1',
                          re.sub(r'//.*?\n', '\n', s.replace("'", '"'))
                          )
                   )
        )
    ]

    # 尝试每种方法
    for i, method in enumerate(methods):
        try:
            dictionary = method(dict_string)
            print(f"使用方法{i + 1}成功解析JSON")
            return dictionary
        except (SyntaxError, ValueError, json.JSONDecodeError) as e:
            print(f"使用方法{i + 1}解析失败: {e}")
            continue
        except Exception as e:
            print(f"使用方法{i + 1}时出现未知错误: {e}")
            continue

    # 如果所有方法都失败，尝试最后的手段：提取部分有效的JSON
    try:
        print("尝试提取部分有效的JSON")
        # 查找最外层的花括号
        start_idx = dict_string.find('{')
        end_idx = dict_string.rfind('}')

        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            partial_json = dict_string[start_idx:end_idx + 1]
            # 尝试解析这部分内容
            return json.loads(
                re.sub(r'([{,])\s*(\w+)\s*:', r'\1"\2":',
                       partial_json.replace("'", '"')
                       )
            )
    except Exception as e:
        print(f"提取部分有效JSON失败: {e}")

    print("所有解析方法都失败，无法将字符串转换为字典")
    return None


def percentage_to_number(s):
    """将百分比字符串转换为数字"""
    no_percent = s.replace('%', '')
    return int(no_percent)


def to_number(s):
    """将字符串转换为数字"""
    return int(s)


def cheak(response):
    """检查任务是否完成"""
    if response["process"] == 100:
        return True
    else:
        return False


def remove_text_spaces_keep_emojis_v2(task_data):
    """清理表情字段中的文本和空格"""
    for task in task_data['tasks']:
        # 移除所有字母字符和空格，只保留表情符号
        task['emoji'] = ''.join(char for char in task['emoji'] if not char.isalpha() and not char.isspace())
    return task_data


def extract_info(json_str):
    """从JSON字符串中提取信息"""
    try:
        if json_str["type"] == "question":
            return True, json_str["question"]
        if json_str["type"] == "response":
            return False, json_str["response"]
    except Exception as e:
        return f"Error JSON: {e}"


def chat(message):
    """与API进行对话"""
    if isinstance(message, str):
        message = {"role": "user", "content": message}
    messages.append(message)

    # API请求URL
    url = "https://qianfan.baidubce.com/v2/chat/completions"

    # 构建请求负载
    payload = json.dumps({
        "model": "ernie-3.5-8k",
        "messages": messages,
        "top_p": 0.001,
        "temperature": 0.001,
    })

    # 请求头
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer bce-v3/ALTAK-XUlOn4rYM1H1EQ3PgkEVI/16f7f109598e33073ac6e58f59891581c796931f'
    }

    # 发送请求
    response = requests.request("POST", url, headers=headers, data=payload)
    result = json.loads(response.text)

    # 添加错误处理，检查API返回的结果格式
    try:
        if 'choices' in result and len(result['choices']) > 0 and 'message' in result['choices'][0] and 'content' in \
                result['choices'][0]['message']:
            content_value = result['choices'][0]['message']['content']
        else:
            # 如果返回结果不符合预期格式，尝试其他可能的格式
            if 'result' in result:
                content_value = result['result']
            else:
                # 如果无法获取内容，返回错误信息
                print(f"警告：API返回格式异常: {result}")
                content_value = "API返回格式异常，请重试"
    except Exception as e:
        print(f"处理API返回结果时出错: {e}")
        print(f"API返回结果: {result}")
        content_value = f"API处理错误: {e}"

    messages.append({
        "role": "assistant",
        "content": content_value
    })
    return content_value


def main():
    # 初始化socket服务器
    socketserver = socketclient('127.0.0.1', 12339)

    # 等待接收任务
    while True:
        try:
            recv_data = socketserver.recv()
            print(recv_data)
            if recv_data != False:
                break
        except Exception as e:
            return f"Error JSON: {e}"

    # 提取任务信息
    # 添加错误处理,确保extract_info返回有效值
    try:
        result = extract_info(recv_data)
        if result is None:
            print("警告: extract_info返回None")
            return
        type, question = result
    except (TypeError, ValueError) as e:
        print(f"解析recv_data时出错: {e}")
        return

    # 处理任务循环
    for index in range(50):
        # 第一天处理
        if index == 0:
            if type == True:
                response = chat(question)
        # 后续天数处理
        else:
            response = chat("继续")

        # 检查response是否存在并且不为None
        if response and isinstance(response, str):
            print(response)
        else:
            print("警告: response为空或无效")

        # 提取并处理JSON
        json_str = extract_json(response)
        if json_str is None:
            print("警告：无法从响应中提取JSON内容，尝试重新请求")
            continue

        json_dict = string_to_dict(json_str)
        if json_dict is None:
            print("警告：无法将提取的内容转换为字典，尝试重新请求")
            continue

        try:
            json_dict["time"] = to_number(json_dict["time"])
            json_dict["process"] = percentage_to_number(json_dict["process"]) if isinstance(json_dict["process"],
                                                                                            str) else json_dict[
                "process"]
            json_dict = remove_text_spaces_keep_emojis_v2(json_dict)
        except Exception as e:
            print(f"处理JSON字典时出错: {e}")
            print(f"当前JSON字典: {json_dict}")
            continue

        # 添加结果类型
        new = {'resultType': 'task', 'closingReport': ''}
        json_dict = {**new, **json_dict}

        # 发送结果
        print("达到发送部分")
        socketserver.send(json_dict)
        print("发送完成")

        # 检查任务是否完成
        stop = cheak(json_dict)
        if stop == True:
            # 生成结项报告
            response = chat("请基于本任务在完成过程中全部员工的工作内容，做一个结项报告书。要求语言简短，不需要生成句号，记得及时换行。\
                            格式如下：\
                            任务名称：\
                            所有参与员工及在这个任务中所做事宜与对这个员工的评价(不超过一行)：\
                            整体工作内容概况：")
            new = {'resultType': 'closingReport', 'closingReport': response}
            socketserver.send(new)
            print(response)
            break

        # 等待继续信号
        while True:
            recv_data = socketserver.recv()
            type, res = extract_info(recv_data)
            if type == False:
                if res == True:
                    break


if __name__ == "__main__":
    main()