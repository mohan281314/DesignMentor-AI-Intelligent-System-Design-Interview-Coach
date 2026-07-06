# DesignMentor AI — Setup & Run Guide

## Prerequisites
- Python 3.11+
- An OpenAI API key

## 1. Install dependencies

```bash
pip install -r requirements.txt
```

## 2. Configure environment

```bash
copy .env.example .env      # Windows
# cp .env.example .env      # macOS / Linux
```

Edit `.env` and set your `OPENAI_API_KEY`.

## 3. Run the server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

---

## Endpoints

| Method   | Path                     | Description                              |
|----------|--------------------------|------------------------------------------|
| GET      | `/health`                | Liveness check                           |
| POST     | `/design`                | Generate a full system design            |
| POST     | `/interview/start`       | Start a mock interview session           |
| POST     | `/interview/answer`      | Submit answer → get evaluation + next Q |
| POST     | `/evaluate`              | One-shot answer evaluation (no session) |
| POST     | `/diagram`               | Generate a Mermaid architecture diagram  |
| POST     | `/feedback`              | Post-interview learning report           |
| POST     | `/chat`                  | Free-form coaching conversation          |
| DELETE   | `/session/{session_id}`  | End and delete a session                 |

---

## Example: Generate a design

```bash
curl -X POST http://localhost:8000/design \
  -H "Content-Type: application/json" \
  -d '{"topic": "Instagram"}'
```

## Example: Run a mock interview

```bash
# Start
curl -X POST http://localhost:8000/interview/start \
  -H "Content-Type: application/json" \
  -d '{"topic": "Netflix"}'

# Answer (use the session_id from the response above)
curl -X POST http://localhost:8000/interview/answer \
  -H "Content-Type: application/json" \
  -d '{"session_id": "<id>", "answer": "I would use a CDN for video delivery..."}'
```

---

## Project structure

```
.
├── app/
│   ├── __init__.py
│   ├── config.py          # Pydantic settings (reads .env)
│   ├── schemas.py         # Request / response models
│   ├── chains.py          # LangChain chain functions
│   ├── session_manager.py # In-memory TTL session store
│   └── main.py            # FastAPI app & routes
├── prompts/
│   ├── system.txt
│   ├── design_generator.txt
│   ├── interview_questions.txt
│   ├── answer_evaluator.txt
│   ├── diagram_generator.txt
│   └── feedback_resources.txt
├── .env.example
├── requirements.txt
└── pyproject.toml
```
