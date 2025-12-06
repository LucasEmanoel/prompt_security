FROM python:3.11

WORKDIR /app

COPY requirements.txt .

ENV PIP_DEFAULT_TIMEOUT=500

RUN pip install -r requirements.txt

RUN guardrails configure --enable-metrics --enable-remote-inferencing  --token "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJnaXRodWJ8NDgwOTkwOTkiLCJhcGlLZXlJZCI6ImVhZThkNGJjLWE1MTEtNDg4ZS1iZGQ1LTFjY2I0NTU3ZmU1NCIsInNjb3BlIjoicmVhZDpwYWNrYWdlcyIsInBlcm1pc3Npb25zIjpbXSwiaWF0IjoxNzYzNzUzODgxLCJleHAiOjE3NzE1Mjk4ODF9.22gWtrSNvvrCgEH0m-q-7poCG8BBSq6nLO-KtprNkHY"
RUN guardrails hub install hub://guardrails/gibberish_text

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "4000"]
