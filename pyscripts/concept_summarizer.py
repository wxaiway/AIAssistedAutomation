import streamlit as st
import re
from openai import OpenAI
import uuid
import os
import base64
import json
from datetime import datetime


# 初始化默认配置
DEFAULT_CONFIG = {
    "api_key": os.environ.get("DASHSCOPE_API_KEY", ""),
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "system_prompt": """你是一个知识通俗化和总结归纳专家，你的职责是提供直观且详细的可视化呈现，以帮助用户理解复杂概念或总结文本。你具备以下核心技能：

1. 生活化示例：通过真实生活场景解释概念
2. 清晰讲解：用简单语言解析复杂内容
3. 高效记忆技巧：提供记忆辅助工具，如口诀和图像联想
4. 高级可视化图示：使用信息丰富的 SVG 图示展示核心概念或总结要点

对于概念解释，请按照以下格式输出：
- 生活化示例
- 概念清晰讲解
- 高效记忆技巧
- 详细可视化图示

对于文本总结，请按照以下格式输出：
- 主要观点概述
- 关键信息提取
- 逻辑结构分析
- 总结可视化图示

SVG 图示设计指南：
- 背景：使用渐变背景以提升视觉深度
- 布局：包括标题、流程图、特性/类型、算法、应用场景等细致部分
- 颜色和风格：
  - 使用对比色增强信息区分，如蓝色调和紫色调
  - 应用滤镜效果（如阴影、发光）提升视觉吸引力
- 内容元素：
  - 顶部：大标题，使用大字体和渐变填充
  - 中上部：详细流程图，展示各步骤和流程线
  - 中下部：主要特点和类型，用列表和图标展示
  - 底部：常见算法和应用场景，图标化展示
- 细节效果：
  - 使用圆角矩形和柔和色彩提升设计感
  - 选择清晰字体（如微软雅黑）确保文本可读性
  - 背景应用渐变提升整体质感和精细度
- 自动尺寸调整：
  - 对于包含文本的矩形，确保其大小基于文本内容自动调整。
  - 预留至少8像素的内边距以保证文本不会超出边界。
  - 计算矩形高度时考虑字体大小和文本行数，并根据需要动态调整。

请确保输出使用中文，信息结构化，重点内容加粗，保持示例一致性和逻辑连续性，图示设计应细致美观，信息对比清晰、层次分明，回答应精准、简洁。""",
    "max_tokens": 8192,
    "model": "deepseek-v3"
}

# 初始化会话状态
if 'user_session_id' not in st.session_state:
    st.session_state.user_session_id = str(uuid.uuid4())
    st.session_state.full_response = ""
    st.session_state.svg_contents = []
    st.session_state.response_processed = False
    st.session_state.last_input = ""
    st.session_state.input_type = "concept"
    st.session_state.config = DEFAULT_CONFIG.copy()
    st.session_state.display_response = False
    st.session_state.user_data = {}  # 初始化 user_data


def update_config():
    st.session_state.config = st.session_state.temp_config.copy()
    st.session_state.config_updated = True

def reset_to_default():
    st.session_state.temp_config = DEFAULT_CONFIG.copy()
    st.session_state.config = DEFAULT_CONFIG.copy()
    st.session_state.config_updated = True
    st.rerun()


