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
├── evaluation_rubric.json
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

`Final Score = Sum((Dimension Score / 5) × Weight) × 100`

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

The rubric is validated using the Python script:

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

## Technologies Used

- Python 3.11
- JSON
- CSV
- PowerShell
- Git and GitHub

## Project Status

The dataset contains 24 loan eligibility questions with expected answers. The evaluation rubric defines three scoring dimensions and has successfully passed validation.

## Disclaimer

This project is intended for AI response evaluation and educational purposes. It does not provide actual loan approval decisions or financial advice.