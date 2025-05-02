#!/usr/bin/env python3
"""
inference_engine.py

Recommends courses using Experta based on student CGPA, passed/failed courses,
semester, track, and level progression. Returns both:
  - A list of recommended courses with explanations.
  - A list of unavailable-course explanations.
"""

import logging
import collections
import collections.abc
# Compatibility patch for frozendict dependency
collections.Mapping = collections.abc.Mapping

from experta import KnowledgeEngine, Fact, Field, DefFacts, Rule, MATCH
from KnowledgeBase import list_all_courses, get_course, max_credits_for_cgpa, retake_failed_first

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CourseFact(Fact):
    course_code      = Field(str,  mandatory=True)
    course_name      = Field(str,  mandatory=True)
    prerequisites    = Field(list, default=[])
    corequisites     = Field(list, default=[])
    credits          = Field(int,  mandatory=True)
    semester_offered = Field(str,  mandatory=True)
    track            = Field(str,  default='All')
    level            = Field(int,  mandatory=True)


class Student(Fact):
    cgpa           = Field(float, mandatory=True)
    passed_courses = Field(list,  default=[])
    failed_courses = Field(list,  default=[])
    semester       = Field(str,  mandatory=True)
    track          = Field(str,  mandatory=True)


class EligibleCourse(Fact):
    course_code = Field(str, mandatory=True)
    credits     = Field(int, mandatory=True)
    level       = Field(int, mandatory=True)
    reason      = Field(str)


class CourseAdvisorEngine(KnowledgeEngine):
    @DefFacts()
    def _load_courses(self):
        """Load all courses into working memory."""
        for course in list_all_courses():
            prereqs = [c.strip() for c in course['Prerequisites'].split(',') if c.strip()]
            coreqs = [c.strip() for c in course['Co-requisites'].split(',') if c.strip()]
            yield CourseFact(
                course_code      = course['Course Code'],
                course_name      = course['Course Name'],
                prerequisites    = prereqs,
                corequisites     = coreqs,
                credits          = int(course['Credit Hours']),
                semester_offered = course['Semester Offered'],
                track            = course['Track'],
                level            = int(course['Level'])
            )

    @Rule(Student(cgpa=MATCH.cgpa))
    def _set_credit_limit(self, cgpa):
        """Declare max_credits fact based on CGPA band."""
        limit = max_credits_for_cgpa(cgpa)
        self.declare(Fact(max_credits=limit))
        logger.info(f"Credit limit set to {limit}")

    @Rule(
        Student(passed_courses=MATCH.passed,
                failed_courses=MATCH.failed,
                semester=MATCH.sem,
                track=MATCH.strack),
        Fact(max_credits=MATCH.max_credits),
        CourseFact(course_code=MATCH.code,
                   prerequisites=MATCH.prereqs,
                   corequisites=MATCH.coreqs,
                   credits=MATCH.credits,
                   semester_offered=MATCH.sem_offered,
                   track=MATCH.ctrack,
                   level=MATCH.lev)
    )
    def _evaluate(self, passed, failed, sem, strack,
                  max_credits, code, prereqs, coreqs,
                  credits, sem_offered, ctrack, lev):
        # 0) Exclude already-completed courses
        if code in passed:
            return

        # 1) Semester filter
        if sem_offered not in (sem, 'Both'):
            return
        # 2) Track filter
        if ctrack not in (strack, 'All'):
            return
        # 3) Prerequisites check
        unmet_pr = [p for p in prereqs if p not in passed]
        if unmet_pr:
            return
        # 4) Corequisites check
        unmet_cr = [c for c in coreqs if c not in passed]
        if unmet_cr:
            return
        # 5) Level progression: at most one above current max level
        levels = [
            int(get_course(pc)['Level'])
            for pc in passed
            if get_course(pc)
        ]
        current = max(levels) if levels else 0
        if lev > current + 1:
            return

        # 6) Build explanation (reason)
        if code in failed and retake_failed_first():
            reason = f"{code} is prioritized because you failed it previously."
        elif prereqs:
            reason = f"{code} is recommended because you passed {prereqs[0]}, its prerequisite."
        else:
            reason = f"{code} is recommended."

        # Declare eligible course
        self.declare(EligibleCourse(
            course_code=code,
            credits=credits,
            level=lev,
            reason=reason
        ))


def recommend_courses(cgpa: float, passed: list, failed: list,
                      semester: str, track: str) -> tuple:
    """
    Runs the engine and returns:
      - List of recommended course dicts: {
            'course_code', 'credits', 'level', 'reason'
        }
      - List of unavailable-course explanation strings
    """
    engine = CourseAdvisorEngine()
    engine.reset()
    engine.declare(Student(
        cgpa=cgpa,
        passed_courses=passed,
        failed_courses=failed,
        semester=semester,
        track=track
    ))
    engine.run()

    # 1) Gather all EligibleCourse facts
    eligibles = [
        f for f in engine.facts.values()
        if isinstance(f, EligibleCourse)
    ]
    # 2) Sort by level, then by descending credits
    eligibles.sort(key=lambda f: (f['level'], -f['credits']))

    # 3) Enforce credit cap
    cap = max_credits_for_cgpa(cgpa)
    recommendations = []
    total = 0
    for f in eligibles:
        if total + f['credits'] <= cap:
            recommendations.append({
                'course_code': f['course_code'],
                'credits':     f['credits'],
                'level':       f['level'],
                'reason':      f['reason']
            })
            total += f['credits']

    # 4) Build unavailable-course explanations
    explanations = []
    all_codes = {c['Course Code'] for c in list_all_courses()}
    rec_codes = {r['course_code'] for r in recommendations}
    for code in sorted(all_codes - rec_codes - set(passed)):
        course = get_course(code)
        # unmet prereq?
        prereqs = [p for p in course['Prerequisites'].split(',') if p.strip()]
        unmet = next((p for p in prereqs if p not in passed), None)
        if unmet:
            explanations.append(
                f"{code} is unavailable due to an unmet prerequisite, {unmet}."
            )
        elif code in failed and retake_failed_first():
            # already prioritized and recommended if eligible
            continue
        else:
            explanations.append(f"{code} is unavailable.")

    return recommendations, explanations


if __name__ == "__main__":
    # Demo run
    recs, notes = recommend_courses(
        cgpa=3.2,
        passed=['CSE014', 'MAT111'],
        failed=['UC1'],
        semester='Fall',
        track='AI Science'
    )

    print("Recommended Courses:")
    for r in recs:
        print(f"- {r['course_code']} (Level {r['level']}, {r['credits']} cr): {r['reason']}")

    print("\nExplanations for Unavailable Courses:")
    for note in notes:
        print(f"- {note}")
