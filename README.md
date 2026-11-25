# Loan Eligibility Evaluation Harness

## Project Overview

The Loan Eligibility Evaluation Harness is a dataset and rubric-based project designed to evaluate AI-generated responses to loan eligibility questions.

It focuses on factual correctness, completeness, and professional communication.

## Project Structure

```text
loan-eligibility-evaluation-harness/
│
├── data/
│   └── loan_eligibility_dataset.csv
│
├── scripts/
│   └── validate_rubric.py
│
├── tests/
│   └── test_scoring.py
│
├── dashboard/
│   └── app.py
│
├── app.py
├── database.py
├── scoring.py
├── evaluation_rubric.json
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── render.yaml
├── README.md
└── .gitignore
```

## Dataset Creation

The dataset was created to represent realistic customer questions about loan eligibility and common loan application situations.

It contains **24 distinct questions with expected answer templates** and is stored in:

`data/loan_eligibility_dataset.csv`

### How the Dataset Was Created

The dataset was manually developed using common loan eligibility scenarios and frequently asked questions that potential loan applicants may have.

The following steps were followed to create it:

1. **Topic Identification:** Identified common loan eligibility topics such as age, CNIC, income, employment, credit history, guarantors, documents, and repayment.
2. **Question Generation:** Created 24 distinct questions based on realistic situations and concerns of loan applicants.
3. **Categorization:** Organized each question into a relevant category to make the dataset structured and easy to use.
4. **Expected Answer Preparation:** Wrote an expected answer template for each question using general loan eligibility guidance.
5. **Unique Identification:** Assigned a unique question ID to every record, from LEQ001 to LEQ024.
6. **CSV Organization:** Stored all questions, categories, IDs, and expected answers in a CSV file for consistent evaluation of AI-generated responses.

The dataset contains general eligibility guidance and does not assume the specific policies of any particular lender. Expected answers are reference templates and may require adjustment according to actual lender requirements.

### Dataset Columns

The CSV contains four columns:

- `question_id`: Unique identifier for each question.
- `category`: Category or topic of the question.
- `question`: Realistic customer loan eligibility question.
- `expected_answer`: Expected answer template used as a reference when evaluating AI responses.

### Dataset Topics

The dataset covers:

- Basic eligibility
- Age and CNIC requirements
- Salary and business income
- Freelancing income
- Loan affordability
- Credit history
- Guarantor and collateral
- Loan documents
- Application status and rejection
- Loan charges and repayment

## Evaluation Rubric

The evaluation rubric is stored in `evaluation_rubric.json`.

It defines three scoring dimensions:

| Dimension | Weight | Description |
|---|---:|---|
| Correctness | 50% | Measures factual accuracy and avoids unsupported loan eligibility claims. |
| Completeness | 30% | Measures whether the answer covers all important parts of the question. |
| Tone | 20% | Measures professionalism, clarity, and respectful communication. |
| **Total** | **100%** | |

Each dimension receives an integer score from 0 to 5.

### Scoring Formula

```text
Final Score = Sum((Dimension Score / 5) × Weight) × 100
```

### Score Interpretation

- Excellent: 90 or above
- Good: 75–89
- Needs Improvement: 60–74
- Poor: Below 60

**Passing Threshold: 75/100**

## Evaluation Rules

- Each dimension must receive an integer score from 0 to 5.
- All dimension weights must sum to 1.0.
- Never guarantee loan approval.
- Do not invent lender-specific eligibility policies.
- Mention when additional information is required.

## Rubric Validation

The rubric is validated using:

`scripts/validate_rubric.py`

The validation script checks the rubric structure, scoring dimensions, dimension weights, and passing threshold.

Make sure Python 3.11 is installed.

Run:

```powershell
python scripts/validate_rubric.py
```

If the Python command does not work on Windows, use:

```powershell
& "C:\Users\HP\AppData\Local\Programs\Python\Python311\python.exe" scripts/validate_rubric.py
```

Expected output:

```text
SUCCESS: Rubric validation passed!
Dimensions: 3
Total weight: 1.0
Pass threshold: 75
```

## Scoring Engine

The scoring engine is implemented in:

`scoring.py`

It evaluates AI-generated responses using the evaluation rubric.

### Main Features

- Calculates scores for each evaluation dimension.
- Calculates the weighted overall score.
- Handles missing scoring dimensions.
- Ignores extra response keys.
- Handles malformed JSON responses.
- Checks whether the response meets the passing threshold.

