import streamlit as st
import uuid
import os
import hashlib
from openai import OpenAI, AuthenticationError, APIError

# 生成或获取用户特定的会话ID
if 'user_session_id' not in st.session_state:
    st.session_state.user_session_id = str(uuid.uuid4())

# 使用用户会话ID来获取或初始化用户特定的数据
def get_user_data():
    if 'user_data' not in st.session_state:
        st.session_state.user_data = {}

    if st.session_state.user_session_id not in st.session_state.user_data:
        st.session_state.user_data[st.session_state.user_session_id] = {
            'messages': [
                {"role": "system", "content": "你是一个AI助手，请回答用户提出的问题。"}
            ],
            'uploaded_files': [],
            'api_key': 'sk-',
            'base_url': 'https://dashscope.aliyuncs.com/compatible-mode/v1',
            'model_name': 'deepseek-r1',
            'past_sessions': []
        }

    return st.session_state.user_data[st.session_state.user_session_id]

# 更新用户数据的辅助函数
def update_user_data(key, value):
    user_data = get_user_data()
    user_data[key] = value

# 保存当前会话
def save_current_session():
    user_data = get_user_data()
    if len(user_data['messages']) > 1:  # 只有当有实际对话时才保存
        current_session = {
            'id': st.session_state.user_session_id,
            'messages': user_data['messages']
        }
        # 检查是否已存在相同ID的会话，如果存在则更新，不存在则插入
        existing_session = next((session for session in user_data['past_sessions'] if session['id'] == current_session['id']), None)
        if existing_session:
            existing_session.update(current_session)
        else:
            user_data['past_sessions'].insert(0, current_session)
        # 限制保存的会话数量，例如只保留最近的5个会话
        user_data['past_sessions'] = user_data['past_sessions'][:5]

# 加载选定的会话
def load_session(session_id):
    user_data = get_user_data()
    for session in user_data['past_sessions']:
        if session['id'] == session_id:
            st.session_state.user_session_id = session_id
            st.session_state.user_data[session_id] = {
                'messages': session['messages'],
                'uploaded_files': [],
                'api_key': user_data['api_key'],
                'base_url': user_data['base_url'],
                'model_name': user_data['model_name'],
                'past_sessions': user_data['past_sessions']
            }
            break


def save_uploaded_files(upload_dir, uploaded_files):
    """保存上传的 txt 和 markdown 文件到临时目录并返回文件信息"""
    user_data = get_user_data()
    saved_files = []
    current_files = [f["name"] for f in user_data['uploaded_files']]

    for file in uploaded_files:
        if file.name in current_files:
            continue

        if not file.name.lower().endswith(('.txt', '.md', '.markdown')):
            st.warning(f"不支持的文件类型: {file.name}。请上传 .txt 或 .md 文件。")
            continue

        if file.size > 1 * 1024 * 1024:  # 1MB限制
            st.error(f"文件 {file.name} 超过大小限制（1MB）")
            continue

        try:
            # 保存文件到指定目录
            file_path = os.path.join(upload_dir, file.name)
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())

            # 读取文件内容
            with open(file_path, "r", encoding='utf-8') as f:
                content = f.read()

            # 生成内容哈希值
            content_hash = hashlib.md5(content.encode()).hexdigest()

            # 检查重复内容
            if any(f["hash"] == content_hash for f in user_data['uploaded_files']):
                st.info(f"文件 {file.name} 的内容与已上传的文件重复，已跳过。")
                continue

            saved_files.append({
                "name": file.name,
                "content": content,
                "size": file.size,
                "hash": content_hash
            })
            st.success(f"成功上传文件: {file.name}")

        except Exception as e:
            st.error(f"处理文件 {file.name} 时出错: {str(e)}")
            continue

    return saved_files

def format_file_contents(files):
    return "\n".join([f"=== {f['name']} ===\n{f['content']}\n" for f in files])

def get_active_api_config():
    user_data = get_user_data()
    return user_data['base_url'], user_data['api_key'], user_data['model_name']

def process_stream(stream):
    """合并处理思考阶段和响应阶段"""
    thinking_content = ""
    response_content = ""

    # 在状态块外部预先创建响应占位符
    response_placeholder = st.empty()

    with st.status("思考中...", expanded=True) as status:
        thinking_placeholder = st.empty()
        thinking_phase = True  # 思考阶段标记

        for chunk in stream:
            # 解析数据块
            delta = chunk.choices[0].delta
            reasoning = delta.reasoning_content if hasattr(delta, 'reasoning_content') else ""
            content = delta.content if hasattr(delta, 'content') else ""
            role = delta.role if hasattr(delta, 'role') else ""

            # 处理思考阶段
            if thinking_phase:
                if reasoning:
                    thinking_content += reasoning
                    thinking_placeholder.markdown(f"思考过程：\n{thinking_content}")

                # 检测思考阶段结束
                if content:
                    status.update(label="思考完成", state="complete", expanded=False)
                    thinking_phase = False
                    response_placeholder.markdown("回答：\n▌")  # 初始化响应光标

            # 处理响应阶段（无论是否在思考阶段都收集内容）
            if content:
                response_content += content
                if not thinking_phase:
                    response_placeholder.markdown(f"回答：\n{response_content}▌")

        # 流结束后移除光标
        response_placeholder.markdown(f"回答：\n{response_content}")

    return f"{thinking_content}{response_content}"

