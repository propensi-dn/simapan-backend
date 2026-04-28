FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate && gunicorn simapan.wsgi:application --bind 0.0.0.0:8000 --workers 2"]