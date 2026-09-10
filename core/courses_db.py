"""
Comprehensive course database mapped to technical, analytical, management, and domain skills.
Provides direct links, provider information, and difficulty levels.
"""

COURSE_CATALOG = {
    # Data & Analytics
    "python for data analysis": {
        "title": "Python for Data Science and Machine Learning Bootcamp",
        "provider": "Coursera / Udemy",
        "url": "https://www.coursera.org/learn/python-for-applied-data-science-ai",
        "category": "Data Science",
        "level": "Intermediate"
    },
    "sql": {
        "title": "SQL Basics & Advanced Database Querying for Analysts",
        "provider": "Coursera / UC Davis",
        "url": "https://www.coursera.org/learn/sql-for-data-science",
        "category": "Data & Databases",
        "level": "Beginner to Intermediate"
    },
    "power bi": {
        "title": "Microsoft Power BI Data Analyst Professional Certificate",
        "provider": "Microsoft / Coursera",
        "url": "https://www.coursera.org/professional-certificates/microsoft-power-bi-data-analyst",
        "category": "Business Intelligence",
        "level": "Intermediate"
    },
    "tableau": {
        "title": "Tableau Business Intelligence and Data Visualization",
        "provider": "Tableau / Coursera",
        "url": "https://www.coursera.org/specializations/data-visualization",
        "category": "Business Intelligence",
        "level": "Intermediate"
    },
    "data modeling": {
        "title": "Data Warehouse & Data Modeling Fundamentals",
        "provider": "Coursera / IBM",
        "url": "https://www.coursera.org/learn/data-warehouse-fundamentals",
        "category": "Data Engineering",
        "level": "Advanced"
    },
    "machine learning": {
        "title": "Machine Learning Specialization by Andrew Ng",
        "provider": "DeepLearning.AI / Stanford",
        "url": "https://www.coursera.org/specializations/machine-learning-introduction",
        "category": "AI / ML",
        "level": "Advanced"
    },

    # Software Engineering & Web Development
    "advanced algorithms": {
        "title": "Algorithms & Data Structures Masterclass",
        "provider": "Coursera / Princeton",
        "url": "https://www.coursera.org/learn/algorithms-part1",
        "category": "Computer Science",
        "level": "Advanced"
    },
    "full stack development": {
        "title": "Full Stack Web Development with React & Node.js",
        "provider": "freeCodeCamp / Coursera (IBM)",
        "url": "https://www.coursera.org/professional-certificates/ibm-full-stack-cloud-developer",
        "category": "Software Engineering",
        "level": "Intermediate"
    },
    "react": {
        "title": "Meta Front-End Developer Professional Certificate (React)",
        "provider": "Meta / Coursera",
        "url": "https://www.coursera.org/professional-certificates/meta-front-end-developer",
        "category": "Front-End",
        "level": "Intermediate"
    },
    "fastapi": {
        "title": "Building High-Performance APIs with FastAPI & Python",
        "provider": "Udemy / TestDriven.io",
        "url": "https://testdriven.io/courses/fastapi-celery/",
        "category": "Backend",
        "level": "Intermediate"
    },
    "microservices": {
        "title": "Microservices Architecture & System Design",
        "provider": "Educative / Coursera",
        "url": "https://www.coursera.org/learn/microservices-architecture",
        "category": "System Design",
        "level": "Advanced"
    },
    "system design": {
        "title": "Grokking the System Design Interview & Architecture",
        "provider": "Educative.io / NeetCode",
        "url": "https://www.educative.io/courses/grokking-the-system-design-interview",
        "category": "Architecture",
        "level": "Advanced"
    },

    # Cloud & DevOps
    "aws": {
        "title": "AWS Certified Solutions Architect & DevOps Professional",
        "provider": "Amazon Web Services / Coursera",
        "url": "https://www.coursera.org/learn/aws-cloud-technical-essentials",
        "category": "Cloud Computing",
        "level": "Intermediate"
    },
    "kubernetes": {
        "title": "Certified Kubernetes Administrator (CKA) & Cloud Native Architect",
        "provider": "Linux Foundation / CNCF",
        "url": "https://www.cncf.io/certification/cka/",
        "category": "DevOps",
        "level": "Advanced"
    },
    "terraform": {
        "title": "HashiCorp Certified: Terraform Associate Infrastructure as Code",
        "provider": "HashiCorp / Coursera",
        "url": "https://www.hashicorp.com/certification/terraform-associate",
        "category": "DevOps / IaC",
        "level": "Intermediate"
    },
    "ci/cd": {
        "title": "Continuous Integration and Continuous Delivery (CI/CD) with GitLab & GitHub Actions",
        "provider": "GitLab / Coursera",
        "url": "https://www.coursera.org/learn/continuous-integration",
        "category": "DevOps",
        "level": "Intermediate"
    },
    "finops": {
        "title": "FinOps Certified Practitioner (Cloud Cost Optimization)",
        "provider": "Linux Foundation / FinOps Foundation",
        "url": "https://www.finops.org/certification/",
        "category": "Cloud Economics",
        "level": "Intermediate"
    },

    # Marketing & Growth
    "brand strategy": {
        "title": "Advanced Brand Strategy & P&L Management",
        "provider": "Coursera / Northwestern Kellogg",
        "url": "https://www.coursera.org/learn/strategic-brand-management",
        "category": "Marketing Management",
        "level": "Advanced"
    },
    "marketing analytics": {
        "title": "Marketing Analytics & Multi-Touch Attribution Modeling",
        "provider": "Reforge / Coursera (Meta)",
        "url": "https://www.coursera.org/professional-certificates/meta-marketing-analytics",
        "category": "Growth Marketing",
        "level": "Advanced"
    },
    "seo/sem": {
        "title": "Google Digital Marketing & E-commerce Professional Certificate",
        "provider": "Google / Coursera",
        "url": "https://www.coursera.org/professional-certificates/google-digital-marketing-ecommerce",
        "category": "Digital Marketing",
        "level": "Intermediate"
    },
    "crm & automation": {
        "title": "HubSpot & Salesforce Marketing Automation Mastery",
        "provider": "HubSpot Academy / Trailhead",
        "url": "https://academy.hubspot.com/",
        "category": "MarTech",
        "level": "Intermediate"
    },

    # HR & Talent Acquisition
    "hr compliance": {
        "title": "Strategic Human Resources & Employment Compliance Management",
        "provider": "SHRM / Coursera",
        "url": "https://www.coursera.org/specializations/human-resource-management",
        "category": "Human Resources",
        "level": "Intermediate"
    },
    "compensation & benefits": {
        "title": "Compensation, Benefits, and Total Rewards Essentials",
        "provider": "AIHR (Academy to Innovate HR)",
        "url": "https://www.aihr.com/courses/compensation-and-benefits-certificate/",
        "category": "HR Operations",
        "level": "Intermediate"
    },
    "hr analytics": {
        "title": "People Analytics & HR Metrics for Strategic Decision Making",
        "provider": "Coursera / Wharton",
        "url": "https://www.coursera.org/learn/wharton-people-analytics",
        "category": "People Analytics",
        "level": "Advanced"
    },
    "talent acquisition": {
        "title": "Full-Cycle Talent Acquisition & Technical Recruitment",
        "provider": "LinkedIn Learning / Coursera",
        "url": "https://www.coursera.org/learn/recruiting-hiring-onboarding",
        "category": "Talent Acquisition",
        "level": "Intermediate"
    },

    # Product & Agile Management
    "product management": {
        "title": "Digital Product Management: Modern Fundamentals",
        "provider": "University of Virginia / Coursera",
        "url": "https://www.coursera.org/learn/uva-darden-digital-product-management",
        "category": "Product Management",
        "level": "Intermediate"
    },
    "agile & scrum": {
        "title": "Professional Scrum Master (PSM I) & Agile Delivery",
        "provider": "Scrum.org / Coursera",
        "url": "https://www.scrum.org/assessments/professional-scrum-master-i-certification",
        "category": "Agile Delivery",
        "level": "Intermediate"
    },

    # Cybersecurity & Compliance
    "cybersecurity": {
        "title": "Google Cybersecurity Professional Certificate",
        "provider": "Google / Coursera",
        "url": "https://www.coursera.org/professional-certificates/google-cybersecurity",
        "category": "Information Security",
        "level": "Intermediate"
    },
    "cloud security": {
        "title": "Certified Kubernetes Security Specialist (CKS) & Cloud Security",
        "provider": "CNCF / Linux Foundation",
        "url": "https://www.cncf.io/certification/cks/",
        "category": "Cloud Security",
        "level": "Advanced"
    }
}


