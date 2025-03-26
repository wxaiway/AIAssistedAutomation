import streamlit as st
import tempfile
import os
import base64
import uuid
import fitz  # PyMuPDF
from pdf_tool import process_pdf, merge_pdfs, extract_images_from_pdf, encrypt_pdf, decrypt_pdf


def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">下载 {file_label}</a>'
    return href


def check_pdf_encryption(file_content):
    with fitz.open(stream=file_content, filetype="pdf") as doc:
        return doc.is_encrypted

def process_pdf_ui():
    st.header("处理 PDF")

    if 'processed_files' not in st.session_state:
        st.session_state.processed_files = []

    uploaded_file = st.file_uploader("选择一个 PDF 文件", type="pdf")
    if uploaded_file is not None:
        file_content = uploaded_file.getvalue()
        is_encrypted = check_pdf_encryption(file_content)

        password = None
        if is_encrypted:
            st.warning("这个 PDF 文件是加密的。请输入密码以解密。")
            password = st.text_input("输入密码", type="password")

        page_range = st.text_input("输入页面范围 (例如: 1,3-5,7-9)，留空处理所有页面")
        output_format = st.selectbox("选择输出格式", ["pdf", "png", "jpg"])
        dpi = st.slider("选择 DPI (仅用于图片输出)", 72, 600, 300)
        split_pages = st.checkbox("分割页面")

        if st.button("处理"):
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_input:
                tmp_input.write(file_content)
                tmp_input_path = tmp_input.name

            try:
                with tempfile.TemporaryDirectory() as tmp_dir:
                    base_name = os.path.join(tmp_dir, "output")
                    process_pdf(tmp_input_path, page_range, f"{base_name}.{output_format}", dpi, split_pages, password)

                    output_files = [f for f in os.listdir(tmp_dir) if f.endswith(f'.{output_format}')]

                    st.session_state.processed_files = []
                    for file in sorted(output_files):
                        with open(os.path.join(tmp_dir, file), "rb") as f:
                            file_content = f.read()
                            st.session_state.processed_files.append({
                                'name': file,
                                'content': file_content,
                                'mime': f"application/{output_format}" if output_format == 'pdf' else f"image/{output_format}",
                                'key': str(uuid.uuid4())
                            })

                    st.success("文件处理完成！")

            except Exception as e:
                st.error(f"处理过程中出错: {str(e)}")
            finally:
                os.unlink(tmp_input_path)

    if st.session_state.processed_files:
        st.write("处理后的文件:")
        for file in st.session_state.processed_files:
            st.download_button(
                label=f"下载 {file['name']}",
                data=file['content'],
                file_name=file['name'],
                mime=file['mime'],
                key=file['key']
            )


def merge_pdfs_ui():
    st.header("合并 PDF")
    uploaded_files = st.file_uploader("选择多个 PDF 文件", type="pdf", accept_multiple_files=True)
    if uploaded_files:
        if st.button("合并"):
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_output:
                    tmp_output_path = tmp_output.name

                input_paths = []
                for uploaded_file in uploaded_files:
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_input:
                        tmp_input.write(uploaded_file.getvalue())
                        input_paths.append(tmp_input.name)

                merge_pdfs(input_paths, tmp_output_path)

                with open(tmp_output_path, "rb") as file:
                    st.download_button(
                        label="下载合并后的 PDF",
                        data=file,
                        file_name="merged.pdf",
                        mime="application/pdf"
                    )
            except Exception as e:
                st.error(f"合并过程中出错: {str(e)}")
            finally:
                for path in input_paths:
                    os.unlink(path)
                os.unlink(tmp_output_path)


