import re

def extract_personal_info(text: str):
    """Extracts name, email, phone, and links (LinkedIn, GitHub, etc.)."""
    # Email and phone regex
    email = re.search(r'[\w\.-]+@[\w\.-]+', text)
    phone = re.search(r'(\+?\d{1,3}[\s-]?)?\d{10}', text)

    # URL detection
    urls = re.findall(r'(https?://[^\s]+|www\.[^\s]+|linkedin\.com/[^\s]+|github\.com/[^\s]+)', text)
    links = list(set(urls))

    # LinkedIn and GitHub separation
    linkedin = [u for u in links if "linkedin" in u.lower()]
    github = [u for u in links if "github" in u.lower()]
    portfolio = [u for u in links if not any(x in u.lower() for x in ["linkedin", "github"])]

    # Heuristic name extraction (first line, before email or phone)
    lines = text.split("\n")
    probable_name = None
    for line in lines[:5]:  # Only top 5 lines of resume
        if not re.search(r'\d|@|www|linkedin|github', line) and 2 <= len(line.strip().split()) <= 4:
            probable_name = line.strip()
            break

    return {
        "name": probable_name,
        "email": email.group(0) if email else None,
        "phone": phone.group(0) if phone else None,
        "linkedin": linkedin[0] if linkedin else None,
        "github": github[0] if github else None,
        "portfolio": portfolio[0] if portfolio else None,
    }


def extract_skills(text: str):
    """Find common skill sections."""
    skills_section = re.search(r'(skills|technologies|proficiencies|technical skills)[:\n\r]+(.*?)\n\n', text, re.IGNORECASE | re.DOTALL)
    if skills_section:
        skills = skills_section.group(2)
        return [s.strip() for s in re.split(r'[,\n]', skills) if s.strip()]
    return []


def extract_education(text: str):
    """Extract education details."""
    edu_matches = re.findall(
        r'(?i)(b\.?tech|bachelor|master|b\.?e|m\.?tech|12th|10th|high school|secondary|university|college).*?(?:\n|$)',
        text)
    return list(set([e.strip() for e in edu_matches]))


def extract_projects(text: str):
    """Extract project titles and brief context."""
    project_blocks = re.findall(r'(?i)([A-Z][A-Za-z0-9\s\-\:]+)\n(?:Technologies|Tech|Description)?:?\s*(.*?)\n\n', text)
    projects = []
    for title, desc in project_blocks:
        projects.append({"title": title.strip(), "description": desc.strip()})
    return projects
