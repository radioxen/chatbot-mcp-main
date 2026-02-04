FROM python:3.11-slim

WORKDIR /app

# Install requirements
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8100
EXPOSE 8100

# Create entrypoint script that passes environment variables as arguments
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

CMD ["/app/entrypoint.sh"] 