import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from resume_parser import extract_text_from_pdf
from matcher import compute_match_score
from career_analyzer import (
    parse_experience_dates,
    detect_career_gap,
    detect_job_hopping
)

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Recruitment Dashboard",
    layout="wide",
    page_icon="🤖"
)

st.title("🤖 AI-Powered Recruitment Dashboard")
st.markdown("Advanced Candidate–Job Matching & Risk Intelligence")
st.divider()

# ================= LOAD JOB DATA =================
@st.cache_data
def load_jobs():
    df = pd.read_csv("job_clean_data.csv")
    df.columns = df.columns.str.strip()
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    df["Combined_JD"] = (
        df.get("Roles_Responsibility", "").astype(str) + " " +
        df.get("Skills_Required", "").astype(str)
    )
    return df

jobs_df = load_jobs()
job_titles = jobs_df["Job_title"].unique().tolist()

# ================= SIDEBAR =================
st.sidebar.header("⚙️ Configuration")

match_scope = st.sidebar.radio(
    "🎯 Match Job",
    ["Single Job", "Auto Detect Best Job"]
)

matching_mode = st.sidebar.radio(
    "🧠 Matching Mode",
    ["Overall Job Description", "Single Field"]
)

selected_field = None
if matching_mode == "Single Field":
    selected_field = st.sidebar.selectbox(
        "Select Field to Match",
        ["Roles_Responsibility", "Skills_Required"]
    )

selected_job = None
if match_scope == "Single Job":
    selected_job = st.sidebar.selectbox(
        "Select Job Role",
        job_titles
    )

st.sidebar.success("System Ready ✅")

# ================= UPLOAD =================
st.subheader("📂 Upload Resumes")
uploaded_files = st.file_uploader(
    "Upload Resume PDFs",
    type=["pdf"],
    accept_multiple_files=True
)

match_button = st.button("🚀 Run AI Matching")
st.divider()

# ================= RISK LOGIC =================
def risk_indicator(gap, job_hop):
    if gap > 12 or job_hop:
        return "🔴 High Risk"
    elif gap > 6:
        return "🟠 Medium Risk"
    else:
        return "🟢 Low Risk"

# ================= MATCHING =================
if match_button and uploaded_files:

    st.info("🔎 AI Matching in Progress...")

    candidates = []

    for file in uploaded_files:
        name = file.name.replace(".pdf", "")
        resume_text = extract_text_from_pdf(file)

        exp_list = parse_experience_dates(resume_text)
        gaps = detect_career_gap(exp_list)
        job_hop_flag, avg_tenure = detect_job_hopping(exp_list)

        for _, row in jobs_df.iterrows():

            job_title = row["Job_title"]

            if match_scope == "Single Job" and job_title != selected_job:
                continue

            # ---- MATCHING MODE LOGIC ----
            if matching_mode == "Single Field" and selected_field:
                job_text = str(row[selected_field])
            else:
                job_text = row["Combined_JD"]

            match_score, skill_score, exp_score = compute_match_score(
                resume_text, job_text
            )

            candidates.append({
                "Candidate": name,
                "Job_Title": job_title,
                "Match_Score": match_score,
                "Skill_Score": skill_score,
                "Experience_Score": exp_score,
                "Career_Gap_Months": max(gaps) if gaps else 0,
                "Job_Hopping": "Yes" if job_hop_flag else "No",
                "Avg_Tenure_Months": round(avg_tenure, 1),
                "Risk_Level": risk_indicator(
                    max(gaps) if gaps else 0,
                    job_hop_flag
                )
            })

    results_df = pd.DataFrame(candidates)

    # ================= AUTO DETECT =================
    if match_scope == "Auto Detect Best Job":
        results_df = results_df.sort_values(
            "Match_Score", ascending=False
        ).groupby("Candidate").head(1)

    # ================= VISUAL ANALYTICS =================
    st.subheader("📈 Match & Risk Analytics")

    col1, col2 = st.columns(2)

    fig1 = px.histogram(
        results_df,
        x="Match_Score",
        nbins=10,
        title="Match Score Distribution"
    )
    col1.plotly_chart(fig1, use_container_width=True)

    fig2 = px.pie(
        results_df,
        names="Risk_Level",
        title="Risk Level Distribution"
    )
    col2.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # ================= RANKED TABLE =================
    st.subheader("🏆 Ranked Candidates")

    results_df = results_df.sort_values(
        "Match_Score", ascending=False
    ).reset_index(drop=True)

    # Add Rank starting from 1
    results_df.insert(0, "Rank", results_df.index + 1)

    display_df = results_df[
        [
            "Rank",
            "Candidate",
            "Job_Title",
            "Match_Score",
            "Skill_Score",
            "Experience_Score",
            "Career_Gap_Months",
            "Job_Hopping",
            "Risk_Level"
        ]
    ]

    st.dataframe(display_df, use_container_width=True)

    # ================= DOWNLOAD =================
    csv = display_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "📥 Download Ranked Candidates CSV",
        csv,
        "ranked_candidates.csv",
        "text/csv"
    )

    st.divider()

    # ================= EXECUTIVE SUMMARY (AT LAST) =================
    st.subheader("📊 Executive Summary")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Candidates", results_df["Candidate"].nunique())
    col2.metric("Average Match Score",
                round(results_df["Match_Score"].mean(), 2))
    col3.metric("High Risk Candidates",
                len(results_df[results_df["Risk_Level"] == "🔴 High Risk"]))

    st.success("✅ AI Matching Completed Successfully!")

elif match_button:
    st.warning("Please upload resumes first.")
