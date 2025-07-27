import streamlit as st
import os

# --- Page Configuration ---
st.set_page_config(page_title="College Portal", layout="wide")

# --- Title ---
st.title("🏛️ Welcome to the College Portal")

# --- Sidebar Navigation ---
st.sidebar.title("🔀 Navigation")
selected_page = st.sidebar.radio("Go to", [
    "🏠 Home",
    "🏫 College Admin",
    "📊 College Analyst Report",
    "🏥 Hospital Admin"
])

# --- Helper function to run another script ---
def run_script(script_name):
    with open(script_name, "r", encoding="utf-8") as file:
        code = file.read()
    exec(code, globals())

# --- Main Content ---
if selected_page == "🏠 Home":
    st.subheader("Welcome!")
    st.write("Use the sidebar to navigate to different modules of the system.")

elif selected_page == "🏫 College Admin":
    run_script("college_admin.py")

elif selected_page == "📊 College Analyst Report":
    run_script("college_analyst_report.py")

elif selected_page == "🏥 Hospital Admin":
    run_script("hospital_admin.py")

# Optional footer
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit")
