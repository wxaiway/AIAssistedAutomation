## 公众号

伟贤AI之路

![伟贤AI之路](../images/mp.jpg)

## 文章介绍

[DeepSeek 实战：打造你的专属 AI 助手，从概念到图示仅需几步！](https://mp.weixin.qq.com/s/tSa8DcZfRsVucga9ChHXiA)

## 概念解释与文本总结工具

这是一个基于 Streamlit 和 OpenAI API 开发的交互式 Web 应用，用于解释复杂概念和总结文本。该工具利用人工智能生成详细的解释、总结和可视化 SVG 图表。

### 功能特点

- 概念解释：通过生活化示例和清晰讲解帮助用户理解复杂概念
- 文本总结：提取关键信息，分析逻辑结构，生成简洁总结
- 可视化图示：自动生成 SVG 格式的信息图表，直观展示概念或总结
- 交互式界面：用户友好的 Streamlit 界面，支持实时输入和响应
- 动态内容更新：每次新的查询都会清除之前的内容，确保信息的相关性

### 安装指南

1. 确保您的系统已安装 Python 3.7 或更高版本。

2. 安装所需的 Python 包：

```
pip install streamlit openai
```

3. 设置环境变量：
在系统环境变量中设置 `DASHSCOPE_API_KEY`：

```
DASHSCOPE_API_KEY=your_api_key_here
```


### 使用方法

1. 运行 Streamlit 应用：

```
streamlit run concept_summarizer.py
```

2. 在浏览器中打开显示的本地 URL（通常是 `http://localhost:8501`）

3. 选择输入类型（概念解释或文本总结）

4. 输入您想要解释的概念或需要总结的文本

5. 查看生成的解释、总结和可视化图表

6. 使用 Screen 或 tmux 在后台运行应用：

### 长期服务

```
screen -S concept_summarizer
streamlit run concept_summarizer.py --server.port 8501
```

按 Ctrl+A 然后按 D 来分离 screen 会话

