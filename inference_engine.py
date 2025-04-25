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