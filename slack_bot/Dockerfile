FROM python:3.11-slim

WORKDIR /app

# Install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot files
COPY . .

# Set Python path to include workspace directory (mounted at runtime)
ENV PYTHONPATH=/workspace

# Run the bot
CMD ["python", "bot.py"] 