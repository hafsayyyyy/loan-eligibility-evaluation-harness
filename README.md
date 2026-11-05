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

## Dataset
The dataset contains 24 loan eligibility questions with expected answers.

It covers:
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

The evaluation rubric uses three dimensions:

| Dimension | Weight |
|---|---:|
| Correctness | 50% |
| Completeness | 30% |
| Tone | 20% |
| Total | 100% |

Each dimension receives a score from 0 to 5.

### Scoring Formula

`Final Score = Sum((Dimension Score / 5) × Weight) × 100`

- Excellent: 90 or above
- Good: 75–89
- Needs Improvement: 60–74
- Poor: Below 60

**Passing Threshold:** 75/100

## Evaluation Rules
- Each dimension must receive an integer score from 0 to 5.
- All dimension weights must sum to 1.0.
- Never guarantee loan approval.
- Do not invent lender-specific eligibility policies.
- Mention when additional information is required.

## Validation

Make sure Python 3.11 is installed.

Run the rubric validation script:

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
The loan eligibility dataset and evaluation rubric have been created. Rubric validation has passed successfully.

## Disclaimer
This project is intended for AI response evaluation and educational purposes. It does not provide actual loan approval decisions or financial advice.