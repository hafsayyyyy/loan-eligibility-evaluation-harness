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
    return {
        "message": "Loan Eligibility Evaluation API is running"
    }


def create_demo_response(question: str):
    """
    Creates a local demo evaluation when OpenAI is not available.
    This allows the dashboard and API to be tested without an OpenAI API key.
    """

    question_lower = question.lower()

    if "document" in question_lower or "cnic" in question_lower:
        answer = (
            "Applicants should normally provide valid identification such as "
            "a CNIC, proof of income or business activity, and any other "
            "documents required by the lender. Exact requirements may vary "
            "by loan product and lender."
        )

    elif "age" in question_lower:
        answer = (
            "Age requirements depend on the lender and loan product. "
            "The applicant should meet the minimum and maximum age limits "
            "specified by the lender at the time of application."
        )

    elif "salary" in question_lower or "income" in question_lower:
        answer = (
            "The applicant may need to provide evidence of regular income, "
            "such as salary records, bank statements, or business income "
            "documents. The required income level depends on the loan "
            "amount and lender's eligibility criteria."
        )

    elif "loan" in question_lower and "eligible" in question_lower:
        answer = (
            "Loan eligibility usually depends on factors such as age, "
            "income, repayment capacity, credit history, required documents, "
            "and the lender's eligibility criteria. Final approval depends "
            "on the lender's assessment."
        )

    else:
        answer = (
            "Loan eligibility depends on the applicant's income, repayment "
            "capacity, age, credit history, required documents, and the "
            "specific lender's policy. Additional information may be needed "
            "to determine eligibility accurately."
        )

    return {
        "answer": answer,
        "scores": {
            "correctness": 4,
            "completeness": 4,
            "tone": 5
        }
    }


@app.post("/evaluate")
def evaluate(request: EvaluationRequest):

    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    api_key = os.getenv("OPENAI_API_KEY")

    # ==================================================
    # DEMO MODE
    # ==================================================

    if not api_key:

        parsed_response = create_demo_response(
            request.question
        )

        raw_response = json.dumps(
            parsed_response,
            ensure_ascii=False
        )

        computed_scores = score_response(
            parsed_response,
            RUBRIC
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
                "scores": computed_scores,
                "mode": "demo"
            }

        except Exception as exc:
            db.rollback()

            raise HTTPException(
                status_code=500,
                detail=f"Database error: {str(exc)}"
            )

        finally:
            db.close()

    # ==================================================
    # OPENAI MODE
    # ==================================================

    client = OpenAI(api_key=api_key)

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
            model=os.getenv(
                "OPENAI_MODEL",
                "gpt-4o-mini"
            ),
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
            response_format={
                "type": "json_object"
            }
        )

        raw_response = (
            llm_result.choices[0].message.content
        )

        if not raw_response:
            raise ValueError(
                "LLM returned an empty response"
            )

        parsed_response = json.loads(
            raw_response
        )

        if not isinstance(
            parsed_response,
            dict
        ):
            raise ValueError(
                "LLM response must be a JSON object"
            )

        if not isinstance(
            parsed_response.get("answer"),
            str
        ):
            raise ValueError(
                "LLM response must contain an answer"
            )

        computed_scores = score_response(
            parsed_response,
            RUBRIC
        )

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=502,
            detail="LLM returned invalid JSON"
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc)
        )

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
            "scores": computed_scores,
            "mode": "openai"
        }

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(exc)}"
        )

    finally:
        db.close()