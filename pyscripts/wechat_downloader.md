## 公众号

伟贤AI之路

![伟贤AI之路](../images/mp.jpg)

## 文章介绍

[AI 编程小白必看：如何批量下载公众号文章为 Markdown 格式](https://mp.weixin.qq.com/s/cALc-nLIn0fHhyock_8thQ)


## 1. 安装依赖

在使用这个脚本之前，您需要安装以下 Python 库：

```bash
pip install requests beautifulsoup4 markdownify
```

## 2. 使用方法

```
python wechat_downloader.py articles.csv
```


articles.csv格式

```
公众号,标题,链接,日期
科普中国,宇宙的奥秘,https://mp.weixin.qq.com/s/example1,2025-01-01
科技日报,AI最新进展,https://mp.weixin.qq.com/s/example2,2025-01-02
```