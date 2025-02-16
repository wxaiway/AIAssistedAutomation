import argparse
import os
from pdf2image import convert_from_path
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter


def try_remove_pdf_password(input_path, password=None):
    with open(input_path, 'rb') as file:
        pdf_reader = PdfReader(file)

        if pdf_reader.is_encrypted:
            if password is None:
                # 尝试无密码解密
                if pdf_reader.decrypt(''):
                    print("PDF文件已成功解密（无需密码）")
                    return input_path
                else:
                    raise ValueError("PDF文件已加密，需要密码")
            else:
                if pdf_reader.decrypt(password):
                    pdf_writer = PdfWriter()
                    for page in pdf_reader.pages:
                        pdf_writer.add_page(page)

                    output_path = input_path.replace('.pdf', '_decrypted.pdf')
                    with open(output_path, 'wb') as output_file:
                        pdf_writer.write(output_file)

                    print(f"已解密的PDF保存到: {output_path}")
                    return output_path
                else:
                    raise ValueError("提供的密码不正确")
        else:
            print("PDF文件未加密")
            return input_path


def parse_page_ranges(page_range_str, total_pages):
    pages = set()
    ranges = page_range_str.split(',')
    for r in ranges:
        if '-' in r:
            start, end = map(int, r.split('-'))
            pages.update(range(start, min(end + 1, total_pages + 1)))
        else:
            page = int(r)
            if 1 <= page <= total_pages:
                pages.add(page)
    return sorted(list(pages))


def process_pdf(pdf_path, page_range_str, output_path, dpi=300, split_pages=False):
    try:
        pdf_reader = PdfReader(pdf_path)
        total_pages = len(pdf_reader.pages)
    except Exception as e:
        raise ValueError(f"无法读取PDF文件: {str(e)}。请确保poppler已安装并配置好。")

    pages_to_process = parse_page_ranges(page_range_str, total_pages)

    _, file_extension = os.path.splitext(output_path)
    output_format = file_extension[1:].lower()

    if output_format in ['jpg', 'jpeg', 'png']:
        try:
            all_images = convert_from_path(pdf_path, dpi=dpi)
        except Exception as e:
            raise ValueError(f"无法转换PDF页面为图像: {str(e)}。请确保poppler已安装并配置好。")

        if split_pages:
            base_name, ext = os.path.splitext(output_path)
            for i, page_num in enumerate(pages_to_process):
                img = all_images[page_num - 1]
                page_output_path = f"{base_name}_{page_num}{ext}"
                if output_format in ['jpg', 'jpeg']:
                    img.save(page_output_path, format='JPEG', quality=85, optimize=True)
                else:  # png
                    img.save(page_output_path, format='PNG', optimize=True)
                print(f"输出文件已保存到: {page_output_path}")
        else:
            images = [all_images[i - 1] for i in pages_to_process]

            if len(images) == 1:
                if output_format in ['jpg', 'jpeg']:
                    images[0].save(output_path, format='JPEG', quality=85, optimize=True)
                else:  # png
                    images[0].save(output_path, format='PNG', optimize=True)
            else:
                total_height = sum(img.height for img in images)
                max_width = max(img.width for img in images)

                long_image = Image.new('RGB', (max_width, total_height), (255, 255, 255))

                y_offset = 0
                for img in images:
                    long_image.paste(img, (0, y_offset))
                    y_offset += img.height

                if output_format in ['jpg', 'jpeg']:
                    long_image.save(output_path, format='JPEG', quality=85, optimize=True)
                else:  # png
                    long_image.save(output_path, format='PNG', optimize=True)

    elif output_format == 'pdf':
        pdf_writer = PdfWriter()
        for page_num in pages_to_process:
            pdf_writer.add_page(pdf_reader.pages[page_num - 1])

        with open(output_path, 'wb') as output_file:
            pdf_writer.write(output_file)

    else:
        raise ValueError(f"不支持的输出格式: {output_format}")

    if not split_pages:
        print(f"输出文件已保存到: {output_path}")


def merge_pdfs(input_pdfs, output_path):
    pdf_writer = PdfWriter()

    for pdf_path in input_pdfs:
        pdf_reader = PdfReader(pdf_path)
        for page in pdf_reader.pages:
            pdf_writer.add_page(page)

    with open(output_path, 'wb') as output_file:
        pdf_writer.write(output_file)

    print(f"合并的PDF文件已保存到: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="处理PDF文件：选择页面并输出为JPG、PNG或PDF，或合并多个PDF")
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

if __name__ == "__main__":
    main()