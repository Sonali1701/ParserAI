def generate_justification(score_data: dict) -> dict:
    """Generate detailed justification for the score"""

    overall_score = score_data['overall_score']
    skill_data = score_data['skill_match']
    exp_data = score_data['experience_match']
    edu_data = score_data['education_match']

    # Determine fit level
    if overall_score >= 85:
        fit_level = "Excellent Fit"
        fit_color = "green"
    elif overall_score >= 70:
        fit_level = "Good Fit"
        fit_color = "blue"
    elif overall_score >= 50:
        fit_level = "Moderate Fit"
        fit_color = "orange"
    else:
        fit_level = "Poor Fit"
        fit_color = "red"

    # Build detailed justification
    cert_data = score_data.get('certification_match', {})
    justification = {
        'fit_level': fit_level,
        'fit_color': fit_color,
        'summary': generate_summary(overall_score),
        'skill_analysis': generate_skill_analysis(skill_data),
        'experience_analysis': generate_experience_analysis(exp_data),
        'education_analysis': generate_education_analysis(edu_data),
        'certification_analysis': generate_certification_analysis(cert_data),
        'improvements': generate_improvements(score_data)
    }

    return justification


def generate_summary(score: float) -> str:
    """Generate overall summary"""
    if score >= 85:
        return f"Candidate is an excellent match for this position ({score}% match). Strong alignment across skills, experience, and education."
    elif score >= 70:
        return f"Candidate is a good match for this position ({score}% match). Most requirements are met with minor gaps."
    elif score >= 50:
        return f"Candidate has moderate fit for this position ({score}% match). Some key requirements are missing but foundational skills are present."
    else:
        return f"Candidate is not well-suited for this position ({score}% match). Significant gaps in critical requirements."


def generate_skill_analysis(skill_data: dict) -> dict:
    """Generate detailed skill analysis"""
    score = skill_data['score']
    matched = skill_data['matched']
    missing = skill_data['missing']

    analysis = {
        'score': score,
        'summary': f"{score}% of required skills are present",
        'matched_skills': matched[:10] if matched else [],  # Top 10
        'missing_skills': missing[:10] if missing else [],  # Top 10
        'insight': ""
    }

    if not missing:
        analysis['insight'] = "Excellent! Candidate has all required technical skills."
    elif len(matched) >= len(missing) * 2:
        analysis['insight'] = f"Good skill coverage. Candidate has {len(matched)} required skills but is missing {len(missing)} key skills."
    else:
        analysis['insight'] = f"Candidate has {len(matched)} required skills but is missing {len(missing)} important skills. Consider training or pairing with experienced team members."

    return analysis


def generate_experience_analysis(exp_data: dict) -> dict:
    """Generate experience analysis"""
    return {
        'score': exp_data['score'],
        'explanation': exp_data['explanation'],
        'insight': determine_experience_insight(exp_data['score'])
    }


def generate_education_analysis(edu_data: dict) -> dict:
    """Generate education analysis"""
    score = edu_data['score']
    matched_fields = edu_data['matched_fields']

    return {
        'score': score,
        'matched_fields': matched_fields,
        'insight': "Relevant educational background matches job requirements" if score >= 70 else "Educational background partially meets requirements"
    }


def generate_certification_analysis(cert_data: dict) -> dict:
    """Generate certification analysis"""
    score = cert_data.get('score', 0)
    matched = cert_data.get('matched', [])
    missing = cert_data.get('missing', [])

    return {
        'score': score,
        'matched': matched,
        'missing': missing,
        'insight': "All required certifications present" if score == 100 else f"Candidate has {len(matched)} required certifications but missing {len(missing)}"
    }


def generate_improvements(score_data: dict) -> list:
    """Generate list of improvements needed"""
    improvements = []
    skill_data = score_data['skill_match']
    exp_data = score_data['experience_match']
    cert_data = score_data.get('certification_match', {})

    if cert_data.get('missing'):
        improvements.append({
            'area': 'Certifications',
            'recommendation': f"Obtain missing certifications: {', '.join(cert_data['missing'][:3])}",
            'priority': 'High'
        })

    if skill_data['missing']:
        improvements.append({
            'area': 'Skills',
            'recommendation': f"Develop expertise in: {', '.join(skill_data['missing'][:3])}",
            'priority': 'High' if cert_data.get('missing') else 'Medium'
        })

    if exp_data['score'] < 100:
        improvements.append({
            'area': 'Experience',
            'recommendation': exp_data['explanation'],
            'priority': 'Medium'
        })

    if score_data['education_match']['score'] < 70:
        improvements.append({
            'area': 'Education',
            'recommendation': "Consider pursuing relevant certifications or degrees",
            'priority': 'Medium'
        })

    if not improvements:
        improvements.append({
            'area': 'None',
            'recommendation': "Candidate meets all major requirements!",
            'priority': 'N/A'
        })

    return improvements


def determine_experience_insight(score: float) -> str:
    """Generate insight based on experience score"""
    if score == 100:
        return "Experience level perfectly matches job requirements."
    elif score >= 85:
        return "Experience level is slightly below requirements but acceptable."
    elif score >= 60:
        return "Candidate has some relevant experience but may need mentoring."
    else:
        return "Candidate lacks required experience level. Significant onboarding needed."
