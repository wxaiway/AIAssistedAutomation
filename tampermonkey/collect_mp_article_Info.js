// ==UserScript==
// @name         公众号链接收集器
// @namespace    http://tampermonkey.net/
// @version      1.2
// @description  收集微信公众号文章链接
// @match        https://mp.weixin.qq.com/*action=edit*
// @grant        GM_download
// ==/UserScript==

(function() {
    'use strict';

    // 全局状态
    const state = {
        accountName: '未知公众号',
        isCollecting: false,
        currentPage: 1,
        totalPages: 1,
        startDate: null,
        dialogObserver: null,
        articlesObserver: null,
        accountCheckInterval: null
    };

    // 安全存储系统
    const storage = {
        save: (articles, accountName) => {
            try {
                const data = {
                    account: accountName,
                    articles: articles
                };
                localStorage.setItem('collectedArticles', JSON.stringify(data));
                return true;
            } catch (error) {
                console.error('存储错误:', error);
                return false;
            }
        },
        load: () => {
            try {
                const value = localStorage.getItem('collectedArticles');
                if (!value) return {account: '未知公众号', articles: []};

                const data = JSON.parse(value);
                // 兼容旧版本数据
                if (Array.isArray(data)) {
                    return {account: '未知公众号', articles: data};
                }
                return data;
            } catch (error) {
                console.error('读取错误:', error);
                return {account: '未知公众号', articles: []};
            }
        },
        clear: () => {
            try {
                localStorage.removeItem('collectedArticles');
                return true;
            } catch (error) {
                console.error('清除错误:', error);
                return false;
            }
        },
        getArticles: () => {
            return storage.load().articles;
        },
        getAccount: () => {
            return storage.load().account;
        }
    };

    // 防抖函数
    function debounce(func, delay) {
        let timeout;
        return function() {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, arguments), delay);
        };
    }

    // 超时安全的账号名获取
    function getAccountNameSafely() {
        return new Promise(resolve => {
            const timeout = setTimeout(() => {
                console.warn('获取账号名超时');
                resolve('未知公众号');
            }, 1000);

            try {
                const accountContainer = document.querySelector('.inner_link_account_msg');
                if (!accountContainer) {
                    clearTimeout(timeout);
                    return resolve('未知公众号');
                }

                const clone = accountContainer.cloneNode(true);
                clone.querySelector('.weui-desktop-btn')?.remove();
                const accountName = clone.textContent.trim();
                clearTimeout(timeout);
                resolve(accountName || '未知公众号');
            } catch (e) {
                console.error('安全获取出错:', e);
                clearTimeout(timeout);
                resolve('未知公众号');
            }
        });
    }

    // 检查并更新账号名
    async function checkAndUpdateAccount() {
        const newName = await getAccountNameSafely();
        if (newName !== state.accountName) {
            state.accountName = newName;
            updateAccountNameDisplay();

            // 更新存储中的账号名
            const data = storage.load();
            if (data.account !== newName) {
                storage.save(data.articles, newName);
            }
        }
    }

    // 检查文章
    function checkForArticles() {
        const articles = document.querySelectorAll('.inner_link_article_item');
        const startCollectBtn = document.getElementById('start-collect');
        const downloadCsvBtn = document.getElementById('download-csv');

        if (articles.length > 0 && !state.isCollecting) {
            startCollectBtn.disabled = false;
            startCollectBtn.style.display = 'block';
        } else {
            startCollectBtn.disabled = true;
        }
        downloadCsvBtn.disabled = storage.getArticles().length === 0;
    }

    // 更新账号显示
    function updateAccountNameDisplay() {
        const element = document.getElementById('account-name');
        if (element) {
            element.textContent = state.accountName;
        }
    }

    // 初始化文章观察者
    function initArticlesObserver() {
        if (state.articlesObserver) {
            state.articlesObserver.disconnect();
        }

        // 立即检查一次
        checkForArticles();

        // 设置观察者定期检查文章列表
        state.articlesObserver = new MutationObserver(debounce(() => {
            checkForArticles();
        }, 500));

        // 观察文章区域的变化
        const targetNode = document.querySelector('.inner_link_article_list') || document.body;
        state.articlesObserver.observe(targetNode, {
            childList: true,
            subtree: true
        });
    }

    // 优化的对话框观察者
    function initSafeDialogObserver() {
        if (state.dialogObserver) {
            state.dialogObserver.disconnect();
        }

        const checkDialog = debounce(async () => {
            const dialog = document.querySelector('.weui-desktop-dialog');
            if (!dialog || dialog.style.display === 'none') return;

            await checkAndUpdateAccount();
            initArticlesObserver(); // 对话框出现时初始化文章观察
        }, 300);

        state.dialogObserver = new MutationObserver((mutations) => {
            if (mutations.some(m => m.addedNodes.length > 0)) {
                checkDialog();
            }
        });

        state.dialogObserver.observe(document.body, {
            childList: true,
            subtree: false
        });

        checkDialog();
    }

    // 更新按钮状态
    function updateButtonStates(collecting) {
        document.getElementById('start-collect').style.display = collecting ? 'none' : 'block';
        document.getElementById('stop-collect').style.display = collecting ? 'block' : 'none';
        document.getElementById('download-csv').disabled = storage.getArticles().length === 0;
    }

    // 创建UI界面
    function createSafeUI() {
        // 初始化时从存储加载账号名
        const storedData = storage.load();
        state.accountName = storedData.account;

        const container = document.createElement('div');
        container.id = 'article-collector-safe';
        container.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            background: white;
            border: 1px solid #ddd;
            padding: 10px;
            z-index: 9999;
            width: 280px;
            max-width: 90vw;
            box-sizing: border-box;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
        `;

        container.innerHTML = `
            <h3 style="margin:0 0 10px;font-size:16px;">公众号链接收集器</h3>
            <p style="margin:0 0 10px;word-break:break-all;">公众号: <span id="account-name">${state.accountName}</span></p>
            <label style="display:block;margin-bottom:5px;font-size:14px;">起始日期(可选):</label>
            <input type="date" id="start-date" style="width:100%;margin-bottom:10px;padding:8px;box-sizing:border-box;">
            <div style="display:flex;gap:5px;margin-bottom:10px;">
                <button id="start-collect" style="flex:1;padding:8px;background:#07C160;color:white;border:none;border-radius:4px;" disabled>开始</button>
                <button id="stop-collect" style="flex:1;padding:8px;display:none;background:#FA5151;color:white;border:none;border-radius:4px;">停止</button>
            </div>
            <div id="collect-status" style="margin:10px 0;min-height:20px;font-size:12px;"></div>
            <button id="download-csv" style="width:100%;padding:8px;margin-bottom:5px;background:#576B95;color:white;border:none;border-radius:4px;" disabled>下载CSV</button>
            <button id="clear-data" style="width:100%;padding:8px;background:#FF9C19;color:white;border:none;border-radius:4px;">清除数据</button>
        `;

        document.body.appendChild(container);

        // 事件绑定
        document.getElementById('start-collect').addEventListener('click', startCollection);
        document.getElementById('stop-collect').addEventListener('click', stopCollection);
        document.getElementById('download-csv').addEventListener('click', downloadCSV);
        document.getElementById('clear-data').addEventListener('click', clearCollectedData);

        // 初始化观察者
        initSafeDialogObserver();

        // 启动账号名定期检查
        state.accountCheckInterval = setInterval(checkAndUpdateAccount, 5000);
    }

    // 开始收集
    function startCollection() {
        if (state.isCollecting) return;

        state.isCollecting = true;
        state.currentPage = 1;
        state.startDate = document.getElementById('start-date').value ? new Date(document.getElementById('start-date').value) : null;

        updateButtonStates(true);
        document.getElementById('collect-status').textContent = '收集中...';
        collectArticleInfo();
    }

    // 停止收集
    function stopCollection() {
        state.isCollecting = false;
        updateButtonStates(false);

        const collectedArticles = storage.getArticles();
        document.getElementById('collect-status').textContent = `收集已停止，已收集 ${collectedArticles.length} 篇文章`;
    }

    // 收集文章信息
    function collectArticleInfo() {
        if (!state.isCollecting) return;

        const articles = document.querySelectorAll('.inner_link_article_item');
        if (articles.length === 0) {
            stopCollection();
            return;
        }

        let shouldContinue = true;
        const storedData = storage.load();
        let collectedArticles = storedData.articles;

        articles.forEach(article => {
            if (!shouldContinue || !state.isCollecting) return;

            const title = article.querySelector('.inner_link_article_title span:last-child')?.textContent?.trim();
            const url = article.querySelector('.inner_link_article_date a')?.href;
            const dateStr = article.querySelector('.inner_link_article_date span:first-child')?.textContent?.trim();

            if (!title || !url || !dateStr) return;

            const date = new Date(dateStr);
            if (state.startDate && date < state.startDate) {
                shouldContinue = false;
                return;
            }

            collectedArticles.push(`${title}|${url}|${dateStr}`);
        });

        storage.save(collectedArticles, storedData.account);

        // 处理分页
        const paginationLabel = document.querySelector('.weui-desktop-pagination__num__wrp');
        if (paginationLabel) {
            const match = paginationLabel.textContent.match(/(\d+)\s*\/\s*(\d+)/);
            if (match) {
                state.currentPage = parseInt(match[1]);
                state.totalPages = parseInt(match[2]);
            }
        }

        const nextPageButton = document.querySelector('.weui-desktop-pagination__nav a:last-child');
        if (nextPageButton && !nextPageButton.classList.contains('weui-desktop-btn_disabled') && shouldContinue && state.isCollecting) {
            const randomDelay = Math.floor(Math.random() * 2000) + 1000;

            document.getElementById('collect-status').textContent =
                `收集中...第 ${state.currentPage}/${state.totalPages} 页，等待 ${(randomDelay/1000).toFixed(1)} 秒`;

            setTimeout(() => {
                if (state.isCollecting) {
                    nextPageButton.click();
                    setTimeout(collectArticleInfo, 1000);
                }
            }, randomDelay);
        } else {
            finishCollection();
        }
    }

    // 完成收集
    function finishCollection() {
        state.isCollecting = false;
        updateButtonStates(false);

        const collectedArticles = storage.getArticles();
        document.getElementById('collect-status').textContent = `收集完成，共 ${collectedArticles.length} 篇文章`;
    }

    // 下载CSV
    function downloadCSV() {
        const currentDate = new Date().toISOString().split('T')[0];
        const storedData = storage.load();
        const fileName = `${storedData.account}_${currentDate}.csv`;

        const csvContent = "公众号,标题,链接,日期\n" +
            storedData.articles.map(info => {
                const [title, url, date] = info.split('|');
                return `"${storedData.account}","${title.replace(/"/g, '""')}","${url}","${date}"`;
            }).join("\n");

        const blob = new Blob(["\uFEFF" + csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);

        GM_download({
            url: url,
            name: fileName,
            onload: () => URL.revokeObjectURL(url),
            onerror: (error) => {
                console.error('下载失败:', error);
                URL.revokeObjectURL(url);
            }
        });
    }

    // 清除数据
    function clearCollectedData() {
        if (confirm('确定要清除所有收集的数据吗？')) {
            storage.clear();
            document.getElementById('collect-status').textContent = '数据已清除';
            updateButtonStates(false);
        }
    }

    // 清理函数
    function cleanup() {
        if (state.dialogObserver) state.dialogObserver.disconnect();
        if (state.articlesObserver) state.articlesObserver.disconnect();
        if (state.accountCheckInterval) clearInterval(state.accountCheckInterval);
    }

    // 页面加载初始化
    window.addEventListener('load', () => {
        setTimeout(() => {
            try {
                createSafeUI();
            } catch (e) {
                console.error('初始化失败:', e);
            }
        }, 1500);
    });

    // 页面卸载时清理
    window.addEventListener('unload', cleanup);
})();
