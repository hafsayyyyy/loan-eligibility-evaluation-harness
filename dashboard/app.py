import html
import json
from io import BytesIO

import pandas as pd
import plotly.express as px
import requests
import streamlit as st


# ==================================================
# WEASYPRINT
# ==================================================

try:
    from weasyprint import HTML as WeasyprintHTML

    WEASYPRINT_AVAILABLE = True

except Exception as exc:
    WeasyprintHTML = None
    WEASYPRINT_AVAILABLE = False
    WEASYPRINT_IMPORT_ERROR = str(exc)


# ==================================================
# STREAMLIT CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Loan Eligibility Evaluation Dashboard",
    page_icon="💰",
    layout="wide",
)


# ==================================================
# SESSION STATE
# ==================================================

if "evaluations" not in st.session_state:
    st.session_state.evaluations = []


# ==================================================
# HELPER FUNCTIONS
# ==================================================

def safe_json_loads(value):
    """Safely parse JSON data."""

    if isinstance(value, dict):
        return value

    if not isinstance(value, str):
        return {}

    try:
        return json.loads(value)

    except Exception:
        return {}


def get_score_data(result):
    """Extract score information from API response."""

    scores_data = result.get(
        "scores",
        {},
    )

    if isinstance(scores_data, dict) and "scores" in scores_data:

        scores = scores_data.get(
            "scores",
            {},
        )

        overall_score = scores_data.get(
            "overall_score",
            0,
        )

        passed = scores_data.get(
            "passed",
            False,
        )

    else:

        scores = scores_data

        overall_score = result.get(
            "overall_score",
            0,
        )

        passed = result.get(
            "passed",
            False,
        )

    return {
        "correctness": scores.get(
            "correctness",
            0,
        ),

        "completeness": scores.get(
            "completeness",
            0,
        ),

        "tone": scores.get(
            "tone",
            0,
        ),

        "overall_score": overall_score,

        "passed": passed,
    }


def evaluate_question(api_url, question):
    """Send question to FastAPI /evaluate endpoint."""

    response = requests.post(
        f"{api_url.rstrip('/')}/evaluate",
        json={
            "question": question,
        },
        timeout=60,
    )

    response.raise_for_status()

    return response.json()


def check_api_health(api_url):
    """Check FastAPI health endpoint."""

    try:

        response = requests.get(
            f"{api_url.rstrip('/')}/health",
            timeout=5,
        )

        if response.status_code == 200:

            return True, response.json()

        return False, {
            "status_code": response.status_code,
        }

    except Exception as exc:

        return False, {
            "error": str(exc),
        }


def build_pdf_html(evaluations):
    """Build HTML report for PDF generation."""

    rows = []

    for index, item in enumerate(
        evaluations,
        start=1,
    ):

        question = html.escape(
            str(
                item.get(
                    "question",
                    "",
                )
            )
        )

        raw_response = html.escape(
            str(
                item.get(
                    "raw_response",
                    "",
                )
            )
        )

        correctness = item.get(
            "correctness",
            0,
        )

        completeness = item.get(
            "completeness",
            0,
        )

        tone = item.get(
            "tone",
            0,
        )

        overall_score = item.get(
            "overall_score",
            0,
        )

        status = (
            "PASS"
            if item.get(
                "passed",
                False,
            )
            else "FAIL"
        )

        mode = html.escape(
            str(
                item.get(
                    "mode",
                    "unknown",
                )
            )
        )

        rows.append(
            f"""
            <tr>
                <td>{index}</td>
                <td>{question}</td>
                <td>{raw_response}</td>
                <td>{correctness}/5</td>
                <td>{completeness}/5</td>
                <td>{tone}/5</td>
                <td>{overall_score}%</td>
                <td>{status}</td>
                <td>{mode}</td>
            </tr>
            """
        )

    if not rows:

        rows.append(
            """
            <tr>
                <td colspan="9">
                    No evaluation results available.
                </td>
            </tr>
            """
        )

    return f"""
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<style>

body {{
    font-family: Arial, sans-serif;
    margin: 30px;
    color: #222;
}}

h1 {{
    font-size: 26px;
    margin-bottom: 5px;
}}

h2 {{
    margin-top: 25px;
    font-size: 20px;
}}

.summary {{
    background: #f5f5f5;
    padding: 15px;
    margin-bottom: 20px;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 9px;
}}

th,
td {{
    border: 1px solid #ccc;
    padding: 6px;
    vertical-align: top;
}}

th {{
    background: #eeeeee;
}}

.footer {{
    margin-top: 30px;
    font-size: 10px;
    color: #666;
}}

</style>

</head>

<body>

<h1>
Loan Eligibility Evaluation Report
</h1>

<div class="summary">

<p>
<strong>Total Evaluations:</strong>
{len(evaluations)}
</p>

<p>
<strong>Generated By:</strong>
Loan Eligibility Evaluation Dashboard
</p>

</div>

<h2>
Evaluation Results
</h2>

<table>

<thead>

<tr>
<th>#</th>
<th>Question</th>
<th>Raw Response</th>
<th>Correctness</th>
<th>Completeness</th>
<th>Tone</th>
<th>Overall</th>
<th>Status</th>
<th>Mode</th>
</tr>

</thead>

<tbody>

{''.join(rows)}

</tbody>

</table>

<div class="footer">

Generated by the Loan Eligibility Evaluation Dashboard.

</div>

</body>

</html>
"""


