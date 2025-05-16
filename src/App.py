import streamlit as st
import pandas as pd

from KnowledgeBase import list_all_courses, get_course
from inference_engine import recommend_courses

st.set_page_config(page_title="AIU Course Advisor", layout="wide")

# Add custom CSS for styling buttons and hiding default Streamlit elements
st.markdown("""
<style>
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom button styling for a more appealing UI */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Make streamlit containers nicer */
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
      /* Improve header styling */
    h1, h2, h3 {
        color: #1E3A8A;
    }
      /* Panel styling for role selection */
    .role-panel {
        background-color: white;
        border-radius: 25px;
        /* padding: 15px 25px; */
        /* box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); */
        margin: 80px auto 20px;
        height: 2px;
        text-align: center;
    }
      /* Role icons styling */
    .role-icon {
        font-size: 38px;
        margin-bottom: 0;
        text-align: center;
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    
    /* Container styling for centering content */
    .center-content {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'admin_password' not in st.session_state:
    st.session_state.admin_password = "admin123"  # Demo password, change in production
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'role_selected' not in st.session_state:
    st.session_state.role_selected = False
if 'role' not in st.session_state:
    st.session_state.role = None
if 'selected_role_button' not in st.session_state:
    st.session_state.selected_role_button = None

# Function to toggle role selection
def select_role(role):
    st.session_state.selected_role_button = role

# Role Selection Modal
if not st.session_state.role_selected:
    
    # Create three columns for horizontal centering
    left_col, center_col, right_col = st.columns([1, 3, 1])
    
    with center_col:
        # Create a panel with rounded borders
        with st.container():
            # Apply the role-panel class for styling
            st.markdown('<div class="role-panel">', unsafe_allow_html=True)
            
            # Panel title and content
            st.markdown("<h1 style='text-align: center;'>Welcome to AIU Course Registration Advisor</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; font-size: 18px;'>Please select your role to continue:</p>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
              # Create two columns for role selection buttons
            role_col1, role_col2 = st.columns(2)
            
            with role_col1:
                # Student option
                st.markdown("<div class='center-content'><div class='role-icon'>👨‍🎓</div></div>", unsafe_allow_html=True)
                student_button = st.button("Student", use_container_width=True, key="student_role")
                if student_button:
                    st.session_state.role = "Student"
                    st.session_state.role_selected = True
                    st.rerun()
            
            with role_col2:
                # Instructor option
                st.markdown("<div class='center-content'><div class='role-icon'>👨‍🏫</div></div>", unsafe_allow_html=True)
                instructor_button = st.button("Instructor", use_container_width=True, key="instructor_role")
                if instructor_button:
                    st.session_state.selected_role_button = "Instructor"
            
            # Close the panel div
            st.markdown('</div>', unsafe_allow_html=True)
    
    # If instructor role is selected, show password input
    if st.session_state.selected_role_button == "Instructor":
        left_col, center_col, right_col = st.columns([1, 3, 1])
        with center_col:
            # Create another panel for password input
            st.markdown('<div class="role-panel">', unsafe_allow_html=True)
            
            st.markdown("<h3 style='text-align: center;'>Enter Admin Password</h3>", unsafe_allow_html=True)
            password = st.text_input("Password:", type="password", key="instructor_password", label_visibility="collapsed")
            login = st.button("Login", use_container_width=True)
            
            # Close the panel div
            st.markdown('</div>', unsafe_allow_html=True)
            
            if login:
                if password == st.session_state.admin_password:
                    st.session_state.authenticated = True
                    st.session_state.role = "Instructor"
                    st.session_state.role_selected = True
                    st.rerun()
                else:
                    st.error("Incorrect password")

else:
    # Create a header with logout button on left and role indicator on right
    header_cols = st.columns([1, 10, 1])
    
    # Logout button in left column
    with header_cols[0]:
        if st.button("Logout", key="logout_button"):
            st.session_state.authenticated = False
            st.session_state.role_selected = False
            st.session_state.role = None
            st.session_state.selected_role_button = None
            st.rerun()
            
    # Role indicator in right column
    with header_cols[2]:
        st.info(f"Role: {st.session_state.role}")

# Only show the interface if a role is selected

if st.session_state.role_selected:
    # Create tabs based on role
    if st.session_state.role == "Instructor" and st.session_state.authenticated:
        tab1, tab2 = st.tabs(["Student Advisor", "Knowledge Base Editor"])
    else:
        # Student role only sees Student Advisor tab
        tab1 = st.tabs(["Student Advisor"])[0]

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

if st.session_state.role == "Instructor" and st.session_state.authenticated:
    with tab2:
        st.title("Knowledge Base Editor")
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
