import re
from typing import Dict, List, Set


TECHNICAL_SKILLS = {
    'nursing_certifications': [
        'rn', 'registered nurse', 'bsn', 'adn', 'lpn', 'lvn',
        'nrp', 'acls', 'bls', 'pals', 'ccrn', 'tncc', 'enpc',
        'awhonn', 'fetal monitoring', 'efm', 'advanced fetal monitoring'
    ],
    'specialty_skills': [
        'labor and delivery', 'labor delivery', 'l&d', 'ld', 'ob/gyn', 'obstetrics',
        'maternal care', 'postpartum', 'newborn care', 'neonatal', 'obstetric',
        'triage', 'cesarean', 'c-section', 'epidural', 'pitocin', 'magnesium sulfate',
        'fetal monitoring', 'iufd', 'induction', 'emergency obstetrics'
    ],
    'clinical_procedures': [
        'iv therapy', 'medication administration', 'patient assessment', 'monitoring',
        'wound care', 'catheterization', 'phlebotomy', 'ekg', 'resuscitation',
        'code blue', 'chest compressions', 'rescue breathing'
    ],
    'emr_systems': [
        'epic', 'meditech', 'cerner', 'allscripts', 'obix', 'ehr', 'emr',
        'medical record', 'charting', 'documentation'
    ],
    'soft_skills': [
        'communication', 'teamwork', 'critical thinking', 'patient care', 'compassion',
        'multitasking', 'leadership', 'time management', 'collaboration'
    ],
    'other_skills': [
        'patient education', 'care coordination', 'infection control', 'hipaa',
        'safety protocols', 'emergency response', 'stress management'
    ]
}

EDUCATION_KEYWORDS = {
    'degrees': [
        'bachelor', 'masters', 'phd', 'associate', 'diploma',
        'b.tech', 'b.e.', 'm.tech', 'mba', 'bca', 'mca',
        'bsn', 'adn', 'msn'
    ],
    'fields': [
        'computer science', 'engineering', 'information technology', 'it', 'cse',
        'data science', 'ai', 'ml', 'nursing', 'registered nursing', 'healthcare',
        'nursing science', 'medical science'
    ]
}

EXPERIENCE_PATTERNS = [
    r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s+)?experience',
    r'worked\s+(?:for|at)\s+([^,\.]+)',
    r'(?:senior|junior|lead|staff)?\s*(?:developer|engineer|manager|analyst)',
]


def extract_skills(text: str) -> Dict[str, List[str]]:
    """Extract technical skills from text"""
    text_lower = text.lower()
    extracted = {category: [] for category in TECHNICAL_SKILLS}

    for category, skills in TECHNICAL_SKILLS.items():
        for skill in skills:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                extracted[category].append(skill)

    return extracted


def extract_education(text: str) -> Dict[str, any]:
    """Extract education details from text"""
    text_lower = text.lower()
    education = {
        'degrees': [],
        'fields': [],
        'gpa': None
    }

    for degree in EDUCATION_KEYWORDS['degrees']:
        pattern = r'\b' + re.escape(degree) + r'\b'
        if re.search(pattern, text_lower):
            education['degrees'].append(degree)

    for field in EDUCATION_KEYWORDS['fields']:
        pattern = r'\b' + re.escape(field) + r'\b'
        if re.search(pattern, text_lower):
            education['fields'].append(field)

    # Look for GPA
    gpa_pattern = r'(?:gpa|gp[a-z]*)\s*:?\s*([\d\.]+)'
    gpa_match = re.search(gpa_pattern, text_lower)
    if gpa_match:
        education['gpa'] = float(gpa_match.group(1))

    return education


def extract_experience(text: str) -> Dict[str, any]:
    """Extract experience details from text"""
    experience = {
        'years': 0,
        'companies': [],
        'positions': []
    }

    text_lower = text.lower()

    # Extract years of experience
    for pattern in EXPERIENCE_PATTERNS:
        match = re.search(pattern, text_lower)
        if match:
            try:
                years = int(match.group(1))
                if years > experience['years']:
                    experience['years'] = years
            except (ValueError, IndexError):
                pass

    # Extract company names (common patterns)
    company_pattern = r'(?:worked\s+(?:at|for)|@|company|employer|experience)\s*:?\s*([A-Z][a-zA-Z\s&\.]+)'
    companies = re.findall(company_pattern, text)
    experience['companies'] = [c.strip() for c in companies if c.strip()]

    # Extract job titles
    positions_pattern = r'(?:position|title|role|designation)\s*:?\s*([A-Za-z\s]+?)(?:\n|,|$)'
    positions = re.findall(positions_pattern, text, re.IGNORECASE)
    experience['positions'] = [p.strip() for p in positions if p.strip()]

    return experience


def extract_certifications(text: str) -> List[str]:
    """Extract certifications from text"""
    certifications = []
    cert_keywords = [
        'nrp', 'acls', 'bls', 'pals', 'ccrn', 'tncc', 'enpc',
        'awhonn', 'crisp', 'cen', 'certified nurse', 'american heart association',
        'certification', 'certified'
    ]

    text_lower = text.lower()
    for cert in cert_keywords:
        pattern = r'\b' + re.escape(cert) + r'\b'
        if re.search(pattern, text_lower):
            certifications.append(cert)

    return list(set(certifications))


def extract_all_entities(text: str) -> Dict:
    """Extract all entities from document"""
    return {
        'skills': extract_skills(text),
        'education': extract_education(text),
        'experience': extract_experience(text),
        'certifications': extract_certifications(text),
        'raw_text': text
    }


def flatten_skills(skills_dict: Dict) -> Set[str]:
    """Flatten nested skills dict to a single set"""
    flat = set()
    for category_skills in skills_dict.values():
        flat.update(category_skills)
    return flat
