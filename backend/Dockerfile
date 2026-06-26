FROM python:3.12-slim

# Не буферизировать вывод Python — логи сразу в stdout/stderr
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Копируем только requirements первым слоем — кэш не сбрасывается при изменении кода
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Запуск от непривилегированного пользователя
RUN adduser --disabled-password --gecos "" appuser
USER appuser

EXPOSE 8000

# Liveness-проба: проверяем /api/v1/health каждые 30 секунд
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')" || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]
