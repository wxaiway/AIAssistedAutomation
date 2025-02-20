import argparse
import os
import fitz  # PyMuPDF
import io
from PIL import Image

def try_remove_pdf_password(input_path, password=None):
    doc = fitz.open(input_path)
    if doc.is_encrypted:
        if password is None:
            # 尝试无密码解密
            if doc.authenticate(""):
                print("PDF文件已成功解密（无需密码）")
                return input_path
            else:
                raise ValueError("PDF文件已加密，需要密码")
        else:
            if doc.authenticate(password):
                output_path = input_path.replace('.pdf', '_decrypted.pdf')
                doc.save(output_path)
                print(f"已解密的PDF保存到: {output_path}")
                return output_path
            else:
                raise ValueError("提供的密码不正确")
    else:
        print("PDF文件未加密")
        return input_path


def parse_page_ranges(page_range, total_pages):
    if not page_range:
        return list(range(1, total_pages + 1))  # 如果没有指定页码，返回所有页面

    pages = set()
    ranges = page_range.split(',')
    for r in ranges:
        if '-' in r:
            start, end = map(int, r.split('-'))
            pages.update(range(start, min(end + 1, total_pages + 1)))
        else:
            page = int(r)
            if 1 <= page <= total_pages:
                pages.add(page)
    return sorted(list(pages))


def process_pdf(input_path, page_range, output_path, dpi=300, split_pages=False, password=None):
    doc = fitz.open(input_path)
    if doc.is_encrypted:
        if not doc.authenticate(password):
            raise ValueError("密码不正确")

    total_pages = len(doc)
    pages_to_process = parse_page_ranges(page_range, total_pages)

    _, file_extension = os.path.splitext(output_path)
    output_format = file_extension[1:].lower()

    if output_format in ['jpg', 'jpeg', 'png']:
        zoom = dpi / 72  # 默认 DPI 为 72
        mat = fitz.Matrix(zoom, zoom)

        if split_pages:
            base_name, ext = os.path.splitext(output_path)
            for page_num in pages_to_process:
                page = doc[page_num - 1]
                pix = page.get_pixmap(matrix=mat, alpha=False)
                img = Image.open(io.BytesIO(pix.tobytes()))
                page_output_path = f"{base_name}_{page_num}{ext}"
                img.save(page_output_path)
                print(f"输出文件已保存到: {page_output_path}")
        else:
            images = []
            for page_num in pages_to_process:
                page = doc[page_num - 1]
                pix = page.get_pixmap(matrix=mat, alpha=False)
                img = Image.open(io.BytesIO(pix.tobytes()))
                images.append(img)

            if len(images) == 1:
                images[0].save(output_path)
            else:
                # 计算总高度和最大宽度
                total_height = sum(img.height for img in images)
                max_width = max(img.width for img in images)

                # 如果总高度超过限制，分割图像
                max_height = 65000  # PIL的最大支持高度
                if total_height > max_height:
                    parts = []
                    current_height = 0
                    current_part = []
                    for img in images:
                        if current_height + img.height > max_height:
                            parts.append(current_part)
                            current_part = [img]
                            current_height = img.height
                        else:
                            current_part.append(img)
                            current_height += img.height
                    if current_part:
                        parts.append(current_part)

                    # 保存每个部分
                    base_name, ext = os.path.splitext(output_path)
                    for i, part in enumerate(parts):
                        part_height = sum(img.height for img in part)
                        combined_img = Image.new('RGB', (max_width, part_height), (255, 255, 255))
                        y_offset = 0
                        for img in part:
                            combined_img.paste(img, (0, y_offset))
                            y_offset += img.height
                        part_output_path = f"{base_name}_part{i + 1}{ext}"
                        combined_img.save(part_output_path)
                        print(f"输出文件（部分 {i + 1}）已保存到: {part_output_path}")
                else:
                    # 如果总高度没有超过限制，按原方式处理
                    combined_img = Image.new('RGB', (max_width, total_height), (255, 255, 255))
                    y_offset = 0
                    for img in images:
                        combined_img.paste(img, (0, y_offset))
                        y_offset += img.height
                    combined_img.save(output_path)
                    print(f"输出文件已保存到: {output_path}")

    elif output_format == 'pdf':
        new_doc = fitz.open()
        for page_num in pages_to_process:
            new_doc.insert_pdf(doc, from_page=page_num - 1, to_page=page_num - 1)
        new_doc.save(output_path)
        print(f"输出文件已保存到: {output_path}")
    else:
        raise ValueError(f"不支持的输出格式: {output_format}")

    doc.close()

