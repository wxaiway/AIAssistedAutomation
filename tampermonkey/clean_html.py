import re
from bs4 import BeautifulSoup

def clean_html(html_content):
    """
    清理 HTML 内容，移除指定的干扰项和base64图片。
    """
    # 使用 BeautifulSoup 解析 HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # 定义需要移除的属性列表
    attrs_to_remove = [
        'd', 'style', 'id', 'xmlns', 'viewbox', 'fill-opacity', 'width', 'height',
        'preserveaspectratio', 'clip-rule', 'fill-rule', 'opacity', 'role',
        'data-follow-fill', 'fetchpriority', 'loading', 'crossorigin'
    ]

    # 遍历所有标签，移除指定的属性
    for tag in soup.find_all(True):  # 遍历所有标签
        for attr in attrs_to_remove:
            if attr in tag.attrs:
                del tag[attr]

    # 清理base64图片
    cleaned_html = str(soup)
    cleaned_html = re.sub(r'data:image/[^;]+;base64,[a-zA-Z0-9+/]+={0,2}', '[BASE64_IMAGE]', cleaned_html)

    return cleaned_html

def clean_js(js_content):
    """
    清理 JavaScript 文件中的所有 base64 数据。
    """
    # 使用正则表达式替换所有 base64 数据
    cleaned_js = re.sub(r'("data:[^;]+;base64,)[a-zA-Z0-9+/]+={0,2}', r'\1[BASE64_DATA]', js_content)

    return cleaned_js

def read_and_clean_file(file_path):
    """
    从指定文件读取内容，清理后返回。
    """
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # 根据文件扩展名决定使用哪个清理函数
        if file_path.endswith('html'):
            cleaned_content = clean_html(content)
        elif file_path.endswith('.js'):
            cleaned_content = clean_js(content)
        else:
            print(f"不支持的文件类型: {file_path}")
            return

        # 打印清理后的内容（不换行）
        print(cleaned_content)

        # 如果需要保存到新文件，可以使用以下代码：
        # output_path = f'cleaned_{file_path}'
        # with open(output_path, 'w', encoding='utf-8') as output_file:
        #     output_file.write(cleaned_content)

    except FileNotFoundError:
        print(f"错误：文件 '{file_path}' 未找到！")
    except Exception as e:
        print(f"发生错误：{e}")

# 指定文件路径
file_path = 'original_html'

# 调用函数读取和清理文件
read_and_clean_file(file_path)
