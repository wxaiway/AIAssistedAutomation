import os
import argparse

def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def should_include(path, name, exclude_list, directory):
    full_path = os.path.normpath(os.path.join(path, name))
    rel_path = os.path.relpath(full_path, directory)
    for item in exclude_list:
        if item.endswith('/'):  # It's a directory
            if rel_path == item.rstrip('/') or rel_path.startswith(item):
                return False
        else:  # It's a file
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
                result.append(f'{indent}  - {file}')
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
                result.append(f"File: {relative_path}")
                result.append("```")
                result.append(read_file(file_path))
                result.append("```")
                result.append("")  # Add a blank line after each file content
    return '\n'.join(result)

def main():
    parser = argparse.ArgumentParser(description="Generate project structure and code analysis.")
    parser.add_argument("-d", "--directory", default=os.getcwd(), help="Specify the project directory")
    parser.add_argument("-f", "--files", nargs='+', help="Specify key files to include")
    parser.add_argument("-e", "--extensions", nargs='+', default=['.py'], help="Specify file extensions to include (e.g., .py .js .html)")
    parser.add_argument("-x", "--exclude", nargs='+', default=[], help="Specify files and directories to exclude (use '/' suffix for directories)")
    args = parser.parse_args()

    directory = os.path.abspath(args.directory)
    key_files = args.files
    extensions = args.extensions
    exclude_list = args.exclude

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

    print(output)

    # Optionally, save the output to a file
    with open('project_analysis.txt', 'w', encoding='utf-8') as f:
        f.write(output)

if __name__ == '__main__':
    main()
