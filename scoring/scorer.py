from typing import Dict, Tuple
from parsers.entity_extractor import flatten_skills


def calculate_skill_match(resume_skills: Dict, jd_skills: Dict) -> Tuple[float, list, list]:
    """
    Calculate skill match percentage with fuzzy matching
    Returns: (score, matched_skills, missing_skills)
    """
    resume_skills_flat = flatten_skills(resume_skills)
    jd_skills_flat = flatten_skills(jd_skills)

    if not jd_skills_flat:
        return 100.0, list(resume_skills_flat), []

    # Fuzzy matching for similar skills
    skill_mappings = {
        'fetal monitoring': ['efm', 'electronic fetal monitoring', 'fetal heart rate monitoring'],
        'c-section assistance': ['cesarean', 'cesarean section', 'circulating', 'surgical support'],
        'labor management': ['labor support', 'induction', 'labor care', 'labor patient'],
        'obstetrics': ['obstetric', 'ob', 'obstetrical'],
        'medication administration': ['medications', 'drug administration', 'iv therapy'],
        'patient assessment': ['assessment', 'patient monitoring', 'vital signs'],
    }

    matched = resume_skills_flat.intersection(jd_skills_flat)

    # Add fuzzy matches
    for jd_skill in jd_skills_flat:
        if jd_skill not in matched:
            # Check if skill is in mappings
            for key, variations in skill_mappings.items():
                if jd_skill.lower() == key.lower() or any(v in jd_skill.lower() for v in variations):
                    # Check if any variation exists in resume
                    for resume_skill in resume_skills_flat:
                        if any(v in resume_skill.lower() for v in variations + [key]):
                            matched.add(jd_skill)
                            break

            # Partial matching - check if key words match
            if jd_skill not in matched:
                jd_words = set(jd_skill.lower().split())
                for resume_skill in resume_skills_flat:
                    resume_words = set(resume_skill.lower().split())
                    if jd_words.intersection(resume_words):
                        matched.add(jd_skill)
                        break

    missing = jd_skills_flat - matched

    match_score = (len(matched) / len(jd_skills_flat)) * 100 if jd_skills_flat else 0

    return match_score, list(matched)[:10], list(missing)[:10]


def calculate_experience_match(resume_exp: Dict, jd_exp: Dict) -> Tuple[float, str]:
    """
    Calculate experience match
    Returns: (score, explanation)
    """
    resume_years = resume_exp.get('years', 0)
    jd_years = jd_exp.get('years', 0)

    if jd_years == 0:
        return 100.0, f"Candidate has {resume_years} years of experience"

    if resume_years >= jd_years:
        score = 100.0
        explanation = f"Candidate has {resume_years} years (required: {jd_years} years)"
    elif resume_years >= jd_years * 0.8:
        score = 85.0
        explanation = f"Candidate has {resume_years} years (required: {jd_years} years) - slightly below"
    elif resume_years >= jd_years * 0.5:
        score = 60.0
        explanation = f"Candidate has {resume_years} years (required: {jd_years} years) - moderately below"
    else:
        score = 30.0
        explanation = f"Candidate has {resume_years} years (required: {jd_years} years) - significantly below"

    return score, explanation


def calculate_education_match(resume_edu: Dict, jd_edu: Dict) -> Tuple[float, list]:
    """
    Calculate education match
    Returns: (score, matched_fields)
    """
    resume_degrees = set(resume_edu.get('degrees', []))
    resume_fields = set(resume_edu.get('fields', []))
    jd_degrees = set(jd_edu.get('degrees', []))
    jd_fields = set(jd_edu.get('fields', []))

    matched_degrees = resume_degrees.intersection(jd_degrees)
    matched_fields = resume_fields.intersection(jd_fields)

    degree_score = (len(matched_degrees) / len(jd_degrees) * 100) if jd_degrees else 100
    field_score = (len(matched_fields) / len(jd_fields) * 100) if jd_fields else 100

    overall_edu_score = (degree_score + field_score) / 2

    return overall_edu_score, list(matched_fields)


def calculate_overall_score(skill_score: float, experience_score: float, education_score: float) -> float:
    """
    Calculate weighted overall score
    Weights: Skills 50%, Experience 30%, Education 20%
    """
    return (skill_score * 0.50) + (experience_score * 0.30) + (education_score * 0.20)


