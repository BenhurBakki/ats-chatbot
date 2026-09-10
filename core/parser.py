"""
Parser for Resumes and Job Descriptions across multiple formats (Plain text, PDF, DOCX).
Extracts candidate info, skills, years of experience, and role requirements.
"""

import re
from typing import Dict, Any, List

def parse_text(raw_text: str) -> Dict[str, Any]:
    """Parse raw plain text from a resume or job description."""
    cleaned_text = re.sub(r'\r\n', '\n', raw_text).strip()
    return {
        "raw_text": cleaned_text,
        "sections": extract_sections(cleaned_text),
        "experience_years": estimate_years_of_experience(cleaned_text),
        "skills": extract_skills_from_text(cleaned_text),
        "education": extract_education_from_text(cleaned_text)
    }

def extract_sections(text: str) -> Dict[str, str]:
    """Segment document text into standard resume / JD sections."""
    sections = {
        "summary": "",
        "experience": "",
        "skills": "",
        "education": "",
        "projects": ""
    }

    section_patterns = {
        "summary": r"(?:summary|profile|about me|objective)",
        "experience": r"(?:experience|work history|employment|professional background)",
        "skills": r"(?:skills|technical skills|competencies|technologies|expertise)",
        "education": r"(?:education|academic background|qualifications)",
        "projects": r"(?:projects|key projects|portfolio)"
    }

    # Normalize lines
    lines = text.split("\n")
    current_section = "summary"
    section_buffer: Dict[str, List[str]] = {k: [] for k in sections}

    for line in lines:
        line_clean = line.strip()
        matched = False
        for sec_name, pattern in section_patterns.items():
            if re.match(rf"^(?:#+|\*+)?\s*{pattern}\s*[:\-]?\s*$", line_clean, re.IGNORECASE):
                current_section = sec_name
                matched = True
                break
        if not matched:
            section_buffer[current_section].append(line)

    for k, v in section_buffer.items():
        sections[k] = "\n".join(v).strip()

    return sections

def estimate_years_of_experience(text: str) -> float:
    """Estimate years of experience from date ranges or explicit mentions."""
    # Look for explicit mentions like '5+ years', '3 years of experience'
    explicit_match = re.search(r'(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)(?:\s+of)?(?:\s+experience)?', text, re.IGNORECASE)
    if explicit_match:
        try:
            return float(explicit_match.group(1))
        except ValueError:
            pass

    # Look for year ranges like 2018 - 2023, 2020 to Present
    year_ranges = re.findall(r'(?:19|20)\d{2}\s*(?:-|–|to)\s*(?:(?:19|20)\d{2}|present|current|now)', text, re.IGNORECASE)
    total_years = 0.0
    current_year = 2026

    for r in year_ranges:
        years = re.findall(r'(?:19|20)\d{2}', r)
        if len(years) == 2:
            start, end = int(years[0]), int(years[1])
            total_years += max(0, end - start)
        elif len(years) == 1:
            start = int(years[0])
            total_years += max(0, current_year - start)

    return total_years if total_years > 0 else 2.0

COMMON_SKILL_KEYWORDS = [
    "python", "javascript", "typescript", "react", "angular", "vue", "node.js", "nodejs",
    "fastapi", "django", "flask", "java", "spring boot", "c++", "c#", ".net", "golang",
    "rust", "sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ci/cd", "git",
    "linux", "bash", "graphql", "rest api", "microservices", "system design",
    "machine learning", "deep learning", "nlp", "llm", "pandas", "numpy", "scikit-learn",
    "power bi", "tableau", "data analysis", "data modeling", "data engineering",
    "seo", "sem", "google analytics", "hubspot", "salesforce", "marketing analytics",
    "brand strategy", "content marketing", "social media marketing", "roas", "cac",
    "talent acquisition", "hr compliance", "employee relations", "workday", "bamboohr",
    "compensation", "benefits", "people analytics", "onboarding", "performance management",
    "agile", "scrum", "jira", "product management", "stakeholder management"
]

def extract_skills_from_text(text: str) -> List[str]:
    """Identify key skills and technology mentions from text."""
    found_skills = set()
    text_lower = text.lower()

    for skill in COMMON_SKILL_KEYWORDS:
        # Match as full word / token
        pattern = rf"\b{re.escape(skill)}\b"
        if re.search(pattern, text_lower):
            found_skills.add(skill.title() if len(skill) > 3 else skill.upper())

    return sorted(list(found_skills))

def extract_education_from_text(text: str) -> List[str]:
    """Extract degree mentions."""
    degrees = []
    edu_patterns = [
        r"(?:Bachelor|Master|Doctor|Ph\.?D|B\.?S|M\.?S|B\.?Tech|B\.?E|M\.?Tech|MBA)\s*(?:of|in)?\s*[A-Za-z\s]+",
        r"High School Diploma"
    ]
    for p in edu_patterns:
        matches = re.findall(p, text, re.IGNORECASE)
        for m in matches:
            cleaned = m.strip()
            if len(cleaned) < 50:
                degrees.append(cleaned)
    return degrees
