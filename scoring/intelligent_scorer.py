"""
Intelligent, domain-aware scoring system.
Adapts weights and matching logic based on job domain.
"""

import re
from typing import Dict, Tuple


def _normalize_cert(cert: str) -> str:
    """Strip license numbers, expiry dates, state names, and issuer names."""
    c = cert.lower().strip()
    c = re.sub(r'#[\w\d]+', '', c)                          # license numbers
    c = re.sub(r'\b\d{1,2}/\d{4}\b', '', c)                # MM/YYYY dates
    c = re.sub(r'expir\w*\s*:?\s*[\d/]*', '', c)           # expiry ...
    c = re.sub(r'\bcurrent\b', '', c)
    for issuer in ['american heart association', 'american red cross',
                   'los angeles fire department', r'\baha\b', r'\barc\b', r'\blafd\b']:
        c = re.sub(issuer, '', c)
    for state in ['california', 'texas', 'new york', 'florida', 'alaska',
                  'ohio', 'illinois', 'washington']:
        c = c.replace(state, '')
    c = re.sub(r'[–—]', ' ', c)
    c = re.sub(r'\(.*?\)', '', c)
    c = ' '.join(c.split())
    return c


# Healthcare certifications that are accepted equivalents of each other
CERT_EQUIVALENTS = {
    "awhonn fetal monitoring": ["advanced fetal monitoring", "fetal monitoring", "efm", "electronic fetal monitoring"],
    "advanced fetal monitoring": ["awhonn fetal monitoring", "fetal monitoring", "efm"],
    "nrp": ["neonatal resuscitation program", "neonatal resuscitation"],
    "neonatal resuscitation program": ["nrp", "neonatal resuscitation"],
    "bls": ["basic life support"],
    "acls": ["advanced cardiovascular life support", "advanced cardiac life support"],
}


def _cert_matches(candidate_norm: str, required_norm: str) -> bool:
    """True if tokens match, substring matches, or certs are known equivalents."""
    if not required_norm:
        return False
    if required_norm in candidate_norm or candidate_norm in required_norm:
        return True
    req_tokens = set(required_norm.split())
    cand_tokens = set(candidate_norm.split())
    if req_tokens.issubset(cand_tokens):
        return True
    # Check known equivalents
    for equiv in CERT_EQUIVALENTS.get(required_norm, []):
        if equiv in candidate_norm or candidate_norm in equiv:
            return True
    return False


def _skill_matches(candidate_skill: str, required_skill: str) -> bool:
    """True if either skill string is contained in the other."""
    return required_skill in candidate_skill or candidate_skill in required_skill


def _field_matches(candidate_field: str, required_field: str) -> bool:
    """True if either field string is contained in the other."""
    return required_field in candidate_field or candidate_field in required_field


# Domain-specific scoring weights
DOMAIN_WEIGHTS = {
    "healthcare": {"skills": 0.30, "experience": 0.25, "education": 0.15, "certifications": 0.30},
    "tech": {"skills": 0.45, "experience": 0.30, "education": 0.15, "certifications": 0.10},
    "finance": {"skills": 0.35, "experience": 0.30, "education": 0.20, "certifications": 0.15},
    "sales": {"skills": 0.25, "experience": 0.40, "education": 0.10, "certifications": 0.05, "traits": 0.20},
    "legal": {"skills": 0.30, "experience": 0.35, "education": 0.20, "certifications": 0.15},
    "general": {"skills": 0.40, "experience": 0.30, "education": 0.15, "certifications": 0.15},
}


def get_domain_weights(domain: str = "general") -> dict:
    """Get scoring weights for specific domain"""
    return DOMAIN_WEIGHTS.get(domain.lower(), DOMAIN_WEIGHTS["general"])


