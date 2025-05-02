import streamlit as st
import pandas as pd

from KnowledgeBase import list_all_courses, get_course
from inference_engine import recommend_courses

st.set_page_config(page_title="AIU Course Advisor", layout="centered")
st.title("AIU Course Registration Advisor")

# Load courses KB
courses = list_all_courses()
courses_df = pd.DataFrame(courses)
all_codes = courses_df['Course Code'].tolist()

# ——— Inputs ———

# Semester dropdown (season)
semester_options = ["Fall", "Spring"]
semester_sel = st.selectbox("Select Semester", semester_options)

# CGPA input
cgpa = st.number_input(
    "Enter your CGPA",
    min_value=0.0,
    max_value=4.0,
    value=2.5,
    step=0.01,
    format="%.2f",
    help="Must be between 0.0 and 4.0"
)

# Passed / Failed courses
passed = st.multiselect(
    "Select courses you have **passed**:",
    options=all_codes
)
failed = st.multiselect(
    "Select courses you have **failed**:",
    options=all_codes
)

# ——— Recommendation Trigger ———
if st.button("Recommend Courses"):
    # CGPA sanity check
    if cgpa < 0.0 or cgpa > 4.0:
        st.error("CGPA must be between 0.0 and 4.0.")
    else:
        # Call engine, unpacking recommendations and explanations
        recs, explanations = recommend_courses(
            cgpa=cgpa,
            passed=passed,
            failed=failed,
            semester=semester_sel,
            track="Ais"
        )

        if not recs:
            st.info("No courses can be recommended with the given inputs.")
        else:
            # Build and display recommendation table
            table_rows = []
            total_credits = 0
            for r in recs:
                
                row = {
                "Course Code": r['course_code'],
                "Course Name": get_course(r['course_code'])['Course Name'],
                "Credits": r['credits'],
                "Explanation": r['reason']
                   }
                table_rows.append(row)
                total_credits += r['credits']

            df_display = pd.DataFrame(table_rows)
            st.markdown("### Recommended Courses")
            st.table(df_display)
            st.markdown(f"**Total Credit Hours:** {total_credits}")

            # Show why other courses were unavailable
            if explanations:
                with st.expander("Why other courses are unavailable"):
                    for note in explanations:
                        st.write(f"- {note}")
