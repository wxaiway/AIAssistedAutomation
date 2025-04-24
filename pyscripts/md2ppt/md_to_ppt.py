import argparse
import os
import subprocess
from pdf2image import convert_from_path
import shutil
import sys

def inject_marp_header(input_file, output_file, theme_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        content = file.read()

    marp_header = f"""---
marp: true
theme: {os.path.abspath(theme_file)}
paginate: true
size: 16:9
---

"""
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(marp_header + content)

def convert_md_to_formats(input_file, output_dir, formats, theme_file):
    input_file = os.path.abspath(input_file)
    output_dir = os.path.abspath(output_dir)
    theme_file = os.path.abspath(theme_file)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    filename = os.path.splitext(os.path.basename(input_file))[0]
    preprocessed_file = os.path.join(output_dir, f"preprocessed_{filename}.md")

    # 创建预处理的 Markdown 文件
    inject_marp_header(input_file, preprocessed_file, theme_file)

    try:
        pdf_generated = False
        for format in formats:
            output_file = os.path.join(output_dir, f"{filename}.{format}")

            if format in ['pdf', 'pptx', 'html']:
                marp_command = [
                    "marp", "--html", "--allow-local-files",
                    "--theme", theme_file,
                    "--output", output_file,
                    preprocessed_file
                ]
                print(f"执行命令: {' '.join(marp_command)}")
                result = subprocess.run(marp_command, check=False, cwd=os.path.dirname(input_file), capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"错误: Marp 命令失败")
                    print(f"标准输出: {result.stdout}")
                    print(f"标准错误: {result.stderr}")
                    sys.exit(1)
                print(f"已生成 {output_file}")
                if format == 'pdf':
                    pdf_generated = True

            elif format in ['png', 'jpeg']:
                if not pdf_generated:
                    pdf_file = os.path.join(output_dir, f"{filename}.pdf")
                    marp_command = [
                        "marp", "--html", "--allow-local-files",
                        "--theme", theme_file,
                        "--output", pdf_file,
                        preprocessed_file
                    ]
                    print(f"执行命令: {' '.join(marp_command)}")
                    result = subprocess.run(marp_command, check=False, cwd=os.path.dirname(input_file), capture_output=True, text=True)
                    if result.returncode != 0:
                        print(f"错误: Marp 命令失败")
                        print(f"标准输出: {result.stdout}")
                        print(f"标准错误: {result.stderr}")
                        sys.exit(1)
                    pdf_generated = True

                pages = convert_from_path(pdf_file, dpi=300)
                for i, page in enumerate(pages):
                    image_file = os.path.join(output_dir, f"{filename}_{i + 1}.{format}")
                    page.save(image_file, format.upper())
                print(f"已生成 {format.upper()} 文件在 {output_dir}")

    except Exception as e:
        print(f"发生错误: {str(e)}")
        sys.exit(1)

def process_input(input_path, output_dir, formats, theme_file):
    input_path = os.path.abspath(input_path)
    output_dir = os.path.abspath(output_dir)
    theme_file = os.path.abspath(theme_file)

    if os.path.isfile(input_path):
        convert_md_to_formats(input_path, output_dir, formats, theme_file)
    elif os.path.isdir(input_path):
        for filename in os.listdir(input_path):
            if filename.endswith('.md'):
                file_path = os.path.join(input_path, filename)
                file_output_dir = os.path.join(output_dir, os.path.splitext(filename)[0])
                convert_md_to_formats(file_path, file_output_dir, formats, theme_file)
    else:
        print(f"错误：{input_path} 既不是文件也不是目录")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="将Markdown文件转换为指定格式（PDF、PPTX、HTML、PNG和JPEG）")
    parser.add_argument("input_path", help="输入的Markdown文件或目录路径")
    parser.add_argument("output_dir", help="输出目录路径")
    parser.add_argument("--formats", nargs='+', default=['pdf', 'pptx', 'png'],
                        help="输出格式，可选 pdf, pptx, html, png, jpeg，可以多选")
    parser.add_argument("--theme", default="default", help="自定义主题CSS文件路径")
    args = parser.parse_args()

    process_input(args.input_path, args.output_dir, args.formats, args.theme)
