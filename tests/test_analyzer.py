"""
Unit tests for core ATS evaluation and scoring logic.
"""

from core.ats_analyzer import ATSAnalyzer, BatchATSQueue

def test_single_ats_analysis_format():
    analyzer = ATSAnalyzer()
    jd = "JD for Data Analyst: Requirements: 3+ years experience in Python for data analysis, SQL, and Power BI."
    resume = "Jane Smith: Data Analyst with 3 years experience using Python, SQL, Tableau, and Pandas."

    result = analyzer.analyze(jd, resume)

    assert "ats_score" in result
    assert "breakdown" in result
    assert "skills_match" in result["breakdown"]
    assert "experience_match" in result["breakdown"]
    assert "suggested_courses" in result
    assert "think_aloud" in result
    assert "formatted_output" in result

    # Check standardized string format requirements
    output_str = result["formatted_output"]
    assert "ATS Score:" in output_str
    assert "Breakdown: [Skills match:" in output_str
    assert "Suggested Courses:" in output_str
    assert "Overall Analytics:" in output_str

def test_software_developer_analysis():
    analyzer = ATSAnalyzer()
    jd = "JD for Software Developer: 4+ years in Python, React, Advanced Algorithms, Full Stack Development, Docker."
    resume = "John Doe: Software Engineer with 4 years in Python, React, FastAPI, Docker, Microservices."

    result = analyzer.analyze(jd, resume)
    assert result["ats_score"] >= 70
    assert result["target_role"] in ["Software Developer", "Software Engineer", "Developer"]

def test_batch_processing_priority_order():
    batch_queue = BatchATSQueue()
    items = [
        {"jd": "JD for Marketing Manager", "resume": "Resume of Alice Nguyen"},
        {"jd": "JD for HR Specialist", "resume": "Resume of Bob Brown"},
        {"jd": "JD for DevOps Engineer", "resume": "Resume of Carlos Mendez"}
    ]

    results = batch_queue.process_batch(items)
    assert len(results) == 3
    assert results[0]["queue_order"] == 1
    assert results[1]["queue_order"] == 2
    assert results[2]["queue_order"] == 3
