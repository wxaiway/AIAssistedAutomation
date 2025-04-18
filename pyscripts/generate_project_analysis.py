import os
import argparse
import base64

def read_file(file_path):
    """读取文件，区分文本和二进制文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return {"type": "text", "content": content}
    except UnicodeDecodeError:
        # 这可能是二进制文件
        with open(file_path, 'rb') as file:
            binary_content = file.read()
            encoded = base64.b64encode(binary_content).decode('ascii')
            return {"type": "binary", "content": encoded}

def write_file(file_path, file_data):
    """写入文件，根据类型区分处理"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    if file_data["type"] == "text":
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(file_data["content"])
    elif file_data["type"] == "binary":
        try:
            binary_data = base64.b64decode(file_data["content"])
            with open(file_path, 'wb') as file:
                file.write(binary_data)
        except Exception as e:
            print(f"错误:无法重建二进制文件 {file_path}: {e}")

def should_include(path, name, exclude_list, directory):
    full_path = os.path.normpath(os.path.join(path, name))
    rel_path = os.path.relpath(full_path, directory)
    for item in exclude_list:
        if item.endswith('/'):  # 是目录
            if rel_path == item.rstrip('/') or rel_path.startswith(item):
                return False
        else:  # 是文件
            if rel_path == item or name == item:
                return False
    return True

def explore_directory(directory, key_files=None, extensions=None, exclude_list=None):
    result = []
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if should_include(root, d, exclude_list, directory)]

        if not should_include(os.path.dirname(root), os.path.basename(root), exclude_list, directory):
            continue

        level = root.replace(directory, '').count(os.sep)
        indent = '  ' * level
        result.append(f'{indent}- {os.path.basename(root)}/')
        for file in files:
            if should_include(root, file, exclude_list, directory) and \
               (not extensions or any(file.endswith(ext) for ext in extensions)) and \
               (not key_files or file in key_files):
                result.append(f'{indent}- {file}')
    return '\n'.join(result)

def generate_file_contents(directory, key_files=None, extensions=None, exclude_list=None):
    result = []
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if should_include(root, d, exclude_list, directory)]

        if not should_include(os.path.dirname(root), os.path.basename(root), exclude_list, directory):
            continue

        for file in files:
            if should_include(root, file, exclude_list, directory) and \
               (not extensions or any(file.endswith(ext) for ext in extensions)) and \
               (not key_files or file in key_files):
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, directory)
                file_data = read_file(file_path)
                result.append(f"File: {relative_path}")
                result.append(f"Type: {file_data['type']}")
                result.append("```")
                result.append(file_data['content'])
                result.append("```")
                result.append("")  # 在每个文件内容后添加空行
    return '\n'.join(result)

def parse_project_file(file_path):
    """
    解析项目分析文件并提取文件路径和内容
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    # 查找"文件内容"部分
    if "文件内容:" not in content:
        print("错误: 在导入文件中未找到'文件内容:'部分。")
        return {}
    
    file_content_section = content.split("文件内容:")[1].strip()
    # 解析文件内容部分以提取路径和内容
    files_data = {}
    file_entries = file_content_section.split("File: ")
    for entry in file_entries[1:]:  # 跳过第一个空部分
        lines = entry.split('\n', 2)  # 最多分成3部分
        if len(lines) < 3:
            continue
        file_path = lines[0].strip()
        type_line = lines[1]
        remaining_content = lines[2]
        
        # 提取文件类型
        file_type = "text"  # 默认值
        if type_line.startswith("Type:"):
            file_type = type_line.split(":", 1)[1].strip()
        
        # 查找三个反引号之间的内容
        start_marker = "```\n"
        end_marker = "\n```"
        
        start_idx = remaining_content.find(start_marker)
        if start_idx == -1:
            continue
        start_idx += len(start_marker)
        end_idx = remaining_content.find(end_marker, start_idx)
        if end_idx == -1:
            continue
        file_content = remaining_content[start_idx:end_idx]
        files_data[file_path] = {"type": file_type, "content": file_content}
    return files_data

def recreate_project(target_directory, files_data):
    """
    从解析的数据重建项目目录和文件
    """
    os.makedirs(target_directory, exist_ok=True)
    for file_path, file_data in files_data.items():
        full_path = os.path.join(target_directory, file_path)
        write_file(full_path, file_data)
        print(f"已创建: {full_path} ({file_data['type']})")

def export_project(directory, key_files, extensions, exclude_list, output_file):
    """
    将项目结构和文件内容导出到文件
    """
    project_name = os.path.basename(directory)
    output = f"""
请根据以下项目结构和代码内容，帮助我修改和优化代码。

项目名称: {project_name}

修改需求:
[在此处描述你的修改需求]

项目结构:
{explore_directory(directory, key_files, extensions, exclude_list)}

文件内容:
{generate_file_contents(directory, key_files, extensions, exclude_list)}

请根据上述信息和我的修改需求，提供详细的代码修改建议和优化方案。如果需要添加新文件或对现有文件进行大幅修改，请提供完整的代码。谢谢！
"""

    print(f"导出项目结构和内容到{output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output)

def main():
    parser = argparse.ArgumentParser(description="生成项目结构和代码分析或从分析文件重建项目。")
    parser.add_argument("-d", "--directory", default=os.getcwd(), help="指定项目目录")
    parser.add_argument("-f", "--files", nargs='+', help="指定要包含的关键文件")
    parser.add_argument("-e", "--extensions", nargs='+', default=['.py'], help="指定要包含的文件扩展名（例如 .py .js .html）")
    parser.add_argument("-x", "--exclude", nargs='+', default=[], help="指定要排除的文件和目录（目录用'/'后缀表示）")
    parser.add_argument("-o", "--output", default="project_analysis.txt", help="导出模式的输出文件")
    parser.add_argument("-i", "--import-file", help="从此文件导入并重建项目")
    parser.add_argument("-t", "--target", help="重建项目的目标目录（仅与--import-file一起使用）")
    args = parser.parse_args()

    # 导入模式
    if args.import_file:
        if not os.path.exists(args.import_file):
            print(f"错误:导入文件'{args.import_file}'不存在。")
            return
        target_dir = args.target or os.path.join(os.getcwd(), "recreated_project")
        files_data = parse_project_file(args.import_file)
        recreate_project(target_dir, files_data)
        print(f"项目已成功重建于: {target_dir}")
        return

    # 导出模式（默认）
    directory = os.path.abspath(args.directory)
    key_files = args.files
    extensions = args.extensions
    exclude_list = args.exclude
    output_file = args.output
    export_project(directory, key_files, extensions, exclude_list, output_file)
    print(f"项目分析已导出至: {output_file}")

if __name__ == '__main__':
    main()

