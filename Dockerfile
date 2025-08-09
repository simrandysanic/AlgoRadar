FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ .
COPY wsgi.py .
RUN ls -la /app
RUN ls -la /app/templates
ENV FLASK_APP=wsgi.py
ENV FLASK_ENV=production
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--log-level", "debug", "wsgi:app"]