def calculate_certification_match(resume_certs: list, jd_certs: list) -> Tuple[float, list, list]:
    """
    Calculate certification match with fuzzy matching
    Returns: (score, matched_certs, missing_certs)
    """
    def normalize_cert(cert_text: str) -> str:
        """Normalize certification text for matching"""
        cert = cert_text.lower().strip()
        # Remove parenthetical descriptions
        cert = cert.split('(')[0].strip()
        # Remove 'issued through' parts
        cert = cert.split('issued')[0].strip()
        # Remove 'certification' or 'certified'
        cert = cert.replace('certification', '').replace('certified', '').strip()
        # Remove commas and extra spaces
        cert = ' '.join(cert.split())
        return cert

    # Normalize all certifications
    resume_certs_norm = set(normalize_cert(c) for c in resume_certs if c)
    jd_certs_norm = set(normalize_cert(c) for c in jd_certs if c)

    if not jd_certs_norm:
        return 100.0, list(resume_certs), []

    # Fuzzy matching for common abbreviations
    cert_mappings = {
        'nrp': 'neonatal resuscitation',
        'bls': 'basic life support',
        'acls': 'advanced cardiovascular life support',
        'awhonn': 'fetal monitoring',
        'efm': 'fetal monitoring',
        'rnc': 'registered nurse',
    }

    # Expand certifications with common mappings
    resume_expanded = resume_certs_norm.copy()
    for cert in resume_certs_norm:
        for abbr, full in cert_mappings.items():
            if abbr in cert:
                resume_expanded.add(full)

    jd_expanded = jd_certs_norm.copy()
    for cert in jd_certs_norm:
        for abbr, full in cert_mappings.items():
            if abbr in cert:
                jd_expanded.add(full)

    # Find matches with partial matching
    matched = []
    for jd_cert in jd_expanded:
        for resume_cert in resume_expanded:
            if jd_cert in resume_cert or resume_cert in jd_cert or jd_cert.split()[0] in resume_cert:
                matched.append(jd_cert)
                break

    missing = jd_expanded - set(matched)

    match_score = (len(matched) / len(jd_certs_norm)) * 100 if jd_certs_norm else 0

    return match_score, list(matched)[:5], list(missing)[:5]


def score_candidate(resume_data: Dict, jd_data: Dict) -> Dict:
    """
    Complete scoring pipeline
    """
    resume_skills = resume_data.get('skills', {})
    resume_exp = resume_data.get('experience', {})
    resume_edu = resume_data.get('education', {})
    resume_certs = resume_data.get('certifications', [])

    jd_skills = jd_data.get('skills', {})
    jd_exp = jd_data.get('experience', {})
    jd_edu = jd_data.get('education', {})
    jd_certs = jd_data.get('certifications', [])

    skill_score, matched_skills, missing_skills = calculate_skill_match(resume_skills, jd_skills)
    exp_score, exp_explanation = calculate_experience_match(resume_exp, jd_exp)
    edu_score, matched_edu_fields = calculate_education_match(resume_edu, jd_edu)
    cert_score, matched_certs, missing_certs = calculate_certification_match(resume_certs, jd_certs)

    # Adjust weights if certifications are critical (healthcare, finance, etc.)
    has_required_certs = len(jd_certs) > 0
    if has_required_certs:
        # For roles with required certifications, weight them heavily
        overall_score = (skill_score * 0.35) + (exp_score * 0.25) + (edu_score * 0.15) + (cert_score * 0.25)
    else:
        overall_score = (skill_score * 0.50) + (exp_score * 0.30) + (edu_score * 0.20)

    return {
        'overall_score': round(overall_score, 2),
        'skill_match': {
            'score': round(skill_score, 2),
            'matched': matched_skills,
            'missing': missing_skills
        },
        'experience_match': {
            'score': round(exp_score, 2),
            'explanation': exp_explanation
        },
        'education_match': {
            'score': round(edu_score, 2),
            'matched_fields': matched_edu_fields
        },
        'certification_match': {
            'score': round(cert_score, 2),
            'matched': matched_certs,
            'missing': missing_certs
        }
    }
