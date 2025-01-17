// ==UserScript==
// @name         下载即梦HD图片(webp/jpg)
// @namespace    http://tampermonkey.net/
// @version      1.1
// @description  Collect and download specific image URLs containing aigc_resize:2400:2400 and labeled as '超清' from the page, with option to convert webp to jpg
// @match        https://jimeng.jianying.com/*
// @grant        GM_download
// @author       WxaiWay
// ==/UserScript==

(function() {
    'use strict';

    class ImageCollector {
        constructor() {
            this.collectedUrls = [];
            this.downloadBtn = null;
            this.isDownloading = false;
            this.progressBar = null;
        }

        init() {
            this.createControlPanel();
            this.observeImages();
        }

        decodeHTMLEntities(text) {
            const textArea = document.createElement('textarea');
            textArea.innerHTML = text;
            return textArea.value;
        }

        getImageUrl(img) {
            let src = img.getAttribute('src');
            if (src) {
                src = this.decodeHTMLEntities(src);
                if (src.includes('aigc_resize:2400:2400')) {
                    return src;
                }
            }
            return null;
        }

        createControlPanel() {
            const panel = document.createElement('div');
            panel.style.cssText = `
                position: fixed;
                top: 0;
                left: 50%;
                transform: translateX(-50%);
                background: white;
                border: 1px solid black;
                border-top: none;
                padding: 10px;
                z-index: 10000;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                border-radius: 0 0 5px 5px;
                cursor: move;
            `;

            const dragHandle = document.createElement('div');
            dragHandle.style.cssText = `
                width: 100%;
                height: 10px;
                background: #ddd;
                margin-bottom: 5px;
                cursor: move;
            `;
            panel.appendChild(dragHandle);

            const collectBtn = this.createButton('重新收集图片', () => this.collectImages());
            this.downloadBtn = this.createButton('批量下载(0)', () => this.showDownloadDialog());

            this.progressBar = document.createElement('div');
            this.progressBar.style.cssText = `
                width: 100%;
                height: 5px;
                background-color: #f0f0f0;
                margin-top: 5px;
                display: none;
            `;

            const progressInner = document.createElement('div');
            progressInner.style.cssText = `
                width: 0%;
                height: 100%;
                background-color: #4CAF50;
                transition: width 0.3s;
            `;
            this.progressBar.appendChild(progressInner);

            panel.appendChild(dragHandle);
            panel.appendChild(collectBtn);
            panel.appendChild(this.downloadBtn);
            panel.appendChild(this.progressBar);

            document.body.appendChild(panel);

            this.makeDraggable(panel, dragHandle);
        }

        createButton(text, onClick) {
            const button = document.createElement('button');
            button.textContent = text;
            button.style.marginRight = '5px';
            button.addEventListener('click', onClick);
            return button;
        }

        updateDownloadButtonText() {
            if (this.downloadBtn) {
                this.downloadBtn.textContent = `批量下载(${this.collectedUrls.length})`;
            }
        }

        collectImages() {
            this.collectedUrls = [];
            document.querySelectorAll('.container-EdniD0').forEach(container => {
                const imgElement = container.querySelector('.image-mh68Se');
                const metaRightElements = container.querySelectorAll('.metaRight-fF8GZJ');
                const editSection = document.querySelector('.container-RBbKMJ');
                const disabledHDButton = editSection ? editSection.querySelector('.optItem-iyWnC2.disabled-R018rY') : null;

                let isHD = false;

                for (const metaRight of metaRightElements) {
                    if (metaRight.textContent.trim() === '超清') {
                        isHD = true;
                        break;
                    }
                }

                if (!isHD && disabledHDButton) {
                    const buttonText = disabledHDButton.textContent.trim();
                    if (buttonText === '超清') {
                        isHD = true;
                    }
                }

                if (isHD) {
                    let url = this.getImageUrl(imgElement);
                    if (url && !this.collectedUrls.includes(url)) {
                        this.collectedUrls.push({url: url, element: imgElement});
                        console.log('收集图片URL:', url);
                    }
                }
            });
            this.showNotification(`已重新收集 ${this.collectedUrls.length} 个符合条件的图片URL`);
            this.updateDownloadButtonText();
        }

        showDownloadDialog() {
            const dialog = document.createElement('div');
            dialog.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: white;
        padding: 20px;
        border-radius: 5px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        z-index: 10002;
        width: 250px; // 设置固定宽度
    `;

            const createInput = (type, placeholder, defaultValue) => {
                const input = document.createElement('input');
                input.type = type;
                input.placeholder = placeholder;
                input.value = defaultValue;
                input.style.marginBottom = '10px';
                input.style.width = '100%';
                input.style.boxSizing = 'border-box'; // 确保padding不会增加总宽度
                return input;
            };

            const prefixInput = createInput('text', '输入文件名前缀', '');
            const startInput = createInput('number', '起始索引', '1');
            const delayInput = createInput('number', '下载延迟(ms)', '1000');

            const formatSelect = document.createElement('select');
            formatSelect.style.marginBottom = '10px';
            formatSelect.style.width = '100%';
            formatSelect.style.boxSizing = 'border-box';
            ['webp', 'jpg'].forEach(format => {
                const option = document.createElement('option');
                option.value = format;
                option.textContent = format.toUpperCase();
                formatSelect.appendChild(option);
            });

            const startDownloadBtn = this.createButton('开始下载', () => {
                const prefix = prefixInput.value;
                const startIndex = parseInt(startInput.value, 10) || 1;
                const delay = parseInt(delayInput.value, 10) || 1000;
                const format = formatSelect.value;
                dialog.remove();
                this.downloadImages(prefix, startIndex, delay, format);
            });
            startDownloadBtn.style.width = '100%';
            startDownloadBtn.style.boxSizing = 'border-box';
            startDownloadBtn.style.marginBottom = '10px';

            const cancelBtn = this.createButton('取消', () => dialog.remove());
            cancelBtn.style.width = '100%';
            cancelBtn.style.boxSizing = 'border-box';

            dialog.appendChild(prefixInput);
            dialog.appendChild(startInput);
            dialog.appendChild(delayInput);
            dialog.appendChild(formatSelect);
            dialog.appendChild(startDownloadBtn);
            dialog.appendChild(cancelBtn);

            document.body.appendChild(dialog);
        }

        downloadImages(prefix, startIndex, delay, format) {
            if (this.isDownloading) {
                this.showNotification('下载已在进行中');
                return;
            }

            this.isDownloading = true;
            let downloadedCount = 0;

            const downloadNext = (index) => {
                if (index >= this.collectedUrls.length) {
                    this.isDownloading = false;
                    this.showNotification(`全部 ${this.collectedUrls.length} 张图片下载完成`);
                    this.updateProgressIndicator(0, 1);
                    return;
                }

                const {url, element} = this.collectedUrls[index];
                const filename = `${prefix}${startIndex + index}.${format}`;

                this.convertAndSave(element, filename, format, () => {
                    downloadedCount++;
                    this.updateProgressIndicator(downloadedCount, this.collectedUrls.length);
                    setTimeout(() => downloadNext(index + 1), delay);
                });
            };

            this.showNotification(`开始下载 ${this.collectedUrls.length} 张图片`);
            this.progressBar.style.display = 'block';
            downloadNext(0);
        }

        convertAndSave(imgElement, filename, format, callback) {
            const canvas = document.createElement('canvas');
            canvas.width = imgElement.naturalWidth;
            canvas.height = imgElement.naturalHeight;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(imgElement, 0, 0);

            canvas.toBlob((blob) => {
                const url = URL.createObjectURL(blob);
                GM_download({
                    url: url,
                    name: filename,
                    onload: () => {
                        console.log(`Downloaded: ${filename}`);
                        URL.revokeObjectURL(url);
                        callback();
                    },
                    onerror: (error) => {
                        console.error(`Error downloading ${filename}:`, error);
                        URL.revokeObjectURL(url);
                        callback();
                    }
                });
            }, format === 'jpg' ? 'image/jpeg' : 'image/webp');
        }

        updateProgressIndicator(current, total) {
            const percentage = (current / total) * 100;
            const progressInner = this.progressBar.firstChild;
            progressInner.style.width = `${percentage}%`;
        }

        showNotification(message) {
            const notification = document.createElement('div');
            notification.textContent = message;
            notification.style.cssText = `
                position: fixed;
                top: 10px;
                right: 10px;
                background: rgba(0, 0, 0, 0.7);
                color: white;
                padding: 10px;
                border-radius: 5px;
                z-index: 10001;
            `;
            document.body.appendChild(notification);
            setTimeout(() => {
                notification.style.opacity = '0';
                notification.style.transition = 'opacity 0.5s';
                setTimeout(() => notification.remove(), 500);
            }, 3000);
        }

        observeImages() {
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    if (mutation.type === 'childList') {
                        mutation.addedNodes.forEach((node) => {
                            if (node.nodeType === Node.ELEMENT_NODE) {
                                const containers = node.querySelectorAll('.container-EdniD0');
                                containers.forEach(container => {
                                    const imgElement = container.querySelector('.image-mh68Se');
                                    const metaRightElements = container.querySelectorAll('.metaRight-fF8GZJ');
                                    const editSection = document.querySelector('.container-RBbKMJ');
                                    const disabledHDButton = editSection ? editSection.querySelector('.optItem-iyWnC2.disabled-R018rY') : null;

                                    let isHD = false;

                                    for (const metaRight of metaRightElements) {
                                        if (metaRight.textContent.trim() === '超清') {
                                            isHD = true;
                                            break;
                                        }
                                    }

                                    if (!isHD && disabledHDButton) {
                                        const buttonText = disabledHDButton.textContent.trim();
                                        if (buttonText === '超清') {
                                            isHD = true;
                                        }
                                    }

                                    if (isHD) {
                                        let url = this.getImageUrl(imgElement);
                                        if (url && !this.collectedUrls.some(item => item.url === url)) {
                                            this.collectedUrls.push({url: url, element: imgElement});
                                            console.log('收集新加载图片URL:', url);
                                            this.updateDownloadButtonText();
                                        }
                                    }
                                });
                            }
                        });
                    }
                });
            });

            observer.observe(document.body, { childList: true, subtree: true });
        }

        makeDraggable(element, handle) {
            let isDragging = false;
            let startX, startY, startLeft, startTop;

            const movePanel = (e) => {
                if (!isDragging) return;
                const dx = e.clientX - startX;
                const dy = e.clientY - startY;
                element.style.left = `${startLeft + dx}px`;
                element.style.top = `${startTop + dy}px`;
                element.style.transform = 'none';
            };

            const stopDragging = () => {
                isDragging = false;
                document.removeEventListener('mousemove', movePanel);
                document.removeEventListener('mouseup', stopDragging);
            };

            handle.addEventListener('mousedown', (e) => {
                isDragging = true;
                startX = e.clientX;
                startY = e.clientY;
                startLeft = element.offsetLeft;
                startTop = element.offsetTop;
                document.addEventListener('mousemove', movePanel);
                document.addEventListener('mouseup', stopDragging);
            });
        }
    }

    const collector = new ImageCollector();
    collector.init();
})();