def display_chat_history():
    user_data = get_user_data()
    for message in user_data['messages']:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def handle_user_input():
    user_data = get_user_data()
    base_url, api_key, model_name = get_active_api_config()

    if not api_key or api_key == 'sk-':
        st.error("请在侧边栏输入有效的 API Key。")
        return

    try:
        client = OpenAI(api_key=api_key, base_url=base_url)

        uploaded_files = st.file_uploader(
            "上传文本文件（支持 .txt 和 .md）",
            type=["txt", "md", "markdown"],
            accept_multiple_files=True,
            key="file_uploader"
        )

        if uploaded_files:
            new_files = save_uploaded_files(dirs, uploaded_files)
            user_data['uploaded_files'].extend(new_files)

        user_content = []
        if user_input := st.chat_input("请问我任何事!"):
            user_content.append(user_input)

            if user_data['uploaded_files']:
                file_content = format_file_contents(user_data['uploaded_files'])
                user_content.append("\n[上传文件内容]\n" + file_content)
                user_data['uploaded_files'] = []  # 清空已处理的文件列表

            full_content = "\n".join(user_content)

            user_data['messages'].append({"role": "user", "content": full_content})
            with st.chat_message("user"):
                st.markdown(user_input)

            with st.chat_message("assistant"):
                try:
                    stream = client.chat.completions.create(
                        model=model_name,
                        messages=user_data['messages'],
                        stream=True
                    )
                    response = process_stream(stream)
                    user_data['messages'].append(
                        {"role": "assistant", "content": response}
                    )
                except AuthenticationError:
                    st.error("API 认证失败。请检查您的 API Key 是否正确。")
                except APIError as e:
                    st.error(f"API 错误: {str(e)}")
                except Exception as e:
                    st.error(f"发生未知错误: {str(e)}")

    except Exception as e:
        st.error(f"设置 OpenAI 客户端时发生错误: {str(e)}")

def main_interface():
    st.title("AI 助手")
    user_data = get_user_data()

    with st.sidebar:
        api_key = st.text_input("API Key", user_data['api_key'], type="password")
        if api_key:
            update_user_data('api_key', api_key)
        else:
            st.warning("请输入有效的 API Key")

        # Base URL 选项
        base_url_options = {
            "DashScope": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "ARK": "https://ark.cn-beijing.volces.com/api/v3",
            "自定义": "custom"
        }
        selected_base_url = st.selectbox(
            "选择 Base URL",
            options=list(base_url_options.keys()),
            index=list(base_url_options.keys()).index("DashScope") if user_data['base_url'] == base_url_options["DashScope"] else 0
        )
        if selected_base_url == "自定义":
            custom_base_url = st.text_input("自定义 Base URL", user_data['base_url'])
            update_user_data('base_url', custom_base_url)
        else:
            update_user_data('base_url', base_url_options[selected_base_url])

        # Model Name 选项
        model_options = {
            "deepseek-r1": "deepseek-r1",
            "deepseek-v3": "deepseek-v3",
            "自定义": "custom"
        }
        selected_model = st.selectbox(
            "选择 Model",
            options=list(model_options.keys()),
            index=list(model_options.keys()).index("deepseek-r1") if user_data['model_name'] == "deepseek-r1" else 0
        )
        if selected_model == "自定义":
            custom_model = st.text_input("自定义 Model Name", user_data['model_name'])
            update_user_data('model_name', custom_model)
        else:
            update_user_data('model_name', model_options[selected_model])

        if st.button("🆕 新会话"):
            save_current_session()  # 保存当前会话
            new_session_id = str(uuid.uuid4())
            st.session_state.user_data[new_session_id] = {
                'messages': [
                    {"role": "system", "content": "你是一个AI助手，请回答用户提出的问题。"}
                ],
                'uploaded_files': [],
                'api_key': user_data['api_key'],  # 保留当前的 API Key
                'base_url': user_data['base_url'],  # 保留当前的 Base URL
                'model_name': user_data['model_name'],  # 保留当前的 Model Name
                'past_sessions': user_data['past_sessions']  # 保留过去的会话记录
            }
            st.session_state.user_session_id = new_session_id
            st.rerun()

        # 显示过去的会话
        st.write("过去的会话：")
        for past_session in user_data['past_sessions']:
            if st.button(f"加载会话 {past_session['id'][:8]}...", key=past_session['id']):
                load_session(past_session['id'])
                st.rerun()

    display_chat_history()
    handle_user_input()

def main():
    if 'user_session_id' not in st.session_state:
        st.session_state.user_session_id = str(uuid.uuid4())

    main_interface()

if __name__ == "__main__":
    dirs = 'uploads/'

    if not os.path.exists(dirs):
        os.makedirs(dirs)

    main()