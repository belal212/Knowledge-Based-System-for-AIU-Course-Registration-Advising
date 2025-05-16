import pandas as pd
import json
import os
from pathlib import Path

# 1. Load files
# Get the absolute path to the data directory regardless of where the script is run from
base_dir = Path(__file__).parent.parent
courses_path = os.path.join(base_dir, "data", "courses.csv")
policies_path = os.path.join(base_dir, "data", "policies.json")

_courses_df = pd.read_csv(courses_path).fillna('')
with open(policies_path) as f:
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
