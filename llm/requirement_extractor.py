"""
Intelligent JD requirement extraction.
Handles various JD formats and extracts structured requirements.
"""

import re
import json
from anthropic import Anthropic

client = Anthropic()


def _parse_json(text: str) -> dict:
    """
    Robustly extract a JSON object from LLM output.
    Handles markdown fences, leading/trailing prose, and extra backticks.
    """
    text = text.strip()

    # Strip markdown code fences (``` or ```json)
    fence = re.search(r'```(?:json)?\s*([\s\S]*?)```', text)
    if fence:
        text = fence.group(1).strip()
    elif not text.startswith('{'):
        # Find the first { ... } block in case there is prose before/after
        obj = re.search(r'\{[\s\S]*\}', text)
        if obj:
            text = obj.group(0)

    return json.loads(text)


def extract_requirements(jd_text: str) -> dict:
    """
    Extract structured requirements from any JD format.
    Handles bullet points, paragraphs, tables, etc.
    """
    prompt = f"""Extract structured requirements from this job description.
Handle ANY format - bullet points, paragraphs, tables, etc.

JD TEXT:
{jd_text}

Return ONLY a raw JSON object with no markdown, no prose, no explanation:
{{
    "job_title": "exact title",
    "required_skills": ["skill1", "skill2"],
    "nice_to_have_skills": ["skill1", "skill2"],
    "required_experience_years": 0,
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

IMPORTANT FORMATTING RULES:
- required_certifications: canonical short names only (e.g., "rn license", "bls", "acls") - no license numbers or state info
- required_skills: ONLY the 4-8 core clinical skills that truly differentiate candidates. Do NOT list generic nursing tasks every RN has. Include the unit specialty (e.g., "labor and delivery", "sdu", "icu") and key clinical competencies.
- If profession/specialty is stated (RN, SDU, ICU, L&D) add the specialty as a required skill"""

    try:
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}],
        )
        return _parse_json(message.content[0].text)
    except Exception as e:
        raise RuntimeError(f"JD extraction failed: {e}")


def extract_candidate_profile(resume_text: str) -> dict:
    """
    Extract comprehensive candidate profile from resume.
    Works with ANY resume format.
    """
    prompt = f"""Extract a comprehensive candidate profile from this resume.
Handle ANY format - chronological, functional, combination, etc.

RESUME TEXT:
{resume_text}

Return ONLY a raw JSON object with no markdown, no prose, no explanation:
{{
    "name": "name if present",
    "job_title": "current or most recent title",
    "summary": "professional summary (2-3 sentences)",
    "years_total_experience": 0,
    "years_relevant_experience": 0,
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
            "duration_years": 0,
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
- certifications_licenses: canonical short names ONLY (e.g., "rn license", "bls", "acls", "ccrn") - no license numbers, expiry dates, state names, or issuer names
- technical_skills: include clinical unit specialties actually worked (e.g., "sdu", "icu", "telemetry", "med-surg") AND EMR systems
- education_fields: use simple field names like "nursing", "nursing science" (not full degree names)"""

    try:
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )
        return _parse_json(message.content[0].text)
    except Exception as e:
        raise RuntimeError(f"Resume extraction failed: {e}")
