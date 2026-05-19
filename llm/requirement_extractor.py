"""
Intelligent JD requirement extraction.
Handles various JD formats and extracts structured requirements.
"""

import re
import json
from anthropic import Anthropic

client = Anthropic()

# Cap inputs so Haiku output stays well within max_tokens
_RESUME_MAX_CHARS = 4000
_JD_MAX_CHARS     = 3000


def _parse_json(text: str) -> dict:
    """Robustly extract a JSON object from LLM output."""
    text = text.strip()
    fence = re.search(r'```(?:json)?\s*([\s\S]*?)```', text)
    if fence:
        text = fence.group(1).strip()
    elif not text.startswith('{'):
        obj = re.search(r'\{[\s\S]*\}', text)
        if obj:
            text = obj.group(0)
    return json.loads(text)


def extract_requirements(jd_text: str) -> dict:
    """Extract structured requirements from any JD format."""
    prompt = f"""Extract requirements from this job description. Return ONLY raw JSON, no prose.

JD:
{jd_text[:_JD_MAX_CHARS]}

JSON schema (use exactly these keys, keep arrays short):
{{
    "job_title": "title",
    "required_skills": ["up to 8 core differentiating skills only"],
    "nice_to_have_skills": ["skill1"],
    "required_experience_years": 0,
    "required_education": ["bsn"],
    "required_certifications": ["rn license", "bls", "acls"],
    "required_attributes": ["attribute1"],
    "role_level": "entry|mid|senior|lead",
    "key_responsibilities": ["resp1", "resp2"],
    "must_haves": ["req1"],
    "nice_to_haves": ["req1"],
    "industry_domain": "healthcare",
    "specialized_knowledge": ["knowledge1"]
}}

Rules:
- required_certifications: short canonical names only (e.g. "rn license", "bls") no license numbers or states
- required_skills: 4-8 clinical differentiators only, NOT generic tasks every RN does; include unit specialty (sdu, icu, l&d)"""

    try:
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        return _parse_json(message.content[0].text)
    except Exception as e:
        raise RuntimeError(f"JD extraction failed: {e}")


def extract_candidate_profile(resume_text: str) -> dict:
    """Extract candidate profile from resume — only fields used in scoring."""
    prompt = f"""Extract candidate info from this resume. Return ONLY raw JSON, no prose, keep values concise.

RESUME:
{resume_text[:_RESUME_MAX_CHARS]}

JSON schema (use exactly these keys):
{{
    "name": "Full Name",
    "job_title": "most recent title",
    "years_relevant_experience": 0,
    "current_role_level": "entry|mid|senior|lead",
    "core_competencies": ["comp1", "comp2"],
    "technical_skills": ["sdu", "icu", "epic"],
    "soft_skills": ["communication"],
    "certifications_licenses": ["rn license", "bls", "acls"],
    "education_degrees": ["bsn"],
    "education_fields": ["nursing"],
    "work_history": [
        {{"title": "RN", "company": "Hospital", "duration_years": 2, "keywords": ["sdu", "telemetry"]}}
    ],
    "industries_experience": ["healthcare"],
    "career_trajectory": "up|stable|lateral|down"
}}

Rules:
- certifications_licenses: short canonical names ONLY (e.g. "rn license", "bls") no numbers, dates, states, or issuers
- technical_skills: include unit specialties worked (sdu, icu, telemetry, med-surg) and EMR systems
- work_history: max 4 entries, keywords array max 5 items, no achievements field
- education_fields: simple names like "nursing" not full degree titles"""

    try:
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}],
        )
        return _parse_json(message.content[0].text)
    except Exception as e:
        raise RuntimeError(f"Resume extraction failed: {e}")