def merge_pdfs(input_pdfs, output_path):
    merged_doc = fitz.open()
    for pdf_path in input_pdfs:
        with fitz.open(pdf_path) as doc:
            merged_doc.insert_pdf(doc)
    merged_doc.save(output_path)
    print(f"合并的PDF文件已保存到: {output_path}")


def extract_images_from_pdf(pdf_path, page_range_str, output_directory):
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    pages_to_process = parse_page_ranges(page_range_str, total_pages)

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for page_num in pages_to_process:
        page = doc[page_num - 1]
        image_list = page.get_images()

        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]

            # 获取图片格式
            image_format = base_image["ext"]

            # 使用 PIL 打开图片
            image = Image.open(io.BytesIO(image_bytes))

            # 保存图片
            image_filename = f"page_{page_num}_image_{img_index + 1}.{image_format}"
            image_path = os.path.join(output_directory, image_filename)
            image.save(image_path)
            print(f"已保存图片: {image_path}")

    print(f"所有图片已提取到目录: {output_directory}")


def encrypt_pdf(input_path, output_path, user_password, owner_password=None):
    doc = fitz.open(input_path)

    if owner_password is None:
        owner_password = user_password

    encryption_method = fitz.PDF_ENCRYPT_AES_256
    permissions = int(
        fitz.PDF_PERM_ACCESSIBILITY
        | fitz.PDF_PERM_PRINT
        | fitz.PDF_PERM_COPY
        | fitz.PDF_PERM_ANNOTATE
    )

    doc.save(
        output_path,
        encryption=encryption_method,
        user_pw=user_password,
        owner_pw=owner_password,
        permissions=permissions
    )
    print(f"已加密的PDF保存到: {output_path}")


