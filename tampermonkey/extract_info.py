import re
import csv

def extract_info_from_html(html_content):
    # 正则表达式模式
    title_pattern = r'<p class="Ja95nb2Z VdTyguLN">(.*?)</p>'
    url_pattern = r'<a\s+class="hY8lWHgA SF0P5HVG h0CXDpkg"\s+href="(/video/\d+)"'
    like_count_pattern = r'<span class="b3Dh2ia8">(\d+(?:\.\d+)?万?)</span>'

    # 提取标题
    titles = re.findall(title_pattern, html_content)
    # 提取网址
    urls = re.findall(url_pattern, html_content)
    # 提取点赞数
    like_counts = re.findall(like_count_pattern, html_content)

    # 将网址转换为完整URL
    base_url = "https://www.douyin.com"
    full_urls = [f"{base_url}{url}" for url in urls]

    # 确保所有列表长度一致
    max_length = max(len(titles), len(full_urls), len(like_counts))
    titles += [''] * (max_length - len(titles))
    full_urls += [''] * (max_length - len(full_urls))
    like_counts += [''] * (max_length - len(like_counts))

    # 创建CSV文件
    with open('output.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['标题', '网址', '点赞数'])
        for title, url, likes in zip(titles, full_urls, like_counts):
            writer.writerow([title, url, likes])

    print("CSV文件已生成: output.csv")

if __name__ == "__main__":
    # 读取HTML文件内容
    with open('/Users/weixian.lwx/github/AIAssistedAutomation/tampermonkey/original_html', 'r', encoding='utf-8') as file:
        html_content = file.read()

    # 调用函数提取信息并生成CSV
    extract_info_from_html(html_content)