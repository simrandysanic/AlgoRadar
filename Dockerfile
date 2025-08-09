FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .

RUN chmod +x /app/src/entrypoint.sh

RUN ls -la /app  # Debug: Verify files copied
RUN ls -la /app/templates  # Debug: Verify templates

ENV FLASK_APP=app.py
ENV FLASK_ENV=production

EXPOSE 5000

CMD ["/app/src/entrypoint.sh"]
