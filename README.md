# 🎓 AIU Course Registration Advisor

An intelligent rule-based system that helps AIU students choose the best courses to register based on their academic profile.

## 💡 Overview

This system provides course recommendations for students. It uses an expert system engine (`experta`) to apply academic rules such as:

- CGPA-based credit hour limits
- Semester offerings
- Course prerequisites & co-requisites
- Previously passed or failed courses
- Student level (1, 2, 3, or 4)

## 🛠️ Tech Stack

- **Python**
- **Streamlit** – for the frontend interface
- **Experta** – for building the rule-based expert system
- **Pandas** – for handling course data


## 🛠️ Setup Guide

### 📦 1. Create a Virtual Environment (venv)

Open a terminal in the root directory of the project and run:

```bash
python -m venv venv
```

### ▶️ 2. Activate the Virtual Environment

```bash
venv\Scripts\activate
```

### 📥 3. Install Requirements

After activating the environment, install all dependencies using:

```bash
pip install -r requirements.txt
```

## 🚀 4. Run the App

With everything set up, launch the app using:

```bash
streamlit run App.py
```

This will open a new tab in your browser where the Course Recommendation Advisor will be running.

---
