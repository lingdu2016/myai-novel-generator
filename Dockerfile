# AI 小说创作工具 Dockerfile (Hugging Face Spaces 适配版)
FROM python:3.11-slim

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV HF_SPACE=1
ENV GRADIO_SERVER_NAME="0.0.0.0"
ENV GRADIO_SERVER_PORT=7860

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 创建非特权用户 (Hugging Face Spaces 默认使用 UID 1000)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# 设置工作目录
WORKDIR $HOME/app

# 复制并安装依赖
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# 复制应用代码
COPY --chown=user . .

# 创建持久化目录 (在 HF Spaces 中 /data 是挂载点)
USER root
RUN mkdir -p /data && chown -R user:user /data
USER user

# 暴露端口
EXPOSE 7860

# 启动脚本
CMD ["python", "run_hf.py"]