def calculate_semantic_match(
    candidate_data: dict, jd_data: dict, domain: str = "general", skill_analysis: dict = None
) -> dict:
    """
    Calculate match using semantic understanding, not just keywords.
    When skill_analysis (from find_equivalent_skills) is provided it is used for the skill
    score so the algorithmic number stays consistent with the LLM narrative.
    """

    weights = get_domain_weights(domain)

    # Skill matching — prefer semantic analysis over crude substring matching
    if skill_analysis:
        skill_match = _calculate_skill_match_from_analysis(
            skill_analysis, jd_data.get("required_skills", [])
        )
    else:
        skill_match = _calculate_skill_match(candidate_data, jd_data)

    # Experience matching
    experience_match = _calculate_experience_match(candidate_data, jd_data, domain)

    # Education matching
    education_match = _calculate_education_match(candidate_data, jd_data)

    # Certification matching
    cert_match = _calculate_cert_match(candidate_data, jd_data)

    # Weighted overall score
    overall = (
        skill_match["score"] * weights.get("skills", 0.40)
        + experience_match["score"] * weights.get("experience", 0.30)
        + education_match["score"] * weights.get("education", 0.15)
        + cert_match["score"] * weights.get("certifications", 0.15)
    )

    return {
        "overall_score": round(overall, 2),
        "skill_match": skill_match,
        "experience_match": experience_match,
        "education_match": education_match,
        "certification_match": cert_match,
        "domain": domain,
        "weights": weights,
    }


def _calculate_skill_match_from_analysis(skill_analysis: dict, required_skills: list) -> dict:
    """
    Compute skill score from Claude's find_equivalent_skills result.
    Penalises only truly missing_critical skills; gives full credit for exact matches
    and 85% credit for semantic equivalents.
    """
    n_required = max(len(required_skills), 1)
    n_missing = len(skill_analysis.get("missing_critical", []))
    n_exact = len(skill_analysis.get("exact_matches", []))
    n_equiv = len(skill_analysis.get("equivalent_matches", []))

    base_score = max(0.0, 100.0 - (n_missing / n_required) * 100.0)
    equiv_bonus = min(15.0, (n_equiv / n_required) * 15.0)

    matched = (skill_analysis.get("exact_matches", []) or []) + (skill_analysis.get("equivalent_matches", []) or [])
    missing = skill_analysis.get("missing_critical", []) or []

    return {
        "score": round(min(100.0, base_score + equiv_bonus), 2),
        "exact_matches": n_exact,
        "total_required": n_required,
        "bonus_matches": n_equiv,
        "matched": matched[:10],
        "missing": missing[:10],
    }


def _calculate_skill_match(candidate_data: dict, jd_data: dict) -> dict:
    """Semantic skill matching (fallback when no LLM skill analysis is available)"""
    candidate_skills = set()

    # Extract core competencies
    core_comps = candidate_data.get("core_competencies", [])
    if core_comps:
        for skill_list in (core_comps if isinstance(core_comps, list) else []):
            if isinstance(skill_list, str):
                candidate_skills.update([s.lower().strip() for s in skill_list.split(",")])

    # Extract technical and soft skills
    tech_skills = candidate_data.get("technical_skills", [])
    if tech_skills:
        candidate_skills.update([s.lower().strip() for s in tech_skills if s])

    soft_skills = candidate_data.get("soft_skills", [])
    if soft_skills:
        candidate_skills.update([s.lower().strip() for s in soft_skills if s])

    # Also include cert names so "rn" in required_skills matches "rn license" in certs
    certs = candidate_data.get("certifications_licenses", [])
    if certs:
        candidate_skills.update([_normalize_cert(c) for c in certs if c])

    required_skills = set()
    req = jd_data.get("required_skills", [])
    if req:
        required_skills = set([s.lower().strip() for s in req if s])

    nice_to_have = set()
    nice = jd_data.get("nice_to_have_skills", [])
    if nice:
        nice_to_have = set([s.lower().strip() for s in nice if s])

    # Count matches — partial/substring matching so "sdu" matches "sdu nursing", etc.
    required_matched = sum(
        1 for req in required_skills
        if any(_skill_matches(cand, req) for cand in candidate_skills)
    )
    nice_to_have_matched = sum(
        1 for req in nice_to_have
        if any(_skill_matches(cand, req) for cand in candidate_skills)
    )

    if not required_skills:
        required_score = 100.0
    else:
        required_score = min(100, (required_matched / len(required_skills)) * 100)

    bonus = (nice_to_have_matched / max(len(nice_to_have), 1)) * 15 if nice_to_have else 0

    return {
        "score": round(min(100, required_score + bonus), 2),
        "exact_matches": required_matched,
        "total_required": len(required_skills),
        "bonus_matches": nice_to_have_matched,
    }