# ==================================================
# SIDEBAR
# ==================================================

st.sidebar.title(
    "⚙️ Dashboard Settings"
)

api_url = st.sidebar.text_input(
    "FastAPI URL",
    value="http://127.0.0.1:8000",
)

st.sidebar.markdown("---")

st.sidebar.subheader(
    "API Status"
)

health_ok, health_data = check_api_health(
    api_url
)

if health_ok:

    st.sidebar.success(
        "API Connected"
    )

    if isinstance(
        health_data,
        dict,
    ):

        st.sidebar.json(
            health_data
        )

else:

    st.sidebar.error(
        "API Not Connected"
    )

    if isinstance(
        health_data,
        dict,
    ):

        st.sidebar.caption(
            str(
                health_data.get(
                    "error",
                    "Unable to connect to API.",
                )
            )
        )


# ==================================================
# MAIN HEADER
# ==================================================

st.title(
    "💰 Loan Eligibility Evaluation Dashboard"
)

st.markdown(
    """
Interactive dashboard for evaluating and comparing
loan eligibility responses using the FastAPI evaluation API.
"""
)

st.markdown("---")


# ==================================================
# QUESTION INPUT
# ==================================================

st.subheader(
    "📝 Evaluate Loan Eligibility Question"
)

question = st.text_area(
    "Enter a loan eligibility question:",
    placeholder=(
        "Example: What documents are required "
        "to apply for a loan?"
    ),
    height=120,
)


col1, col2 = st.columns(2)


with col1:

    evaluate_button = st.button(
        "🚀 Evaluate Question",
        use_container_width=True,
    )


with col2:

    clear_button = st.button(
        "🗑️ Clear Results",
        use_container_width=True,
    )


# ==================================================
# CLEAR RESULTS
# ==================================================

if clear_button:

    st.session_state.evaluations = []

    st.rerun()


# ==================================================
# EVALUATE QUESTION
# ==================================================

if evaluate_button:

    if not question.strip():

        st.warning(
            "Please enter a question first."
        )

    elif not health_ok:

        st.error(
            "FastAPI is not connected. "
            "Start the API on http://127.0.0.1:8000."
        )

    else:

        with st.spinner(
            "Evaluating response..."
        ):

            try:

                result = evaluate_question(
                    api_url,
                    question.strip(),
                )

                score_data = get_score_data(
                    result
                )

                evaluation = {
                    "question": question.strip(),

                    "raw_response": result.get(
                        "raw_response",
                        "",
                    ),

                    "correctness": score_data[
                        "correctness"
                    ],

                    "completeness": score_data[
                        "completeness"
                    ],

                    "tone": score_data[
                        "tone"
                    ],

                    "overall_score": score_data[
                        "overall_score"
                    ],

                    "passed": score_data[
                        "passed"
                    ],

                    "mode": result.get(
                        "mode",
                        "unknown",
                    ),
                }

                st.session_state.evaluations.append(
                    evaluation
                )

                st.success(
                    "Evaluation completed successfully."
                )

            except requests.exceptions.RequestException as exc:

                st.error(
                    "Could not connect to the evaluation API."
                )

                st.code(
                    str(exc)
                )

            except Exception as exc:

                st.error(
                    "Evaluation failed."
                )

                st.code(
                    f"{type(exc).__name__}: {exc}"
                )


