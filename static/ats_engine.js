/**
 * ATS Evaluation Engine — Pure Client-Side
 * Skills matching, scoring, think-aloud, course recommendations
 */

const PRESETS = {
  data_analyst: {
    jd: "Senior Data Analyst\n\nRequirements:\n- 3+ years experience in data analysis\n- Strong proficiency in Python for data analysis\n- Advanced SQL and database querying\n- Data visualization with Power BI or Tableau\n- ETL pipeline development and data modeling\n- Statistical analysis and reporting\n- Experience with Pandas, NumPy, Scikit-learn",
    resume: "Jane Smith\nEmail: jane@example.com | LinkedIn: linkedin.com/in/janesmith\n\nSummary:\nData Analyst with 3.5 years transforming complex datasets into actionable insights. Proven track record in building automated SQL reports and interactive dashboards.\n\nExperience:\nSenior Data Analyst – Acme Corp (2022–Present)\n• Built 15+ automated SQL reports, reducing turnaround by 35%\n• Developed Tableau dashboards tracking $5M revenue pipeline\n• Implemented Python-based ETL pipelines for daily data ingestion\n\nSkills:\nPython, SQL, Tableau, Pandas, NumPy, Excel, Git, Data Modeling\n\nEducation:\nBachelor of Science in Statistics – University of Texas, 2021"
  },
  software_dev: {
    jd: "Software Developer\n\nRequirements:\n- 4+ years in software development\n- Python and JavaScript proficiency\n- React frontend development\n- FastAPI or Django backend\n- Docker and container orchestration\n- CI/CD pipelines and DevOps practices\n- System design and microservices architecture\n- Advanced algorithms and data structures",
    resume: "John Doe\nEmail: john@example.com\n\nSummary:\nFull Stack Software Engineer with 4.5 years building scalable web services and cloud-native backends.\n\nExperience:\nSoftware Engineer – Nexus Tech (2021–Present)\n• Architected microservices serving 500k daily requests on AWS\n• Built React dashboards with FastAPI backends, reducing load time by 40%\n• Implemented Docker + CI/CD pipelines cutting deployment time by 60%\n\nSkills:\nPython, JavaScript, React, FastAPI, Docker, Microservices, PostgreSQL, Git, CI/CD\n\nEducation:\nB.Tech Computer Science – MIT, 2020"
  },
  marketing_manager: {
    jd: "Marketing Manager\n\nRequirements:\n- 5+ years digital and brand marketing management\n- Brand strategy and P&L management experience\n- Marketing analytics and multi-touch attribution\n- SEO/SEM campaign management\n- HubSpot or Salesforce CRM automation\n- CAC/LTV and ROAS optimization\n- Team leadership 5+ members",
    resume: "Alice Nguyen\nEmail: alice@example.com\n\nSummary:\nPerformance Marketing Specialist with 4 years leading digital acquisition and content strategy.\n\nExperience:\nSenior Marketing Lead – Horizon Media (2022–Present)\n• Managed $250K quarterly ad budgets with 4.2x ROAS\n• Led SEO/SEM campaigns generating 85K organic monthly visitors\n• Implemented HubSpot automation reducing lead response time by 65%\n\nSkills:\nSEO/SEM, Google Analytics, HubSpot, Social Media Marketing, Content Strategy, ROAS\n\nEducation:\nMBA Marketing – NYU Stern, 2021"
  },
  hr_specialist: {
    jd: "HR Specialist\n\nRequirements:\n- 3+ years in human resources operations\n- Full-cycle talent acquisition and recruitment\n- HR compliance knowledge (FLSA, EEOC, OSHA)\n- Employee relations and conflict resolution\n- HRIS experience with Workday or BambooHR\n- Onboarding program development\n- Performance management systems",
    resume: "Bob Brown\nEmail: bob@example.com\n\nSummary:\nHuman Resources Professional with 3.5 years managing recruitment cycles and employee relations.\n\nExperience:\nHR Coordinator & Generalist – Apex Global (2022–Present)\n• Streamlined hiring lifecycle reducing time-to-hire by 28%\n• Managed Workday HRIS for 400+ employees\n• Resolved 50+ employee relations cases with 95% satisfaction score\n\nSkills:\nTalent Acquisition, HR Compliance, Employee Relations, Workday, Onboarding, BambooHR\n\nEducation:\nBachelor of Business Administration – Ohio State, 2021"
  },
  devops: {
    jd: "Cloud DevOps Engineer\n\nRequirements:\n- 4+ years cloud infrastructure engineering\n- AWS (EC2, ECS, EKS, Lambda, RDS) expertise\n- Kubernetes container orchestration\n- Terraform Infrastructure as Code\n- Docker containerization\n- CI/CD automation (GitHub Actions, GitLab)\n- Cloud security and compliance\n- Linux systems administration",
    resume: "Carlos Mendez\nEmail: carlos@example.com\n\nSummary:\nCloud Infrastructure Engineer with 5 years automating high-availability distributed systems.\n\nExperience:\nDevOps Engineer – CloudScale Systems (2021–Present)\n• Maintained 99.99% uptime across 200+ AWS microservices\n• Migrated 40 monolith apps to Kubernetes EKS clusters\n• Built Terraform modules managing $2M cloud infrastructure\n\nSkills:\nAWS, Kubernetes, Terraform, Docker, CI/CD, Python, Linux, Bash, Prometheus, Grafana\n\nEducation:\nB.S. Computer Engineering – Georgia Tech, 2020"
  }
};

