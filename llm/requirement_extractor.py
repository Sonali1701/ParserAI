"""
Intelligent JD requirement extraction.
Handles various JD formats and extracts structured requirements.
"""

from anthropic import Anthropic

client = Anthropic()


def extract_requirements(jd_text: str) -> dict:
    """
    Extract structured requirements from any JD format.
    Handles bullet points, paragraphs, or unstructured text.
    """
    prompt = f"""Extract structured requirements from this job description.
Handle ANY format - bullet points, paragraphs, tables, etc.

JD TEXT:
{jd_text}

Return ONLY JSON (no markdown):
{{
    "job_title": "exact title",
    "required_skills": ["skill1", "skill2"],
    "nice_to_have_skills": ["skill1", "skill2"],
    "required_experience_years": <number>,
    "required_education": ["degree1", "degree2"],
    "required_certifications": ["cert1", "cert2"],
    "required_attributes": ["attribute1", "attribute2"],
    "role_level": "entry/mid/senior/lead",
    "key_responsibilities": ["resp1", "resp2", "resp3"],
    "must_haves": ["requirement1"],
    "nice_to_haves": ["requirement1"],
    "industry_domain": "detected domain",
    "specialized_knowledge": ["knowledge1"]
}}

Be comprehensive. Extract ALL mentioned requirements.
Distinguish between required (must-have) and nice-to-have.
Be generous in identifying skills and attributes.

IMPORTANT FORMATTING RULES:
- required_certifications: canonical short names matching what a candidate would list (e.g., "rn license", "bls", "acls") - no license numbers or state info
- required_skills: ONLY the 4-8 core clinical skills that truly differentiate candidates (e.g., specialty unit type, key procedures). Do NOT list generic nursing tasks (medication administration, IV therapy, patient care) that every RN has. Include the unit specialty (e.g., "labor and delivery", "l&d", "sdu") and key clinical competencies specific to this role.
- If profession/specialty is stated (RN, SDU, ICU, L&D) add the specialty as a required skill"""

    try:
        message = client.messages.create(
            model="claude-opus-4-1",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}],
        )

        import json

        text = message.content[0].text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.strip().rstrip("`")

        return json.loads(text)
    except Exception as e:
        return {
            "job_title": "Unknown",
            "required_skills": [],
            "nice_to_have_skills": [],
            "required_experience_years": 0,
            "required_education": [],
            "required_certifications": [],
            "required_attributes": [],
            "role_level": "unknown",
            "key_responsibilities": [],
            "must_haves": [],
            "nice_to_haves": [],
            "industry_domain": "general",
            "specialized_knowledge": [],
        }


def extract_candidate_profile(resume_text: str) -> dict:
    """
    Extract comprehensive candidate profile from resume.
    Works with ANY resume format.
    """
    prompt = f"""Extract a comprehensive candidate profile from this resume.
Handle ANY format - chronological, functional, combination, etc.

RESUME TEXT:
{resume_text}

Return ONLY JSON (no markdown):
{{
    "name": "name if present",
    "job_title": "current or most recent title",
    "summary": "professional summary (2-3 sentences)",
    "years_total_experience": <number>,
    "years_relevant_experience": <number>,
    "current_role_level": "entry/mid/senior/lead",
    "core_competencies": ["competency1", "competency2"],
    "technical_skills": ["skill1", "skill2"],
    "soft_skills": ["skill1", "skill2"],
    "certifications_licenses": ["rn license", "bls", "acls"],
    "education_degrees": ["bsn", "bachelor"],
    "education_fields": ["nursing", "nursing science"],
    "work_history": [
        {{
            "title": "job title",
            "company": "company",
            "duration_years": <number>,
            "achievements": ["achievement1"],
            "keywords": ["keyword1"]
        }}
    ],
    "industries_experience": ["industry1", "industry2"],
    "career_progression": "description",
    "unique_strengths": ["strength1", "strength2"],
    "potential_gaps": ["gap1", "gap2"],
    "career_trajectory": "up/stable/lateral/down"
}}

Be thorough. Extract ALL skills, certifications, and achievements.
Infer experience years from dates if not stated.
Identify career progression patterns.

IMPORTANT FORMATTING RULES:
- certifications_licenses: canonical short names ONLY (e.g., "rn license", "bls", "acls", "ccrn", "fire card") - no license numbers, expiry dates, state names, or issuer names
- technical_skills: include clinical unit specialties actually worked (e.g., "sdu", "icu", "telemetry", "med-surg") AND EMR systems
- education_fields: use simple field names like "nursing", "nursing science" (not full degree names)"""

    try:
        message = client.messages.create(
            model="claude-opus-4-1",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )

        import json

        text = message.content[0].text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.strip().rstrip("`")

        return json.loads(text)
    except Exception as e:
        return {
            "name": "Unknown",
            "job_title": "Unknown",
            "summary": "",
            "years_total_experience": 0,
            "years_relevant_experience": 0,
            "current_role_level": "unknown",
            "core_competencies": [],
            "technical_skills": [],
            "soft_skills": [],
            "certifications_licenses": [],
            "education_degrees": [],
            "education_fields": [],
            "work_history": [],
            "industries_experience": [],
            "career_progression": "Unknown",
            "unique_strengths": [],
            "potential_gaps": [],
            "career_trajectory": "unknown",
        }
