from flask import Flask, request, jsonify, send_file
import markdown2
import subprocess
import tempfile
import os
import re
import logging

app = Flask(__name__)

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def prepare_markdown_for_export(content, convert_math=False):
    if convert_math:
        content = re.sub(r'\\\(\s*', '$', content)
        content = re.sub(r'\s*\\\)', '$', content)
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

    def fix_choices(match):
        return f"{match.group(1)}\n{match.group(2)}"

    content = re.sub(r'^(\d+\..+)$\n(\s+[A-D]\..+(?:\n\s+[A-D]\..+)*)',
                     fix_choices, content, flags=re.MULTILINE)

    content = re.sub(r'([^\n])$', r'\1  ', content, flags=re.MULTILINE)
    content = re.sub(r'\n{3,}', r'\n\n', content)

    return content

def run_pandoc(input_path, output_format, extra_args=None):
    command = ['pandoc', '-s', input_path, '-t', output_format, '--wrap=preserve']
    if extra_args:
        command.extend(extra_args)

    result = subprocess.run(command, check=True, capture_output=True, text=True)
    logger.info(f"Pandoc stdout: {result.stdout}")
    logger.info(f"Pandoc stderr: {result.stderr}")
    return result.stdout

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/preview', methods=['POST'])
def preview():
    markdown_text = request.json['markdown']
    prepared_markdown = prepare_markdown_for_export(markdown_text, convert_math=False)

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as temp:
        temp.write(prepared_markdown)
        temp_path = temp.name

    try:
        html = run_pandoc(temp_path, 'html', ['--mathjax'])
        return jsonify({'html': html, 'prepared_markdown': prepared_markdown})
    finally:
        os.remove(temp_path)

@app.route('/convert_math', methods=['POST'])
def convert_math():
    markdown_text = request.json['markdown']
    converted_markdown = prepare_markdown_for_export(markdown_text, convert_math=True)
    return jsonify({'converted_markdown': converted_markdown})

@app.route('/export', methods=['POST'])
def export():
    markdown_text = request.json['markdown']
    format = request.json['format']

    if format not in ['docx', 'html']:
        return jsonify({"error": "Unsupported format"}), 400

    convert_math = format == 'docx'
    prepared_markdown = prepare_markdown_for_export(markdown_text, convert_math=convert_math)

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as temp:
        temp.write(prepared_markdown)
        temp_path = temp.name

    output_path = temp_path.replace('.md', f'.{format}')

    try:
        extra_args = ['--mathjax'] if format == 'html' else []
        run_pandoc(temp_path, format, extra_args + ['-o', output_path])

        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            logger.info(f"Output file created: {output_path}, size: {file_size} bytes")
            return send_file(output_path, as_attachment=True)
        else:
            logger.error(f"Output file not created: {output_path}")
            return jsonify({"error": "Failed to create output file"}), 500
    except subprocess.CalledProcessError as e:
        logger.error(f"Pandoc error: {e.output}")
        return jsonify({"error": f"Conversion failed: {e.output}"}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
    finally:
        try:
            os.remove(temp_path)
            if os.path.exists(output_path):
                os.remove(output_path)
        except Exception as e:
            logger.error(f"Error cleaning up temporary files: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True)
