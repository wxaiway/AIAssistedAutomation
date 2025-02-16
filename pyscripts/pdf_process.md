## 公众号

伟贤AI之路

![伟贤AI之路](../images/mp.jpg)

## 文章介绍

[AI 时代，如何用 Python 脚本轻松搞定 PDF 需求？](https://mp.weixin.qq.com/s/jv9DrRYhD3bK6WFMH881cQ)


这个 Python 脚本是一个多功能 PDF 处理工具，可以执行以下操作：
1. 从 PDF 中提取指定页面
2. 将 PDF 页面转换为 JPG 或 PNG 图像
3. 处理加密的 PDF 文件
4. 合并多个 PDF 文件

## 1. 安装依赖

在使用这个脚本之前，您需要安装以下 Python 库：

```bash
pip install PyPDF2 pdf2image Pillow
```


[poppler 官方页](https://poppler.freedesktop.org/)

注意：
- 对于 Windows 用户，可以下载 poppler for Windows 并将其添加到系统路径中。
- 对于 Mac 用户，可以使用 Homebrew 安装 poppler：brew install poppler
- 对于 Linux 用户，可以使用包管理器安装 poppler，例如 Ubuntu：sudo apt-get install poppler-utils


## 2. 使用方法
这个脚本现在支持两种主要操作：处理单个 PDF 和合并多个 PDF。

### 2.1 处理单个 PDF
基本用法如下：

```
python pdf_processor.py process <input_pdf> <page_range> <output_file> [-d DPI] [-p PASSWORD]
```

- 参数说明：
<input_pdf>: 输入 PDF 文件的路径
<page_range>: 要处理的页面范围，例如 '1,3-5,7-9'
<output_file>: 输出文件的路径（支持 .jpg, .jpeg, .png, .pdf）
-d 或 --dpi: 图像 DPI（仅用于 jpg 和 png 输出，默认: 300）
-p 或 --password: PDF 密码（如果 PDF 加密）

- 示例：
1.将 PDF 的第 1、3、5 页转换为 JPG：
```
python pdf_processor.py process input.pdf 1,3,5 output.jpg
```

2.将 PDF 的第 1 到 10 页转换为高质量 PNG：
```
python pdf_processor.py process input.pdf 1-10 output.png -d 600
```

3.从加密的 PDF 中提取特定页面并创建新的 PDF：
```
python pdf_processor.py process encrypted.pdf 2,4,6,8-10 output.pdf -p your_password
```

### 2.2 合并多个 PDF

基本用法如下：
```
python pdf_processor.py merge <input_pdf1> <input_pdf2> ... <output_pdf>
```

- 参数说明：

<input_pdf1>, <input_pdf2>, ...: 要合并的 PDF 文件路径
<output_pdf>: 合并后的输出 PDF 文件路径

- 示例：

合并三个 PDF 文件：
```
python pdf_processor.py merge input1.pdf input2.pdf input3.pdf merged_output.pdf
```