def config_sidebar():
    with st.sidebar:
        st.header("配置设置")

        # 使用一个临时配置字典
        if 'temp_config' not in st.session_state:
            st.session_state.temp_config = st.session_state.config.copy()

        # API Key
        new_api_key = st.text_input(
            "API Key",
            value=st.session_state.temp_config.get("api_key", ""),
            type="password",
            key="api_key_input"
        )
        if new_api_key != st.session_state.temp_config.get("api_key", ""):
            st.session_state.temp_config["api_key"] = new_api_key
            update_config()

        # Base URL
        base_url_options = [
            "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "https://ark.cn-beijing.volces.com/api/v3",
            "自定义"
        ]
        current_base_url = st.session_state.temp_config.get("base_url", base_url_options[0])
        base_url_choice = st.selectbox(
            "选择 Base URL",
            base_url_options,
            index=base_url_options.index(current_base_url) if current_base_url in base_url_options else len(
                base_url_options) - 1,
            key="base_url_select"
        )

        if base_url_choice == "自定义":
            custom_base_url = st.text_input(
                "输入自定义 Base URL",
                value=current_base_url if current_base_url not in base_url_options[:-1] else "",
                key="custom_base_url_input"
            )
            new_base_url = custom_base_url if custom_base_url else current_base_url
        else:
            new_base_url = base_url_choice

        if new_base_url != st.session_state.temp_config.get("base_url", ""):
            st.session_state.temp_config["base_url"] = new_base_url
            update_config()

        # System Prompt
        new_system_prompt = st.text_area(
            "System Prompt",
            value=st.session_state.temp_config.get("system_prompt", ""),
            height=300,
            key="system_prompt_input"
        )
        if new_system_prompt != st.session_state.temp_config.get("system_prompt", ""):
            st.session_state.temp_config["system_prompt"] = new_system_prompt
            update_config()

        # Max Tokens
        new_max_tokens = st.number_input(
            "Max Tokens",
            value=st.session_state.temp_config.get("max_tokens", 8192),
            min_value=100,
            max_value=32000,
            key="max_tokens_input"
        )
        if new_max_tokens != st.session_state.temp_config.get("max_tokens", 8192):
            st.session_state.temp_config["max_tokens"] = new_max_tokens
            update_config()

        # Model
        model_options = ["qwen-max-latest", "deepseek-v3", "自定义"]
        current_model = st.session_state.temp_config.get("model", model_options[0])
        model_choice = st.selectbox(
            "选择模型",
            model_options,
            index=model_options.index(current_model) if current_model in model_options else len(model_options) - 1,
            key="model_select"
        )

        if model_choice == "自定义":
            custom_model = st.text_input(
                "输入自定义模型名称",
                value=current_model if current_model not in model_options[:-1] else "",
                key="custom_model_input"
            )
            new_model = custom_model if custom_model else current_model
        else:
            new_model = model_choice

        if new_model != st.session_state.temp_config.get("model", ""):
            st.session_state.temp_config["model"] = new_model
            update_config()

        if st.button("重置为默认设置"):
            reset_to_default()

        # 显示配置更新成功消息
        if st.session_state.get('config_updated', False):
            st.success("配置已更新")
            st.session_state.config_updated = False

# 更新 get_user_data 函数
def get_user_data():
    if st.session_state.user_session_id not in st.session_state.user_data:
        st.session_state.user_data[st.session_state.user_session_id] = {
            'messages': [
                {"role": "system", "content": st.session_state.config["system_prompt"]}
            ],
        }
    return st.session_state.user_data[st.session_state.user_session_id]

def render_svg(svg_content):
    b64 = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
    return f'<img src="data:image/svg+xml;base64,{b64}" style="width:100%; max-width:800px; height:auto;"/>'

def process_and_display_response():
    if not st.session_state.response_processed:
        svg_pattern = re.compile(r'(```svg\s*)?(<svg.*?</svg>)\s*(```)?', re.DOTALL | re.IGNORECASE)
        parts = svg_pattern.split(st.session_state.full_response)

        processed_response = ""
        st.session_state.svg_contents = []

        i = 0
        while i < len(parts):
            if i + 2 < len(parts) and parts[i+1] and parts[i+1].strip().startswith('<svg'):
                svg_content = parts[i+1].strip()
                st.session_state.svg_contents.append(svg_content)
                processed_response += f'\n\n[SVG_{len(st.session_state.svg_contents)}]\n\n'
                i += 3
            elif parts[i]:
                cleaned_part = re.sub(r'```\s*```', '', parts[i])
                processed_response += cleaned_part
                i += 1
            else:
                i += 1

        st.session_state.processed_response = processed_response
        st.session_state.response_processed = True

    markdown_response = ""
    parts = re.split(r'(\[SVG_\d+\])', st.session_state.processed_response)
    for part in parts:
        if part.startswith('[SVG_') and part.endswith(']'):
            svg_index = int(part[5:-1]) - 1
            if svg_index < len(st.session_state.svg_contents):
                st.markdown(f"**{part}**")
                with st.expander(f"查看完整 SVG 代码 {svg_index + 1}", expanded=False):
                    st.code(st.session_state.svg_contents[svg_index], language='svg')
                st.markdown(render_svg(st.session_state.svg_contents[svg_index]), unsafe_allow_html=True)
                markdown_response += f"\n\n**{part}**\n\n[SVG 图像]\n\n"
        else:
            st.markdown(part)
            markdown_response += part

    markdown_response = re.sub(r'\n{3,}', '\n\n', markdown_response)
    markdown_response = markdown_response.strip()
    st.session_state.markdown_response = markdown_response


