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