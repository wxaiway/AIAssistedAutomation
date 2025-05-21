// ==UserScript==
// @name         小红书全量数据采集器
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  自动滚动采集小红书全部笔记数据
// @author       YourName
// @match        https://www.xiaohongshu.com/user/profile/*
// @grant        GM_setValue
// @grant        GM_getValue
// @grant        GM_download
// @grant        GM_notification
// @require      https://cdn.jsdelivr.net/npm/papaparse@5.3.0/papaparse.min.js
// ==/UserScript==

(function() {
    'use strict';

    // 配置项
    const CONFIG = {
        STORAGE_KEY: 'XHS_FULL_NOTE_DATA_V8',
        MAX_RECORDS: 5000,
        SCROLL_DELAY: 3000,           // 滚动间隔时间(毫秒)
        SCROLL_STEP: 1000,             // 每次滚动距离(像素)
        LOAD_TIMEOUT: 10000,           // 加载超时时间(毫秒)
        MAX_RETRIES: 8,                // 最大重试次数
        NOTE_SELECTOR: '.note-item',   // 笔记选择器
        CONTAINER_SELECTOR: '#userPostedFeeds', // 容器选择器
        LOADING_INDICATOR: '.feeds-loading' // 加载指示器
    };

    // 运行状态
    let state = {
        isCollecting: false,
        lastNoteCount: 0,
        retryCount: 0,
        scrollAttempts: 0,
        collectedNoteIds: new Set(),
        scrollTimer: null,
        loadCheckTimer: null,
        lastContainerHeight: 0
    };

    // 初始化数据存储
    let allNotesData = GM_getValue(CONFIG.STORAGE_KEY, []);
    allNotesData.forEach(item => state.collectedNoteIds.add(item.noteId));

    // 主入口
    function init() {
        if (isNoteListPage()) {
            createControlPanel();
        } else {
            setTimeout(() => {
                if (isNoteListPage()) createControlPanel();
            }, 3000);
        }
    }

    // 判断是否是笔记列表页
    function isNoteListPage() {
        return document.querySelector(CONFIG.NOTE_SELECTOR) !== null;
    }

    // 提取笔记ID和链接参数
    function extractNoteIdAndParams(url) {
        // 修改正则表达式以匹配新的链接格式
        const matches = url.match(/\/user\/profile\/[^\/]+\/([a-f0-9]{24})(?:\?(.*))?/);
        if (!matches) return null;

        const noteId = matches[1];
        const params = matches[2] ? `?${matches[2]}` : '';

        // 生成新的链接格式
        return { noteId, params };
    }

    // 采集数据
    function collectData() {
        return new Promise(resolve => {
            const notes = document.querySelectorAll(CONFIG.NOTE_SELECTOR);
            const newNotes = [];

            notes.forEach(note => {
                try {
                    const noteLink = note.querySelector('a[href*="/user/profile/"]')?.href || '';
                    const { noteId, params } = extractNoteIdAndParams(noteLink);

                    if (!noteId || state.collectedNoteIds.has(noteId)) return;

                    const title = note.querySelector('.title')?.textContent?.trim() ||
                 note.querySelector('.note-title')?.textContent?.trim() ||
                 '无标题';
                    const author = note.querySelector('.author .name')?.textContent?.trim() ||
                 '未知作者';
                    const authorId = note.querySelector('.author')?.href?.match(/\/user\/profile\/([^\/?]+)/)?.[1] ||
                        '未知ID';
                    const likes = parseLikeCount(note.querySelector('.like-wrapper .count')?.textContent || 0);
                    const imgUrl = note.querySelector('a.cover img')?.src || '';

                    // 修改链接格式，保留参数
                    const url = `https://www.xiaohongshu.com/explore/${noteId}${params}`;

                    newNotes.push({
                        title,
                        noteId,
                        url,
                        author,
                        authorId,
                        likes,
                        imgUrl,
                        collectedAt: new Date().toISOString()
                    });

                    state.collectedNoteIds.add(noteId);
                } catch (e) {
                    console.error('解析笔记时出错:', e);
                }
            });

            if (newNotes.length > 0) {
                allNotesData = [...newNotes, ...allNotesData].slice(0, CONFIG.MAX_RECORDS);
                GM_setValue(CONFIG.STORAGE_KEY, allNotesData);
                updateStats(document.getElementById('xhs-stats'));
                console.log(`新增 ${newNotes.length} 条笔记，总计 ${allNotesData.length} 条`);
            }

            resolve();
        });
    }

    // 创建控制面板
    function createControlPanel() {
        const panel = document.createElement('div');
        panel.id = 'xhs-collector-panel';
        panel.style.position = 'fixed';
        panel.style.bottom = '30px';
        panel.style.right = '30px';
        panel.style.zIndex = '2147483647';
        panel.style.backgroundColor = 'rgba(0,0,0,0.85)';
        panel.style.padding = '15px';
        panel.style.borderRadius = '12px';
        panel.style.boxShadow = '0 4px 20px rgba(0,0,0,0.3)';
        panel.style.width = '320px'; // 固定宽度
        panel.style.border = '2px solid #ff2442';
        panel.style.color = '#ffffff';
        panel.style.height = 'auto'; // 确保高度自适应内容
        panel.style.maxHeight = '300px'; // 设置最大高度以防止过长

        // 允许面板拖拽，但限制宽度和高度
        let isDragging = false;
        let offsetX, offsetY;

        panel.addEventListener('mousedown', (e) => {
            isDragging = true;
            offsetX = e.clientX - panel.offsetLeft;
            offsetY = e.clientY - panel.offsetTop;
        });

        document.addEventListener('mousemove', (e) => {
            if (isDragging) {
                panel.style.left = `${e.clientX - offsetX}px`;
                panel.style.top = `${e.clientY - offsetY}px`;
                panel.style.width = '320px'; // 确保宽度固定
                panel.style.height = 'auto'; // 确保高度自适应内容
            }
        });

        document.addEventListener('mouseup', () => {
            isDragging = false;
        });

        // 标题
        const title = document.createElement('h3');
        title.textContent = '🍠 小红书采集器';
        title.style.margin = '0 0 15px 0';
        title.style.color = '#ff2442';
        title.style.textAlign = 'center';
        panel.appendChild(title);

        // 统计信息
        const statsDiv = document.createElement('div');
        statsDiv.id = 'xhs-stats';
        statsDiv.style.margin = '0 0 15px 0';
        statsDiv.style.color = '#ffffff';
        updateStats(statsDiv);
        panel.appendChild(statsDiv);

        // 按钮组
        const btnGroup = document.createElement('div');
        btnGroup.style.display = 'flex';
        btnGroup.style.gap = '10px';
        btnGroup.style.marginBottom = '12px';

        const toggleBtn = createButton('▶️ 开始采集', '#ff2442', toggleCollection);
        btnGroup.appendChild(toggleBtn);
        panel.appendChild(btnGroup);

        // 操作按钮
        const exportBtn = createButton('💾 导出CSV', '#4CAF50', exportData);
        exportBtn.style.width = '100%';
        exportBtn.style.marginBottom = '8px';
        panel.appendChild(exportBtn);

        const clearBtn = createButton('🗑️ 清空数据', '#f44336', clearData);
        clearBtn.style.width = '100%';
        panel.appendChild(clearBtn);

        document.documentElement.appendChild(panel);
    }

    // 创建按钮
    function createButton(text, color, onClick) {
        const btn = document.createElement('button');
        btn.textContent = text;
        btn.style.padding = '10px 12px';
        btn.style.background = color;
        btn.style.color = 'white';
        btn.style.border = 'none';
        btn.style.borderRadius = '6px';
        btn.style.cursor = 'pointer';
        btn.style.fontWeight = 'bold';
        btn.style.fontSize = '14px';
        btn.style.width = '100%'; // 确保按钮宽度一致
        btn.onclick = onClick;
        return btn;
    }

    // 提取笔记ID
    function extractNoteId(url) {
        const matches = url.match(/\/([a-f0-9]{24})(?:\?|$)/);
        return matches ? matches[1] : null;
    }

    // 更新统计信息
    function updateStats(element) {
        const total = allNotesData.length;
        const latestDate = total > 0 ? new Date(allNotesData[0].collectedAt).toLocaleString() : '无';

        element.innerHTML = `
            <div style="display: flex; justify-content: space-between; color: #ffffff;">
                <span>已采集:</span>
                <strong>${total} 条</strong>
            </div>
            <div style="display: flex; justify-content: space-between; color: #ffffff;">
                <span>最后采集:</span>
                <span>${latestDate}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 8px; color: #ffffff;">
                <span>状态:</span>
                <span style="color:${state.isCollecting ? '#4CAF50' : '#f44336'}; font-weight: bold;">
                    ${state.isCollecting ? '采集中...' : '待机'}
                </span>
            </div>
        `;
    }

    // 新增：切换采集状态
    function toggleCollection() {
        if (state.isCollecting) {
            stopCollection();
        } else {
            startCollection();
        }
    }

    // 更新按钮文本
    function updateButtonState(button, isCollecting) {
        button.textContent = isCollecting ? '⏹️ 停止' : '▶️ 开始采集';
        button.style.background = isCollecting ? '#666' : '#ff2442';
    }

    // 开始采集
    function startCollection() {
        if (state.isCollecting) return;

        state.isCollecting = true;
        const toggleBtn = document.querySelector('#xhs-collector-panel button');
        updateButtonState(toggleBtn, true); // 更新按钮状态

        state.retryCount = 0;
        state.scrollAttempts = 0;
        const container = document.querySelector(CONFIG.CONTAINER_SELECTOR);
        state.lastContainerHeight = container ? container.scrollHeight : 0;
        state.lastNoteCount = document.querySelectorAll(CONFIG.NOTE_SELECTOR).length;

        updateStats(document.getElementById('xhs-stats'));
        showNotification('开始采集数据...');

        // 初始采集
        collectData().then(() => {
            startScrollCycle();
        });
    }

    // 停止采集
    function stopCollection() {
        if (!state.isCollecting) return;

        state.isCollecting = false;
        const toggleBtn = document.querySelector('#xhs-collector-panel button');
        updateButtonState(toggleBtn, false); // 更新按钮状态

        clearTimeout(state.scrollTimer);
        clearTimeout(state.loadCheckTimer);

        updateStats(document.getElementById('xhs-stats'));
        showNotification('采集已停止');
    }

    // 开始滚动循环
    function startScrollCycle() {
        if (!state.isCollecting) return;

        collectData().then(() => {
            window.scrollBy(0, CONFIG.SCROLL_STEP);
            state.scrollAttempts++;
            console.log(`滚动尝试 ${state.scrollAttempts} 次`);

            state.scrollTimer = setTimeout(() => {
                checkForNewData();
            }, CONFIG.SCROLL_DELAY);
        });
    }

    // 检查新数据
    function checkForNewData() {
        if (!state.isCollecting) return;

        const container = document.querySelector(CONFIG.CONTAINER_SELECTOR);
        if (!container) {
            console.error('未找到滚动容器');
            return;
        }

        const currentHeight = container.scrollHeight;
        const currentNoteCount = document.querySelectorAll(CONFIG.NOTE_SELECTOR).length;
        const isLoading = document.querySelector(CONFIG.LOADING_INDICATOR) !== null;

        console.log(`检查: 高度=${currentHeight}, 上次高度=${state.lastContainerHeight}, 笔记数=${currentNoteCount}, 加载中=${isLoading}`);

        if (currentHeight > state.lastContainerHeight || currentNoteCount > state.lastNoteCount) {
            console.log('检测到新内容');
            state.lastContainerHeight = currentHeight;
            state.lastNoteCount = currentNoteCount;
            state.retryCount = 0;

            collectData().then(() => {
                startScrollCycle();
            });
        } else if (isLoading) {
            state.retryCount++;
            console.log(`等待加载完成 (${state.retryCount}/${CONFIG.MAX_RETRIES})`);

            if (state.retryCount > CONFIG.MAX_RETRIES) {
                console.log('达到最大重试次数，继续滚动');
                state.retryCount = 0;
                startScrollCycle();
            } else {
                state.loadCheckTimer = setTimeout(() => {
                    checkForNewData();
                }, 1000);
            }
        } else {
            if (isAtBottom()) {
                console.log('已滚动到底部');
                // 检查是否有新数据更新
                if (state.lastNoteCount === currentNoteCount) {
                    console.log('数据不再更新，采集完成');
                    stopCollection();
                    showNotification('所有数据采集完成');
                } else {
                    startScrollCycle();
                }
            } else {
                console.log('未检测到新内容，继续滚动');
                startScrollCycle();
            }
        }
    }

    // 检查是否滚动到底部
    function isAtBottom() {
        return (window.innerHeight + window.scrollY) >= document.body.scrollHeight - 500;
    }

    // 解析点赞数
    function parseLikeCount(text) {
        if (!text) return 0;
        const numText = text.replace(/[^0-9.]/g, '');
        if (!numText) return 0;

        const num = parseFloat(numText);
        if (text.includes('千')) return num * 1000;
        if (text.includes('万')) return num * 10000;
        return num;
    }

    // 导出数据
    function exportData() {
        if (allNotesData.length === 0) {
            showNotification('没有可导出的数据');
            return;
        }

        const csvData = allNotesData.map(item => ({
            '标题': item.title,
            '笔记ID': item.noteId,
            '链接': item.url,
            '作者': item.author,
            '作者ID': item.authorId,
            '点赞数': item.likes,
            '图片URL': item.imgUrl,
            '采集时间': item.collectedAt
        }));

        const csv = Papa.unparse(csvData);
        const filename = `小红书笔记_${new Date().toISOString().slice(0,10)}.csv`;

        GM_download({
            url: 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv),
            name: filename,
            saveAs: true
        });
    }

    // 清空数据
    function clearData() {
        if (confirm('确定要清空所有采集数据吗？此操作不可撤销！')) {
            allNotesData = [];
            state.collectedNoteIds.clear();
            GM_setValue(CONFIG.STORAGE_KEY, []);
            updateStats(document.getElementById('xhs-stats'));
            showNotification('数据已清空');
        }
    }

    // 显示通知
    function showNotification(message) {
        GM_notification({
            title: '小红书采集器',
            text: message,
            timeout: 3000
        });
    }

    // 页面加载完成后初始化
    if (document.readyState === 'complete') {
        init();
    } else {
        window.addEventListener('load', init);
    }
})();
