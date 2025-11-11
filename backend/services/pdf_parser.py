import re
import fitz
from io import BytesIO

def parse_pdf(file):
    """Parse any resume PDF into structured data using regex + fallback on raw text."""

    pdf_data = BytesIO(file.file.read())
    doc = fitz.open(stream=pdf_data, filetype="pdf")
    text = "\n".join(page.get_text("text") for page in doc)
    text = re.sub(r"\s+", " ", text).strip()

    result = {
        "personal_info": {},
        "skills": {},
        "education": [],
        "projects": [],
        "achievements": [],
        "certifications": [],
        "extras": {},
        "raw_text": text
    }

    # -------- Personal Info (robust regex) --------
    result["personal_info"]["phone"] = (
        re.search(r"(\+91[-\s]?[0-9]{10}|\b[6-9][0-9]{9}\b)", text)
        or re.search(r"\b\d{3}[-\s]?\d{3}[-\s]?\d{4}\b", text)
    )
    if result["personal_info"]["phone"]:
        result["personal_info"]["phone"] = result["personal_info"]["phone"].group(1)

    email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}", text)
    if email_match:
        result["personal_info"]["email"] = email_match.group(0)

    linkedin = re.search(r"(https?:\/\/(www\.)?linkedin\.com\/[^\s)]+)", text)
    if linkedin:
        result["personal_info"]["linkedin"] = linkedin.group(1)

    github = re.search(r"(https?:\/\/(www\.)?github\.com\/[^\s)]+)", text)
    if github:
        result["personal_info"]["github"] = github.group(1)

    # Try to get name (first bold/upper word line or first line before phone/email)
    name_match = re.search(r"([A-Z][a-z]+(?:\s[A-Z][a-z]+){0,2})", text[:120])
    if name_match:
        result["personal_info"]["name"] = name_match.group(1)

    # -------- Education --------
    edu_pattern = re.findall(
        r"(Bachelor|B\.?Tech|BTech|Higher Secondary|High School|Diploma|Intermediate)[^:]*?(?:(CGPA|GPA|Percentage)[:\s]*\d+(\.\d+)?|[A-Za-z]+\s\d{4}\s*[-–]\s*[A-Za-z]+\s\d{4})?",
        text,
        flags=re.I,
    )
    for match in edu_pattern:
        degree = match[0].strip()
        score_type = match[1] or ""
        result["education"].append(
            {"degree": degree, "score_type": score_type}
        )

    # -------- Skills (all variants) --------
    skill_sections = re.findall(
        r"(Programming Languages|Languages|Frameworks|Web Frameworks|Databases|Tools|Technologies|Soft Skills)[:\s]+([^A-Z\n]+)",
        text,
        flags=re.I,
    )
    for key, val in skill_sections:
        clean_key = key.lower().replace(" ", "_")
        result["skills"][clean_key] = val.strip(" ,.-")

    # Fallback: from generic words
    if not result["skills"]:
        lines = re.findall(r"(C\+\+|Python|Java|HTML|CSS|React|Flask|FastAPI|Node|SQL)", text, re.I)
        if lines:
            result["skills"]["keywords"] = list(set(lines))

    # -------- Projects --------
    project_blocks = re.findall(
        r"([A-Z][A-Za-z0-9\s\-]+)\s[-–:]\s*([^A-Z]+?)(?=[A-Z][A-Za-z\s\-]+[-–:]|$)",
        text + " END",
        flags=re.S,
    )
    for title, desc in project_blocks:
        if len(title.split()) < 10:  # skip long text falsely caught
            result["projects"].append(
                {"title": title.strip(), "description": desc.strip()}
            )

    # -------- Achievements / Certifications --------
    ach_text = re.findall(
        r"(NCC|Hackathon|Certificate|Award|Challenge|Contest)[^.!?]+", text, re.I
    )
    result["achievements"] = list(set(ach_text))

    cert_text = re.findall(
        r"(issued by|Certified|Certificate|Internship)[^.!?]+", text, re.I
    )
    result["certifications"] = list(set(cert_text))

    # -------- Extras fallback (all key:value lines) --------
    for line in text.split(". "):
        if ":" in line:
            k, v = line.split(":", 1)
            result["extras"][k.strip()] = v.strip()

    return result
