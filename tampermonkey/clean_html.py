from bs4 import BeautifulSoup

def clean_html(html_content):
    """
    清理 HTML 内容，移除指定的干扰项。
    """
    # 使用 BeautifulSoup 解析 HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # 定义需要移除的属性列表
    attrs_to_remove = [
    'd', 
    'style', 
    'id', 
    'xmlns', 
    'viewbox', 
    'fill-opacity', 
    'width', 
    'height',
    'preserveaspectratio',  # SVG 默认值
    'clip-rule',             # 路径填充规则
    'fill-rule',             # 路径填充规则
    'opacity',               # 透明度
    'role',                  # 辅助功能属性
    'data-follow-fill',      # 冗余数据属性
    'fetchpriority',         # 图片加载优先级
    'loading',               # 懒加载
    'crossorigin'            # 跨域属性
]

    # 遍历所有标签，移除指定的属性
    for tag in soup.find_all(True):  # 遍历所有标签
        for attr in attrs_to_remove:
            if attr in tag.attrs:
                del tag[attr]

    # 返回清理后的 HTML 字符串（不格式化）
    return str(soup)

def read_and_clean_html(file_path):
    """
    从指定文件读取 HTML 内容，清理后返回。
    """
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()

        # 调用清理函数
        cleaned_html = clean_html(html_content)

        # 打印清理后的 HTML（不换行）
        print(cleaned_html)

        # 如果需要保存到新文件，可以使用以下代码：
        # with open('cleaned_html.html', 'w', encoding='utf-8') as output_file:
        #     output_file.write(cleaned_html)

    except FileNotFoundError:
        print(f"错误：文件 '{file_path}' 未找到！")
    except Exception as e:
        print(f"发生错误：{e}")

# 指定文件路径
file_path = 'original_html'

# 调用函数读取和清理 HTML
read_and_clean_html(file_path)