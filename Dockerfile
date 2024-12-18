# Используем официальный образ Python
FROM python:3.9.18-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем необходимые системные зависимости
RUN apt-get update && apt-get install -y \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Создаем директорию для базы данных
RUN mkdir -p /app/data && chmod 777 /app/data

# Обновляем pip
RUN pip install --no-cache-dir --upgrade pip

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Создаем пользователя без прав root
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Определяем команду для запуска бота
CMD ["python", "app.py"] 