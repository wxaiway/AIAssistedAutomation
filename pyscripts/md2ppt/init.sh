# 更新系统包
sudo yum update -y

# 安装必要的系统依赖
sudo yum install gcc libffi-devel openssl-devel -y

# 安装 Chromium (用于 Marp CLI 的无头浏览器操作)
sudo yum install chromium -y

# 安装 poppler-utils（用于 pdf2image）
sudo yum install poppler-utils -y

# 安装必要的 Python 包
pip install pdf2image Pillow

# 安装 Node.js 和 npm
sudo yum install -y nodejs npm

# 安装 Marp CLI
sudo npm install -g @marp-team/marp-cli

