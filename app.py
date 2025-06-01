import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.title("IT Access Issues Analyzer2")

uploaded_file = st.file_uploader(
    "Upload a CSV file with columns: Job Role, Issue Description, Issue Report Date, Issue Resolved Date, Program",
    type="csv"
)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Parse dates and calculate resolution time
    df["Issue Report Date"] = pd.to_datetime(df["Issue Report Date"], errors="coerce")
    df["Issue Resolved Date"] = pd.to_datetime(df["Issue Resolved Date"], errors="coerce")
    df["Resolution Time (days)"] = (df["Issue Resolved Date"] - df["Issue Report Date"]).dt.days

    # Split and explode issues
    issues_exploded = df["Issue Description"].str.split(";", expand=True).stack().str.strip().reset_index(level=1, drop=True)
    issues_exploded.name = "Single Issue"
    issues_df = df.drop("Issue Description", axis=1).join(issues_exploded)

    # ---- Section: Frequency Table ----
    st.subheader("Table: Frequency of Unique IT Access Issues (All Programs)")
    issue_counts = issues_df["Single Issue"].value_counts().reset_index()
    issue_counts.columns = ["Issue Description", "Count"]
    st.dataframe(issue_counts)

    # ---- Section: Donut Chart ----
    st.subheader("Donut Chart: Frequency by Program")
    program_options = ["All Programs"] + sorted(df["Program"].dropna().unique().tolist())
    selected_program = st.selectbox("Select Program for Donut Chart", program_options)

    if selected_program == "All Programs":
        donut_data = issues_df
    else:
        donut_data = issues_df[issues_df["Program"] == selected_program]

    donut_counts = donut_data["Single Issue"].value_counts().reset_index()
    donut_counts.columns = ["Issue Description", "Count"]

    fig_donut = go.Figure(data=[go.Pie(
        labels=donut_counts["Issue Description"],
        values=donut_counts["Count"],
        hole=0.5
    )])
    fig_donut.update_layout(title_text=f"Frequency of Unique IT Access Issues ({selected_program})")
    st.plotly_chart(fig_donut)

    # ---- Section: Avg Resolution Time by Issue ----
    st.subheader("Average Resolution Time by Issue")
    program_options_issue = ["All Programs"] + sorted(df["Program"].dropna().unique().tolist())
    selected_program_issue = st.selectbox("Select Program for Avg Resolution", program_options_issue, key="avg_res")

    filtered_issues_df = issues_df if selected_program_issue == "All Programs" else issues_df[issues_df["Program"] == selected_program_issue]

    avg_resolution_by_issue = (
        filtered_issues_df.groupby("Single Issue")["Resolution Time (days)"]
        .mean()
        .reset_index()
        .sort_values("Resolution Time (days)", ascending=False)
    )
    st.dataframe(avg_resolution_by_issue)

    # ---- Section: Avg Resolution by Program ----
    st.subheader("Average Resolution Time by Program")
    program_options_avg = ["All Programs"] + sorted(df["Program"].dropna().unique().tolist())
    selected_program_avg = st.selectbox("Select Program for Average Resolution Time Table", program_options_avg, key="avg_resolution_program")

    avg_resolution = df.groupby("Program")["Resolution Time (days)"].mean().reset_index()
    if selected_program_avg == "All Programs":
        avg_resolution_filtered = avg_resolution
    else:
        avg_resolution_filtered = avg_resolution[avg_resolution["Program"] == selected_program_avg]
    st.dataframe(avg_resolution_filtered)

    # ---- Section: Most Common Issues by Program ----
    st.subheader("Most Common Issues by Program")
    common_issues = (
        issues_df.groupby(["Program", "Single Issue"])
        .size()
        .reset_index(name="Count")
        .sort_values(["Program", "Count"], ascending=[True, False])
    )
    st.dataframe(common_issues)

    # ---- Section: Top 3 Issues by Program Chart ----
    st.subheader("Clustered Bar Chart: Top 3 Issues per Program")
    top3_by_program = (
        common_issues.groupby("Program")
        .head(3)
        .reset_index(drop=True)
    )
    fig_bar = px.bar(
        top3_by_program,
        x="Program",
        y="Count",
        color="Single Issue",
        barmode="group",
        title="Top 3 IT Access Issues by Program"
    )
    fig_bar.update_layout(xaxis_title="Program", yaxis_title="Count", legend_title="Issue")
    st.plotly_chart(fig_bar)

else:
    st.info("Please upload a CSV file to begin analysis.")