const COURSES = {
  "python": { title: "Python for Data Science & Applied Analytics", provider: "Coursera / IBM", url: "https://www.coursera.org/learn/python-for-applied-data-science-ai", category: "Data Science" },
  "sql": { title: "SQL Basics & Advanced Database Querying", provider: "Coursera / UC Davis", url: "https://www.coursera.org/learn/sql-for-data-science", category: "Databases" },
  "power bi": { title: "Microsoft Power BI Data Analyst Professional", provider: "Microsoft / Coursera", url: "https://www.coursera.org/professional-certificates/microsoft-power-bi-data-analyst", category: "BI" },
  "tableau": { title: "Tableau Business Intelligence & Data Visualization", provider: "Tableau Learning", url: "https://www.tableau.com/learn/training", category: "BI" },
  "machine learning": { title: "Machine Learning Specialization by Andrew Ng", provider: "DeepLearning.AI / Coursera", url: "https://www.coursera.org/specializations/machine-learning-introduction", category: "AI/ML" },
  "react": { title: "Meta Front-End Developer Professional Certificate", provider: "Meta / Coursera", url: "https://www.coursera.org/professional-certificates/meta-front-end-developer", category: "Frontend" },
  "fastapi": { title: "Building High-Performance APIs with FastAPI", provider: "TestDriven.io", url: "https://testdriven.io/courses/fastapi-celery/", category: "Backend" },
  "docker": { title: "Docker & Kubernetes: The Practical Guide", provider: "Udemy", url: "https://www.udemy.com/course/docker-kubernetes-the-practical-guide/", category: "DevOps" },
  "aws": { title: "AWS Certified Solutions Architect – Associate", provider: "Amazon Web Services", url: "https://aws.amazon.com/certification/certified-solutions-architect-associate/", category: "Cloud" },
  "kubernetes": { title: "Certified Kubernetes Administrator (CKA)", provider: "Linux Foundation", url: "https://www.cncf.io/certification/cka/", category: "DevOps" },
  "terraform": { title: "HashiCorp Certified: Terraform Associate", provider: "HashiCorp", url: "https://www.hashicorp.com/certification/terraform-associate", category: "IaC" },
  "ci/cd": { title: "Continuous Integration & Delivery with GitHub Actions", provider: "GitHub Learning", url: "https://github.com/readme/guides/sothebys-github-actions", category: "DevOps" },
  "seo": { title: "Google Digital Marketing & E-commerce Certificate", provider: "Google / Coursera", url: "https://www.coursera.org/professional-certificates/google-digital-marketing-ecommerce", category: "Marketing" },
  "brand strategy": { title: "Advanced Brand Strategy & P&L Management", provider: "Northwestern Kellogg", url: "https://www.coursera.org/learn/strategic-brand-management", category: "Marketing" },
  "hubspot": { title: "HubSpot Marketing Automation Certification", provider: "HubSpot Academy", url: "https://academy.hubspot.com/", category: "MarTech" },
  "hr compliance": { title: "Strategic Human Resources & Compliance", provider: "SHRM / Coursera", url: "https://www.coursera.org/specializations/human-resource-management", category: "HR" },
  "workday": { title: "Workday HCM Fundamentals", provider: "Workday Education", url: "https://www.workday.com/en-us/services/training.html", category: "HR Tech" },
  "people analytics": { title: "People Analytics by Wharton", provider: "University of Pennsylvania", url: "https://www.coursera.org/learn/wharton-people-analytics", category: "HR Analytics" },
  "algorithms": { title: "Algorithms & Data Structures (Princeton)", provider: "Princeton / Coursera", url: "https://www.coursera.org/learn/algorithms-part1", category: "CS Fundamentals" },
  "system design": { title: "Grokking the System Design Interview", provider: "Educative.io", url: "https://www.educative.io/courses/grokking-the-system-design-interview", category: "Architecture" }
};