def get_recommended_courses(missing_skills: list[str], target_role: str = "") -> list[dict]:
    """Find the best course recommendations for missing skills."""
    recommendations = []
    matched_keys = set()

    for skill in missing_skills:
        skill_lower = skill.lower().strip()
        # Direct keyword match or substring match
        for key, course in COURSE_CATALOG.items():
            if key in skill_lower or skill_lower in key:
                if key not in matched_keys:
                    recommendations.append(course)
                    matched_keys.add(key)
                    break

    # Fallback recommendations if none matched or fewer than 2
    if len(recommendations) < 2:
        role_lower = target_role.lower()
        if "data" in role_lower or "analyst" in role_lower:
            fallback_keys = ["python for data analysis", "sql", "power bi"]
        elif "developer" in role_lower or "software" in role_lower or "engineer" in role_lower:
            fallback_keys = ["advanced algorithms", "full stack development", "system design"]
        elif "marketing" in role_lower:
            fallback_keys = ["brand strategy", "marketing analytics", "seo/sem"]
        elif "hr" in role_lower or "human" in role_lower or "recruiter" in role_lower:
            fallback_keys = ["hr compliance", "compensation & benefits", "hr analytics"]
        elif "devops" in role_lower or "cloud" in role_lower:
            fallback_keys = ["aws", "kubernetes", "terraform"]
        else:
            fallback_keys = ["full stack development", "product management", "system design"]

        for key in fallback_keys:
            if key not in matched_keys and key in COURSE_CATALOG:
                recommendations.append(COURSE_CATALOG[key])
                matched_keys.add(key)
                if len(recommendations) >= 3:
                    break

    return recommendations[:3]
