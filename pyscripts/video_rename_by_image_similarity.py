import os
import cv2
from skimage.metrics import structural_similarity as ssim
import numpy as np
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing
from tqdm import tqdm

# 支持的文件类型
SUPPORTED_IMAGE_TYPES = {'.png', '.jpg', '.jpeg', '.webp'}
SUPPORTED_VIDEO_TYPES = {'.mp4'}

def get_frames(video_path, num_frames=1):
    cap = cv2.VideoCapture(video_path)
    frames = []
    for _ in range(num_frames):
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
    cap.release()
    return frames

def compare_images(img1, img2):
    if img1.shape != img2.shape:
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
    return ssim(img1, img2)

def get_unique_filename(directory, base_name, extension):
    counter = 1
    new_name = f"{base_name}{extension}"
    while os.path.exists(os.path.join(directory, new_name)):
        new_name = f"{base_name}_{counter}{extension}"
        counter += 1
    return new_name

def process_video(video_file, directory, image_dict, similarity_threshold, num_frames):
    try:
        video_path = os.path.join(directory, video_file)
        frames = get_frames(video_path, num_frames)

        if not frames:
            return f"无法读取视频 {video_file} 的帧"

        max_similarity = 0
        most_similar_image = None

        for image_file, image in image_dict.items():
            similarity = max(compare_images(frame, image) for frame in frames)
            if similarity > max_similarity:
                max_similarity = similarity
                most_similar_image = image_file

            if similarity > 0.95:  # 提前终止条件
                break

        if max_similarity >= similarity_threshold:
            image_name = os.path.splitext(most_similar_image)[0]
            video_extension = os.path.splitext(video_file)[1]
            new_name = get_unique_filename(directory, image_name, video_extension)
            new_path = os.path.join(directory, new_name)
            if video_file != new_name:
                os.rename(video_path, new_path)
                return f"已将 {video_file} 重命名为 {new_name} (相似度: {max_similarity:.2f})"
            else:
                return f"{video_file} 已经是正确的名称 (相似度: {max_similarity:.2f})"
        else:
            return f"未找到与 {video_file} 相似度达到阈值的图片 (最高相似度: {max_similarity:.2f})"
    except Exception as e:
        return f"处理 {video_file} 时发生错误: {str(e)}"

def main(directory, similarity_threshold, num_frames):
    image_files = [f for f in os.listdir(directory) if os.path.splitext(f.lower())[1] in SUPPORTED_IMAGE_TYPES]
    video_files = [f for f in os.listdir(directory) if os.path.splitext(f.lower())[1] in SUPPORTED_VIDEO_TYPES]

    # 预处理图片
    image_dict = {}
    for image_file in image_files:
        image_path = os.path.join(directory, image_file)
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        image_dict[image_file] = image

    # 并行处理视频
    num_cores = multiprocessing.cpu_count()
    with ThreadPoolExecutor(max_workers=num_cores) as executor:
        futures = [executor.submit(process_video, video_file, directory, image_dict, similarity_threshold, num_frames) for video_file in video_files]
        
        for future in tqdm(as_completed(futures), total=len(video_files), desc="处理视频"):
            print(future.result())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='根据图片相似度重命名视频文件')
    parser.add_argument('directory', type=str, help='包含图片和视频的目录路径')
    parser.add_argument('-t', '--threshold', type=float, default=0.7, help='相似度阈值 (默认: 0.7)')
    parser.add_argument('-f', '--frames', type=int, default=1, help='从每个视频提取的帧数 (默认: 1)')

    args = parser.parse_args()

    main(args.directory, args.threshold, args.frames)
