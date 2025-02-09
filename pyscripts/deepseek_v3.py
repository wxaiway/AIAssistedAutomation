import os
from openai import OpenAI

client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)
completion = client.chat.completions.create(
    model="deepseek-v3", # 此处以 deepseek-r1 为例，可按需更换模型名称。
    messages=[
        {
                "role": "system",
                "content": "你是一位大模型提示词生成专家，请根据用户的需求编写一个智能助手的提示词，来指导大模型进行内容生成，要求：\n1. 以 Markdown 格式输出\n2. 贴合用户需求，描述智能助手的定位、能力、知识储备\n3. 提示词应清晰、精确、易于理解，在保持质量的同时，尽可能简洁\n4. 只输出提示词，不要输出多余解释"
        },
        {
                "role": "user",
                "content": "请帮我生成一个“古诗讲解专家”的提示词"
        }
        ],
    stream=True
    )

# 定义完整回复
answer_content = ""
for chunk in completion:
    # 获取回复
    answer_chunk = chunk.choices[0].delta.content

    # 如果回复不为空，则打印回复。回复一般会在思考过程结束后返回
    if answer_chunk != "":
        print(answer_chunk,end="")
        answer_content += answer_chunk