import streamlit as st
import pandas as pd

from KnowledgeBase import list_all_courses, get_course
from inference_engine import recommend_courses

st.set_page_config(page_title="AIU Course Advisor", layout="wide")

# Initialize session state
if 'admin_password' not in st.session_state:
    st.session_state.admin_password = "admin123"  # Demo password, change in production
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Authentication sidebar
with st.sidebar:
    if not st.session_state.authenticated:
        st.title("Admin Login")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if password == st.session_state.admin_password:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password")
    else:
        st.title("Admin Panel")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.rerun()

# Create tabs for student and admin views
tab1, tab2 = st.tabs(["Student Advisor", "Knowledge Base Editor"])

with tab1:
    st.title("AIU Course Registration Advisor")

    # Load courses KB for student view
    courses = list_all_courses()
    courses_df = pd.DataFrame(courses)
    all_codes = courses_df['Course Code'].tolist()

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

    # Recommendation Trigger
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

with tab2:
    st.title("Knowledge Base Editor")
    if not st.session_state.authenticated:
        st.warning("Please login as admin to access the Knowledge Base Editor")
    else:
        # Sub-tabs for different KB operations
        kb_tab1, kb_tab2, kb_tab3 = st.tabs(["List Courses", "Add Course", "Delete Course"])
        
        with kb_tab1:
            st.header("Current Courses")
            courses_df = pd.DataFrame(list_all_courses())
            st.dataframe(courses_df, use_container_width=True)
            
        with kb_tab2:
            st.header("Add New Course")
            with st.form("add_course_form"):
                col1, col2 = st.columns(2)
                with col1:
                    new_code = st.text_input("Course Code*", placeholder="e.g., CSE123")
                    new_name = st.text_input("Course Name*", placeholder="e.g., Introduction to Programming")
                    new_credits = st.number_input("Credit Hours*", min_value=1, max_value=4, value=3)
                    new_level = st.number_input("Level*", min_value=1, max_value=4, value=1)
                
                with col2:
                    new_semester = st.selectbox("Semester Offered*", ["Fall", "Spring", "Both"])
                    new_track = st.selectbox("Track*", ["All", "Artificial Intelligence Science"])
                    new_prereqs = st.text_input("Prerequisites (comma-separated)", placeholder="e.g., CSE101, CSE102")
                    new_coreqs = st.text_input("Co-requisites (comma-separated)", placeholder="e.g., CSE103, CSE104")
                
                submit_add = st.form_submit_button("Add Course")
                if submit_add:
                    if not new_code or not new_name:
                        st.error("Course Code and Course Name are required!")
                    else:
                        # Check if course already exists
                        existing_courses = pd.DataFrame(list_all_courses())
                        if new_code in existing_courses['Course Code'].values:
                            st.error(f"Course {new_code} already exists!")
                        else:
                            # Create new course dictionary
                            new_course = {
                                'Course Code': new_code,
                                'Course Name': new_name,
                                'Prerequisites': new_prereqs,
                                'Co-requisites': new_coreqs,
                                'Credit Hours': new_credits,
                                'Semester Offered': new_semester,
                                'Track': new_track,
                                'Level': new_level
                            }
                            
                            try:
                                # Append to CSV
                                df = pd.DataFrame([new_course])
                                df.to_csv('data/courses.csv', mode='a', header=False, index=False)
                                st.success(f"Added course {new_code} successfully!")
                                st.rerun()  # Refresh the page to show the new course
                            except Exception as e:
                                st.error(f"Error adding course: {str(e)}")
            
        with kb_tab3:
            st.header("Delete Course")
            courses = list_all_courses()
            course_codes = [c['Course Code'] for c in courses]
              # Course selection outside the form
            del_code = st.selectbox("Select Course to Delete", course_codes)
            course_info = get_course(del_code)
            if course_info:
                st.write("Course Details:")
                st.write(f"Name: {course_info['Course Name']}")
                st.write(f"Level: {course_info['Level']}")
                st.write(f"Credits: {course_info['Credit Hours']}")

            with st.form("delete_course_form"):
                st.write(f"Confirm deletion of course: {del_code}")
                confirm = st.checkbox("I understand this action cannot be undone")
                submit_del = st.form_submit_button("Delete Course")
                
                if submit_del:
                    if not confirm:
                        st.error("Please confirm the deletion")
                    else:
                        try:
                            # Remove course from DataFrame and save
                            df = pd.DataFrame(courses)
                            df = df[df['Course Code'] != del_code]
                            df.to_csv('data/courses.csv', index=False)
                            st.success(f"Deleted course {del_code} successfully!")
                            st.rerun()  # Refresh the page to show the changes
                        except Exception as e:
                            st.error(f"Error deleting course: {str(e)}")
