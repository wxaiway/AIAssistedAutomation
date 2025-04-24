// ==UserScript==
// @name         公众号文章下载器
// @namespace    http://tampermonkey.net/
// @version      1.2
// @description  下载微信文章为Markdown格式，包括图片，兼容新版链接收集器数据结构
// @match        https://mp.weixin.qq.com/*
// @grant        GM_xmlhttpRequest
// @grant        GM_download
// @require      https://unpkg.com/turndown/dist/turndown.js
// ==/UserScript==

(function() {
    'use strict';

    let isDownloading = false;
    let shouldStop = false;
    let checkInterval;

    // 创建UI
    function createUI() {
        const collectorUI = document.getElementById('article-collector-safe') || document.getElementById('article-collector');
        const existingDownloader = document.getElementById('article-downloader');

        // 如果下载器已存在，先移除
        if (existingDownloader) {
            existingDownloader.remove();
        }

        const uiContainer = document.createElement('div');
        uiContainer.id = 'article-downloader';

        let topPosition = '10px';
        let width = '300px';

        if (collectorUI) {
            // 计算位置，放在收集器下方20px处
            const collectorRect = collectorUI.getBoundingClientRect();
            topPosition = `${collectorRect.bottom + window.scrollY + 20}px`;
            width = `${collectorRect.width}px`;
        }

        uiContainer.style.cssText = `
            position: fixed;
            top: ${topPosition};
            right: 10px;
            background: white;
            border: 1px solid #ccc;
            padding: 10px;
            z-index: 10000;
            font-family: Arial, sans-serif;
            width: ${width};
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            box-sizing: border-box;
        `;

        // 获取收集的文章数据（兼容新旧格式）
        const storedData = JSON.parse(localStorage.getItem('collectedArticles') || '{"articles":[]}');
        let collectedArticles = [];

        if (Array.isArray(storedData)) {
            // 旧格式：直接是文章数组
            collectedArticles = storedData;
        } else if (storedData.articles && Array.isArray(storedData.articles)) {
            // 新格式：包含在articles属性中
            collectedArticles = storedData.articles;
        }

        const hasCollectedArticles = collectedArticles.length > 0;

        uiContainer.innerHTML = `
            <h3 style="margin-top: 0; margin-bottom: 10px;">公众号文章下载器</h3>
            ${hasCollectedArticles ? `
                <div style="margin-bottom: 10px;">
                    <input type="checkbox" id="use-collected-articles">
                    <label for="use-collected-articles">使用已收集的 <span id="collected-count">${collectedArticles.length}</span> 篇文章</label>
                </div>
            ` : ''}
            <textarea id="article-urls" rows="5" style="width: 100%; margin-bottom: 10px; padding: 8px; box-sizing: border-box;" placeholder="输入文章URL，每行一个"></textarea>
            <button id="download-articles" class="downloader-btn">下载文章</button>
            <p id="download-status" style="margin: 10px 0; font-size: 14px; min-height: 20px;"></p>
        `;

        const style = document.createElement('style');
        style.textContent = `
            .downloader-btn {
                background-color: #07C160;
                color: white;
                border: none;
                padding: 8px 16px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 14px;
                margin: 4px 0;
                cursor: pointer;
                border-radius: 4px;
                transition: background-color 0.3s;
                width: 100%;
                box-sizing: border-box;
            }
            .downloader-btn:hover {
                background-color: #06AD56;
            }
            .downloader-btn:disabled {
                background-color: #cccccc;
                cursor: not-allowed;
            }
            #article-downloader label {
                font-size: 14px;
                cursor: pointer;
                user-select: none;
            }
        `;

        document.head.appendChild(style);
        document.body.appendChild(uiContainer);

        document.getElementById('download-articles').addEventListener('click', toggleDownload);

        if (hasCollectedArticles) {
            document.getElementById('use-collected-articles').addEventListener('change', function() {
                const textarea = document.getElementById('article-urls');
                if (this.checked) {
                    // 从收集的文章中提取URL（兼容多种格式）
                    textarea.value = collectedArticles.map(article => {
                        // 如果是字符串且包含|分隔符
                        if (typeof article === 'string' && article.includes('|')) {
                            const parts = article.split('|');
                            return parts.length > 1 ? parts[1] : article;
                        }
                        // 如果是对象且有url属性
                        else if (typeof article === 'object' && article.url) {
                            return article.url;
                        }
                        // 其他情况直接返回
                        return article;
                    }).filter(url => url).join('\n');
                } else {
                    textarea.value = '';
                }
            });
        }

        // 开始定期检查
        startPeriodicCheck();
    }

    // 开始定期检查
    function startPeriodicCheck() {
        checkInterval = setInterval(() => {
            if (!isDownloading) {
                checkCollectedArticles();
            }
        }, 5000); // 每5秒检查一次
    }

    // 检查收集的文章
    function checkCollectedArticles() {
        // 获取收集的文章数据（兼容新旧格式）
        const storedData = JSON.parse(localStorage.getItem('collectedArticles') || '{"articles":[]}');
        let collectedArticles = [];

        if (Array.isArray(storedData)) {
            collectedArticles = storedData;
        } else if (storedData.articles && Array.isArray(storedData.articles)) {
            collectedArticles = storedData.articles;
        }

        const countElement = document.getElementById('collected-count');
        const useCollectedCheckbox = document.getElementById('use-collected-articles');

        if (countElement) {
            countElement.textContent = collectedArticles.length;
        }

        if (useCollectedCheckbox && useCollectedCheckbox.checked) {
            const textarea = document.getElementById('article-urls');
            textarea.value = collectedArticles.map(article => {
                // 处理不同格式的文章数据
                if (typeof article === 'string' && article.includes('|')) {
                    const parts = article.split('|');
                    return parts.length > 1 ? parts[1] : article;
                }
                else if (typeof article === 'object' && article.url) {
                    return article.url;
                }
                return article;
            }).filter(url => url).join('\n');
        }
    }

    // 切换下载状态
    function toggleDownload() {
        const button = document.getElementById('download-articles');
        if (isDownloading) {
            shouldStop = true;
            button.textContent = '停止中...';
            button.disabled = true;
        } else {
            shouldStop = false;
            isDownloading = true;
            button.textContent = '停止下载';
            startDownload();
        }
    }

    // 开始下载过程
    async function startDownload() {
        const urls = document.getElementById('article-urls').value.split('\n').filter(url => url.trim());
        const statusElement = document.getElementById('download-status');
        const turndownService = new TurndownService();

        statusElement.textContent = '准备下载...如果出现新窗口，请允许下载并关闭该窗口。';

        for (let i = 0; i < urls.length; i++) {
            if (shouldStop) {
                statusElement.textContent = '下载已停止';
                break;
            }

            let url = urls[i].trim();
            if (!url) continue;

            // 处理URL，确保是有效的文章链接
            if (!url.startsWith('http')) {
                url = 'https://mp.weixin.qq.com' + (url.startsWith('/') ? '' : '/') + url;
            }

            statusElement.textContent = `正在处理第 ${i + 1}/${urls.length} 篇文章...`;

            try {
                const { title, content, createTime } = await fetchArticleContent(url);
                const { markdown, images } = await processContent(url, title, createTime, content, turndownService);

                // 下载 Markdown 文件
                const fileName = `${title.replace(/[\\/:*?"<>|]/g, '')}.md`;
                downloadFile(new Blob([markdown], {type: 'text/markdown'}), fileName);

                // 下载图片
                for (const [imageName, imageUrl] of Object.entries(images)) {
                    if (shouldStop) break;
                    try {
                        await fetchImage(imageUrl, imageName);
                    } catch (error) {
                        console.error(`图片 ${imageName} 下载失败:`, error);
                    }
                }

                if (!shouldStop) {
                    await new Promise(resolve => setTimeout(resolve, 2000)); // 2秒延迟，避免过快请求
                }
            } catch (error) {
                console.error(`下载文章失败: ${url}`, error);
                statusElement.textContent += `\n文章下载失败: ${url}`;
            }
        }

        isDownloading = false;
        const button = document.getElementById('download-articles');
        button.textContent = '下载文章';
        button.disabled = false;

        if (!shouldStop) {
            statusElement.textContent = `下载完成，共处理 ${urls.length} 篇文章。请检查您的下载文件夹。`;
        }
    }

    // 下载文件
    function downloadFile(blob, fileName) {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = fileName;
        a.target = '_blank';  // 在新窗口中打开
        a.rel = 'noopener noreferrer';  // 安全考虑
        a.click();
        setTimeout(() => {
            URL.revokeObjectURL(url);
        }, 100);  // 短暂延迟后释放 URL
    }

    // 获取文章内容
    function fetchArticleContent(url) {
        return new Promise((resolve, reject) => {
            GM_xmlhttpRequest({
                method: "GET",
                url: url,
                headers: {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                },
                onload: function(response) {
                    if (response.status === 200) {
                        const parser = new DOMParser();
                        const doc = parser.parseFromString(response.responseText, "text/html");

                        const titleElement = doc.querySelector('h1#activity-name') ||
                                             doc.querySelector('h2.rich_media_title') ||
                                             doc.querySelector('h1.article-title');
                        const title = titleElement ? titleElement.textContent.trim() : '未知标题';

                        const contentElement = doc.querySelector('#js_content');
                        const content = contentElement ? contentElement.innerHTML : '';

                        let createTime = '';
                        const createTimeMatch = response.responseText.match(/createTime\s+=\s+'(.*)'/);
                        if (createTimeMatch) {
                            createTime = createTimeMatch[1];
                        }

                        resolve({ title, content, createTime });
                    } else {
                        reject(new Error(`请求失败: ${response.status}`));
                    }
                },
                onerror: function(error) {
                    reject(error);
                }
            });
        });
    }

    // 处理内容，包括准备图片下载
    async function processContent(url, title, createTime, content, turndownService) {
        const parser = new DOMParser();
        const doc = parser.parseFromString(content, 'text/html');
        const images = {};
        const imageMap = {};

        // 准备图片下载
        Array.from(doc.querySelectorAll('img')).forEach((img) => {
            const imgSrc = img.getAttribute('data-src') || img.getAttribute('src');
            if (!imgSrc) return;

            const tempFileName = "temp_" + Math.random().toString(36).substr(2, 9) + ".jpg";
            imageMap[imgSrc] = tempFileName;
            images[tempFileName] = imgSrc;

            // 替换图片 src 为临时文件名
            img.setAttribute('src', `./${tempFileName}`);
        });

        const cleanTitle = removeNonvisibleChars(title);
        const formattedCreateTime = createTime ? `publish_time: ${createTime}` : "publish_time: unknown";
        let markdownContent = turndownService.turndown(doc.body.innerHTML);

        // 替换 Markdown 中的图片引用
        markdownContent = markdownContent.replace(/!\[.*?\]\((.*?)\)/g, (match, p1) => {
            const tempFileName = imageMap[p1] || p1;
            return `![](${tempFileName})`;
        });

        let markdown = `# ${cleanTitle}\n\n${formattedCreateTime}\n\nurl: ${url}\n\n${markdownContent}\n`;

        // 处理特殊字符
        markdown = markdown.replace(/\xa0{1,}/g, '\n');
        markdown = markdown.replace(/\]\(http([^)]*)\)/g,
            (match, p1) => `](http${p1.replace(/ /g, '%20')})`);

        return { markdown, images };
    }

    // 获取图片数据
    function fetchImage(url, filename) {
        return new Promise((resolve, reject) => {
            GM_download({
                url: url,
                name: filename,
                onload: function() {
                    resolve();
                },
                onerror: function(error) {
                    reject(error);
                }
            });
        });
    }

    // 移除不可见字符
    function removeNonvisibleChars(text) {
        return text.replace(/[\u200B-\u200D\uFEFF]/g, '');
    }

    // 在页面加载完成后创建UI
    function init() {
        // 等待页面稳定后再创建UI
        setTimeout(() => {
            createUI();

            // 添加监听器，当收集器位置变化时调整下载器位置
            const observer = new MutationObserver(() => {
                const collectorUI = document.getElementById('article-collector-safe') || document.getElementById('article-collector');
                const downloaderUI = document.getElementById('article-downloader');

                if (collectorUI && downloaderUI) {
                    const collectorRect = collectorUI.getBoundingClientRect();
                    downloaderUI.style.top = `${collectorRect.bottom + window.scrollY + 20}px`;
                    downloaderUI.style.width = `${collectorRect.width}px`;
                }
            });

            observer.observe(document.body, {
                childList: true,
                subtree: true,
                attributes: true,
                attributeFilter: ['style']
            });
        }, 1500);
    }

    window.addEventListener('load', init);
})();
