import pandas as pd
import json

# 1. Load files
_courses_df = pd.read_csv( r"C:\Users\Sab3awy\Knowledge-Based-System-for-AIU-Course-Registration-Advising\data\courses.csv"
).fillna('')
with open(r"C:\Users\Sab3awy\Knowledge-Based-System-for-AIU-Course-Registration-Advising\data\policies.json"
) as f:
    _policies = json.load(f)

def list_all_courses():
    return _courses_df.to_dict(orient='records')

def get_course(code):
    row = _courses_df[_courses_df['Course Code'] == code]
    return row.to_dict('records')[0] if not row.empty else None

def max_credits_for_cgpa(cgpa: float) -> int:
    for band in _policies['credit_limits']:
        if band['min_cgpa'] <= cgpa <= band['max_cgpa']:
            return band['max_credits']
    raise ValueError(f"CGPA {cgpa} out of range")

def retake_failed_first() -> bool:
    return _policies.get('retake_failed_priority', False)