const SKILL_KEYWORDS = [
  "python","javascript","typescript","react","angular","vue","node.js","nodejs",
  "fastapi","django","flask","java","spring boot","c++","c#",".net","golang","rust",
  "sql","postgresql","mysql","mongodb","redis","elasticsearch",
  "aws","azure","gcp","docker","kubernetes","terraform","ci/cd","git","linux","bash",
  "graphql","rest api","microservices","system design","algorithms","data structures",
  "machine learning","deep learning","nlp","pandas","numpy","scikit-learn",
  "power bi","tableau","data analysis","data modeling","data engineering","etl",
  "seo","sem","google analytics","hubspot","salesforce","marketing analytics",
  "brand strategy","content marketing","social media marketing","roas","cac",
  "talent acquisition","hr compliance","employee relations","workday","bamboohr",
  "people analytics","onboarding","performance management","compensation",
  "agile","scrum","jira","product management","stakeholder management"
];

function extractSkills(text) {
  const lower = text.toLowerCase();
  const found = new Set();
  for (const kw of SKILL_KEYWORDS) {
    if (new RegExp(`\\b${kw.replace(/[.+]/g,'\\$&')}\\b`).test(lower)) {
      found.add(kw);
    }
  }
  return found;
}

function estimateYears(text) {
  const explicit = text.match(/(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)(?:\s+of)?(?:\s+experience)?/i);
  if (explicit) return parseFloat(explicit[1]);
  const ranges = [...text.matchAll(/(?:19|20)\d{2}\s*(?:-|–|to)\s*(?:(?:19|20)\d{2}|present|current|now)/gi)];
  let total = 0;
  for (const r of ranges) {
    const years = r[0].match(/(?:19|20)\d{2}/g);
    if (years && years.length === 2) total += Math.max(0, parseInt(years[1]) - parseInt(years[0]));
    else if (years && years.length === 1) total += Math.max(0, 2026 - parseInt(years[0]));
  }
  return total || 2;
}

