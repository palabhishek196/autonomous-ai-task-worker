# Autonomous Invoice Task Worker

A narrow, working agent prototype for the CentrAlign AI Engineering Intern challenge. The agent uses LLM tool calling to inspect sandbox invoices, select the latest matching invoice, validate extracted fields, save to SQLite, and verify the persisted record.

## Setup (Windows PowerShell)

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` to set your own `OPENAI_API_KEY`. Never commit `.env`.

```powershell
python agent.py
```

Example task: `Find the latest invoice from ABC Technologies, extract the amount and due date, save it to our system, and confirm once done.`

## Architecture

User request → LLM planner/tool selector → sandbox file tools → validation and SQLite write → independent database read-back → response. The LLM dynamically chooses tools and can react to tool errors. No external business accounts are accessed.

## Design decisions

- Small, testable scope instead of a fake general-purpose desktop operator.
- Deterministic field validation against invoice text before writing.
- Idempotent writes by invoice number.
- Read-back verification is a separate tool call.
- Path traversal is blocked for invoice reads.

## Limitations

- Plain text invoices only; not PDF or OCR.
- Source files use a simple key-value format.
- Requires a configured LLM API and internet access.
- No GUI, authentication, scheduling, or multi-user concurrency.
- Agent decisions are probabilistic; run multiple test prompts before recording a demo.

## Next improvements

PDF extraction, an HTTP-based simulated ERP, user approval gates, richer evaluation, observability, and durable task state.

## Dependencies

Python, OpenAI API (model configured in `.env`), python-dotenv, SQLite (Python standard library). AI coding assistance was used during development.
