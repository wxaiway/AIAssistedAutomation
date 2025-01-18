## 公众号

伟贤AI之路

![伟贤AI之路](../images/mp.jpg)

## 文章介绍

[家长必看！1 小时搞定 RAZ 英文绘本英文提取！](https://mp.weixin.qq.com/s/4VX1AdJUxbz0ZEs6VgdXDA)

## 依赖安装

```
pip install dashscope pydub ffmpeg-python -i https://pypi.tuna.tsinghua.edu.cn/simple
```

- 注意：pydub依赖于ffmpeg，你需要确保ffmpeg已经正确安装在你的系统上。


[阿里云百炼](https://bailian.console.aliyun.com)注册账号，创建好 API-KEY，环境变量中设置DASHSCOPE_API_KEY

```
export DASHSCOPE_API_KEY=your_api_key_here
```

## 使用

```
python AudioBatchTranscriber.py --input mp3_dir --output transcribed
```

