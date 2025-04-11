// ==UserScript==
// @name         公众号文章下载器
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  下载微信文章为Markdown格式，包括图片，并定期检查收集的文章列表
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
        const collectorUI = document.getElementById('article-collector');
        const uiContainer = document.createElement('div');
        uiContainer.id = 'article-downloader';

        let topPosition = '10px';
        let width = '300px';

        if (collectorUI) {
            topPosition = `${collectorUI.offsetTop + collectorUI.offsetHeight + 40}px`;
            width = `${collectorUI.offsetWidth}px`;
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
        `;

        const collectedArticles = JSON.parse(localStorage.getItem('collectedArticles') || '[]');
        const hasCollectedArticles = collectedArticles.length > 0;

        uiContainer.innerHTML = `
            <h3 style="margin-top: 0; margin-bottom: 10px;">公众号文章下载器</h3>
            ${hasCollectedArticles ? `
                <div>
                    <input type="checkbox" id="use-collected-articles">
                    <label for="use-collected-articles">使用已收集的 <span id="collected-count">${collectedArticles.length}</span> 篇文章</label>
                </div>
            ` : ''}
            <textarea id="article-urls" rows="5" style="width: 100%; margin-bottom: 10px;" placeholder="输入文章URL，每行一个"></textarea>
            <button id="download-articles" class="downloader-btn">下载文章</button>
            <p id="download-status" style="margin: 10px 0;"></p>
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
        `;

        document.head.appendChild(style);
        document.body.appendChild(uiContainer);

        document.getElementById('download-articles').addEventListener('click', toggleDownload);

        if (hasCollectedArticles) {
            document.getElementById('use-collected-articles').addEventListener('change', function() {
                const textarea = document.getElementById('article-urls');
                if (this.checked) {
                    textarea.value = collectedArticles.map(article => article.split('|')[1]).join('\n');
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
        const collectedArticles = JSON.parse(localStorage.getItem('collectedArticles') || '[]');
        const countElement = document.getElementById('collected-count');
        const useCollectedCheckbox = document.getElementById('use-collected-articles');

        if (countElement) {
            countElement.textContent = collectedArticles.length;
        }

        if (useCollectedCheckbox && useCollectedCheckbox.checked) {
            const textarea = document.getElementById('article-urls');
            textarea.value = collectedArticles.map(article => article.split('|')[1]).join('\n');
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

            const url = urls[i].trim();
            if (!url) continue;

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
    window.addEventListener('load', createUI);
})();