def extract_images_ui():
    st.header("提取图片")

    if 'extracted_images' not in st.session_state:
        st.session_state.extracted_images = []

    uploaded_file = st.file_uploader("选择一个 PDF 文件", type="pdf", key="extract_pdf_uploader")
    if uploaded_file is not None:
        file_content = uploaded_file.getvalue()
        is_encrypted = check_pdf_encryption(file_content)

        if is_encrypted:
            st.warning("这个 PDF 文件是加密的。请输入密码以解密。")
            password = st.text_input("输入密码", type="password", key="extract_password")
        else:
            password = None

        page_range = st.text_input("输入页面范围 (例如: 1,3-5,7-9)，留空处理所有页面", key="extract_page_range")
        if st.button("提取图片", key="extract_button"):
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_input:
                tmp_input.write(file_content)
                tmp_input_path = tmp_input.name

            with tempfile.TemporaryDirectory() as tmp_dir:
                try:
                    extract_images_from_pdf(tmp_input_path, page_range, tmp_dir, password)

                    st.session_state.extracted_images = []
                    for filename in os.listdir(tmp_dir):
                        with open(os.path.join(tmp_dir, filename), "rb") as file:
                            file_content = file.read()
                            st.session_state.extracted_images.append({
                                'name': filename,
                                'content': file_content,
                                'mime': "image/png",
                                'key': str(uuid.uuid4())
                            })

                    st.success("图片提取完成！")
                except Exception as e:
                    st.error(f"提取图片过程中出错: {str(e)}")
                finally:
                    os.unlink(tmp_input_path)

    if st.session_state.extracted_images:
        st.write("提取的图片:")
        for img in st.session_state.extracted_images:
            st.download_button(
                label=f"下载 {img['name']}",
                data=img['content'],
                file_name=img['name'],
                mime=img['mime'],
                key=img['key']
            )


def encrypt_pdf_ui():
    st.header("加密 PDF")
    uploaded_file = st.file_uploader("选择一个 PDF 文件", type="pdf")
    if uploaded_file is not None:
        user_password = st.text_input("设置用户密码", type="password")
        owner_password = st.text_input("设置所有者密码 (可选)", type="password")
        if st.button("加密"):
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_input:
                tmp_input.write(uploaded_file.getvalue())
                tmp_input_path = tmp_input.name

            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_output:
                tmp_output_path = tmp_output.name

            try:
                encrypt_pdf(tmp_input_path, tmp_output_path, user_password, owner_password)

                with open(tmp_output_path, "rb") as file:
                    st.download_button(
                        label="下载加密后的 PDF",
                        data=file,
                        file_name="encrypted.pdf",
                        mime="application/pdf"
                    )
            except Exception as e:
                st.error(f"加密过程中出错: {str(e)}")
            finally:
                os.unlink(tmp_input_path)
                os.unlink(tmp_output_path)


def decrypt_pdf_ui():
    st.header("解密 PDF")
    uploaded_file = st.file_uploader("选择一个加密的 PDF 文件", type="pdf")
    if uploaded_file is not None:
        password = st.text_input("输入密码", type="password")
        if st.button("解密"):
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_input:
                tmp_input.write(uploaded_file.getvalue())
                tmp_input_path = tmp_input.name

            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_output:
                tmp_output_path = tmp_output.name

            try:
                decrypt_pdf(tmp_input_path, tmp_output_path, password)

                with open(tmp_output_path, "rb") as file:
                    st.download_button(
                        label="下载解密后的 PDF",
                        data=file,
                        file_name="decrypted.pdf",
                        mime="application/pdf"
                    )
            except Exception as e:
                st.error(f"解密过程中出错: {str(e)}")
            finally:
                os.unlink(tmp_input_path)
                os.unlink(tmp_output_path)


def main():
    st.title("PDF 处理工具")

    # 侧边栏用于选择功能
    option = st.sidebar.selectbox(
        "选择功能",
        ("处理 PDF", "合并 PDF", "提取图片", "加密 PDF", "解密 PDF")
    )

    # 为每个功能创建一个独立的 session state
    if 'current_function' not in st.session_state:
        st.session_state.current_function = None

    # 如果功能改变，清除之前功能的状态
    if st.session_state.current_function != option:
        if st.session_state.current_function == "提取图片":
            st.session_state.extracted_images = []
        elif st.session_state.current_function == "处理 PDF":
            st.session_state.processed_files = []
        st.session_state.current_function = option

    if option == "处理 PDF":
        process_pdf_ui()
    elif option == "合并 PDF":
        merge_pdfs_ui()
    elif option == "提取图片":
        extract_images_ui()
    elif option == "加密 PDF":
        encrypt_pdf_ui()
    elif option == "解密 PDF":
        decrypt_pdf_ui()


if __name__ == "__main__":
    main()