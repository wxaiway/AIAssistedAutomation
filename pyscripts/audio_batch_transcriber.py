import os
import dashscope
from dashscope.audio.asr import Recognition, RecognitionCallback, RecognitionResult
import json
from pydub import AudioSegment
from concurrent.futures import ThreadPoolExecutor
import argparse

# 定义回调类
class Callback(RecognitionCallback):
    def on_complete(self) -> None:
        print("Recognition completed successfully.")

    def on_error(self, result: RecognitionResult) -> None:
        print(f"Error during recognition: {result.message}")

    def on_event(self, result: RecognitionResult) -> None:
        print(f"Received transcription event: {result.message}")

# 从环境变量中获取API密钥
dashscope.api_key = os.getenv('DASHSCOPE_API_KEY')

def convert_mp3_to_wav(mp3_file, wav_file):
    audio = AudioSegment.from_file(mp3_file, format='mp3')
    # 确保输出的WAV文件符合要求：单声道、16kHz采样率、16位宽
    audio = audio.set_channels(1).set_frame_rate(16000).set_sample_width(2)
    audio.export(wav_file, format='wav')

def transcribe_audio(file_path, output_dir):
    try:
        # 检查文件是否存在
        if not os.path.isfile(file_path):
            print(f"Error: 文件不存在: {file_path}")
            return None

        # 将MP3文件转换为适合的WAV格式
        if file_path.endswith('.mp3'):
            wav_file = file_path.replace('.mp3', '.wav')
            convert_mp3_to_wav(file_path, wav_file)
            file_path = wav_file

        # 创建回调对象
        callback = Callback()

        # 初始化语音识别对象
        recognition = Recognition(
            model='paraformer-realtime-v2',
            format='pcm',
            sample_rate=16000,
            language_hints=['en'],
            callback=callback
        )

        # 调用语音转文字服务
        result = recognition.call(file_path)

        if result.status_code == 200:
            transcription_result = result.output  # 直接使用 .output 属性

            # 获取音频文件的基本名称
            base_name = os.path.splitext(os.path.basename(file_path))[0]

            # 构建输出文件路径
            json_output_file_path = os.path.join(output_dir, f"{base_name}.json")
            txt_output_file_path = os.path.join(output_dir, f"{base_name}.txt")

            # 将JSON结果写入文件
            with open(json_output_file_path, 'w', encoding='utf-8') as f:
                json.dump(transcription_result, f, indent=4, ensure_ascii=False)

            # 合并所有文本片段，并清理多余的空格
            full_text = ""
            for sentence in transcription_result.get('sentence', []):
                full_text += sentence.get('text', '') + " "

            # 清理多余的空格
            cleaned_full_text = ' '.join(full_text.split()).strip()

            # 将完整文本写入文件
            with open(txt_output_file_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_full_text)

            print(f"Transcription results saved to: {json_output_file_path}")
            print(f"Transcribed text saved to: {txt_output_file_path}")
            return cleaned_full_text
        else:
            print(f"Error: {result.status_code} - {result.message}")
            return None
    except Exception as e:
        print(f"Exception processing {file_path}: {e}")
        return None

def process_all_mp3_files(input_dir, output_dir):
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 获取所有MP3文件
    mp3_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith('.mp3')]

    # 使用ThreadPoolExecutor进行并发处理
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(transcribe_audio, file_path, output_dir): file_path for file_path in mp3_files}
        
        for future in futures:
            file_path = futures[future]
            try:
                result = future.result()
                if result:
                    print(f"Processed {file_path}: {result[:50]}...")  # 打印前50个字符作为示例
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process MP3 files and transcribe them using DashScope.")
    parser.add_argument("--input", type=str, required=True, help="Directory containing MP3 files")
    parser.add_argument("--output", type=str, required=True, help="Directory to save transcription results")

    args = parser.parse_args()

    input_directory = os.path.abspath(args.input)
    output_directory = os.path.abspath(args.output)

    process_all_mp3_files(input_directory, output_directory)
