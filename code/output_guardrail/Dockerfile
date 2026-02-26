FROM python:3.11

WORKDIR /app

COPY requirements.txt .

ENV PIP_DEFAULT_TIMEOUT=500

RUN pip install -r requirements.txt

RUN guardrails configure --enable-metrics --enable-remote-inferencing  --token "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJCVTZUZHhhaGZ6Y1A0N1dneWNBcVh1eTBZU25HQ29PUSIsImFwaUtleUlkIjoiOWNhNzAyNzAtNDk1YS00OTdiLTllZjctNmY0ZTBhMTExMjVkIiwic2NvcGUiOiJyZWFkOnBhY2thZ2VzIiwicGVybWlzc2lvbnMiOlsidGhyZWF0X3Rlc3Rlcl9pbnZpdGU6dHJ1ZSJdLCJpYXQiOjE3NzIxMjkxMjMsImV4cCI6MTc3OTkwNTEyM30.iFhHmxfJlSmDm4P6XBHokePpgPRH4nQah1Eknebdk3E"
RUN guardrails hub install hub://guardrails/gibberish_text

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "4000"]
