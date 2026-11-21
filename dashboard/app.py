import json
from io import BytesIO

import pandas as pd
import plotly.express as px
import requests
import streamlit as st
try:
    from weasyprint import HTML as WeasyprintHTML
    WEASYPRINT_AVAILABLE = True
except Exception:
    WeasyprintHTML = None
    WEASYPRINT_AVAILABLE = False


st.set_page_config(
    page_title="Loan Eligibility Evaluation Dashboard",
    page_icon="ðŸ’°",
    layout="wide",
)


st.title("Loan Eligibility Evaluation Dashboard")
st.write(
    "Evaluate loan eligibility responses and compare scoring dimensions."
)


# --------------------------------------------------
# API Configuration
# --------------------------------------------------

st.sidebar.header("API Configuration")

api_url = st.sidebar.text_input(
    "FastAPI URL",
    value="http://127.0.0.1:8000",
)

evaluate_url = f"{api_url.rstrip('/')}/evaluate"


# --------------------------------------------------
# Session State
# --------------------------------------------------

if "evaluations" not in st.session_state:
    st.session_state.evaluations = []


# --------------------------------------------------
# Evaluation Form
# --------------------------------------------------

st.header("Evaluate a Loan Eligibility Question")

question = st.text_area(
    "Enter loan eligibility question",
    placeholder="Example: What documents are required to apply for a loan?",
)

if st.button("Evaluate Response", type="primary"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        try:
            with st.spinner("Sending question to evaluation API..."):

                response = requests.post(
                    evaluate_url,
                    json={"question": question},
                    timeout=120,
                )

            if response.status_code == 200:
                result = response.json()

                raw_response = result.get("raw_response", "{}")
                scores_data = result.get("scores", {})

                if isinstance(raw_response, str):
                    try:
                        parsed_response = json.loads(raw_response)
                    except json.JSONDecodeError:
                        parsed_response = {
                            "answer": raw_response
                        }
                else:
                    parsed_response = raw_response

                answer = parsed_response.get("answer", "")

                evaluation = {
                    "Question": question,
                    "Raw Response": answer,
                    "Correctness": scores_data.get("scores", {}).get(
                        "correctness", 0
                    ),
                    "Completeness": scores_data.get("scores", {}).get(
                        "completeness", 0
                    ),
                    "Tone": scores_data.get("scores", {}).get(
                        "tone", 0
                    ),
                    "Overall Score": scores_data.get(
                        "overall_score", 0
                    ),
                    "Status": (
                        "Pass"
                        if scores_data.get("passed", False)
                        else "Fail"
                    ),
                }

                st.session_state.evaluations.append(evaluation)

                st.success("Evaluation completed successfully.")

                st.subheader("LLM Response")
                st.write(answer)

            else:
                try:
                    error_detail = response.json().get(
                        "detail",
                        response.text,
                    )
                except Exception:
                    error_detail = response.text

                st.error(
                    f"API request failed ({response.status_code}): "
                    f"{error_detail}"
                )

        except requests.exceptions.RequestException as exc:
            st.error(
                "Could not connect to the FastAPI server. "
                "Make sure the API is running."
            )
            st.code(str(exc))


# --------------------------------------------------
# Dashboard Metrics
# --------------------------------------------------

evaluations = st.session_state.evaluations

st.divider()

st.header("Evaluation Summary")

if evaluations:

    df = pd.DataFrame(evaluations)

    total_evaluations = len(df)
    average_score = df["Overall Score"].mean()
    pass_rate = (
        (df["Status"] == "Pass").mean() * 100
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Evaluations",
        total_evaluations,
    )

    col2.metric(
        "Average Score",
        f"{average_score:.2f}",
    )

    col3.metric(
        "Pass Rate",
        f"{pass_rate:.1f}%",
    )

    # --------------------------------------------------
    # Results Table
    # --------------------------------------------------

    st.header("Evaluation Results")

    display_df = df[
        [
            "Question",
            "Raw Response",
            "Correctness",
            "Completeness",
            "Tone",
            "Overall Score",
            "Status",
        ]
    ]

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )

    # --------------------------------------------------
    # Score Distribution
    # --------------------------------------------------

    st.header("Score Distribution")

    dimension_df = df[
        [
            "Correctness",
            "Completeness",
            "Tone",
        ]
    ].melt(
        var_name="Dimension",
        value_name="Score",
    )

    fig = px.histogram(
        dimension_df,
        x="Score",
        color="Dimension",
        barmode="group",
        title="Score Distribution by Dimension",
        nbins=6,
    )

    fig.update_xaxes(
        tickmode="linear",
        dtick=1,
        range=[0, 5],
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    # --------------------------------------------------
    # Average Dimension Scores
    # --------------------------------------------------

    st.header("Average Score by Dimension")

    average_dimensions = pd.DataFrame(
        {
            "Dimension": [
                "Correctness",
                "Completeness",
                "Tone",
            ],
            "Average Score": [
                df["Correctness"].mean(),
                df["Completeness"].mean(),
                df["Tone"].mean(),
            ],
        }
    )

    fig_dimension = px.bar(
        average_dimensions,
        x="Dimension",
        y="Average Score",
        text="Average Score",
        title="Average Score per Dimension",
    )

    fig_dimension.update_yaxes(
        range=[0, 5],
    )

    st.plotly_chart(
        fig_dimension,
        use_container_width=True,
    )

    # --------------------------------------------------
    # PDF Report
    # --------------------------------------------------

    st.header("Export Report")

    report_rows = ""

    for _, row in df.iterrows():
        report_rows += f"""
        <tr>
            <td>{row["Question"]}</td>
            <td>{row["Raw Response"]}</td>
            <td>{row["Correctness"]}</td>
            <td>{row["Completeness"]}</td>
            <td>{row["Tone"]}</td>
            <td>{row["Overall Score"]}</td>
            <td>{row["Status"]}</td>
        </tr>
        """

    html_report = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">

        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 30px;
            }}

            h1 {{
                margin-bottom: 5px;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}

            th, td {{
                border: 1px solid #999;
                padding: 8px;
                text-align: left;
                vertical-align: top;
            }}

            th {{
                background: #eeeeee;
            }}
        </style>
    </head>

    <body>

        <h1>Loan Eligibility Evaluation Report</h1>

        <p>
            Total Evaluations:
            <strong>{total_evaluations}</strong>
        </p>

        <p>
            Average Score:
            <strong>{average_score:.2f}</strong>
        </p>

        <p>
            Pass Rate:
            <strong>{pass_rate:.1f}%</strong>
        </p>

        <table>

            <thead>
                <tr>
                    <th>Question</th>
                    <th>Raw Response</th>
                    <th>Correctness</th>
                    <th>Completeness</th>
                    <th>Tone</th>
                    <th>Overall Score</th>
                    <th>Status</th>
                </tr>
            </thead>

            <tbody>
                {report_rows}
            </tbody>

        </table>

    </body>
    </html>
    """

    pdf_buffer = BytesIO()

    WeasyprintHTML(
        string=html_report
    ).write_pdf(
        pdf_buffer
    )

    pdf_buffer.seek(0)

    st.download_button(
        label="Download PDF Report",
        data=pdf_buffer,
        file_name="loan_eligibility_evaluation_report.pdf",
        mime="application/pdf",
    )

else:

    st.info(
        "No evaluations yet. Enter a question above and click "
        "'Evaluate Response'."
    )