def decrypt_pdf(input_path, output_path, password):
    doc = fitz.open(input_path)

    if doc.is_encrypted:
        if doc.authenticate(password):
            doc.save(output_path)
            print(f"已解密的PDF保存到: {output_path}")
        else:
            raise ValueError("密码不正确")
    else:
        print("PDF文件未加密")
        doc.save(output_path)
        print(f"PDF文件已复制到: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="处理PDF文件：选择页面并输出为JPG、PNG或PDF，或合并多个PDF，或提取图片")
    subparsers = parser.add_subparsers(dest='command', help='可用的命令')

    # 处理单个PDF的命令
    process_parser = subparsers.add_parser('process', help='处理单个PDF文件')
    process_parser.add_argument("input_pdf", help="输入PDF文件的路径")
    process_parser.add_argument("page_range", help="要处理的页面范围，例如 '1,3-5,7-9'")
    process_parser.add_argument("output", help="输出文件的路径（支持.jpg, .jpeg, .png, .pdf）")
    process_parser.add_argument("-d", "--dpi", type=int, default=300, help="图像DPI (仅用于jpg和png输出，默认: 300)")
    process_parser.add_argument("-p", "--password", help="PDF密码（如果PDF加密）")
    process_parser.add_argument("-s", "--split-pages", action='store_true', help="按每页生成单独的JPG或PNG文件")

    # 合并PDF的命令
    merge_parser = subparsers.add_parser('merge', help='合并多个PDF文件')
    merge_parser.add_argument("input_pdfs", nargs='+', help="要合并的PDF文件路径列表")
    merge_parser.add_argument("output", help="输出的合并PDF文件路径")

    # 提取图片的命令
    extract_parser = subparsers.add_parser('extract', help='从PDF中提取图片')
    extract_parser.add_argument("input_pdf", help="输入PDF文件的路径")
    extract_parser.add_argument("page_range", help="要提取图片的页面范围，例如 '1,3-5,7-9'")
    extract_parser.add_argument("output_directory", help="保存提取图片的目录路径")
    extract_parser.add_argument("-p", "--password", help="PDF密码（如果PDF加密）")

    # 加密PDF的命令
    encrypt_parser = subparsers.add_parser('encrypt', help='加密PDF文件')
    encrypt_parser.add_argument("input_pdf", help="输入PDF文件的路径")
    encrypt_parser.add_argument("output_pdf", help="输出加密PDF文件的路径")
    encrypt_parser.add_argument("user_password", help="用户密码")
    encrypt_parser.add_argument("-o", "--owner_password", help="所有者密码（如果不提供，将与用户密码相同）")

    # 解密PDF的命令
    decrypt_parser = subparsers.add_parser('decrypt', help='解密PDF文件')
    decrypt_parser.add_argument("input_pdf", help="输入加密PDF文件的路径")
    decrypt_parser.add_argument("output_pdf", help="输出解密PDF文件的路径")
    decrypt_parser.add_argument("password", help="PDF密码")

    args = parser.parse_args()

    if args.command == 'process':
        try:
            decrypted_pdf_path = try_remove_pdf_password(args.input_pdf, args.password)
            process_pdf(decrypted_pdf_path, args.page_range, args.output, args.dpi, args.split_pages)
            if decrypted_pdf_path != args.input_pdf:
                os.remove(decrypted_pdf_path)
        except ValueError as e:
            if "PDF文件已加密，需要密码" in str(e):
                password = input("请输入PDF密码: ")
                try:
                    decrypted_pdf_path = try_remove_pdf_password(args.input_pdf, password)
                    process_pdf(decrypted_pdf_path, args.page_range, args.output, args.dpi, args.split_pages)
                except ValueError as e:
                    print(f"处理过程中出错: {str(e)}")
            else:
                print(f"处理过程中出错: {str(e)}")
        except Exception as e:
            print(f"处理过程中出错: {str(e)}")
    elif args.command == 'merge':
        try:
            merge_pdfs(args.input_pdfs, args.output)
        except Exception as e:
            print(f"合并PDF过程中出错: {str(e)}")
    elif args.command == 'extract':
        try:
            decrypted_pdf_path = try_remove_pdf_password(args.input_pdf, args.password)
            extract_images_from_pdf(decrypted_pdf_path, args.page_range, args.output_directory)
            if decrypted_pdf_path != args.input_pdf:
                os.remove(decrypted_pdf_path)
        except ValueError as e:
            if "PDF文件已加密，需要密码" in str(e):
                password = input("请输入PDF密码: ")
                try:
                    decrypted_pdf_path = try_remove_pdf_password(args.input_pdf, password)
                    extract_images_from_pdf(decrypted_pdf_path, args.page_range, args.output_directory)
                except ValueError as e:
                    print(f"处理过程中出错: {str(e)}")
            else:
                print(f"处理过程中出错: {str(e)}")
        except Exception as e:
            print(f"处理过程中出错: {str(e)}")
    elif args.command == 'encrypt':
        try:
            encrypt_pdf(args.input_pdf, args.output_pdf, args.user_password, args.owner_password)
        except Exception as e:
            print(f"加密PDF过程中出错: {str(e)}")
    elif args.command == 'decrypt':
        try:
            decrypt_pdf(args.input_pdf, args.output_pdf, args.password)
        except Exception as e:
            print(f"解密PDF过程中出错: {str(e)}")

if __name__ == "__main__":
    main()
