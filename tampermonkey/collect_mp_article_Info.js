// ==UserScript==
// @name         微信公众号文章收集器
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  收集微信公众号文章链接，提供可视化界面和下载功能，支持收集指定日期后的文章
// @match        https://mp.weixin.qq.com/*action=edit*
// @grant        GM_download
// ==/UserScript==

(function() {
    'use strict';

    let allArticleInfo = [];
    let isCollecting = false;
    let currentPage = 1;
    let totalPages = 1;
    let startDate = null;

    function getAccountName() {
        const accountElement = document.querySelector('.inner_link_account_msg');
        if (accountElement) {
            const fullText = accountElement.textContent.trim();
            return fullText.replace(/选择其他账号$/, '').trim();
        }

        const selectors = [
            '.weui-desktop-account__nickname',
            '.account_setting_nick_name',
        ];

        for (let selector of selectors) {
            const element = document.querySelector(selector);
            if (element) {
                const name = element.textContent.trim();
                if (name) return name;
            }
        }

        return '未知公众号';
    }

    function createUI() {
        const uiContainer = document.createElement('div');
        uiContainer.id = 'article-collector';
        uiContainer.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            background: white;
            border: 1px solid #ccc;
            padding: 10px;
            z-index: 10000;
            font-family: Arial, sans-serif;
            width: 220px;
        `;

        const accountName = getAccountName();

        uiContainer.innerHTML = `
            <h3 style="margin-top: 0; margin-bottom: 10px;">文章收集器</h3>
            <p style="margin-bottom: 10px;">当前公众号: <strong id="account-name">${accountName}</strong></p>
            <label for="start-date" style="display: block; margin-bottom: 5px;">选择起始日期（可选）：</label>
            <input type="date" id="start-date" class="collector-date">
            <p style="font-size: 12px; color: #666; margin-bottom: 10px;">
                提示：如果选择日期，将只收集该日期之后的文章。不选择则收集所有文章。
            </p>
            <button id="start-collect" class="collector-btn" disabled>开始收集</button>
            <button id="stop-collect" class="collector-btn" style="display:none;">停止收集</button>
            <p id="collect-status" style="margin: 10px 0;"></p>
            <button id="download-csv" class="collector-btn" disabled>下载CSV</button>
        `;

        const style = document.createElement('style');
        style.textContent = `
            .collector-btn {
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
            .collector-btn:hover:not(:disabled) {
                background-color: #06AD56;
            }
            .collector-btn:disabled {
                background-color: #9ED5B9;
                cursor: not-allowed;
            }
            .collector-date {
                width: 100%;
                padding: 6px;
                margin-bottom: 10px;
                border: 1px solid #ccc;
                border-radius: 4px;
                box-sizing: border-box;
            }
        `;

        document.head.appendChild(style);
        document.body.appendChild(uiContainer);

        document.getElementById('start-collect').addEventListener('click', startCollection);
        document.getElementById('stop-collect').addEventListener('click', stopCollection);
        document.getElementById('download-csv').addEventListener('click', downloadCSV);

        // 定期检查是否有可收集的文章
        setInterval(checkForArticles, 1000);
    }

    function checkForArticles() {
        const articles = document.querySelectorAll('.inner_link_article_item');
        const startCollectBtn = document.getElementById('start-collect');
        if (articles.length > 0 && !isCollecting) {
            startCollectBtn.disabled = false;
        } else {
            startCollectBtn.disabled = true;
        }
    }

    function updateAccountName() {
        const accountNameElement = document.getElementById('account-name');
        if (accountNameElement) {
            accountNameElement.textContent = getAccountName();
        }
    }

    function startCollection() {
        if (isCollecting) return;
        isCollecting = true;
        allArticleInfo = [];
        currentPage = 1;
        startDate = document.getElementById('start-date').value ? new Date(document.getElementById('start-date').value) : null;
        updateButtonStates(true);
        document.getElementById('collect-status').textContent = '收集中...';
        updateAccountName();
        collectArticleInfo();
    }

    function stopCollection() {
        isCollecting = false;
        updateButtonStates(false);
        const collectedCount = allArticleInfo.length;
        document.getElementById('collect-status').textContent = `收集已停止，已收集 ${collectedCount} 篇文章`;
        console.log(`收集已停止，总共收集到 ${collectedCount} 篇文章信息`);
        if (collectedCount > 0) {
            console.log(allArticleInfo.join('\n'));
        }
    }

    function updateButtonStates(collecting) {
        document.getElementById('start-collect').style.display = collecting ? 'none' : 'inline-block';
        document.getElementById('stop-collect').style.display = collecting ? 'inline-block' : 'none';
        document.getElementById('download-csv').disabled = allArticleInfo.length === 0;

        if (!collecting) {
            checkForArticles(); // 在停止收集后重新检查是否有可收集的文章
        }
    }

    function collectArticleInfo() {
        if (!isCollecting) return;

        const articles = document.querySelectorAll('.inner_link_article_item');
        if (articles.length === 0) {
            console.log("未找到文章列表，请确保弹出框已打开。");
            stopCollection();
            return;
        }

        let shouldContinue = true;

        articles.forEach(article => {
            if (!shouldContinue) return;

            const title = article.querySelector('.inner_link_article_title span:last-child').textContent.trim();
            const url = article.querySelector('.inner_link_article_date a').href;
            const dateStr = article.querySelector('.inner_link_article_date span:first-child').textContent.trim();
            const date = new Date(dateStr);

            if (startDate && date < startDate) {
                shouldContinue = false;
                return;
            }

            allArticleInfo.push(`${title}|${url}|${dateStr}`);
        });

        // 获取总页数
        const paginationLabel = document.querySelector('.weui-desktop-pagination__num__wrp');
        if (paginationLabel) {
            const paginationText = paginationLabel.textContent;
            const match = paginationText.match(/(\d+)\s*\/\s*(\d+)/);
            if (match) {
                currentPage = parseInt(match[1]);
                totalPages = parseInt(match[2]);
            }
        }

        const nextPageButton = document.querySelector('.weui-desktop-pagination__nav a:last-child');
        if (nextPageButton && !nextPageButton.classList.contains('weui-desktop-btn_disabled') && shouldContinue) {
            const randomDelay = Math.floor(Math.random() * (3000 - 1000 + 1) + 1000); // 1-3秒随机延迟
            document.getElementById('collect-status').textContent = `收集中...第 ${currentPage}/${totalPages} 页，等待 ${randomDelay/1000} 秒`;
            setTimeout(() => {
                if (isCollecting) {
                    nextPageButton.click();
                    setTimeout(collectArticleInfo, 1000); // 页面加载等待时间
                }
            }, randomDelay);
        } else {
            // 最后一页或达到指定日期，结束收集
            const finalDelay = 5000; // 5秒延迟
            document.getElementById('collect-status').textContent = `收集完成，最后处理中...等待 ${finalDelay/1000} 秒`;
            setTimeout(finishCollection, finalDelay);
        }
    }

    function finishCollection() {
        isCollecting = false;
        updateButtonStates(false);
        document.getElementById('collect-status').textContent = `收集完成，共 ${allArticleInfo.length} 篇文章`;
        console.log(`总共收集到 ${allArticleInfo.length} 篇文章信息`);
        console.log(allArticleInfo.join('\n'));
    }

    function downloadCSV() {
        const accountName = getAccountName();
        const currentDate = new Date().toISOString().split('T')[0];
        const fileName = `${accountName}_${currentDate}.csv`;

        const csvContent = "公众号,标题,链接,日期\n"
        + allArticleInfo.map(info => {
            const [title, url, date] = info.split('|');
            return `"${accountName}","${title}","${url}","${date}"`;
        }).join("\n");

        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);

        GM_download({
            url: url,
            name: fileName,
            onload: () => {
                console.log(`Downloaded: ${fileName}`);
                URL.revokeObjectURL(url);
            },
            onerror: (error) => {
                console.error(`Error downloading ${fileName}:`, error);
                URL.revokeObjectURL(url);
            }
        });
    }

    window.addEventListener('load', createUI);

    const observer = new MutationObserver(() => {
        updateAccountName();
        checkForArticles();
    });
    observer.observe(document.body, { childList: true, subtree: true });
})();
