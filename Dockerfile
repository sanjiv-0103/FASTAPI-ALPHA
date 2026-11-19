
# 1. Python Base Image
FROM python:3.10-slim

# 2. Prevent Unnecessary Python Cache Files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Set Working Directory
WORKDIR /code

# 4. Install Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy Application Files
COPY . .

# 6. Expose FastAPI Port
EXPOSE 8000

# 7. Start FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