def _calculate_experience_match(candidate_data: dict, jd_data: dict, domain: str) -> dict:
    """Intelligent experience matching considering career progression"""
    candidate_years = candidate_data.get("years_relevant_experience") or 0
    required_years = jd_data.get("required_experience_years") or 0

    # Ensure they're integers
    try:
        candidate_years = int(candidate_years) if candidate_years is not None else 0
        required_years = int(required_years) if required_years is not None else 0
    except (ValueError, TypeError):
        candidate_years = 0
        required_years = 0

    candidate_level = str(candidate_data.get("current_role_level", "mid")).lower()
    required_level = str(jd_data.get("role_level", "mid")).lower()

    # Years of experience score
    if required_years == 0:
        years_score = 100.0
    elif candidate_years >= required_years:
        years_score = 100.0
    elif candidate_years >= required_years * 0.75:
        years_score = 85.0
    elif candidate_years >= required_years * 0.5:
        years_score = 60.0
    else:
        years_score = 40.0

    # Role level score
    level_hierarchy = {"entry": 1, "mid": 2, "senior": 3, "lead": 4}
    candidate_level_num = level_hierarchy.get(candidate_level, 2)
    required_level_num = level_hierarchy.get(required_level, 2)

    if candidate_level_num >= required_level_num:
        level_score = 100.0
    elif candidate_level_num == required_level_num - 1:
        level_score = 85.0
    else:
        level_score = max(50, 100 - (required_level_num - candidate_level_num) * 20)

    # Industry experience bonus
    candidate_industries = set(candidate_data.get("industries_experience", []))
    industry_domain = jd_data.get("industry_domain", "")
    if industry_domain and industry_domain in candidate_industries:
        industry_bonus = 10
    else:
        industry_bonus = 0

    overall_exp_score = (years_score * 0.6 + level_score * 0.4 + industry_bonus) / 1.1

    # Recency: check if the most recent work history entry is in the required domain
    recency_note = _assess_recency(candidate_data, jd_data)

    return {
        "score": round(min(100, overall_exp_score), 2),
        "years_score": round(years_score, 2),
        "level_score": round(level_score, 2),
        "candidate_years": candidate_years,
        "required_years": required_years,
        "career_trajectory_positive": candidate_data.get("career_trajectory") == "up",
        "recency_note": recency_note,
    }


def _assess_recency(candidate_data: dict, jd_data: dict) -> str:
    """Check if candidate's most recent role is in the required specialty/domain."""
    work_history = candidate_data.get("work_history", [])
    if not work_history:
        return "No recent work history available"

    recent = work_history[0]
    recent_title = (recent.get("title", "") + " " + " ".join(recent.get("keywords", []))).lower()

    required_skills = [s.lower() for s in jd_data.get("required_skills", [])]
    specialty = (jd_data.get("job_title", "") + " " + " ".join(required_skills)).lower()

    # Check overlap between recent role and required specialty
    specialty_tokens = set(specialty.split())
    title_tokens = set(recent_title.split())
    overlap = specialty_tokens & title_tokens - {"and", "the", "of", "in", "a", "for", "with"}

    company = recent.get("company", "")
    duration = recent.get("duration_years", "")
    duration_str = f"{duration} yr" if duration else ""

    if len(overlap) >= 2:
        return f"Most recent role ({company}{', ' + str(duration_str) if duration_str else ''}) directly in required specialty"
    elif len(overlap) == 1:
        return f"Most recent role ({company}) partially overlaps with required specialty"
    else:
        return f"Most recent role ({company}) is outside required specialty - verify domain recency"


