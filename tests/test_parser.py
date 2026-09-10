"""
Unit tests for document parsing and keyword extraction.
"""

from core.parser import parse_text, extract_skills_from_text, estimate_years_of_experience

def test_text_skills_extraction():
    sample_text = "Proficient in Python, SQL, Docker, AWS, and React. Experienced with Terraform and CI/CD."
    skills = extract_skills_from_text(sample_text)
    assert "Python" in skills
    assert "SQL" in skills
    assert "Docker" in skills
    assert "AWS" in skills

def test_years_of_experience_estimation():
    sample_1 = "5+ years of experience in full stack software engineering."
    exp_1 = estimate_years_of_experience(sample_1)
    assert exp_1 == 5.0

    sample_2 = "Software Engineer from 2019 - 2023."
    exp_2 = estimate_years_of_experience(sample_2)
    assert exp_2 == 4.0
