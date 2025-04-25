from experta import *
import pandas as pd


class Student(Fact):
    """Student"""
    pass


class CourseRecommendation(KnowledgeEngine):
    def __init__(self, courses, passed, failed):
        super().__init__()
        self.courses = courses
        self.recommendations = []
        self.passed = passed
        self.failed = failed
        self.credit_limit = 0
        self.explanations = []

    @Rule(Student(cgpa=P(lambda x: x < 2.0)))
    def low_cgpa(self):
        self.credit_limit = 12
        self.explanations.append("CGPA < 2.0 → max 12 credits")

    @Rule(Student(cgpa=P(lambda x: 2.0 <= x < 3.0)))
    def mid_cgpa(self):
        self.credit_limit = 15
        self.explanations.append("2.0 ≤ CGPA < 3.0 → max 15 credits")

    @Rule(Student(cgpa=P(lambda x: x >= 3.0)))
    def high_cgpa(self):
        self.credit_limit = 18
        self.explanations.append("CGPA ≥ 3.0 → max 18 credits")

    # break logic into smaller helper methods to improve readability
    def prerequisites_met(self, prereq):
        if not prereq or pd.isna(prereq):
            return True

        prereq_list = prereq.split(',')
        for pr in prereq_list:
            if pr.strip() not in self.passed:
                return False
        return True

    def corequisites_met(self, coreq):
        if not coreq or pd.isna(coreq):
            return True

        coreq_list = coreq.split(',')
        for co in coreq_list:
            if co.strip() not in self.passed:
                return False
        return True

    def is_semester_offered(self, row, semester):
        return semester not in row['Semester Offered'] and row['Semester Offered'] != "Both"

    def is_course_level(self, row, level):
        course_level = int(row.get("Level"))
        if course_level > level + 1 and level + 1 <= 4:
            self.explanations.append(
                f"{row['Course Code']} skipped (Level {course_level} too high for Level {level} student).")
            return True
        return False

    def is_passed_course(self, row):
        return row['Course Code'] in self.passed

    def add_explanation(self, row):
        code = row['Course Code']
        if code in self.failed:
            self.explanations.append(f"{code} prioritized as it was failed previously.")
        else:
            self.explanations.append(f"{code} recommended (fits all rules).")

    def add_to_recommendations(self, row, total_credits):
        if total_credits + row['Credit Hours'] <= self.credit_limit:
            self.recommendations.append(row)
            return True
        return False

    @Rule(Student(semester=MATCH.semester, level=MATCH.level))
    def recommend_courses(self, semester, level):
        total_credits = 0
        for _, row in self.courses.iterrows():

            if self.is_semester_offered(row, semester): continue

            if self.is_course_level(row, level): continue

            if not self.prerequisites_met(row['Prerequisites']):
                self.explanations.append(
                    f"{row['Course Code']} not added due to unmet prerequisites: {row['Prerequisites']}")
                continue

            if not self.corequisites_met(row['Co-requisites']):
                self.explanations.append(
                    f"{row['Course Code']} not added due to unmet co-requisites: {row['Co-requisites']}")
                continue

            if self.is_passed_course(row):
                continue

            self.add_explanation(row)

            if self.add_to_recommendations(row, total_credits):
                total_credits += row['Credit Hours']

    def run_engine(self, semester, cgpa, level):
        self.reset()
        self.declare(Student(semester=semester, cgpa=cgpa, level=level))
        self.run()
        return self.recommendations, self.explanations
