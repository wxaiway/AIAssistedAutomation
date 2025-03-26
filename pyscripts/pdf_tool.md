## 公众号

伟贤AI之路

![伟贤AI之路](../images/mp.jpg)

## 文章介绍

[用 PyMuPDF 和 Pillow 打造 PDF 超级工具](https://mp.weixin.qq.com/s/KH-okJlXSzDFeuJcRPgwjw)

## 依赖库

```
pip install PyMuPDF Pillow
```

## 功能概述

- 处理 PDF：选择特定页面并转换为图片或新的 PDF
- 合并 PDF：将多个 PDF 文件合并为一个
- 提取图片：从 PDF 中提取图片
- 加密 PDF：为 PDF 文件添加密码保护
- 解密 PDF：移除 PDF 文件的密码保护

## 使用方法

### 1. 处理 PDF

```
python pdf_tool.py process <input_pdf> <page_range> <output> [options]
```

- 参数说明：
<input_pdf>: 输入 PDF 文件的路径
<page_range>: 要处理的页面范围，例如 '1,3-5,7-9'
<output>: 输出文件的路径（支持 .jpg, .jpeg, .png, .pdf）

- 选项：
-d, --dpi: 设置图像 DPI（默认：300）
-p, --password: PDF 密码（如果 PDF 加密）
-s, --split-pages: 按每页生成单独的 JPG 或 PNG 文件

- 示例：
```
python pdf_tool.py process input.pdf 1,3-5 output.png -d 200 -s
```

### 2. 合并 PDF

```
python pdf_tool.py merge <input_pdfs> <output>
```

- 参数说明：
<input_pdfs>: 要合并的 PDF 文件路径列表
<output>: 输出的合并 PDF 文件路径

- 示例：
```
python pdf_tool.py merge file1.pdf file2.pdf file3.pdf merged.pdf
```

### 3. 提取图片

```
python pdf_tool.py extract <input_pdf> <page_range> <output_directory> [options]
```

- 参数说明：
<input_pdf>: 输入 PDF 文件的路径
<page_range>: 要提取图片的页面范围，例如 '1,3-5,7-9'
<output_directory>: 保存提取图片的目录路径

- 选项：
-p, --password: PDF 密码（如果 PDF 加密）

- 示例：

```
python pdf_tool.py extract document.pdf 1-5 ./images -p mypassword
```

### 4. 加密 PDF
```
python pdf_tool.py encrypt <input_pdf> <output_pdf> <user_password> [options]
```

- 参数说明：
<input_pdf>: 输入 PDF 文件的路径
<output_pdf>: 输出加密 PDF 文件的路径
<user_password>: 用户密码

- 选项：
-o, --owner_password: 所有者密码（如果不提供，将与用户密码相同）

- 示例：
```
python pdf_tool.py encrypt input.pdf encrypted.pdf userpass -o ownerpass
```

### 5. 解密 PDF
```
python pdf_tool.py decrypt <input_pdf> <output_pdf> <password>
```

- 参数说明：
<input_pdf>: 输入加密 PDF 文件的路径
<output_pdf>: 输出解密 PDF 文件的路径
<password>: PDF 密码

- 示例：

```
python pdf_tool.py decrypt encrypted.pdf decrypted.pdf mypassword
```
