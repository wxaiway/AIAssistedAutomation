##简介

MD2WD是一个轻量级Web应用，用于将Markdown文本转换为Word文档或HTML文件。它提供了实时预览功能，特别优化了数学公式的处理，非常适合学术文档、教学材料和技术文档的编写与转换。

## 功能特点

- 💻 基于Web的简洁用户界面
- 🔍 实时Markdown预览
-➕ 数学公式自动转换（LaTeX格式适配）
- 📝 智能文本格式调整
-📊 角度符号自动处理
-📋 多选题格式优化
-📤 一键导出为Word文档或HTML文件

## 安装部署

### 依赖要求

- Python3.6+
- Flask
- markdown2
- pandoc (外部工具)

### 安装步骤

1. **安装Python依赖**

```bash
pip install flask markdown2
```

2. **安装Pandoc**

- **Windows**:
  从[Pandoc官网](https://pandoc.org/installing.html)下载并安装。

- **macOS**:
```bash
brew install pandoc
```

- **Linux** (Ubuntu/Debian):
```bash
sudo apt-get install pandoc
```

3. **下载项目代码**

```bash
cd md2wd
```

4. **启动应用**

```bash
python app.py
```

应用将在`http://127.0.0.1:5000/`上运行。

## 使用方法

### 基本操作

1. 打开浏览器访问`http://127.0.0.1:5000/`
2. 在左侧编辑区输入Markdown内容
3. 右侧将实时显示渲染后的预览效果

### 数学公式处理

点击"Convert Math Format"按钮可将LaTeX风格的数学公式格式转换：
- `\( ... \)` 将转换为 `$ ... $`（行内公式）
- `\[ ... \]` 将转换为 `$$ ... $$`（独立公式）

这在导出到Word时特别有用，确保公式能够被正确识别。

### 导出功能

- **导出为Word**: 点击"Export to Word"按钮，将自动下载转换后的.docx文件
- **导出为HTML**:点击"Export to HTML"按钮，将自动下载转换后的HTML文件
- **复制Markdown**: 点击"Copy Markdown"按钮，可以复制当前处理后的Markdown文本

## 技术原理

### Markdown处理流程

1. **文本预处理**：
   - 应用程序首先对原始Markdown文本进行一系列预处理
   - 包括数学公式格式转换、角度符号处理、多选题格式调整等

2. **Pandoc转换**：- 使用Pandoc工具将预处理后的Markdown转换为目标格式
   - 对于HTML预览，使用`--mathjax`选项启用数学公式渲染

3. **前端渲染**：- HTML预览通过MathJax库实现数学公式的美观渲染
   - 实现了防抖动的实时预览功能，提高用户体验

### 主要处理功能

1. **数学公式转换**：
   ```python
   content = re.sub(r'\\\(\s*', '$', content)
   content = re.sub(r'\s*\\\)', '$', content)
   content = re.sub(r'\\\[\s*', '$$', content)
   content = re.sub(r'\s*\\\]', '$$', content)
   ```

2. **角度符号处理**：
   为角度表示法（如30^2）添加\circ符号，使其在Word中正确显示为角度

3. **多选题格式优化**：
   自动调整多选题选项的排版格式