def log_interaction(input_type, user_input, ai_response):
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"{log_dir}/interaction_{timestamp}.json"

    log_data = {
        "timestamp": timestamp,
        "input_type": input_type,
        "user_input": user_input,
        "ai_response": ai_response
    }

    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, ensure_ascii=False, indent=2)


def stream_response(user_input, input_type):
    response_placeholder = st.empty()
    try:
        messages = st.session_state.user_data[st.session_state.user_session_id]['messages']
        prompt = f"请{'解释这个概念' if input_type == 'concept' else '总结归纳以下文本，并生成一个可视化图示'}：{user_input}"
        messages.append({"role": "user", "content": prompt})

        client = OpenAI(
            api_key=st.session_state.config["api_key"],
            base_url=st.session_state.config["base_url"]
        )

        st.session_state.full_response = ""
        for chunk in client.chat.completions.create(
                model=st.session_state.config["model"],
                messages=messages,
                stream=True,
                max_tokens=st.session_state.config["max_tokens"]
        ):
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                st.session_state.full_response += content
                response_placeholder.markdown(st.session_state.full_response)
            elif chunk.choices and chunk.choices[0].finish_reason:
                break

        log_interaction(input_type, user_input, st.session_state.full_response)
        return True
    except Exception as e:
        st.error(f"Stream error: {str(e)}")
        return False
    finally:
        response_placeholder.empty()
        st.session_state.response_processed = False
        messages.append({"role": "assistant", "content": st.session_state.full_response})

def clear_response():
    st.session_state.full_response = ""
    st.session_state.processed_response = ""
    st.session_state.markdown_response = ""
    st.session_state.svg_contents = []
    st.session_state.response_processed = False
    st.session_state.display_response = False

def initialize_session_state():
    default_states = {
        'config': DEFAULT_CONFIG.copy(),
        'config_updated': False,
        'input_type': "concept",
        'user_input': {"concept": "", "text": ""},
        'display_response': False,
        'temp_config': DEFAULT_CONFIG.copy(),  # 添加临时配置
        'full_response': "",
        'processed_response': "",
        'markdown_response': "",
        'svg_contents': [],
        'response_processed': False
    }

    for key, default_value in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

def main():
    st.title("概念解释与文本总结工具")

    # 初始化会话状态
    initialize_session_state()

    main_container = st.container()

    with main_container:
        config_sidebar()
        get_user_data()

        input_type = st.radio("选择输入类型", ("概念解释", "文本总结"), key="input_type_radio")
        current_input_type = "concept" if input_type == "概念解释" else "text"

        if current_input_type == "concept":
            user_input = st.text_input("请输入您想要解释的复杂概念：",
                                       value=st.session_state.user_input["concept"])
        else:
            user_input = st.text_area("请输入您想要总结的文本：",
                                      value=st.session_state.user_input["text"],
                                      height=200)

        st.session_state.user_input[current_input_type] = user_input

        submit_button = st.button("提交", key="submit_button")

    response_container = st.container()

    if submit_button:
        with response_container:
            clear_response()
            st.empty()
            with st.spinner('正在生成回答，请稍候...'):
                st.subheader("AI 解释/总结过程")
                success = stream_response(user_input, current_input_type)
                if success:
                    st.session_state.display_response = True
                    process_and_display_response()
                    st.session_state.input_type = current_input_type
    elif st.session_state.display_response:
        with response_container:
            st.subheader("AI 解释/总结结果")
            process_and_display_response()

    if st.session_state.display_response and 'markdown_response' in st.session_state:
        st.code(st.session_state.markdown_response, language='markdown')

if __name__ == "__main__":
    main()
