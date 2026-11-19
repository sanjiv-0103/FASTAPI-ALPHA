
# 1. Use Lightweight Python Image
FROM python:3.10-slim

# 2. Configure Python Environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Set Working Directory
WORKDIR /code

# 4. Copy Dependencies First
COPY requirements.txt .

# 5. Install Python Packages
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy Application Files
COPY . .

# 7. Run Application as Non-Root User
RUN useradd --create-home appuser && chown -R appuser:appuser /code
USER appuser

# 8. Expose FastAPI Port
EXPOSE 8000

# 9. Start FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
