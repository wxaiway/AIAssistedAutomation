import re
import subprocess
import argparse
import os

def prepare_markdown_for_export(content, convert_math=False):
    if convert_math:
        # 替换行内数学公式，包括相邻的空格
        content = re.sub(r'\\\(\s*', '$', content)
        content = re.sub(r'\s*\\\)', '$', content)

        # 替换块级数学公式，包括相邻的空格
        content = re.sub(r'\\\[\s*', '$$', content)
        content = re.sub(r'\s*\\\]', '$$', content)

    # 修复角度符号，只在特定情况下添加 \circ
    def add_circ(match):
        full_match = match.group(0)
        if '$' in full_match:  # 如果匹配内容在数学公式中，不做修改
            return full_match
        num = match.group(1)
        exp = match.group(2)
        if exp.strip() in ['1', '2', '3']:  # 只处理 1, 2, 3 次方
            return f"{num}^{exp}\\circ"
        return full_match

    # 使用负向预查确保不匹配数学公式内的内容
    content = re.sub(r'(\d+)\^(\s*[123](?!\d))(?![^\$]*\$)', add_circ, content)

    # 修复选择题格式，保持原有换行和空格
    def fix_choices(match):
        question = match.group(1)
        choices = match.group(2)
        return f"{question}\n{choices}"

    content = re.sub(r'^(\d+\..+)$\n(\s+[A-D]\..+(?:\n\s+[A-D]\..+)*)',
                     fix_choices, content, flags=re.MULTILINE)

    # 确保每行末尾有两个空格（Markdown 软换行）
    content = re.sub(r'([^\n])$', r'\1  ', content, flags=re.MULTILINE)

    # 保持原有的换行格式
    content = re.sub(r'\n{3,}', r'\n\n', content)

    return content

def convert_to_word(input_file, output_file):
    command = f'pandoc -s {input_file} -o {output_file} --pdf-engine=xelatex --wrap=preserve'
    subprocess.run(command, shell=True, check=True)

def main():
    parser = argparse.ArgumentParser(description='Convert Markdown to Word with optional formula fixes.')
    parser.add_argument('input', help='Input Markdown file')
    parser.add_argument('output', help='Output Word file')
    parser.add_argument('--convert-math', action='store_true', help='Convert math formulas to $ format')
    parser.add_argument('--keep-md', action='store_true', help='Keep the prepared Markdown file')
    args = parser.parse_args()

    prepared_md = 'md_to_word_test.md'

    # 读取输入文件
    with open(args.input, 'r', encoding='utf-8') as file:
        content = file.read()

    # 准备 Markdown 内容
    prepared_content = prepare_markdown_for_export(content, convert_math=args.convert_math)

    # 写入准备好的 Markdown 文件
    with open(prepared_md, 'w', encoding='utf-8') as file:
        file.write(prepared_content)

    # 转换为 Word 文档
    convert_to_word(prepared_md, args.output)

    if not args.keep_md:
        os.remove(prepared_md)

    print(f"转换完成：{args.output}")

if __name__ == "__main__":
    main()
