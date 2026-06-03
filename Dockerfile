FROM python:3.11-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем только requirements.txt сначала для кэширования слоев Docker
COPY requirements.txt .

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь остальной код проекта в контейнер
COPY . .

# Команда для запуска FastAPI приложения
CMD ["uvicorn", "backend.main:api", "--host", "0.0.0.0", "--port", "8000"]