# ==================================================
# LATEST EVALUATION
# ==================================================

if st.session_state.evaluations:

    latest = (
        st.session_state.evaluations[-1]
    )

    st.markdown("---")

    st.subheader(
        "📊 Latest Evaluation"
    )

    metric1, metric2, metric3, metric4 = (
        st.columns(4)
    )

    with metric1:

        st.metric(
            "Correctness",
            f"{latest['correctness']}/5",
        )

    with metric2:

        st.metric(
            "Completeness",
            f"{latest['completeness']}/5",
        )

    with metric3:

        st.metric(
            "Tone",
            f"{latest['tone']}/5",
        )

    with metric4:

        st.metric(
            "Overall Score",
            f"{latest['overall_score']}%",
        )

    if latest["passed"]:

        st.success(
            "✅ Evaluation PASSED"
        )

    else:

        st.error(
            "❌ Evaluation FAILED"
        )

    st.caption(
        f"Evaluation mode: {latest['mode']}"
    )

    with st.expander(
        "View Raw Response"
    ):

        raw_response = (
            latest["raw_response"]
        )

        parsed_response = safe_json_loads(
            raw_response
        )

        if parsed_response:

            st.json(
                parsed_response
            )

        else:

            st.write(
                raw_response
            )


# ==================================================
# EVALUATION RESULTS TABLE
# ==================================================

if st.session_state.evaluations:

    st.markdown("---")

    st.subheader(
        "📋 Evaluation Results"
    )

    table_data = []

    for item in (
        st.session_state.evaluations
    ):

        table_data.append(
            {
                "Question": item[
                    "question"
                ],

                "Raw Response": item[
                    "raw_response"
                ],

                "Correctness": item[
                    "correctness"
                ],

                "Completeness": item[
                    "completeness"
                ],

                "Tone": item[
                    "tone"
                ],

                "Overall Score": item[
                    "overall_score"
                ],

                "Status": (
                    "PASS"
                    if item["passed"]
                    else "FAIL"
                ),

                "Mode": item[
                    "mode"
                ],
            }
        )

    dataframe = pd.DataFrame(
        table_data
    )

    st.dataframe(
        dataframe,
        use_container_width=True,
        hide_index=True,
    )


# ==================================================
# CHARTS
# ==================================================

if st.session_state.evaluations:

    st.markdown("---")

    st.subheader(
        "📈 Score Analysis"
    )

    chart_data = []

    for index, item in enumerate(
        st.session_state.evaluations,
        start=1,
    ):

        chart_data.append(
            {
                "Evaluation": (
                    f"Evaluation {index}"
                ),

                "Correctness": item[
                    "correctness"
                ],

                "Completeness": item[
                    "completeness"
                ],

                "Tone": item[
                    "tone"
                ],

                "Overall Score": item[
                    "overall_score"
                ],
            }
        )

    chart_df = pd.DataFrame(
        chart_data
    )

    # ----------------------------------------------
    # Dimension Score Distribution
    # ----------------------------------------------

    dimension_df = chart_df.melt(
        id_vars=[
            "Evaluation"
        ],

        value_vars=[
            "Correctness",
            "Completeness",
            "Tone",
        ],

        var_name="Dimension",

        value_name="Score",
    )

    fig_dimensions = px.bar(
        dimension_df,
        x="Evaluation",
        y="Score",
        color="Dimension",
        barmode="group",
        title=(
            "Score Distribution "
            "by Evaluation Dimension"
        ),
        range_y=[0, 5],
    )

    fig_dimensions.update_layout(
        xaxis_title="Evaluation",
        yaxis_title="Score (0-5)",
    )

    st.plotly_chart(
        fig_dimensions,
        use_container_width=True,
    )

    # ----------------------------------------------
    # Overall Score Distribution
    # ----------------------------------------------

    fig_histogram = px.histogram(
        chart_df,
        x="Overall Score",
        nbins=10,
        title="Overall Score Distribution",
    )

    fig_histogram.update_layout(
        xaxis_title="Overall Score (%)",
        yaxis_title="Number of Evaluations",
    )

    st.plotly_chart(
        fig_histogram,
        use_container_width=True,
    )

    # ----------------------------------------------
    # Average Dimension Scores
    # ----------------------------------------------

    average_scores = pd.DataFrame(
        {
            "Dimension": [
                "Correctness",
                "Completeness",
                "Tone",
            ],

            "Average Score": [
                chart_df[
                    "Correctness"
                ].mean(),

                chart_df[
                    "Completeness"
                ].mean(),

                chart_df[
                    "Tone"
                ].mean(),
            ],
        }
    )

    fig_average = px.bar(
        average_scores,
        x="Dimension",
        y="Average Score",
        title=(
            "Average Score by Dimension"
        ),
        range_y=[0, 5],
    )

    fig_average.update_layout(
        xaxis_title="Dimension",
        yaxis_title="Average Score (0-5)",
    )

    st.plotly_chart(
        fig_average,
        use_container_width=True,
    )