### Usage Example

```python
import json
from scoring import score_response

with open("evaluation_rubric.json", encoding="utf-8") as file:
    rubric = json.load(file)

response = {
    "scores": {
        "correctness": 4,
        "completeness": 5,
        "tone": 4
    }
}

result = score_response(response, rubric)
print(result)
```

## API

The project includes a FastAPI application in:

`app.py`

The API provides endpoints for evaluating loan eligibility responses and checking service health.

### Run the API Locally

Install the dependencies:

```powershell
python -m pip install -r requirements.txt
```

Start the FastAPI application:

```powershell
uvicorn app:app --host 127.0.0.1 --port 8000
```

The API will be available at:

`http://127.0.0.1:8000`

### Health Check

Open:

`http://127.0.0.1:8000/health`

The endpoint is used to verify that the API service is running correctly.

## Comparison Dashboard

The project includes a Streamlit comparison dashboard in:

`dashboard/app.py`

The dashboard provides a user interface for comparing evaluation results and viewing questions, responses, and scores.

Run the dashboard with:

```powershell
python -m streamlit run dashboard/app.py
```

The dashboard normally runs on:

`http://localhost:8501`

## Database

The application uses SQLite for storing evaluation data.

The database implementation is provided in:

`database.py`

The default database file is:

`loan_evaluations.db`

Database configuration can be controlled through environment-specific settings where required.

## Docker

The repository includes a `Dockerfile` for containerized deployment.

The Docker image uses Python 3.11 and starts the FastAPI application using Uvicorn.

### Docker Build

```powershell
docker build -t loan-eligibility-harness .
```

### Run the Docker Container

```powershell
docker run -p 8000:8000 loan-eligibility-harness
```

The container exposes port `8000`.

The API can then be accessed at:

`http://localhost:8000`

Health check:

`http://localhost:8000/health`

> Note: Docker commands require a working Docker Engine or Docker Desktop installation on the local machine.

## Render Deployment

The repository includes:

`render.yaml`

This file defines the Render web service configuration.

### Render Configuration

The Render service uses:

**Runtime**

```text
Python
```

**Build command**

```text
pip install -r requirements.txt
```

**Start command**

```text
uvicorn app:app --host 0.0.0.0 --port $PORT
```

The `$PORT` environment variable is provided by the hosting platform.

### Deployment Process

1. Push the latest project changes to GitHub.
2. Connect the GitHub repository to Render.
3. Create or update the web service using the repository configuration.
4. Render installs the dependencies from `requirements.txt`.
5. Render starts the FastAPI application using the configured Uvicorn command.
6. Verify the deployment using the `/health` endpoint.

### Health Check After Deployment

After deployment, open:

```text
https://<your-render-service-url>/health
```

A successful deployment should return a JSON response indicating that the service is healthy.

## Environment Variables and Secrets

API keys and other secrets must not be committed to GitHub.

Use environment variables for deployment-specific configuration.

For example:

```text
OPENAI_API_KEY=<your-secret-key>
DATABASE_PATH=<deployment-database-path>
```

Actual secret values should be configured through the hosting platform's environment settings.

## Testing

The project includes automated tests for the scoring functionality.

Run:

```powershell
pytest -q
```

A successful test run confirms that the implemented scoring functionality passes the available automated tests.

## Deployment and Handover Checklist

Before handing over the project, verify the following:

1. The Git working tree is clean.
2. The latest changes are committed.
3. The latest commit is pushed to GitHub.
4. `evaluation_rubric.json` passes validation.
5. The automated tests pass.
6. The FastAPI application starts successfully.
7. The `/health` endpoint responds successfully.
8. The `Dockerfile` is present and configured for container deployment.
9. `render.yaml` contains the deployment configuration.
10. No API keys or private secrets are committed to the repository.
11. The README contains setup, testing, deployment, and handover instructions.

## Project Status

The project contains:

- 24 loan eligibility evaluation questions.
- Expected answer templates.
- A three-dimension evaluation rubric.
- A weighted scoring engine.
- Automated validation and tests.
- A FastAPI application.
- A Streamlit comparison dashboard.
- SQLite database support.
- Docker deployment configuration.
- Render deployment configuration.
- Complete setup and handover documentation.

## Disclaimer

This project is intended for AI response evaluation and educational purposes.

It does not provide actual loan approval decisions or financial advice.

Loan eligibility depends on the policies, requirements, and assessment procedures of the relevant lender.