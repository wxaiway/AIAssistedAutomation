import os
import requests
import markdownify
from bs4 import BeautifulSoup
import re
import unicodedata
import hashlib
import time
import json
import csv
import argparse
import random  # 新增random模块
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from pathlib import Path

@dataclass
class ContentFilterConfig:
    """内容过滤配置"""
    paragraph_keywords: List[str] = field(default_factory=list)
    image_hashes: List[str] = field(default_factory=list)
    skip_ads: bool = False
    skip_promotions: bool = False

class WeChatArticleDownloader:
    CONFIG_FILE = "wechat_downloader_config.json"
    
    @staticmethod
    def hash_byte_data(byte_data: bytes) -> str:
        return hashlib.sha256(byte_data).hexdigest()

    @staticmethod
    def remove_nonvisible_chars(text: str) -> str:
        return ''.join(c for c in text if (unicodedata.category(c) != 'Cn' 
                                        and c not in (' ', '\n', '\r')))

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self.CONFIG_FILE
        self.filter_config = self._load_config()

    def _load_config(self) -> ContentFilterConfig:
        default_config = ContentFilterConfig()
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    return ContentFilterConfig(
                        paragraph_keywords=config_data.get('paragraph_keywords', []),
                        image_hashes=config_data.get('image_hashes', []),
                        skip_ads=config_data.get('skip_ads', False),
                        skip_promotions=config_data.get('skip_promotions', False)
                    )
        except Exception as e:
            print(f"加载配置文件失败，将使用默认配置: {str(e)}")
        return default_config

    def _save_config(self) -> None:
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'paragraph_keywords': self.filter_config.paragraph_keywords,
                    'image_hashes': self.filter_config.image_hashes,
                    'skip_ads': self.filter_config.skip_ads,
                    'skip_promotions': self.filter_config.skip_promotions
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置文件失败: {str(e)}")

    def load_urls_from_csv(self, csv_path: str, url_column: str = "链接") -> List[Dict]:
        """从CSV文件加载URL数据"""
        urls = []
        try:
            with open(csv_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if url_column in row and row[url_column].strip():
                        urls.append({
                            'account': row.get('公众号', '').strip(),
                            'title': row.get('标题', '').strip(),
                            'url': row[url_column].strip(),
                            'date': row.get('日期', '').strip()
                        })
        except Exception as e:
            print(f"读取CSV文件失败: {str(e)}")
        return urls

    def filter_content(self, text: str) -> str:
        if not self.filter_config:
            return text
        if self.filter_config.paragraph_keywords:
            text = self._filter_paragraphs(text, self.filter_config.paragraph_keywords)
        return text

    def _filter_paragraphs(self, text: str, keywords: List[str]) -> str:
        lines = [line.strip() for line in text.split('\n')]
        filtered_lines = []
        current_paragraph = []
        
        for line in lines:
            if not line.strip():
                if not self._paragraph_contains_keywords(current_paragraph, keywords):
                    filtered_lines.extend(current_paragraph)
                current_paragraph = []
            else:
                current_paragraph.append(line)

        if not self._paragraph_contains_keywords(current_paragraph, keywords):
            filtered_lines.extend(current_paragraph)

        return '\n\n'.join(filtered_lines) + '\n\n'

    def _paragraph_contains_keywords(self, paragraph: List[str], keywords: List[str]) -> bool:
        paragraph_text = ' '.join(paragraph)
        return any(keyword in paragraph_text for keyword in keywords)

    def download_images(self, soup: BeautifulSoup, account_dir: str) -> None:
        """下载文章中的所有图片并保存到本地"""
        # 创建images目录（与markdown文件同级）
        image_folder = os.path.join(account_dir, 'images')
        os.makedirs(image_folder, exist_ok=True)

        for img in soup.find_all('img'):
            img_link = img.get('data-src') or img.get('src')
            if not img_link:
                continue

            img_link = img_link.replace(' ', '%20')
            
            if not img_link.startswith(('http://', 'https://')):
                img_link = 'https://mp.weixin.qq.com' + img_link

            try:
                with requests.get(img_link, stream=True) as response:
                    response.raise_for_status()
                    file_content = response.content
                    
                    img_hash = self.hash_byte_data(file_content)
                    if img_hash in self.filter_config.image_hashes:
                        continue

                    file_ext = (img.get('data-type') or 'jpg').split('?')[0]
                    filename = f"{img_hash}.{file_ext}"
                    filepath = os.path.join(image_folder, filename)
                    
                    if not os.path.exists(filepath):
                        with open(filepath, 'wb') as f:
                            f.write(file_content)

                    # 更新图片属性指向本地文件（使用相对路径 ./images/）
                    relative_path = f"./images/{filename}"
                    img['data-src'] = relative_path
                    img['src'] = relative_path
            except requests.exceptions.RequestException as e:
                print(f"图片下载失败，URL: {img_link}, 错误: {e}")

    def convert_to_markdown(self, url: str, title: str, create_time: str, 
                          content_soup: BeautifulSoup, account_dir: str) -> tuple:
        """将HTML内容转换为Markdown格式"""
        self.download_images(content_soup, account_dir)
        markdown_content = markdownify.markdownify(str(content_soup))

        # 处理图片路径（确保使用相对路径）
        markdown_soup = BeautifulSoup(markdown_content, 'html.parser')
        for img in markdown_soup.find_all('img'):
            if img.get('data-src') and not img['data-src'].startswith(('http://', 'https://')):
                img['src'] = img['data-src']

        markdown_content = '\n'.join([line + '\n' for line in markdown_content.split('\n') if line.strip()])
        clean_title = self.remove_nonvisible_chars(title)
        
        markdown = f'# {clean_title}\n\n{create_time}\n\nurl: {url}\n\n{markdown_content}\n'
        
        markdown = re.sub('\xa0{1,}', '\n', markdown, flags=re.UNICODE)
        markdown = re.sub(r'\]\(http([^)]*)\)', 
                         lambda x: '](http' + x.group(1).replace(' ', '%20') + ')', 
                         markdown)

        return self.filter_content(markdown), clean_title

    def get_title_with_retry(self, url: str, max_retries: int = 3) -> tuple:
        """获取文章标题，带有重试机制"""
        retries = 0
        while retries < max_retries:
            try:
                # 设置请求头模拟浏览器访问
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'lxml')
                title_element = soup.find('h1', id="activity-name")
                if not title_element:
                    # 尝试其他可能的标题位置
                    title_element = soup.find('h2', class_="rich_media_title") or \
                                  soup.find('h1', class_="article-title")
                    
                if title_element:
                    title = title_element.text.strip()
                    if title:  # 确保标题不为空
                        return title, soup
                
                raise AttributeError("Title element not found")
                
            except Exception as e:
                retries += 1
                error_msg = str(e)
                if retries < max_retries:
                    print(f"Retrying ({retries}/{max_retries}) for URL {url}: Error - {error_msg}")
                    time.sleep(2 ** retries)  # 指数退避
                else:
                    print(f"Failed to retrieve title for URL {url} after {max_retries} retries. Last error: {error_msg}")
                    return None, None

    def process_url(self, url_data: Dict, output_base: str) -> bool:
        """处理单个URL数据"""
        url = url_data['url']
        account_name = url_data.get('account', 'unknown_account') or 'unknown_account'
        
        # 创建公众号专属目录
        account_dir = os.path.join(output_base, account_name)
        os.makedirs(account_dir, exist_ok=True)

        title, soup = self.get_title_with_retry(url)
        if not title or not soup:
            return False

        # 使用CSV中的日期或从网页提取
        create_time = url_data.get('date', '')
        if not create_time:
            match = re.search(r'createTime\s+=\s+\'(.*)\'', str(soup))
            if match:
                create_time = match.group(1)
        create_time = f"publish_time: {create_time}" if create_time else "publish_time: unknown"

        content_soup = soup.find('div', {'class': 'rich_media_content'})
        if not content_soup:
            return False

        markdown, clean_title = self.convert_to_markdown(
            url, title, create_time, content_soup, account_dir)
        
        # 使用CSV中的标题或网页标题
        filename = url_data.get('title', clean_title)
        filename = re.sub(r'[\\/*?:"<>|]', '', filename)
        filepath = os.path.join(account_dir, f"{filename}.md")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown)
        
        print(f'Processed: {account_name} - {filename}.md')
        return True

    def run(self, csv_path: str, output_dir: str = "./articles", url_column: str = "链接"):
        """运行下载器"""
        urls_data = self.load_urls_from_csv(csv_path, url_column)
        if not urls_data:
            print("没有找到可处理的URL")
            return

        os.makedirs(output_dir, exist_ok=True)
        
        success_count = 0
        for url_data in urls_data:
            if self.process_url(url_data, output_dir):
                success_count += 1
            # 随机延迟3-8秒，避免过于频繁请求
            delay = random.uniform(3, 8)
            print(f"等待 {delay:.2f} 秒后继续...")
            time.sleep(delay)
        
        print(f"\n处理完成: 共{len(urls_data)}条, 成功{success_count}条")

def main():
    parser = argparse.ArgumentParser(description='微信公众号文章下载器')
    parser.add_argument('csv_file', help='包含文章URL的CSV文件路径')
    parser.add_argument('-o', '--output', default='./articles', 
                       help='输出目录 (默认: ./articles)')
    parser.add_argument('-c', '--column', default='链接', 
                       help='CSV中包含URL的列名 (默认: 链接)')
    parser.add_argument('--config', help='自定义配置文件路径')
    
    args = parser.parse_args()
    
    # 初始化下载器
    downloader = WeChatArticleDownloader(args.config)
    
    # 运行下载任务
    downloader.run(
        csv_path=args.csv_file,
        output_dir=args.output,
        url_column=args.column
    )

if __name__ == "__main__":
    main()
