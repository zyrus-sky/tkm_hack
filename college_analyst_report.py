"""
College Analytics Report Generator (CSV-only)
=============================================
- Load and analyze educational data from CSV files.
- Interactive 2D/3D plots including animated charts.
- AI-generated detailed summary report with Ollama.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objs as go
import ollama
import os

# --- CSV data file paths ---
STUDENTS_CSV = "students.csv"
FACULTY_CSV = "faculty.csv"
GRADES_CSV = "grades.csv"
DEPARTMENTS_CSV = "departments.csv"

# Page config
st.set_page_config(page_title="📊 College Analytics Dashboard", layout="wide")

st.title("📊 College Analytics Report Generator")

# Function to load CSV (creates one with headers if missing)
def load_csv(csv_file, columns):
    if not os.path.exists(csv_file):
        # Create an empty CSV with the correct headers
        pd.DataFrame(columns=columns).to_csv(csv_file, index=False)
    return pd.read_csv(csv_file)

# Load all CSV datasets
students = load_csv(STUDENTS_CSV, ['collegeName','wallet','name','rollNo','department','section','year','email'])
faculty = load_csv(FACULTY_CSV, ['collegeName','deptName','wallet','name','role'])
grades = load_csv(GRADES_CSV, ['collegeName','wallet','subject','marks','year'])
departments = load_csv(DEPARTMENTS_CSV, ['collegeName','deptName','deptAdmin'])

# Sidebar: Dataset selector
st.sidebar.header("Dataset & Report Options")
college_name = st.sidebar.text_input("Select College Name for Report", "")

# Main UI Tabs
tab_preview, tab_analytics, tab_animation, tab_ai = st.tabs([
    "🗃 Data Preview",
    "📈 2D & 3D Analytics",
    "🎞 Animated Trends",
    "🤖 AI Summary"
])

# Tab 1: Preview raw data so end users can validate dataset correctness
with tab_preview:
    st.header("🗃 Data Preview")
    st.markdown("Preview first rows of datasets. Upload/replace CSV files externally to refresh data.")

    with st.expander("Students Dataset", expanded=True):
        st.dataframe(students)

    with st.expander("Faculty Dataset"):
        st.dataframe(faculty)

    with st.expander("Department Dataset"):
        st.dataframe(departments)

    with st.expander("Grades Dataset"):
        st.dataframe(grades)

# Tab 2: Interactive 2D and 3D charts to explore distributions and relationships
with tab_analytics:
    st.header("📈 Interactive Analytics")

    if college_name:
        filtered_students = students[students['collegeName'] == college_name]
        filtered_grades = grades[grades['collegeName'] == college_name]

        if filtered_students.empty or filtered_grades.empty:
            st.warning(f"No data available for college: {college_name}")
        else:
            # Average grade by subject over the college
            avg_subject = filtered_grades.groupby("subject").marks.mean().sort_values(ascending=False)
            st.subheader("Average Marks by Subject")
            fig_bar = px.bar(avg_subject, labels={"index": "Subject", "marks": "Average Mark"},
                             title="Average Marks per Subject")
            st.plotly_chart(fig_bar, use_container_width=True)

            # Pie chart for student distribution across departments
            dep_counts = filtered_students['department'].value_counts()
            st.subheader(f"Student Distribution by Department in {college_name}")
            fig_pie = px.pie(names=dep_counts.index, values=dep_counts.values,
                             title="Department Breakdown", hole=0.3)
            st.plotly_chart(fig_pie, use_container_width=True)

            # 3D scatter plot: Subject vs Year vs Marks
            st.subheader("3D Scatter: Subject - Year - Marks")
            merged = filtered_grades.merge(filtered_students[['wallet','department']], left_on='wallet', right_on='wallet', how='left')
            fig_3d = px.scatter_3d(merged, x='subject', y='year', z='marks',
                                   color='department', symbol='department',
                                   hover_data=['wallet'], title="3D View of Grades")
            st.plotly_chart(fig_3d, use_container_width=True)
    else:
        st.info("Please enter a college name in the sidebar to view analytics.")

# Tab 3: Animation tab — visualize trends dynamically across years and departments
with tab_animation:
    st.header("🎞 Animated Analytical Trends")

    if college_name:
        filtered_students = students[students['collegeName'] == college_name]
        filtered_grades = grades[grades['collegeName'] == college_name]

        if filtered_students.empty or filtered_grades.empty:
            st.warning(f"No data available for college: {college_name}")
        else:
            # Avg marks progression by department over years
            merged = filtered_grades.merge(filtered_students[['wallet','department']], on='wallet')
            if merged['year'].nunique() < 2:
                st.info("Insufficient year diversity for animation.")
            else:
                progression = merged.groupby(['year', 'department']).marks.mean().reset_index()
                fig_line = px.line(progression, x="year", y="marks", color="department",
                                   markers=True, animation_frame='department',
                                   title="Average Marks Progression Over Years by Department")
                st.plotly_chart(fig_line, use_container_width=True)

                # Animated 3D scatter by year and department
                fig_ani_3d = px.scatter_3d(merged, x='subject', y='year', z='marks', color='department',
                                          symbol='department', animation_frame='department',
                                          title="Animated 3D Scatter of Subject-Year-Marks")
                st.plotly_chart(fig_ani_3d, use_container_width=True)
    else:
        st.info("Please enter a college name in the sidebar to view animated trends.")

# Tab 4: AI Generated Summary report with Ollama
with tab_ai:
    st.header("🤖 AI Generated Analytical Summary")

    if college_name:
        # Compute stats for prompt
        filtered_students = students[students['collegeName'] == college_name]
        filtered_grades = grades[grades['collegeName'] == college_name]

        if filtered_students.empty or filtered_grades.empty:
            st.warning(f"No data available for college: {college_name}")
        else:
            stats = {
                "total_students": len(filtered_students),
                "total_faculty": len(faculty[faculty['collegeName'] == college_name]),
                "departments": filtered_students['department'].nunique(),
                "subjects": filtered_grades['subject'].nunique(),
                "average_mark": round(filtered_grades['marks'].mean(), 2),
                "median_mark": round(filtered_grades['marks'].median(), 2),
                "max_mark": int(filtered_grades['marks'].max()),
                "min_mark": int(filtered_grades['marks'].min())
            }
            stats_md = "\n".join([f"- **{k.replace('_', ' ').capitalize()}:** {v}" for k, v in stats.items()])

            prompt = (f"Generate a detailed analytical report for the following college: {college_name}.\n"
                      f"Statistics:\n{stats_md}\n\n"
                      f"Subject-wise average grades:\n{filtered_grades.groupby('subject')['marks'].mean().round(2).to_string()}\n\n"
                      f"Department sizes:\n{filtered_students['department'].value_counts().to_string()}\n\n"
                      f"Identify patterns, strengths, weaknesses, and advice for administration and faculty.")

            ollama_prompt = [
                {"role": "system", "content": "You are a university data analyst AI assistant."},
                {"role": "user", "content": prompt}
            ]

            try:
                response = ollama.chat(model="llama3", messages=ollama_prompt)
                report = response['message']['content']
                st.text_area("AI Report", report, height=600)
            except Exception as e:
                st.error(f"Failed to get AI summary: {e}")
    else:
        st.info("Please enter a college name in the sidebar to generate the AI summary.")