def _calculate_education_match(candidate_data: dict, jd_data: dict) -> dict:
    """Education alignment"""
    candidate_degrees = set()
    deg = candidate_data.get("education_degrees", [])
    if deg:
        candidate_degrees = set(d.lower().strip() for d in deg if d)

    candidate_fields = set()
    fields = candidate_data.get("education_fields", [])
    if fields:
        candidate_fields = set(f.lower().strip() for f in fields if f)

    required_degrees = set()
    req_deg = jd_data.get("required_education", [])
    if req_deg:
        required_degrees = set(d.lower().strip() for d in req_deg if d)

    required_fields = set()
    req_fields = jd_data.get("education_fields", [])
    if req_fields:
        required_fields = set(f.lower().strip() for f in req_fields if f)

    # Infer nursing field from degree when Claude didn't extract education_fields
    if not candidate_fields and candidate_degrees:
        nursing_degrees = {"bsn", "msn", "adn", "nursing", "rn"}
        if candidate_degrees & nursing_degrees:
            candidate_fields = {"nursing"}
        elif any("nurs" in d for d in candidate_degrees):
            candidate_fields = {"nursing"}

    # Partial matching so "nursing science" matches "nursing", "bsn" matches "bachelor of science"
    degree_matches = sum(
        1 for req in required_degrees
        if any(_field_matches(cand, req) for cand in candidate_degrees)
    ) if required_degrees else 0
    field_matches = sum(
        1 for req in required_fields
        if any(_field_matches(cand, req) for cand in candidate_fields)
    ) if required_fields else 0

    degree_score = (degree_matches / len(required_degrees)) * 100 if required_degrees else 100
    field_score = (field_matches / len(required_fields)) * 100 if required_fields else 100

    overall_edu = (degree_score + field_score) / 2

    return {
        "score": round(overall_edu, 2),
        "degree_matches": degree_matches,
        "field_matches": field_matches
    }


def _calculate_cert_match(candidate_data: dict, jd_data: dict) -> dict:
    """Certification matching with normalization and fuzzy/substring matching."""
    raw_candidate = candidate_data.get("certifications_licenses", []) or []
    candidate_certs = [_normalize_cert(c) for c in raw_candidate if c]

    raw_required = jd_data.get("required_certifications", []) or []
    required_certs = [_normalize_cert(c) for c in raw_required if c]

    if not required_certs:
        return {"score": 100.0, "matched": [], "missing": [], "total_required": 0}

    matched = []
    missing = []
    for req in required_certs:
        if any(_cert_matches(cand, req) for cand in candidate_certs):
            matched.append(req)
        else:
            missing.append(req)

    score = (len(matched) / len(required_certs)) * 100

    return {
        "score": round(score, 2),
        "matched": matched[:5],
        "missing": missing[:5],
        "total_required": len(required_certs),
    }


def categorize_fit(overall_score: float, domain: str = "general") -> dict:
    """
    Categorize candidate fit based on score and domain requirements.
    """
    if overall_score >= 85:
        return {
            "level": "Exceptional Fit",
            "color": "green",
            "recommendation": "Strong Yes - Highly recommended",
            "priority": "urgent",
            "next_step": "Interview immediately",
        }
    elif overall_score >= 70:
        return {
            "level": "Good Fit",
            "color": "blue",
            "recommendation": "Yes - Good candidate",
            "priority": "high",
            "next_step": "Schedule interview",
        }
    elif overall_score >= 50:
        return {
            "level": "Moderate Fit",
            "color": "orange",
            "recommendation": "Maybe - Has potential but gaps exist",
            "priority": "medium",
            "next_step": "Consider with other candidates",
        }
    else:
        return {
            "level": "Poor Fit",
            "color": "red",
            "recommendation": "No - Significant gaps in requirements",
            "priority": "low",
            "next_step": "Continue searching",
        }
