import requests

import json


def generate_task_assignment(task_name):
    """  
    生成特定任务的员工分配JSON  
    :param task_name: 任务名称  
    :return: 格式化的JSON字符串  
    """  # 系统提示词

    systems = "假如你是一个公司ceo，目前需要你来针对某个具体任务，根据需求，对不同的员工，安排去做不同的事情。员工是固定的，但是每次的职业不同。\
    员工们的姓名为：刘一、陈二、张三、李四、王五、赵六、孙七、周八、吴九、郑十"
    # 构建消息


    messages = [
        {
            "role": "system",
            "content": systems
        },
        {
            "role": "user",
            "content": "假如你是一场虚拟音乐会的总导演，目前需要你来针对音乐会的筹备工作，根据需求，对不同的工作人员安排去做不同的事情。工作人员是固定的，但是每次的职务不同。\
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
         请你特别注意，不要生成过多的表情符号,也不要使用文字来代替表情符号！！！不要生成过多的表情符号,也不要使用文字来代替表情符号！！！"
    }
    ]

    # API请求URL
    url = "https://qianfan.baidubce.com/v2/chat/completions"
    # 构建请求负载
    payload = json.dumps({
    "model": "ernie-3.5-8k",
    "messages": messages
    })

    # 请求头
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer bce-v3/ALTAK-XUlOn4rYM1H1EQ3PgkEVI/16f7f109598e33073ac6e58f59891581c796931f'
    }

    # 发送请求
    response = requests.request("POST", url, headers=headers, data=payload)
    result = response.text

    # 解析响应
    try:
        json_data = json.loads(result)
        content_value = json_data['choices'][0]['message']['content']

        # 提取JSON部分
        json_start = content_value.find('{')
        json_end = content_value.rfind('}')
        if json_start != -1 and json_end != -1:
            json_str = content_value[json_start:json_end + 1]
            # 替换单引号为双引号以确保有效的JSON
            json_str = json_str.replace("'", "\"")
            return json_str
        else:
            return "无法提取有效的JSON数据"
    except Exception as e:
        return f"解析响应时出错: {e}"


def main():
    # 示例：生成公司年会任务分配
    task_name = "筹备公司年会"
    result = generate_task_assignment(task_name)
    print(result)


if __name__ == '__main__':
    main()