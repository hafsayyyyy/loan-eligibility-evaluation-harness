import json
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

from database import SessionLocal, Evaluation, create_tables
from scoring import score_response

load_dotenv()

app = FastAPI(
    title="Loan Eligibility Evaluation API",
    description="API for evaluating loan eligibility responses using an LLM and scoring rubric.",
    version="1.0.0"
)


RUBRIC_PATH = Path(__file__).parent / "evaluation_rubric.json"

with open(RUBRIC_PATH, "r", encoding="utf-8-sig") as file:
    RUBRIC = json.load(file)


class EvaluationRequest(BaseModel):
    question: str


@app.on_event("startup")
def startup():
    create_tables()


@app.get("/")
def home():
    return {"message": "Loan Eligibility Evaluation API is running"}


@app.post("/evaluate")
def evaluate(request: EvaluationRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(
            status_code=503,
            detail="OPENAI_API_KEY is not configured"
        )

    prompt = f"""
You are a professional loan eligibility assistant and evaluator.

Answer the following loan-related question accurately.
Never guarantee loan approval or invent lender-specific policies.
Mention when additional information is required.

Question:
{request.question}

Evaluate your answer using this rubric:
{json.dumps(RUBRIC, indent=2)}

Return ONLY a valid JSON object in this exact structure:
{{
    "answer": "Your complete answer to the question",
    "scores": {{
        "correctness": 0,
        "completeness": 0,
        "tone": 0
    }}
}}

Each score must be an integer between 0 and 5.
"""

    try:
        llm_result = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {
                    "role": "system",
                    "content": "Return valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"}
        )

        raw_response = llm_result.choices[0].message.content

        if not raw_response:
            raise ValueError("LLM returned an empty response")

        parsed_response = json.loads(raw_response)

        if not isinstance(parsed_response, dict):
            raise ValueError("LLM response must be a JSON object")

        if not isinstance(parsed_response.get("answer"), str):
            raise ValueError("LLM response must contain an answer")

        computed_scores = score_response(parsed_response, RUBRIC)

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=502,
            detail="LLM returned invalid JSON"
        )
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"LLM evaluation failed: {str(exc)}"
        )

    db = SessionLocal()

    try:
        evaluation = Evaluation(
            question=request.question,
            raw_response=raw_response,
            scores=json.dumps(computed_scores)
        )

        db.add(evaluation)
        db.commit()

        return {
            "raw_response": raw_response,
            "scores": computed_scores
        }

    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(exc)}"
        )
    finally:
        db.close()

