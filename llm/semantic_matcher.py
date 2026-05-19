"""
Semantic matching for skills, roles, and requirements.
Uses Claude to understand context and find equivalent skills.
"""

import re
import json
from anthropic import Anthropic

client = Anthropic()


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


def detect_domain(resume_text: str, jd_text: str) -> str:
    """
    Detect the job domain/industry.
    Returns: 'healthcare', 'tech', 'finance', 'sales', 'general', etc.
    """
    prompt = f"""Analyze these two documents and identify the job domain/industry.

RESUME:
{resume_text[:500]}

JOB DESCRIPTION:
{jd_text[:500]}

Return ONLY the domain name (one word). Examples: healthcare, software, finance, sales, operations, marketing, legal, construction, manufacturing, education, hospitality"""

    try:
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=50,
            messages=[{"role": "user", "content": prompt}],
        )
        domain = message.content[0].text.strip().lower().split()[0]
        return domain
    except:
        return "general"


def find_equivalent_skills(candidate_skills: list, required_skills: list) -> dict:
    """
    Find equivalent or transferable skills using semantic understanding.
    """
    if not required_skills:
        return {
            "exact_matches": candidate_skills,
            "equivalent_matches": [],
            "transferable_skills": [],
            "missing_skills": [],
        }

    prompt = f"""Analyze the match between candidate skills and required skills.

CANDIDATE HAS:
{', '.join(candidate_skills[:20])}

JOB REQUIRES:
{', '.join(required_skills[:20])}

Return ONLY a raw JSON object with no markdown, no prose:
{{
    "exact_matches": ["skill1", "skill2"],
    "equivalent_matches": ["skill that equals required skill"],
    "transferable_skills": ["skill that can be applied"],
    "missing_critical": ["skill1", "skill2"],
    "missing_nice_to_have": ["skill1", "skill2"],
    "analysis": "One sentence on how skills align"
}}

Be generous with equivalent and transferable matches."""

    try:
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}],
        )
        return _parse_json(message.content[0].text)
    except Exception as e:
        return {
            "exact_matches": [],
            "equivalent_matches": [],
            "transferable_skills": [],
            "missing_critical": required_skills,
            "missing_nice_to_have": [],
            "analysis": f"Skill analysis unavailable: {e}",
        }


def analyze_experience_relevance(
    resume_experience: dict, jd_requirements: dict, domain: str
) -> dict:
    """
    Intelligently analyze if candidate's experience matches role requirements.
    """
    prompt = f"""Analyze if candidate's experience fits this role.

CANDIDATE EXPERIENCE:
- Years: {resume_experience.get('years', 0)}
- Positions: {', '.join(resume_experience.get('positions', [])[:5])}
- Companies: {', '.join(resume_experience.get('companies', [])[:5])}

JOB REQUIREMENTS:
- Years needed: {jd_requirements.get('years', 0)}
- Domain: {domain}
- Role level: {jd_requirements.get('level', 'mid-level')}

Return ONLY a raw JSON object with no markdown, no prose:
{{
    "experience_match_score": 0,
    "years_assessment": "text",
    "progression_fit": "text",
    "domain_knowledge": "text",
    "concern_areas": ["concern1"],
    "strengths": ["strength1"],
    "role_readiness": "Yes/Maybe/No",
    "recommendation": "text"
}}"""

    try:
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}],
        )
        return _parse_json(message.content[0].text)
    except Exception as e:
        return {
            "experience_match_score": 50,
            "years_assessment": "Unable to assess",
            "progression_fit": "Unknown",
            "domain_knowledge": "Unknown",
            "concern_areas": [],
            "strengths": [],
            "role_readiness": "Maybe",
            "recommendation": f"Manual review recommended: {e}",
        }


def generate_smart_analysis(
    resume_text: str, jd_text: str, initial_score: float
) -> dict:
    """
    Generate concise, bullet-point recruiter analysis using Claude.
    """
    prompt = f"""You are an expert healthcare recruiter. Analyze candidate fit concisely.

RESUME (excerpt):
{resume_text[:800]}

JOB DESCRIPTION (excerpt):
{jd_text[:800]}

Return ONLY a raw JSON object with no markdown, no prose. All list items must be SHORT bullet points (under 12 words each).
{{
    "overall_fit": "Strong Yes / Yes / Maybe / No",
    "confidence": "High / Medium / Low",
    "strengths": ["short bullet1", "short bullet2", "short bullet3"],
    "gaps": ["short gap1", "short gap2"],
    "recent_domain_experience": "One sentence on how recent their relevant experience is",
    "career_fit": "Yes / Lateral / No",
    "risk_flags": ["flag1"]
}}

Rules:
- strengths and gaps: 3-5 bullets, each under 12 words, be specific (e.g. "7 yrs L&D travel experience" not paragraphs)
- gaps: only real gaps; use empty list if none
- risk_flags: license expiry, employment gaps, location mismatch, etc. Empty list if clean
- recent_domain_experience: one short sentence about how recent and directly relevant the most recent role is"""

    try:
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}],
        )
        return _parse_json(message.content[0].text)
    except Exception as e:
        return {
            "overall_fit": "Manual review",
            "confidence": "Low",
            "strengths": [],
            "gaps": [],
            "recent_domain_experience": "Unable to assess",
            "career_fit": "Unknown",
            "risk_flags": [f"Analysis error: {e}"],
        }
