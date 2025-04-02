#coding=utf-8
import requests
import json
import re
import ast
import time
from socketplus import *

# 系统提示词
systems = "假如你是一场虚拟音乐会的总导演，目前需要你来针对音乐会的筹备工作，根据需求，对不同的工作人员安排去做不同的事情。工作人员是固定的，但是每次的职务不同。\
        工作人员的姓名为：刘一、陈二、张三、李四、王五、赵六、孙七、周八、吴九、郑十\
        一、角色的名称为'身份'+'姓名'如：策划师张三，安保员李四，舞台工程师王五，等等，具体职务你可以根据任务要求进行实际设计，工作人员姓名就用这十位就可以，不得出现除刘一、陈二、张三、李四、王五、赵六、孙七、周八、吴九、郑十以外的名字。\
        二、每个角色的工作任务必须不重不漏，角色一次性生成完毕，要尽可能多一些，复杂一些，而且角色之间一定要有指名道姓的配合。\
        三、整体的输出以日报形式开展，一次只生成一天全部工作人员的任务，当我说'继续'的时候，就相当于请你生成下一天的日报，每次说'继续'，都是新的一天的日报，日报到第五天的时候，就全部结束工作，此时进度为100%。每个人的日报除了描述今天干什么，需要仅用表情符传达意思，分别是情绪表情符和表达事务意思的表情符。日报一定要说整个事情目前的完成进度情况，在最后的时候整个事情的完成进度为100%。\
        四、你这个总导演的音乐会场地，有以下房间:休息化妆间、排练设计室、后勤保障处、场务设备处、宣发处、财务室、会议室\
        每个角色如果要做某个事情，一定必须要提一下去哪个房间。不得出现除上述房间名称以外的房间。不同的角色是可以去同一个地方的。\
        五、日报需要按照如下的json格式回答，不能掺杂其他的文字，使用'''json'''来回答\
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
		            'position':'策划师', // string，意思是这个员工当前的角色\
		            'to':'会议室', // string，该员工要去的地方\
		            'do_':'负责确定音乐会主题、节目安排、场地选择，与陈二协商流行趋势分析，同时组织现场预案讨论', // string，该员工的日报（今天要做的事情，描述得尽可能详细）\
                    'emoji':'😀🎶' ,// emoji unicode string，2个表情（其中不可以使用文字，且只要两个），分别表达情绪和工作类型 \
			    },\
			    {\
			        'name':'陈二', // string,意思是是哪个员工\
			        'position':'舞台搭建工程师', // string，意思是这个员工当前的角色\
			        'to':'电脑室', // string，该员工要去的地方\
			        'do_':'根据刘一的策划方案，设计舞台搭建方案，调试灯光、音响和大屏幕效果，并与张三核对技术参数', // string，该员工的日报（今天要做的事情，描述得尽可能详细）\
		            'emoji':'😎🔧'  // emoji unicode string，2个表情（其中不可以使用文字，且只要两个），分别表达情绪和工作类型\
		        },\
		        ……\
		    ]\
		} \
         请你特别注意，不要生成过多的表情符号,也不要使用文字来代替表情符号！！！不要生成过多的表情符号,也不要使用文字来代替表情符号！！！\
            请在生成完 第一天的 后就停止，除非输入'继续'后，才能继续生成"

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
    """从文本中提取JSON内容，增强版"""
    if content is None:
        print("输入内容为None，无法提取JSON")
        return None
        
    try:
        # 预处理内容，移除可能的干扰字符
        content = content.strip()
        print(f"原始API响应内容:\n{content}\n")
        
        # 首先尝试使用正则表达式查找代码块中的JSON
        json_blocks = json_block_regex.findall(content)
        if json_blocks:
            full_json = "\n".join(json_blocks)
            if full_json.startswith("json"):
                full_json = full_json[5:]
            print(f"提取的JSON内容:\n{full_json[:1000]}...\n")
            return full_json
        
        # 如果没有找到代码块，尝试直接从内容中提取JSON
        print("未找到代码块中的JSON内容，尝试直接提取")
        
        # 尝试修复常见JSON格式问题
        # 1. 处理单引号问题
        content = content.replace("'", '"')
        # 2. 处理中文引号问题
        content = content.replace("“", '"').replace("”", '"')
        # 3. 处理多余的逗号
        content = re.sub(r',\s*([\]\}])', r'\1', content)
        # 4. 处理注释
        content = re.sub(r'//.*?\n', '\n', content)
        # 5. 处理属性名缺少引号的问题
        content = re.sub(r'(\{|\,)\s*(\w+)\s*:', r'\1"\2":', content)
        
        # 尝试查找最外层的花括号对
        start_idx = content.find('{')
        end_idx = content.rfind('}')
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            possible_json = content[start_idx:end_idx+1]
            
            try:
                # 尝试解析修复后的JSON
                result = json.loads(possible_json)
                print(f"成功提取到有效JSON内容: {possible_json[:100]}...")
                return possible_json
            except json.JSONDecodeError as e:
                print(f"JSON解析错误: {e}")
                # 尝试更激进的修复
                try:
                    # 处理可能的Unicode转义问题
                    possible_json = possible_json.encode('unicode-escape').decode('ascii')
                    possible_json = re.sub(r'\\\\u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), possible_json)
                    result = json.loads(possible_json)
                    print(f"通过Unicode转义修复后提取到JSON内容: {possible_json[:100]}...")
                    return possible_json
                except Exception:
                    pass
        
        # 如果所有方法都失败，尝试构建最小有效JSON
        print("尝试构建最小有效JSON")
        minimal_json = {
            "task": "",
            "process": "0",
            "time": "1",
            "tasks": []
        }
        
        # 提取关键字段
        task_match = re.search(r'"task"\s*:\s*"([^"]*)"', content)
        process_match = re.search(r'"process"\s*:\s*"?([\d]+)"?', content)
        time_match = re.search(r'"time"\s*:\s*"?([\d]+)"?', content)
        
        if task_match: minimal_json["task"] = task_match.group(1)
        if process_match: minimal_json["process"] = process_match.group(1)
        if time_match: minimal_json["time"] = time_match.group(1)
        
        # 提取tasks数组
        tasks_match = re.search(r'"tasks"\s*:\s*\[(.*?)\]', content, re.DOTALL)
        if tasks_match:
            task_items = re.findall(r'\{([^\}]*)\}', tasks_match.group(1))
            for task_item in task_items[:10]:  # 最多处理10个任务
                task_dict = {}
                name_match = re.search(r'"name"\s*:\s*"([^"]*)"', task_item)
                position_match = re.search(r'"position"\s*:\s*"([^"]*)"', task_item)
                to_match = re.search(r'"to"\s*:\s*"([^"]*)"', task_item)
                do_match = re.search(r'"do_"\s*:\s*"([^"]*)"', task_item)
                emoji_match = re.search(r'"emoji"\s*:\s*"([^"]*)"', task_item)
                
                if name_match: task_dict["name"] = name_match.group(1)
                if position_match: task_dict["position"] = position_match.group(1)
                if to_match: task_dict["to"] = to_match.group(1)
                if do_match: task_dict["do_"] = do_match.group(1)
                if emoji_match: task_dict["emoji"] = emoji_match.group(1)
                
                if task_dict:
                    minimal_json["tasks"].append(task_dict)
        
        print("成功构建最小有效JSON")
        return json.dumps(minimal_json, ensure_ascii=False)
    except Exception as e:
        print(f"提取JSON时出错: {e}")
        return None
        
        # 尝试修复常见JSON格式问题
        # 1. 处理单引号问题
        content = content.replace("'", '"')
        # 2. 处理中文引号问题
        content = content.replace("“", '"').replace("”", '"')
        # 3. 处理多余的逗号
        content = re.sub(r',\s*([\]\}])', r'\1', content)
        # 4. 处理注释
        content = re.sub(r'//.*?\n', '\n', content)
        # 5. 处理属性名缺少引号的问题
        content = re.sub(r'(\{|\,)\s*(\w+)\s*:', r'\1"\2":', content)
        
        # 尝试查找最外层的花括号对
        start_idx = content.find('{')
        end_idx = content.rfind('}')
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            possible_json = content[start_idx:end_idx+1]
            
            try:
                # 尝试解析修复后的JSON
                result = json.loads(possible_json)
                print(f"成功提取到有效JSON内容: {possible_json[:100]}...")
                return possible_json
            except json.JSONDecodeError as e:
                print(f"JSON解析错误: {e}")
                # 尝试更激进的修复
                try:
                    # 处理可能的Unicode转义问题
                    possible_json = possible_json.encode('unicode-escape').decode('ascii')
                    possible_json = re.sub(r'\\\\u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), possible_json)
                    result = json.loads(possible_json)
                    print(f"通过Unicode转义修复后提取到JSON内容: {possible_json[:100]}...")
                    return possible_json
                except Exception:
                    pass
        
        # 如果所有方法都失败，尝试构建最小有效JSON
        print("尝试构建最小有效JSON")
        minimal_json = {
            "task": "",
            "process": "0",
            "time": "1",
            "tasks": []
        }
        
        # 提取关键字段
        task_match = re.search(r'"task"\s*:\s*"([^"]*)"', content)
        process_match = re.search(r'"process"\s*:\s*"?([\d]+)"?', content)
        time_match = re.search(r'"time"\s*:\s*"?([\d]+)"?', content)
        
        if task_match: minimal_json["task"] = task_match.group(1)
        if process_match: minimal_json["process"] = process_match.group(1)
        if time_match: minimal_json["time"] = time_match.group(1)
        
        # 提取tasks数组
        tasks_match = re.search(r'"tasks"\s*:\s*\[(.*?)\]', content, re.DOTALL)
        if tasks_match:
            task_items = re.findall(r'\{([^\}]*)\}', tasks_match.group(1))
            for task_item in task_items[:10]:  # 最多处理10个任务
                task_dict = {}
                name_match = re.search(r'"name"\s*:\s*"([^"]*)"', task_item)
                position_match = re.search(r'"position"\s*:\s*"([^"]*)"', task_item)
                to_match = re.search(r'"to"\s*:\s*"([^"]*)"', task_item)
                do_match = re.search(r'"do_"\s*:\s*"([^"]*)"', task_item)
                emoji_match = re.search(r'"emoji"\s*:\s*"([^"]*)"', task_item)
                
                if name_match: task_dict["name"] = name_match.group(1)
                if position_match: task_dict["position"] = position_match.group(1)
                if to_match: task_dict["to"] = to_match.group(1)
                if do_match: task_dict["do_"] = do_match.group(1)
                if emoji_match: task_dict["emoji"] = emoji_match.group(1)
                
                if task_dict:
                    minimal_json["tasks"].append(task_dict)
        
        print("成功构建最小有效JSON")
        return json.dumps(minimal_json, ensure_ascii=False)
    except Exception as e:
        print(f"提取JSON时出错: {e}")
        return None
        
        # 如果上述方法都失败，尝试使用更宽松的方式提取
        # 查找可能的JSON开始和结束位置
        start_idx = content.find('{')
        end_idx = content.rfind('}')
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            # 提取可能的JSON字符串
            possible_json = content[start_idx:end_idx+1]
            
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
    """将字符串转换为字典，增强版"""
    if dict_string is None:
        print("输入字符串为None，无法转换为字典")
        return None
        
    # 预处理字符串，移除可能干扰解析的字符
    dict_string = dict_string.strip()
    
    # 检查字符串是否为空或过短
    if len(dict_string) < 5:  # 至少需要 {}
        print(f"输入字符串过短，无法解析: '{dict_string}'")
        return None
    
    # 尝试多种方法解析JSON
    methods = [
        # 方法1: 直接使用ast.literal_eval
        lambda s: ast.literal_eval(s),
        
        # 方法2: 替换单引号后使用json.loads
        lambda s: json.loads(s.replace("'", '"')),
        
        # 方法3: 处理注释和多余逗号后使用json.loads
        lambda s: json.loads(
            re.sub(r',\s*([\]\}])', r'\1',
                re.sub(r'//.*?\n', '\n', 
                    s.replace("'", '"')
                )
            )
        ),
        
        # 方法4: 尝试修复常见JSON格式问题
        lambda s: json.loads(
            re.sub(r'([{,})\s*(\w+)\s*:', r'\1"\2":', 
                re.sub(r',\s*([\]\}])', r'\1',
                    re.sub(r'//.*?\n', '\n', 
                        re.sub(r'\\([^"\\])', r'\\\\\1', s.replace("'", '"'))
                    )
                )
            )
        ),
        
        # 方法5: 更激进的修复，处理可能的Unicode转义问题
        lambda s: json.loads(
            re.sub(r'([{,})\s*(\w+)\s*:', r'\1"\2":', 
                re.sub(r',\s*([\]\}])', r'\1',
                    re.sub(r'//.*?\n', '\n', 
                        re.sub(r'\\([^"\\])', r'\\\\\1', s.replace("'", '"'))
                    )
                )
            )
        ),
        
        # 方法6: 尝试修复可能的嵌套引号问题
        lambda s: json.loads(
            re.sub(r'"([^"]*?)"([^"]*?)"([^"]*?)"', r'"\1\'\2\'\3"', 
                re.sub(r'([{,}])\s*(\w+)\s*:', r'\1"\2":',
                    re.sub(r',\s*([\]\}])', r'\1',
                        re.sub(r'//.*?\n', '\n', s.replace('\'', '"'))
                    )
                )
            )
        ),
        
        # 方法7: 尝试修复不完整的JSON片段
        lambda s: json.loads(
            re.sub(r'([{,}])\s*(\w+)\s*:', r'\1"\2":',
                re.sub(r',\s*([\]\}])', r'\1',
                    re.sub(r'//.*?\n', '\n', 
                        s.replace('\'', '"')
                    )
                )
            )
        ),
        
        # 方法8: 尝试修复可能的转义字符问题
        lambda s: json.loads(
            re.sub(r'\\(?!["\\bfnrt])', '', 
                re.sub(r'([{,}])\s*(\w+)\s*:', r'\1"\2":', 
                    s.replace('\'', '"')
                )
            )
        )
    ]
    
    # 尝试每种方法
    for i, method in enumerate(methods):
        try:
            dictionary = method(dict_string)
            print(f"使用方法{i+1}成功解析JSON")
            return dictionary
        except (SyntaxError, ValueError, json.JSONDecodeError) as e:
            print(f"使用方法{i+1}解析失败: {e}")
            continue
        except Exception as e:
            print(f"使用方法{i+1}时出现未知错误: {e}")
            continue
    
    # 如果所有方法都失败，尝试最后的手段：提取部分有效的JSON
    try:
        print("尝试提取部分有效的JSON")
        # 查找最外层的花括号
        start_idx = dict_string.find('{')
        end_idx = dict_string.rfind('}')
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            partial_json = dict_string[start_idx:end_idx+1]
            # 尝试解析这部分内容
            try:
                return json.loads(
                    re.sub(r'([{,})\s*(\w+)\s*:', r'\1"\2":', 
                        partial_json.replace("'", '"')
                    )
                )
            except json.JSONDecodeError:
                # 尝试更激进的清理
                cleaned_json = re.sub(r'[\n\r\t]', ' ', partial_json)  # 移除换行符等
                cleaned_json = re.sub(r'\s+', ' ', cleaned_json)  # 压缩空白
                cleaned_json = re.sub(r'"([^"]*?)"([^"]*?)"([^"]*?)"', r'"\1\'\2\'\3"', cleaned_json)  # 处理嵌套引号
                
                # 尝试手动构建一个最小有效的JSON
                if 'task' in cleaned_json and 'process' in cleaned_json and 'time' in cleaned_json and 'tasks' in cleaned_json:
                    try:
                        # 提取关键字段
                        task_match = re.search(r'"task"\s*:\s*"([^"]*)"', cleaned_json)
                        process_match = re.search(r'"process"\s*:\s*"?([\d]+)"?', cleaned_json)
                        time_match = re.search(r'"time"\s*:\s*"?([\d]+)"?', cleaned_json)
                        
                        if task_match and process_match and time_match:
                            # 构建最小JSON
                            minimal_json = {
                                'task': task_match.group(1),
                                'process': process_match.group(1),
                                'time': time_match.group(1),
                                'tasks': []
                            }
                            
                            # 尝试提取tasks数组
                            tasks_match = re.search(r'"tasks"\s*:\s*\[(.*?)\]', cleaned_json, re.DOTALL)
                            if tasks_match:
                                # 简单处理，提取name和position
                                task_items = re.findall(r'\{([^\}]*)\}', tasks_match.group(1))
                                for task_item in task_items[:10]:  # 最多处理10个任务
                                    task_dict = {}
                                    name_match = re.search(r'"name"\s*:\s*"([^"]*)"', task_item)
                                    position_match = re.search(r'"position"\s*:\s*"([^"]*)"', task_item)
                                    to_match = re.search(r'"to"\s*:\s*"([^"]*)"', task_item)
                                    do_match = re.search(r'"do_"\s*:\s*"([^"]*)"', task_item)
                                    emoji_match = re.search(r'"emoji"\s*:\s*"([^"]*)"', task_item)
                                    
                                    if name_match: task_dict['name'] = name_match.group(1)
                                    if position_match: task_dict['position'] = position_match.group(1)
                                    if to_match: task_dict['to'] = to_match.group(1)
                                    if do_match: task_dict['do_'] = do_match.group(1)
                                    if emoji_match: task_dict['emoji'] = emoji_match.group(1)
                                    
                                    if task_dict:
                                        minimal_json['tasks'].append(task_dict)
                        
                        print("成功构建最小有效JSON")
                        return minimal_json
                    except Exception as e:
                        print(f"构建最小JSON失败: {e}")
    except Exception as e:
        print(f"提取部分有效JSON失败: {e}")
    
    print("所有解析方法都失败，无法将字符串转换为字典")
    return None
    
    # 尝试每种方法
    for i, method in enumerate(methods):
        try:
            dictionary = method(dict_string)
            print(f"使用方法{i+1}成功解析JSON")
            return dictionary
        except (SyntaxError, ValueError, json.JSONDecodeError) as e:
            print(f"使用方法{i+1}解析失败: {e}")
            continue
        except Exception as e:
            print(f"使用方法{i+1}时出现未知错误: {e}")
            continue
    
    # 如果所有方法都失败，尝试最后的手段：提取部分有效的JSON
    try:
        print("尝试提取部分有效的JSON")
        # 查找最外层的花括号
        start_idx = dict_string.find('{')
        end_idx = dict_string.rfind('}')
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            partial_json = dict_string[start_idx:end_idx+1]
            # 尝试解析这部分内容
            try:
                return json.loads(
                    re.sub(r'([{,})\s*(\w+)\s*:', r'\1"\2":', 
                        partial_json.replace("'", '"')
                    )
                )
            except json.JSONDecodeError:
                # 尝试更激进的清理
                cleaned_json = re.sub(r'[\n\r\t]', ' ', partial_json)  # 移除换行符等
                cleaned_json = re.sub(r'\s+', ' ', cleaned_json)  # 压缩空白
                cleaned_json = re.sub(r'"([^"]*?)"([^"]*?)"([^"]*?)"', r'"\1\'\2\'\3"', cleaned_json)  # 处理嵌套引号
                
                # 尝试手动构建一个最小有效的JSON
                if 'task' in cleaned_json and 'process' in cleaned_json and 'time' in cleaned_json and 'tasks' in cleaned_json:
                    try:
                        # 提取关键字段
                        task_match = re.search(r'"task"\s*:\s*"([^"]*)"', cleaned_json)
                        process_match = re.search(r'"process"\s*:\s*"?([\d]+)"?', cleaned_json)
                        time_match = re.search(r'"time"\s*:\s*"?([\d]+)"?', cleaned_json)
                        
                        if task_match and process_match and time_match:
                            # 构建最小JSON
                            minimal_json = {
                                'task': task_match.group(1),
                                'process': process_match.group(1),
                                'time': time_match.group(1),
                                'tasks': []
                            }
                            
                            # 尝试提取tasks数组
                            tasks_match = re.search(r'"tasks"\s*:\s*\[(.*?)\]', cleaned_json, re.DOTALL)
                            if tasks_match:
                                # 简单处理，提取name和position
                                task_items = re.findall(r'\{([^\}]*)\}', tasks_match.group(1))
                                for task_item in task_items[:10]:  # 最多处理10个任务
                                    task_dict = {}
                                    name_match = re.search(r'"name"\s*:\s*"([^"]*)"', task_item)
                                    position_match = re.search(r'"position"\s*:\s*"([^"]*)"', task_item)
                                    to_match = re.search(r'"to"\s*:\s*"([^"]*)"', task_item)
                                    do_match = re.search(r'"do_"\s*:\s*"([^"]*)"', task_item)
                                    emoji_match = re.search(r'"emoji"\s*:\s*"([^"]*)"', task_item)
                                    
                                    if name_match: task_dict['name'] = name_match.group(1)
                                    if position_match: task_dict['position'] = position_match.group(1)
                                    if to_match: task_dict['to'] = to_match.group(1)
                                    if do_match: task_dict['do_'] = do_match.group(1)
                                    if emoji_match: task_dict['emoji'] = emoji_match.group(1)
                                    
                                    if task_dict:
                                        minimal_json['tasks'].append(task_dict)
                            
                            print("成功构建最小有效JSON")
                            return minimal_json
                    except Exception as e:
                        print(f"构建最小JSON失败: {e}")
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

def check(response):
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

def estimate_token_count(text):
    """估算文本的token数量，这是一个粗略估计"""
    # 中文字符大约是1个token，英文单词大约是0.75个token
    # 这里使用一个简单的估算方法
    chinese_count = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
    other_count = len(text) - chinese_count
    return chinese_count + int(other_count * 0.75)

def manage_message_history(messages, max_tokens=3500):
    """管理消息历史，确保不超过token限制，更激进的版本"""
    if len(messages) <= 2:  # 保留系统提示和第一条消息
        return messages
    
    # 计算当前消息的总token数
    total_tokens = sum(estimate_token_count(msg.get('content', '')) for msg in messages)
    
    # 如果总token数小于限制，直接返回
    if total_tokens <= max_tokens:
        return messages
    
    # 保留系统提示和最近的消息
    preserved_messages = [messages[0], messages[1]]  # 系统提示和助手的第一个回复
    recent_messages = []  # 最近的消息
    
    # 从最新的消息开始添加，直到接近token限制
    current_tokens = estimate_token_count(messages[0]['content']) + estimate_token_count(messages[1]['content'])
    
    # 确保至少保留最后一轮对话
    if len(messages) >= 4:
        last_user_msg = messages[-2]  # 用户的最后一条消息
        last_assistant_msg = messages[-1]  # 助手的最后一条回复
        last_round_tokens = estimate_token_count(last_user_msg.get('content', '')) + estimate_token_count(last_assistant_msg.get('content', ''))
        
        # 如果最后一轮对话太长，可能需要截断
        if last_round_tokens > max_tokens - current_tokens - 500:
            # 优先保留用户消息
            user_msg_tokens = estimate_token_count(last_user_msg.get('content', ''))
            if user_msg_tokens < max_tokens - current_tokens - 500:
                recent_messages.append(last_user_msg)
                # 截断助手消息
                assistant_content = last_assistant_msg.get('content', '')
                max_assistant_tokens = max_tokens - current_tokens - user_msg_tokens - 500
                if max_assistant_tokens > 200:  # 确保至少有一些有用的内容
                    truncated_content = assistant_content[:int(max_assistant_tokens * 4)]  # 粗略估计字符数
                    truncated_msg = {"role": "assistant", "content": truncated_content}
                    recent_messages.append(truncated_msg)
            else:
                # 如果用户消息也太长，可能需要更激进的策略
                # 这里简单地只保留系统提示和第一条回复
                pass
        else:
            # 最后一轮对话可以完整保留
            recent_messages.append(last_user_msg)
            recent_messages.append(last_assistant_msg)
    
    # 如果还有token余量，尝试添加更多历史消息
    remaining_messages = list(reversed(messages[2:-2])) if len(messages) >= 4 else list(reversed(messages[2:]))
    for msg in remaining_messages:
        msg_tokens = estimate_token_count(msg.get('content', ''))
        if current_tokens + msg_tokens <= max_tokens - 700:  # 留出更多余量
            recent_messages.insert(0, msg)
            current_tokens += msg_tokens
        else:
            break
    
    # 合并保留的消息
    managed_messages = preserved_messages + recent_messages
    print(f"消息历史已管理: 从{len(messages)}条减少到{len(managed_messages)}条，估计token数: {current_tokens}")
    return managed_messages

def chat(message):
    """与API进行对话"""
    global messages
    if isinstance(message, str):
        message = {"role": "user", "content": message}
    messages.append(message)
    
    # 管理消息历史，确保不超过token限制
    messages = manage_message_history(messages)

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
    max_retries = 3
    for retry in range(max_retries):
        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            result = json.loads(response.text)
            
            # 检查是否有错误
            if 'error' in result:
                error_msg = result['error'].get('message', '')
                if 'token limit' in error_msg and retry < max_retries - 1:
                    print(f"警告：API返回token限制错误，尝试进一步减少消息历史 (重试 {retry+1}/{max_retries})")
                    # 更激进地减少消息历史
                    messages = manage_message_history(messages, max_tokens=3000 - retry * 500)
                    # 更新payload
                    payload = json.dumps({
                        "model": "ernie-3.5-8k",
                        "messages": messages,
                        "top_p": 0.001,
                        "temperature": 0.001,
                    })
                    continue  # 重试
                else:
                    print(f"警告：API返回错误: {error_msg}")
                    return f"API错误: {error_msg}"
            break  # 成功获取结果，跳出重试循环
        except Exception as e:
            if retry < max_retries - 1:
                print(f"请求出错，正在重试 ({retry+1}/{max_retries}): {e}")
                time.sleep(1)  # 等待1秒后重试
            else:
                print(f"请求多次失败: {e}")
                return f"API请求失败: {e}"
    
    # 添加错误处理，检查API返回的结果格式
    try:
        if 'choices' in result and len(result['choices']) > 0 and 'message' in result['choices'][0] and 'content' in result['choices'][0]['message']:
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
    try:
        socketserver = socketclient('127.0.0.1', 12339)
    except Exception as e:
        print(f"初始化socket服务器失败: {e}")
        return
    
    # 等待接收任务
    max_recv_attempts = 5  # 最多尝试5次接收数据
    for recv_attempt in range(max_recv_attempts):
        try:
            recv_data = socketserver.recv()
            print(f"接收到数据: {recv_data}")
            if recv_data != False:
                break
            time.sleep(1)  # 等待1秒后重试
        except Exception as e:
            print(f"接收数据时出错 (尝试 {recv_attempt+1}/{max_recv_attempts}): {e}")
            time.sleep(1)  # 等待1秒后重试
            if recv_attempt == max_recv_attempts - 1:
                print("达到最大接收尝试次数，退出程序")
                return f"Error JSON: {e}"
    
    # 提取任务信息
    try:
        result = extract_info(recv_data)
        if result is None or isinstance(result, str):
            print(f"警告: extract_info返回无效值: {result}")
            return
        type, question = result
    except (TypeError, ValueError) as e:
        print(f"解析recv_data时出错: {e}")
        return
    
    # 初始化天数计数器
    current_day = 0
    
    # 主循环 - 每次只处理一天的任务
    while current_day < 50:  # 设置最大天数限制
        max_attempts = 5  # 每天最多尝试5次
        success = False
        json_dict = None  # 初始化json_dict
        
        for attempt in range(max_attempts):
            try:
                # 根据是否是第一天决定发送的内容
                if current_day == 0:
                    if type == True:
                        response = chat(question)
                else:
                    response = chat("继续")
                
                # 检查response是否存在并且不为None
                if not response or not isinstance(response, str):
                    print(f"警告: response为空或无效 (尝试 {attempt+1}/{max_attempts})")
                    time.sleep(1)  # 等待1秒后重试
                    continue
                    
                print(f"API响应: {response[:200]}..." if len(response) > 200 else f"API响应: {response}")  # 只打印部分响应内容
                
                # 提取并处理JSON
                json_str = extract_json(response)
                if json_str is None:
                    print(f"警告：无法从响应中提取JSON内容 (尝试 {attempt+1}/{max_attempts})")
                    # 如果是最后一次尝试，尝试更激进的方法
                    if attempt == max_attempts - 1:
                        print("尝试更激进的JSON提取方法")
                        # 尝试直接从响应中提取任何看起来像JSON的内容
                        json_pattern = re.compile(r'\{[^\{\}]*\}', re.DOTALL)
                        json_matches = json_pattern.findall(response)
                        if json_matches:
                            for potential_json in json_matches:
                                try:
                                    # 尝试解析这个潜在的JSON
                                    test_dict = json.loads(potential_json.replace("'", '"'))
                                    if 'task' in test_dict and 'tasks' in test_dict:
                                        json_str = potential_json
                                        print(f"使用激进方法成功提取JSON: {json_str[:100]}...")
                                        break
                                except:
                                    continue
                    if json_str is None:
                        time.sleep(1)  # 等待1秒后重试
                        continue
                    
                json_dict = string_to_dict(json_str)
                if json_dict is None:
                    print(f"警告：无法将提取的内容转换为字典 (尝试 {attempt+1}/{max_attempts})")
                    # 如果是最后一次尝试，尝试手动构建一个基本的JSON结构
                    if attempt == max_attempts - 1 and json_str:
                        print("尝试手动构建基本JSON结构")
                        try:
                            # 尝试提取关键字段
                            task_match = re.search(r'["\'](task)["\'](\s)*:(\s)*["\'](.*?)["\'](,)?', json_str)
                            process_match = re.search(r'["\'](process)["\'](\s)*:(\s)*["\'](\d+)["\'](,)?', json_str)
                            time_match = re.search(r'["\'](time)["\'](\s)*:(\s)*["\'](\d+)["\'](,)?', json_str)
                            
                            if task_match and process_match and time_match:
                                json_dict = {
                                    'task': task_match.group(1),
                                    'process': process_match.group(1),
                                    'time': time_match.group(1),
                                    'tasks': []
                                }
                                print(f"手动构建的基本JSON: {json_dict}")
                        except Exception as e:
                            print(f"手动构建JSON失败: {e}")
                    
                    if json_dict is None:
                        time.sleep(1)  # 等待1秒后重试
                        continue
                    
                # 处理JSON字典
                try:
                    # 确保必要的字段存在
                    required_fields = ['task', 'process', 'time', 'tasks']
                    missing_fields = [field for field in required_fields if field not in json_dict]
                    if missing_fields:
                        print(f"警告：JSON缺少必要字段: {missing_fields}")
                        if attempt < max_attempts - 1:
                            time.sleep(1)  # 等待1秒后重试
                            continue
                        else:
                            # 最后一次尝试，尝试填充缺失字段
                            for field in missing_fields:
                                if field == 'task':
                                    json_dict['task'] = question if current_day == 0 else "继续任务"
                                elif field == 'process':
                                    json_dict['process'] = str(min(20 * (current_day + 1), 100))  # 简单估算进度
                                elif field == 'time':
                                    json_dict['time'] = str(current_day + 1)
                                elif field == 'tasks':
                                    json_dict['tasks'] = []
                    
                    # 转换字段类型
                    json_dict["time"] = to_number(json_dict["time"])
                    json_dict["process"] = percentage_to_number(json_dict["process"]) if isinstance(json_dict["process"], str) else json_dict["process"]
                    
                    # 确保tasks字段是列表且不为空
                    if not isinstance(json_dict['tasks'], list) or not json_dict['tasks']:
                        print("警告：tasks字段不是有效列表或为空")
                        if attempt < max_attempts - 1:
                            time.sleep(1)  # 等待1秒后重试
                            continue
                    
                    # 清理表情字段
                    json_dict = remove_text_spaces_keep_emojis_v2(json_dict)
                    
                    success = True  # 标记成功
                    break  # 成功处理，跳出尝试循环
                except Exception as e:
                    print(f"处理JSON字典时出错 (尝试 {attempt+1}/{max_attempts}): {e}")
                    if json_dict:
                        print(f"当前JSON字典: {str(json_dict)[:200]}..." if len(str(json_dict)) > 200 else str(json_dict))
                    time.sleep(1)  # 等待1秒后重试
            except Exception as e:
                print(f"处理当天任务时出错 (尝试 {attempt+1}/{max_attempts}): {e}")
                time.sleep(1)  # 等待1秒后重试
        
        # 如果所有尝试都失败，但我们有一个部分有效的json_dict，尝试使用它
        if not success and json_dict and isinstance(json_dict, dict):
            print("尝试使用部分有效的JSON继续处理")
            # 确保必要的字段存在
            required_fields = ['task', 'process', 'time', 'tasks']
            for field in required_fields:
                if field not in json_dict:
                    if field == 'task':
                        json_dict['task'] = question if current_day == 0 else "继续任务"
                    elif field == 'process':
                        json_dict['process'] = min(20 * (current_day + 1), 100)  # 简单估算进度
                    elif field == 'time':
                        json_dict['time'] = current_day + 1
                    elif field == 'tasks':
                        json_dict['tasks'] = []
            success = True
        
        # 如果所有尝试都失败，跳过当天
        if not success:
            print(f"警告：第{current_day+1}天的任务处理失败，尝试继续下一天")
            current_day += 1
            continue
        
        # 添加结果类型
        new = {'resultType': 'task', 'closingReport': ''}
        json_dict = {**new, **json_dict}
        
        # 发送结果
        print(f"准备发送第{current_day+1}天任务数据")
        try:
            socketserver.send(json_dict)
            print(f"第{current_day+1}天任务数据发送完成")
        except Exception as e:
            print(f"发送结果时出错: {e}")
            # 尝试重新发送
            try:
                print("尝试重新发送结果")
                time.sleep(1)
                socketserver.send(json_dict)
                print("重新发送成功")
            except Exception as e:
                print(f"重新发送结果失败: {e}")
                current_day += 1
                continue  # 继续下一天的处理
        
        # 检查任务是否完成
        try:
            stop = check(json_dict)
            if stop == True:
                # 生成结项报告
                try:
                    response = chat("请基于本任务在完成过程中全部员工的工作内容，做一个结项报告书。要求语言简短，不需要生成句号，记得及时换行。\
                                    格式如下：\
                                    任务名称：\
                                    所有参与员工及在这个任务中所做事宜与对这个员工的评价(不超过一行)：\
                                    整体工作内容概况：")
                    new = {'resultType': 'closingReport', 'closingReport': response}
                    socketserver.send(new)
                    print(f"结项报告: {response[:200]}..." if len(response) > 200 else f"结项报告: {response}")
                except Exception as e:
                    print(f"生成或发送结项报告时出错: {e}")
                    # 尝试发送一个简单的结项报告
                    try:
                        simple_report = f"任务名称：{json_dict.get('task', '未知任务')}\n整体工作内容概况：任务已完成"
                        new = {'resultType': 'closingReport', 'closingReport': simple_report}
                        socketserver.send(new)
                        print(f"发送简单结项报告: {simple_report}")
                    except:
                        pass
                break  # 任务完成，退出主循环
        except Exception as e:
            print(f"检查任务完成状态时出错: {e}")
        
        # 等待30秒后再继续下一天的处理
        print(f"等待2秒后继续处理第{current_day+2}天的任务...")
        time.sleep(2)
        
        # 等待继续信号
        wait_signal_attempts = 5  # 最多等待5次继续信号
        received_signal = False
        
        for signal_attempt in range(wait_signal_attempts):
            try:
                recv_data = socketserver.recv()
                if recv_data == False:
                    print(f"等待继续信号时接收到无效数据 (尝试 {signal_attempt+1}/{wait_signal_attempts})")
                    if signal_attempt == wait_signal_attempts - 1:
                        # 最后一次尝试，如果仍然失败，我们假设可以继续
                        print("未能接收到有效的继续信号，但尝试继续处理")
                        received_signal = True
                    else:
                        time.sleep(1)  # 等待1秒后重试
                    continue
                    
                result = extract_info(recv_data)
                if result is None or isinstance(result, str):
                    print(f"警告: 解析继续信号时extract_info返回无效值: {result} (尝试 {signal_attempt+1}/{wait_signal_attempts})")
                    time.sleep(1)  # 等待1秒后重试
                    continue
                    
                type, res = result
                if type == False and res == True:
                    received_signal = True
                    print("收到有效的继续信号，处理下一天任务")
                    break
                else:
                    print(f"收到意外的继续信号: type={type}, res={res} (尝试 {signal_attempt+1}/{wait_signal_attempts})")
                    time.sleep(1)  # 等待1秒后重试
            except Exception as e:
                print(f"等待继续信号时出错 (尝试 {signal_attempt+1}/{wait_signal_attempts}): {e}")
                time.sleep(1)  # 等待1秒后重试
        
        # 如果没有收到有效的继续信号，但已经不是第一天，可以尝试继续
        if not received_signal and current_day > 0:
            print("未收到有效的继续信号，但尝试继续处理下一天")
        # 如果是第一天且没有收到继续信号，可能需要退出
        elif not received_signal and current_day == 0:
            print("第一天未收到有效的继续信号，退出程序")
            break
            
        # 增加天数计数器
        current_day += 1

if __name__ == "__main__":
    main()