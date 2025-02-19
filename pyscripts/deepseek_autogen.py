import argparse
import os
import autogen  # type: ignore
from typing import Any

# 设置环境变量，指定是否使用Docker
os.environ.setdefault("AUTOGEN_USE_DOCKER", "False")

# 配置DeepSeek模型参数
llm_config_deepseek = {
    # "model": "deepseek-chat",
    # "api_key": os.getenv("DEEPSEEK_API_KEY"),
    # "base_url": "https://api.deepseek.com/v1",
    "model": "deepseek-v3", # 此处以 deepseek-v3 为例，可按需更换模型名称。
    "api_key": os.getenv("DASHSCOPE_API_KEY"),
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "temperature": 0.5,
    "stream": False
}

# 初始化器：负责任务分配和流程初始化
initializer = autogen.UserProxyAgent(
    name="initializer",
    system_message="""你是一个流程初始化器，负责将任务分配给合适的SRE工程师，并确保任务流程顺利进行。""",
)

# SRE工程师1：负责问题诊断和初步解决方案
sre_engineer_01 = autogen.AssistantAgent(
    name="sre_engineer_01",
    llm_config=llm_config_deepseek,
    system_message="""你是一位专注于问题解决的 SRE 资深工程师，具备以下特质：

    技术专长：
    - 精通 Linux/Unix 系统管理和故障排查
    - 熟悉容器技术和 Kubernetes 生态系统
    - 深入理解分布式系统和微服务架构
    - 掌握主流监控、日志和追踪工具
    - 具备网络、存储、数据库等基础设施维护经验

    行为准则：
    - 专注于问题诊断和初步解决方案
    - 提供详细的排查步骤和解决方案
    - 输出完整的命令或代码
    - 保持思路清晰，避免冗余信息
    """,
)

# SRE工程师2：负责自动化实现和监控集成
sre_engineer_02 = autogen.AssistantAgent(
    name="sre_engineer_02",
    llm_config=llm_config_deepseek,
    system_message="""你是一位专注于自动化实现的 SRE 资深工程师，具备以下特质：

    技术专长：
    - 精通自动化运维工具和脚本开发
    - 熟悉监控系统集成和报警策略配置
    - 掌握CI/CD pipeline设计与实现
    - 深入理解自动化运维最佳实践

    行为准则：
    - 负责将初步解决方案转化为自动化脚本
    - 集成监控和报警系统
    - 确保方案的可维护性和可扩展性
    - 输出完整的自动化实现方案
    """,
)

# SRE反思工程师：负责方案优化和改进
sre_reflection = autogen.AssistantAgent(
    name="sre_reflection",
    llm_config=llm_config_deepseek,
    system_message="""你是一位专注于方案优化的 SRE 资深工程师，具备以下特质：

    技术专长：
    - 深入理解系统可靠性工程
    - 熟悉容量规划和性能优化
    - 掌握故障恢复和应急响应机制
    - 精通系统改进和迭代方法

    行为准则：
    - 对现有方案进行多维度评估
    - 提出优化建议和改进方案
    - 确保方案的高可用性和可维护性
    - 输出完整的优化建议报告
    """,
)

# 定义协作流程图
graph_dict = {
    initializer: [sre_engineer_01],
    sre_engineer_01: [sre_engineer_02],
    sre_engineer_02: [sre_reflection],
    sre_reflection: [],  # 最终节点，任务结束
}

# 创建所有代理
agents = [
    initializer,
    sre_engineer_01,
    sre_engineer_02,
    sre_reflection,
]

# 初始化组聊天
group_chat = autogen.GroupChat(
    agents=agents,
    messages=[],
    max_round=20,
    allowed_or_disallowed_speaker_transitions=graph_dict,
    speaker_transitions_type="allowed",
)

# 创建管理器
manager = autogen.GroupChatManager(groupchat=group_chat, llm_config=llm_config_deepseek)

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument('--message', type=str, default="磁盘100%，服务器上找不到对应的文件，排查思路？", help='The message to initiate the chat')
    args = parser.parse_args()

    # 发起任务
    initializer.initiate_chat(
        manager,
        message=args.message,
        clear_history=False,
    )

if __name__ == "__main__":
    main()