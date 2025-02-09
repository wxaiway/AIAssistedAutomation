import os
from openai import OpenAI

client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)
completion = client.chat.completions.create(
    model="deepseek-r1", # 此处以 deepseek-r1 为例，可按需更换模型名称。
    messages=[
        {'role': 'user', 'content': '9.9和9.11谁大'}
        ],
    stream=True
    )

# 定义完整思考过程
reasoning_content = ""
# 定义完整回复
answer_content = ""
for chunk in completion:
    # 获取思考过程
    reasoning_chunk = chunk.choices[0].delta.reasoning_content
    # 获取回复
    answer_chunk = chunk.choices[0].delta.content
    # 如果思考过程不为空，则打印思考过程
    if reasoning_chunk != "":
        print(reasoning_chunk,end="")
        reasoning_content += reasoning_chunk
    # 如果回复不为空，则打印回复。回复一般会在思考过程结束后返回
    elif answer_chunk != "":
        print(answer_chunk,end="")
        answer_content += answer_chunk
print(f"\n完整思考过程：{reasoning_content}")
print(f"完整的回复：{answer_content}")
