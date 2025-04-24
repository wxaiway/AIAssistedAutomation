# Markdown to Presentation Converter

这个项目提供了一个 Python 脚本，用于将 Markdown 文件转换为各种演示格式，包括 PDF、PPTX、HTML、PNG 和 JPEG。它使用 Marp CLI 进行转换，并支持自定义主题。

## 功能

- 将单个 Markdown 文件或整个目录中的 Markdown 文件转换为多种格式
- 支持输出为 PDF、PPTX、HTML、PNG 和 JPEG 格式
- 允许使用自定义 CSS 主题
- 自动处理 Marp 配置
- 支持在无图形界面的 Linux 服务器上运行

## 安装

### 在 Mac 上安装

1. 安装 Node.js（如果尚未安装）：
   ```
   brew install node
   ```

2. 安装 Marp CLI：
   ```
   npm install -g @marp-team/marp-cli
   ```

3. 安装 Python 依赖：
   ```
   pip install Pillow pdf2image
   ```

4. 安装 Poppler：
   ```
   brew install poppler
   ```

### 在 AliOS Linux 服务器上安装

运行以下命令：

```bash
# 更新系统包
sudo yum update -y

# 安装 Python 3 (如果尚未安装)
sudo yum install python3 python3-pip -y

# 安装必要的系统依赖
sudo yum install gcc libffi-devel openssl-devel -y

# 安装 Chromium (用于 Marp CLI 的无头浏览器操作)
sudo yum install chromium -y

# 安装 poppler-utils（用于 pdf2image）
sudo yum install poppler-utils -y

# 安装必要的 Python 包
pip install pdf2image Pillow

# 安装 Node.js 和 npm
sudo yum install -y nodejs npm

# 安装 Marp CLI
sudo npm install -g @marp-team/marp-cli
```

## 使用方法

1. 转换单个文件到所有格式：
   ```
   python md_to_ppt.py input.md output_dir
   ```

2. 转换单个文件到指定格式：
   ```
   python md_to_ppt.py input.md output_dir --formats pdf png
   ```

3. 使用自定义主题：
   ```
   python md_to_ppt.py input.md output_dir --theme path/to/custom-theme.css
   ```

4. 处理整个目录：
   ```
   python md_to_ppt.py input_directory output_dir
   ```

5. 组合使用：
   ```
   python md_to_ppt.py input_directory output_dir --formats pptx png --theme custom-theme.css
   ```

## 自定义主题

创建一个 `custom-theme.css` 文件来自定义演示文稿的样式。例如：

```css
/* custom-theme.css */
@import 'default';

section {
  background: #f5f5f5;
  font-family: Arial, sans-serif;
}

h1 {
  color: #333;
  font-size: 2.5em;
}

h2 {
  color: #666;
  font-size: 2em;
}
```

更多主题模板可以参考：https://github.com/zhaoluting/marp-themes/tree/master

## 注意事项

- 确保您的系统上安装了所有必要的依赖。
- 在无图形界面的服务器上运行时，确保已正确配置 Chromium。
- 对于大文件或复杂的演示文稿，转换过程可能需要一些时间。

