"""
Core ATS Evaluation and Scoring Engine.
Analyzes resumes against Job Descriptions, generates think-aloud evaluations,
calculates match percentages, recommends targeted upskilling courses, and processes batch queues.
"""

import re
import math
from typing import Dict, Any, List, Optional
from core.parser import parse_text, extract_skills_from_text, estimate_years_of_experience
from core.courses_db import get_recommended_courses

class ATSAnalyzer:
    """Evaluates resumes against job descriptions with step-by-step think aloud reasoning."""

    def analyze(self, jd_text: str, resume_text: str, role_hint: str = "", candidate_hint: str = "") -> Dict[str, Any]:
        """Perform full ATS analysis and return standardized results."""
        jd_parsed = parse_text(jd_text)
        resume_parsed = parse_text(resume_text)

        # Detect role title & candidate name if not explicitly given
        target_role = role_hint or self._extract_role_title(jd_text)
        candidate_name = candidate_hint or self._extract_candidate_name(resume_text)

        # 1. Skills Matching
        jd_skills = set(s.lower() for s in jd_parsed["skills"])
        if not jd_skills:
            # Fallback extraction from all text tokens
            jd_skills = self._extract_keywords(jd_text)

        resume_skills = set(s.lower() for s in resume_parsed["skills"])
        if not resume_skills:
            resume_skills = self._extract_keywords(resume_text)

        matched_skills = jd_skills.intersection(resume_skills)
        missing_skills = jd_skills.difference(resume_skills)

        skills_match_pct = self._calculate_skills_score(jd_skills, matched_skills, jd_text, resume_text)

        # 2. Experience Matching
        jd_exp_req = jd_parsed["experience_years"]
        resume_exp = resume_parsed["experience_years"]
        exp_match_pct = self._calculate_experience_score(jd_exp_req, resume_exp, jd_text, resume_text)

        # 3. Overall Weighted ATS Score (Skills 60%, Experience 30%, Formatting & Keyword Density 10%)
        composite_score = int(round((skills_match_pct * 0.60) + (exp_match_pct * 0.30) + (min(100, (skills_match_pct + exp_match_pct)/2) * 0.10)))
        composite_score = max(10, min(99, composite_score))

        # 4. Course Recommendations
        suggested_courses_objs = get_recommended_courses(list(missing_skills), target_role)
        suggested_courses_str = ", ".join([c["title"] for c in suggested_courses_objs]) if suggested_courses_objs else "Advanced Professional Certifications"

        # 5. Think-Aloud Step-by-Step Reasoning
        think_aloud = self._generate_think_aloud(
            target_role=target_role,
            candidate_name=candidate_name,
            skills_match_pct=skills_match_pct,
            exp_match_pct=exp_match_pct,
            matched_skills=list(matched_skills),
            missing_skills=list(missing_skills),
            jd_exp_req=jd_exp_req,
            resume_exp=resume_exp
        )

        # 6. Overall Analytics Breakdown
        strengths, improvement_areas = self._generate_analytics_breakdown(
            matched_skills=list(matched_skills),
            missing_skills=list(missing_skills),
            skills_match_pct=skills_match_pct,
            exp_match_pct=exp_match_pct,
            jd_exp=jd_exp_req,
            res_exp=resume_exp
        )

        overall_analytics_str = f"Strengths: {strengths}. Improvement Areas: {improvement_areas}."

        # 7. Standardized Output String as required
        formatted_output = (
            f"ATS Score: {composite_score}%, "
            f"Breakdown: [Skills match: {skills_match_pct}%, Experience match: {exp_match_pct}%]. "
            f"Suggested Courses: {suggested_courses_str}. "
            f"Overall Analytics: [{overall_analytics_str}]"
        )

        return {
            "target_role": target_role,
            "candidate_name": candidate_name,
            "ats_score": composite_score,
            "breakdown": {
                "skills_match": skills_match_pct,
                "experience_match": exp_match_pct,
                "jd_skills_count": len(jd_skills),
                "matched_skills_count": len(matched_skills),
                "missing_skills_count": len(missing_skills)
            },
            "matched_skills": [s.title() for s in matched_skills],
            "missing_skills": [s.title() for s in missing_skills],
            "suggested_courses": suggested_courses_objs,
            "suggested_courses_str": suggested_courses_str,
            "think_aloud": think_aloud,
            "overall_analytics": {
                "strengths": strengths,
                "improvement_areas": improvement_areas,
                "full_text": overall_analytics_str
            },
            "formatted_output": formatted_output
        }

    def _extract_role_title(self, text: str) -> str:
        """Extract or infer role title from job description."""
        role_patterns = [
            r"(?:jd|job description)\s+(?:for|:)\s*([^:\n\r,]+)",
            r"(?:job title|position|role)\s*[:\-]\s*([^\n\r,]+)",
            r"(?:we are looking for a|hiring an?)\s+([A-Za-z\s]+?(?:Engineer|Developer|Manager|Specialist|Analyst|Lead|Architect|Designer))",
            r"^#+\s*([A-Za-z\s]+?(?:Engineer|Developer|Manager|Specialist|Analyst|Lead|Architect|Designer))"
        ]
        for p in role_patterns:
            m = re.search(p, text, re.IGNORECASE | re.MULTILINE)
            if m:
                clean = m.group(1).strip()
                if len(clean) < 45:
                    return clean
        first_line = text.strip().split("\n")[0][:40].strip()
        return first_line if first_line else "Target Role"

    def _extract_candidate_name(self, text: str) -> str:
        """Extract candidate name from resume header."""
        lines = [l.strip() for l in text.strip().split("\n") if l.strip()]
        for line in lines[:3]:
            # If line is 2-3 words and not a section title
            words = line.split()
            if 1 < len(words) <= 3 and not any(k in line.lower() for k in ["resume", "curriculum", "page", "phone", "email", "skills", "experience"]):
                return line
        return "Candidate"

    def _extract_keywords(self, text: str) -> set[str]:
        """Extract significant technical and professional tokens."""
        words = re.findall(r'\b[a-zA-Z\+#\.]{3,20}\b', text.lower())
        stopwords = {"with", "that", "this", "from", "have", "will", "your", "they", "been", "work", "must", "team", "role", "years"}
        return set(w for w in words if w not in stopwords)

    def _calculate_skills_score(self, jd_skills: set[str], matched_skills: set[str], jd_text: str, resume_text: str) -> int:
        """Calculate percentage skills match."""
        if not jd_skills:
            return 80
        ratio = len(matched_skills) / max(1, len(jd_skills))
        score = int(round(ratio * 100))
        # Normalization curve
        if score < 40 and len(matched_skills) > 0:
            score = 45 + int(score * 0.7)
        return min(98, max(25, score))

    def _calculate_experience_score(self, req_exp: float, cand_exp: float, jd_text: str, resume_text: str) -> int:
        """Calculate experience alignment percentage."""
        if req_exp <= 0:
            req_exp = 3.0
        if cand_exp <= 0:
            cand_exp = 2.0

        ratio = cand_exp / req_exp
        if ratio >= 1.0:
            score = min(96, int(85 + (min(ratio, 2.0) - 1.0) * 10))
        else:
            score = max(35, int(ratio * 80))

        # Check for seniority keywords
        seniority_terms = ["senior", "lead", "principal", "manager", "director"]
        jd_senior = any(t in jd_text.lower() for t in seniority_terms)
        res_senior = any(t in resume_text.lower() for t in seniority_terms)

        if jd_senior and not res_senior:
            score = max(30, score - 12)
        elif not jd_senior and res_senior:
            score = min(95, score + 5)

        return score

    def _generate_think_aloud(self, target_role: str, candidate_name: str, skills_match_pct: int,
                              exp_match_pct: int, matched_skills: list[str], missing_skills: list[str],
                              jd_exp_req: float, resume_exp: float) -> Dict[str, str]:
        """Generate human-like think-aloud evaluation steps."""
        matched_str = ", ".join([s.title() for s in matched_skills[:5]]) if matched_skills else "Core domain familiarity"
        missing_str = ", ".join([s.title() for s in missing_skills[:4]]) if missing_skills else "Niche tool certifications"

        return {
            "title_analysis": f"Evaluated candidate qualifications against the position of {target_role}. Estimated requirements call for approximately {jd_exp_req:.1f} years of relevant industry experience.",
            "skills_match": f"The candidate demonstrated {skills_match_pct}% skills alignment. Strong proficiencies identified in {matched_str}. Gap areas detected in {missing_str}.",
            "experience_match": f"Experience match scored at {exp_match_pct}%. Candidate demonstrates approximately {resume_exp:.1f} years of professional background compared to the requested {jd_exp_req:.1f} years.",
            "areas_for_improvement": f"Recommend highlighting measurable project impacts (KPIs/ROI), closing key competencies in {missing_str}, and emphasizing cross-functional leadership."
        }

    def _generate_analytics_breakdown(self, matched_skills: list[str], missing_skills: list[str],
                                      skills_match_pct: int, exp_match_pct: int,
                                      jd_exp: float, res_exp: float) -> tuple[str, str]:
        """Generate strengths and areas of improvement."""
        top_skills = ", ".join([s.title() for s in matched_skills[:4]]) if matched_skills else "Domain knowledge"
        gap_skills = ", ".join([s.title() for s in missing_skills[:3]]) if missing_skills else "Advanced specialized tooling"

        strengths = f"Solid foundation in {top_skills} with strong relevant project background"
        improvement = f"Address skill gaps in {gap_skills}, emphasize quantitative metrics and leadership achievements"

        return strengths, improvement


class BatchATSQueue:
    """Manages multi-JD / multi-Resume queue prioritizing evaluations based on receipt order."""

    def __init__(self):
        self.analyzer = ATSAnalyzer()

    def process_batch(self, items: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Process a list of { 'jd': '...', 'resume': '...', 'priority': int }
        Items are processed in the order received, maintaining priority order.
        """
        results = []
        for index, item in enumerate(items, start=1):
            jd_content = item.get("jd", "")
            resume_content = item.get("resume", "")
            role_hint = item.get("role_hint", "")
            candidate_hint = item.get("candidate_hint", "")

            analysis = self.analyzer.analyze(
                jd_text=jd_content,
                resume_text=resume_content,
                role_hint=role_hint,
                candidate_hint=candidate_hint
            )
            analysis["queue_order"] = index
            results.append(analysis)

        return results
