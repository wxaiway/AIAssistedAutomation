import os
import re
import argparse

def parse_txt_to_md(txt_content):
    # 首先去除首尾的空白字符
    txt_content = txt_content.strip()

    # 初始化变量以避免未定义错误
    title = ''
    author = ''
    focus_question = ''
    body = ''

    # 查找 'focus question' 关键字来进一步分割文本，忽略大小写，并考虑不同符号
    focus_question_match = re.search(r'\sfocus\squestion[:,\s]*(.*?\?)', txt_content, re.IGNORECASE)

    if focus_question_match:
        before_focus_question = txt_content[:focus_question_match.start()].strip()
        focus_question = focus_question_match.group(1).strip()
        after_focus_question = txt_content[focus_question_match.end():].strip()

        title_author_match = re.match(r'^(?P<title>.*?)\swritten\sby\s(?P<author>.*)', before_focus_question, re.IGNORECASE)
        
        if title_author_match:
            title = title_author_match.group('title').strip()
            author_parts = re.split(r'\s*,\s*', title_author_match.group('author').strip(), maxsplit=1)
            author = author_parts[0]
            body = after_focus_question
        else:
            title = before_focus_question
            body = after_focus_question
    else:
        title_author_match = re.match(r'^(?P<title>.*?)\swritten\sby\s(?P<author>.*)', txt_content, re.IGNORECASE)
        
        if title_author_match:
            title = title_author_match.group('title').strip()
            author_parts = re.split(r'\s*,\s*', title_author_match.group('author').strip(), maxsplit=1)
            author = author_parts[0]
            if len(author_parts) > 1:
                body = author_parts[1].strip()
            else:
                body = ''
        else:
            body = txt_content

    md_content = f"## Title\n\n{title or 'No title'}\n\n"
    md_content += f"## Author\n\nWritten by {author}\n\n" if author else "## Author\n\nNo author information\n\n"
    md_content += f"## Focus question\n\n{focus_question or 'No focus question'}\n\n"
    md_content += f"## Body\n\n{body}"

    return md_content

def convert_txt_files_to_md(src_directory, dest_directory):
    if not os.path.exists(dest_directory):
        os.makedirs(dest_directory)

    for filename in os.listdir(src_directory):
        if filename.endswith(".txt"):
            txt_path = os.path.join(src_directory, filename)
            md_filename = os.path.splitext(filename)[0] + '.md'
            md_path = os.path.join(dest_directory, md_filename)

            with open(txt_path, 'r', encoding='utf-8') as file:
                txt_content = file.read()

            try:
                md_content = parse_txt_to_md(txt_content)
                with open(md_path, 'w', encoding='utf-8') as file:
                    file.write(md_content)
            except Exception as e:
                print(f"Error processing file {filename}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert TXT files to Markdown.")
    parser.add_argument('src_dir', help='Source directory containing TXT files.')
    parser.add_argument('dest_dir', help='Destination directory for MD files.')

    args = parser.parse_args()

    convert_txt_files_to_md(args.src_dir, args.dest_dir)
