# Sử dụng Python 3.12 base image
FROM python:3.12-slim

# Thiết lập working directory
WORKDIR /app

# Copy requirements.txt trước để tận dụng Docker cache
COPY uiclient.egg-info/requires.txt .

# Cài đặt các dependencies với version cụ thể
RUN pip install --no-cache-dir \
    fastapi==0.115.4 \
    groq==0.11.0 \
    openai==1.54.3 \
    pydantic==2.9.2 \
    python-dotenv==1.0.1 \
    python-multipart==0.0.17 \
    requests==2.32.3 \
    uvicorn==0.32.0 \
    httpx==0.24.1 \
    redis

# Copy toàn bộ code vào container
COPY . .

# Expose port 8000 (port mặc định của ứng dụng)
EXPOSE 8000

# Command để chạy ứng dụng
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]