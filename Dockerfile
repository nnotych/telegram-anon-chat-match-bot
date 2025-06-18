FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot.py .

ENV TOKEN='"7712103509:AAGoxMdX7byQUDMkEKwiwnEp0HAVdWBa-vo"'


CMD ["python", "bot.py"]