function extractRole(jd) {
  const patterns = [
    /(?:job title|position|role)\s*[:\-]\s*([^\n\r]+)/i,
    /^(?:#+\s*)?([A-Za-z\s]+?(?:Engineer|Developer|Manager|Specialist|Analyst|Lead|Architect|Designer|Coordinator))/m
  ];
  for (const p of patterns) {
    const m = jd.match(p);
    if (m && m[1].trim().length < 50) return m[1].trim();
  }
  return jd.split('\n')[0].slice(0, 40).trim() || 'Target Role';
}

function extractCandidateName(resume) {
  const lines = resume.split('\n').map(l => l.trim()).filter(Boolean);
  for (const line of lines.slice(0, 3)) {
    const words = line.split(' ');
    if (words.length >= 2 && words.length <= 3 && !line.toLowerCase().includes('@')) return line;
  }
  return 'Candidate';
}

function getCourses(missingSkills, role) {
  const recs = [];
  const matched = new Set();
  for (const skill of missingSkills) {
    for (const [key, course] of Object.entries(COURSES)) {
      if ((skill.includes(key) || key.includes(skill)) && !matched.has(key)) {
        recs.push(course);
        matched.add(key);
        if (recs.length >= 3) return recs;
      }
    }
  }
  // Fallback by role
  const rl = role.toLowerCase();
  const fallbacks = rl.includes('data') || rl.includes('analyst') ? ['sql','power bi','machine learning'] :
    rl.includes('developer') || rl.includes('engineer') ? ['algorithms','system design','docker'] :
    rl.includes('marketing') ? ['seo','brand strategy','hubspot'] :
    rl.includes('hr') ? ['hr compliance','workday','people analytics'] :
    rl.includes('devops') || rl.includes('cloud') ? ['aws','kubernetes','terraform'] :
    ['algorithms','system design','docker'];
  for (const k of fallbacks) {
    if (!matched.has(k) && COURSES[k]) { recs.push(COURSES[k]); matched.add(k); }
    if (recs.length >= 3) break;
  }
  return recs;
}

window.analyzeATS = function(jdText, resumeText) {
  const jdSkills = extractSkills(jdText);
  const resumeSkills = extractSkills(resumeText);
  const matched = new Set([...jdSkills].filter(s => resumeSkills.has(s)));
  const missing = new Set([...jdSkills].filter(s => !resumeSkills.has(s)));

  const jdExp = estimateYears(jdText) || 3;
  const resExp = estimateYears(resumeText) || 2;
  const role = extractRole(jdText);
  const candidate = extractCandidateName(resumeText);

  // Skills score
  const skillsPct = jdSkills.size > 0
    ? Math.min(98, Math.max(30, Math.round((matched.size / jdSkills.size) * 100)))
    : 75;

  // Experience score
  let expRatio = resExp / Math.max(1, jdExp);
  let expPct = expRatio >= 1 ? Math.min(96, Math.round(85 + (Math.min(expRatio, 2) - 1) * 10))
    : Math.max(35, Math.round(expRatio * 82));
  const jdSenior = /senior|lead|principal|manager|director/i.test(jdText);
  const resSenior = /senior|lead|principal|manager|director/i.test(resumeText);
  if (jdSenior && !resSenior) expPct = Math.max(30, expPct - 12);
  else if (!jdSenior && resSenior) expPct = Math.min(95, expPct + 5);

  const atsScore = Math.max(10, Math.min(99, Math.round(skillsPct * 0.6 + expPct * 0.3 + Math.min(100, (skillsPct + expPct) / 2) * 0.1)));
  const courses = getCourses([...missing], role);
  const coursesStr = courses.map(c => c.title).join(', ') || 'Advanced Professional Certifications';

  const matchedArr = [...matched].map(s => s.charAt(0).toUpperCase() + s.slice(1));
  const missingArr = [...missing].map(s => s.charAt(0).toUpperCase() + s.slice(1));

  const strengths = matchedArr.length > 0
    ? `Solid proficiency in ${matchedArr.slice(0,4).join(', ')} with hands-on project experience`
    : 'Strong domain background and professional experience';
  const improvementAreas = missingArr.length > 0
    ? `Address skill gaps in ${missingArr.slice(0,3).join(', ')}, add quantitative impact metrics`
    : 'Emphasize leadership achievements, certifications, and quantitative KPI impact';

  const formattedOutput = `ATS Score: ${atsScore}%, Breakdown: [Skills match: ${skillsPct}%, Experience match: ${expPct}%]. Suggested Courses: ${coursesStr}. Overall Analytics: [Strengths: ${strengths}. Improvement Areas: ${improvementAreas}].`;

  return {
    role, candidate, atsScore, skillsPct, expPct,
    matched: matchedArr, missing: missingArr,
    courses, formattedOutput, strengths, improvementAreas,
    jdExp, resExp,
    thinkAloud: {
      role: `Evaluated candidate qualifications against the position of ${role}. Requirements indicate ~${jdExp.toFixed(1)} years of relevant industry experience.`,
      skills: `${skillsPct}% skills alignment detected. Matched: ${matchedArr.slice(0,4).join(', ') || 'General domain skills'}. ${missingArr.length > 0 ? `Gaps in: ${missingArr.slice(0,3).join(', ')}.` : 'No critical skill gaps detected.'}`,
      experience: `Candidate demonstrates ~${resExp.toFixed(1)} years of experience vs. the required ${jdExp.toFixed(1)} years — yielding a ${expPct}% experience alignment score.`,
      improve: `Highlight quantifiable project outcomes (ROI, latency, revenue impact). Pursue certifications in gap areas. ${jdSenior && !resSenior ? 'Apply for senior-level positioning by demonstrating cross-functional leadership.' : ''}`
    }
  };
};