# ==================================================
# MODEL / MODE COMPARISON
# ==================================================

if st.session_state.evaluations:

    st.markdown("---")

    st.subheader(
        "🤖 Model / Evaluation Mode Comparison"
    )

    mode_data = []

    for item in (
        st.session_state.evaluations
    ):

        mode_data.append(
            {
                "Mode": item[
                    "mode"
                ],

                "Overall Score": item[
                    "overall_score"
                ],

                "Correctness": item[
                    "correctness"
                ],

                "Completeness": item[
                    "completeness"
                ],

                "Tone": item[
                    "tone"
                ],
            }
        )

    mode_df = pd.DataFrame(
        mode_data
    )

    if not mode_df.empty:

        comparison = (
            mode_df
            .groupby("Mode")
            [
                [
                    "Overall Score",
                    "Correctness",
                    "Completeness",
                    "Tone",
                ]
            ]
            .mean()
            .reset_index()
        )

        st.dataframe(
            comparison,
            use_container_width=True,
            hide_index=True,
        )

        comparison_long = (
            comparison.melt(
                id_vars=[
                    "Mode"
                ],

                var_name="Metric",

                value_name="Score",
            )
        )

        fig_model = px.bar(
            comparison_long,
            x="Mode",
            y="Score",
            color="Metric",
            barmode="group",
            title=(
                "Comparison by "
                "Evaluation Mode"
            ),
        )

        st.plotly_chart(
            fig_model,
            use_container_width=True,
        )


# ==================================================
# PDF EXPORT
# ==================================================

if st.session_state.evaluations:

    st.markdown("---")

    st.subheader(
        "📄 Export Report"
    )

    report_html = build_pdf_html(
        st.session_state.evaluations
    )

    # ------------------------------------------------
    # WeasyPrint unavailable
    # ------------------------------------------------

    if (
        not WEASYPRINT_AVAILABLE
        or WeasyprintHTML is None
    ):

        st.warning(
            "PDF export is unavailable in "
            "the current environment."
        )

        st.info(
            "WeasyPrint could not be loaded. "
            "The evaluation table, API fetching, "
            "and Plotly charts are still working."
        )

        if "WEASYPRINT_IMPORT_ERROR" in globals():

            with st.expander(
                "Show WeasyPrint import error"
            ):

                st.code(
                    WEASYPRINT_IMPORT_ERROR
                )

    # ------------------------------------------------
    # WeasyPrint available
    # ------------------------------------------------

    else:

        try:

            pdf_buffer = BytesIO()

            pdf_document = WeasyprintHTML(
                string=report_html
            )

            pdf_document.write_pdf(
                pdf_buffer
            )

            pdf_buffer.seek(0)

            st.download_button(
                label="⬇️ Download PDF Report",

                data=pdf_buffer.getvalue(),

                file_name=(
                    "loan_evaluation_report.pdf"
                ),

                mime="application/pdf",

                use_container_width=True,
            )

            st.success(
                "PDF report generated successfully."
            )

        except Exception as exc:

            st.error(
                "PDF generation failed."
            )

            st.code(
                f"{type(exc).__name__}: {exc}"
            )

            st.info(
                "The dashboard itself is working. "
                "The remaining issue is the local "
                "WeasyPrint PDF environment."
            )


# ==================================================
# FOOTER
# ==================================================

st.markdown("---")

st.caption(
    "Loan Eligibility Evaluation Harness | "
    "Streamlit Dashboard | FastAPI Evaluation API"
)