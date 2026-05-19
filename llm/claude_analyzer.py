import os
import json
from anthropic import Anthropic

client = Anthropic()


def extract_with_llm(document_text: str, document_type: str = "resume") -> dict:
    """
    Use Claude to intelligently extract entities from resume or JD
    document_type: "resume" or "jd"
    """
    cert_instruction = """CRITICAL for certifications:
- Extract ALL certifications mentioned: BLS, ACLS, NRP, AWHONN, RN license, BSN, etc.
- Include the full form (e.g., "BLS-AHA", "Advanced Fetal Monitoring")
- Include certification names with acronyms and full descriptions
- Include license types (RN, LPN, etc.)
- Extract from sections like "LICENSE AND CERTIFICATION", "CERTIFICATIONS", "CREDENTIALS"
"""

    prompt = f"""Analyze this {document_type} and extract key information in JSON format.

{document_type.upper()}:
{document_text}

{cert_instruction}

Return ONLY valid JSON (no markdown, no extra text) with this exact structure:
{{
    "skills": ["skill1", "skill2", ...],
    "certifications": ["cert1", "cert2", ...],
    "years_experience": <number>,
    "education_degrees": ["degree1", "degree2", ...],
    "education_fields": ["field1", "field2", ...],
    "specialties": ["specialty1", "specialty2", ...],
    "key_accomplishments": ["achievement1", "achievement2", ...]
}}

Extract ALL skills and certifications mentioned, even if not explicitly listed.
For years of experience, estimate from work history if not stated."""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    try:
        response_text = message.content[0].text.strip()
        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()

        extracted = json.loads(response_text)
        return extracted
    except json.JSONDecodeError:
        return {
            "skills": [],
            "certifications": [],
            "years_experience": 0,
            "education_degrees": [],
            "education_fields": [],
            "specialties": [],
            "key_accomplishments": [],
        }


def generate_detailed_analysis(
    resume_data: dict, jd_data: dict, initial_score: float
) -> dict:
    """
    Use Claude to generate nuanced analysis and scoring explanation
    """
    prompt = f"""You are an expert recruiter. Analyze this job match:

RESUME HIGHLIGHTS:
- Skills: {', '.join(resume_data.get('skills', [])[:10])}
- Certifications: {', '.join(resume_data.get('certifications', []))}
- Years Experience: {resume_data.get('years_experience', 0)}
- Education: {', '.join(resume_data.get('education_degrees', []))}
- Specialties: {', '.join(resume_data.get('specialties', [])[:5])}

JOB REQUIREMENTS:
- Required Skills: {', '.join(jd_data.get('skills', [])[:10])}
- Required Certifications: {', '.join(jd_data.get('certifications', []))}
- Experience Required: {jd_data.get('years_experience', 0)} years
- Education: {', '.join(jd_data.get('education_fields', []))}
- Specialties: {', '.join(jd_data.get('specialties', [])[:5])}

Current automated score: {initial_score}%

Provide analysis in JSON format:
{{
    "fit_assessment": "one paragraph assessment",
    "strengths": ["strength1", "strength2", ...],
    "weaknesses": ["gap1", "gap2", ...],
    "quick_wins": ["improvement1", "improvement2", ...],
    "overall_assessment": "Excellent/Good/Moderate/Poor fit",
    "hiring_recommendation": "Strong Yes/Yes/Maybe/No"
}}"""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    try:
        response_text = message.content[0].text.strip()
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()

        analysis = json.loads(response_text)
        return analysis
    except json.JSONDecodeError:
        return {
            "fit_assessment": "Analysis unavailable",
            "strengths": [],
            "weaknesses": [],
            "quick_wins": [],
            "overall_assessment": "Unable to determine",
            "hiring_recommendation": "Manual review recommended",
        }


def is_llm_enabled() -> bool:
    """Check if Claude API key is available"""
    return bool(os.environ.get("ANTHROPIC_API_KEY"))
