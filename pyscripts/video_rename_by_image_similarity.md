## 公众号

伟贤AI之路

![伟贤AI之路](../images/mp.jpg)

## 文章介绍

[批量下载即梦 AI 高清图并自动重命名视频，高效又省心！](https://mp.weixin.qq.com/s/Uyn41_Tj3wXAgcZepHf2Tw)

## 依赖安装

```
pip install opencv-python scikit-image numpy
#建议指定国内源
# pip install opencv-python scikit-image numpy -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 使用

```
python video_rename_by_image_similarity.py /path/to/your/directory
```

可以通过 -t 或 --threshold 参数指定自定义的相似度阈值：　

```
python video_rename_by_image_similarity.py /path/to/your/directory -t 0.6
```
