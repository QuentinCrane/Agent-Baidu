
import erniebot

erniebot.api_type = 'aistudio'
erniebot.access_token = "0bdd018d5819d729071de9651a506253c18c122d"

response = erniebot.ChatCompletion.create(
    model='ernie-3.5',
    messages=[{'role': 'user', 'content': "请对我说“你好，世界！”"}],
)
print(response.get_result())