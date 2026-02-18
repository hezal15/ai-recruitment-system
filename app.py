import streamlit as st
import pandas as pd
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
    page_title="Talency Recruitment System",
    layout="wide",
    page_icon="🚀"
)

# ================= HEADER =================
st.markdown("""
<div style="text-align: center; padding: 20px 0px;">
    <h1 style="font-size: 42px;">Talency Recruitment System</h1>
    <h3 style="color: grey; font-weight: normal;">
        AI-Powered Recruitment & Candidate–Job Matching System
    </h3>
    <p style="font-size: 16px; color: #555;">
        Intelligent Resume Screening • Semantic Matching • Recruitment Risk Analysis
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ================= JOB DESCRIPTION SOURCE =================
jd_source = st.sidebar.radio(
    "Select Job Description Source",
    ["Use Saved Job Description", "Upload New Job Description (.csv)"]
)

def process_jd_dataframe(df):
    df.columns = df.columns.str.strip()
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    df["Combined_JD"] = (
        df.get("Roles_Responsibility", "").astype(str) + " " +
        df.get("Skills_Required", "").astype(str)
    )
    return df

if jd_source == "Use Saved Job Description":
    jobs_df = pd.read_csv("job_clean_data.csv")
    jobs_df = process_jd_dataframe(jobs_df)
else:
    uploaded_jd = st.sidebar.file_uploader(
        "Upload Job Description CSV",
        type=["csv"]
    )

    if uploaded_jd:
        jobs_df = pd.read_csv(uploaded_jd)
        jobs_df = process_jd_dataframe(jobs_df)
        st.sidebar.success("Job Description Uploaded Successfully ✅")
    else:
        st.warning("Please upload a Job Description CSV file.")
        st.stop()

job_titles = jobs_df["Job_title"].unique().tolist()

# ================= SYSTEM CONFIGURATION =================
match_scope = st.sidebar.radio(
    "Job Selection Strategy",
    ["Single Job Role", "Auto Detect Best Role"]
)

matching_mode = st.sidebar.radio(
    "Matching Configuration",
    ["Overall Job Description", "Specific Field Matching"]
)

selected_field = None
if matching_mode == "Specific Field Matching":
    selected_field = st.sidebar.selectbox(
        "Select Field",
        ["Roles_Responsibility", "Skills_Required"]
    )

selected_job = None
if match_scope == "Single Job Role":
    selected_job = st.sidebar.selectbox(
        "Select Target Role",
        job_titles
    )

st.sidebar.success("System Configuration Active")

# ================= RESUME UPLOAD =================
st.subheader("📂 Candidate Resume Upload")

uploaded_files = st.file_uploader(
    "Upload Resume Files (PDF)",
    type=["pdf"],
    accept_multiple_files=True
)

match_button = st.button("🚀 Execute Recruitment Analysis")

st.markdown("---")

# ================= RISK LOGIC =================
def risk_indicator(gap, job_hop):
    if gap > 12 and job_hop:
        return "🔴 High Risk"
    elif gap > 6 or job_hop:
        return "🟠 Medium Risk"
    else:
        return "🟢 Low Risk"

# ================= MATCHING PROCESS =================
if match_button and uploaded_files:

    with st.spinner("Running AI Recruitment Engine..."):

        candidates = []

        for file in uploaded_files:
            candidate_name = file.name.replace(".pdf", "")
            resume_text = extract_text_from_pdf(file)

            exp_list = parse_experience_dates(resume_text)
            gaps = detect_career_gap(exp_list)
            job_hop_flag, avg_tenure = detect_job_hopping(exp_list)

            for _, row in jobs_df.iterrows():

                job_title = row["Job_title"]

                if match_scope == "Single Job Role" and job_title != selected_job:
                    continue

                if matching_mode == "Specific Field Matching" and selected_field:
                    job_text = str(row[selected_field])
                else:
                    job_text = row["Combined_JD"]

                match_score, skill_score, exp_score = compute_match_score(
                    resume_text, job_text
                )

                candidates.append({
                    "Candidate": candidate_name,
                    "Job_Title": job_title,
                    "Match_Score": round(match_score, 2),
                    "Skill_Score": round(skill_score, 2),
                    "Experience_Score": round(exp_score, 2),
                    "Career_Gap_Months": max(gaps) if gaps else 0,
                    "Job_Hopping": "Yes" if job_hop_flag else "No",
                    "Risk_Level": risk_indicator(
                        max(gaps) if gaps else 0,
                        job_hop_flag
                    )
                })

        results_df = pd.DataFrame(candidates)

    if results_df.empty:
        st.error("No matching results found.")
        st.stop()

    if match_scope == "Auto Detect Best Role":
        results_df = results_df.sort_values(
            "Match_Score", ascending=False
        ).groupby("Candidate").head(1)

    # ================= ANALYTICS =================
    st.markdown("## 📈 Match & Risk Analytics")

    col1, col2 = st.columns(2)

    # Histogram (Professional Blue)
    fig1 = px.histogram(
        results_df,
        x="Match_Score",
        nbins=10,
        title="Match Score Distribution",
        color_discrete_sequence=["#1f77b4"]
    )
    fig1.update_layout(template="plotly_white")
    col1.plotly_chart(fig1, use_container_width=True)

    # Pie Chart (Custom Corporate Colors)
    fig2 = px.pie(
        results_df,
        names="Risk_Level",
        title="Risk Level Distribution",
        color="Risk_Level",
        color_discrete_map={
            "🔴 High Risk": "#2F3E46",
            "🟠 Medium Risk": "#52796F",
            "🟢 Low Risk": "#84A98C"
        }
    )
    fig2.update_layout(template="plotly_white")
    col2.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # ================= RANKING =================
    st.markdown("## 🏆 Ranked Candidates")

    results_df = results_df.sort_values(
        "Match_Score", ascending=False
    ).reset_index(drop=True)

    results_df.insert(0, "Rank", results_df.index + 1)

    # Top Candidate Highlight
    top_candidate = results_df.iloc[0]
    st.info(
        f"🏆 Top Candidate: {top_candidate['Candidate']} "
        f"| Match Score: {top_candidate['Match_Score']}"
    )

    st.dataframe(results_df, use_container_width=True)

    st.markdown("---")

    # ================= EXECUTIVE OVERVIEW (MOVED TO BOTTOM) =================
    st.markdown("## 📊 Recruitment Performance Summary")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Candidates", results_df["Candidate"].nunique())
    col2.metric("Average Match Score",
                round(results_df["Match_Score"].mean(), 2))
    col3.metric("High Risk Candidates",
                len(results_df[results_df["Risk_Level"] == "🔴 High Risk"]))
    col4.metric("Top Match Score",
                round(results_df["Match_Score"].max(), 2))

    st.success("AI Recruitment Analysis Completed Successfully.")

elif match_button:
    st.warning("Please upload resume files to proceed.")
