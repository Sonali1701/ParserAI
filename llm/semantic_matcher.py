"""
Semantic matching for skills, roles, and requirements.
Uses Claude tool use (forced structured output) for guaranteed valid JSON.
"""

from anthropic import Anthropic

client = Anthropic()


def detect_domain(resume_text: str, jd_text: str) -> str:
    """Detect job domain. Returns one word: healthcare, tech, finance, etc."""
    prompt = f"""What is the job domain/industry for these documents?

RESUME (excerpt): {resume_text[:400]}
JD (excerpt): {jd_text[:400]}

Reply with ONE word only. Examples: healthcare, software, finance, sales, legal, education"""

    try:
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=20,
            temperature=0,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text.strip().lower().split()[0]
    except:
        return "general"


def find_equivalent_skills(candidate_skills: list, required_skills: list) -> dict:
    """
    Find equivalent/transferable skills using Claude tool use.
    Tool use guarantees structurally valid JSON — no parsing needed.
    """
    if not required_skills:
        return {
            "exact_matches": candidate_skills,
            "equivalent_matches": [],
            "transferable_skills": [],
            "missing_critical": [],
            "analysis": "No required skills specified.",
        }

    prompt = f"""Analyze skill alignment between this candidate and job requirements.

CANDIDATE SKILLS: {', '.join(candidate_skills[:25])}

REQUIRED SKILLS: {', '.join(required_skills[:15])}

For healthcare/nursing: unit specialties (SDU, ICU, L&D), procedures, and certifications count as exact matches when the candidate has direct experience in the same clinical area. Be generous — if the candidate clearly practiced a skill under a different name, count it as equivalent."""

    tool = {
        "name": "skill_match_report",
        "description": "Report the structured skill match analysis results",
        "input_schema": {
            "type": "object",
            "properties": {
                "exact_matches": {
                    "type": "array", "items": {"type": "string"},
                    "description": "Required skills the candidate has by the same or obvious name"
                },
                "equivalent_matches": {
                    "type": "array", "items": {"type": "string"},
                    "description": "Required skills the candidate meets via equivalent experience or alternate name"
                },
                "transferable_skills": {
                    "type": "array", "items": {"type": "string"},
                    "description": "Candidate skills not required but applicable to this role"
                },
                "missing_critical": {
                    "type": "array", "items": {"type": "string"},
                    "description": "Required skills the candidate genuinely lacks"
                },
                "analysis": {
                    "type": "string",
                    "description": "One sentence summary of overall skill alignment"
                }
            },
            "required": ["exact_matches", "equivalent_matches", "transferable_skills", "missing_critical", "analysis"]
        }
    }

    try:
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1000,
            temperature=0,
            tools=[tool],
            tool_choice={"type": "tool", "name": "skill_match_report"},
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].input
    except Exception as e:
        return {
            "exact_matches": [],
            "equivalent_matches": [],
            "transferable_skills": [],
            "missing_critical": required_skills,
            "analysis": f"Skill analysis error: {e}",
        }


def analyze_experience_relevance(
    resume_experience: dict, jd_requirements: dict, domain: str
) -> dict:
    """Analyze experience fit using Claude tool use."""
    prompt = f"""Analyze whether the candidate's experience fits this role.

CANDIDATE: {resume_experience.get('years', 0)} years, positions: {', '.join(resume_experience.get('positions', [])[:4])}, companies: {', '.join(resume_experience.get('companies', [])[:4])}

ROLE NEEDS: {jd_requirements.get('years', 0)} years minimum, level: {jd_requirements.get('level', 'mid')}, domain: {domain}"""

    tool = {
        "name": "experience_report",
        "description": "Report structured experience fit analysis",
        "input_schema": {
            "type": "object",
            "properties": {
                "experience_match_score": {"type": "integer", "description": "0-100 score"},
                "years_assessment": {"type": "string", "description": "One sentence on years fit"},
                "progression_fit": {"type": "string", "description": "One sentence on career progression fit"},
                "domain_knowledge": {"type": "string", "description": "One sentence on domain expertise"},
                "concern_areas": {"type": "array", "items": {"type": "string"}},
                "strengths": {"type": "array", "items": {"type": "string"}},
                "role_readiness": {"type": "string", "enum": ["Yes", "Maybe", "No"]},
                "recommendation": {"type": "string", "description": "One sentence recommendation"}
            },
            "required": ["experience_match_score", "years_assessment", "progression_fit",
                         "domain_knowledge", "concern_areas", "strengths", "role_readiness", "recommendation"]
        }
    }

    try:
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=800,
            temperature=0,
            tools=[tool],
            tool_choice={"type": "tool", "name": "experience_report"},
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].input
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
    resume_text: str, jd_text: str, score_breakdown: dict
) -> dict:
    """
    Generate the authoritative recruiter assessment using Claude tool use.
    The AI sees the algorithmic breakdown and produces an overall_fit_score
    that is constrained to match its overall_fit verdict.
    """
    skill   = score_breakdown.get("skill_match", {})
    exp     = score_breakdown.get("experience_match", {})
    edu     = score_breakdown.get("education_match", {})
    cert    = score_breakdown.get("certification_match", {})

    prompt = f"""You are an expert healthcare recruiter. Assess this candidate holistically.

RESUME (excerpt):
{resume_text[:1500]}

JOB DESCRIPTION (excerpt):
{jd_text[:1500]}

ALGORITHMIC BREAKDOWN (use as a signal, not the final word):
- Skills: {skill.get('score', 0)}% — {skill.get('exact_matches', 0)}/{skill.get('total_required', 0)} required matched
- Experience: {exp.get('score', 0)}% — {exp.get('candidate_years', 0)} yrs vs {exp.get('required_years', 0)} required
- Education: {edu.get('score', 0)}%
- Certifications: {cert.get('score', 0)}% — missing: {', '.join(cert.get('missing', []) or []) or 'none'}

Decide overall_fit using real recruiter judgment. A candidate can be Strong Yes even with mediocre skill-match if they bring directly relevant recent experience. They can be No despite 100% on every metric if there are red flags (expired license, wrong specialty, employment gaps, location mismatch).

CRITICAL: overall_fit_score MUST be inside the band of overall_fit:
- Strong Yes -> 85 to 100
- Yes        -> 70 to 84
- Maybe      -> 50 to 69
- No         -> 0 to 49

Rules:
- strengths/gaps: 3-5 bullets, under 12 words each, specific (e.g. "7 yrs L&D travel RN experience")
- gaps: real gaps only; empty list if none
- risk_flags: license expiry, employment gaps, location mismatch, specialty mismatch; empty if clean
- recent_domain_experience: one short sentence on how recent and directly relevant the most recent role is"""

    tool = {
        "name": "smart_analysis_report",
        "description": "Report the authoritative recruiter assessment",
        "input_schema": {
            "type": "object",
            "properties": {
                "overall_fit": {
                    "type": "string",
                    "enum": ["Strong Yes", "Yes", "Maybe", "No"]
                },
                "overall_fit_score": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 100,
                    "description": "0-100 holistic fit score. MUST be in the band matching overall_fit: Strong Yes 85-100, Yes 70-84, Maybe 50-69, No 0-49."
                },
                "confidence": {
                    "type": "string",
                    "enum": ["High", "Medium", "Low"]
                },
                "strengths": {"type": "array", "items": {"type": "string"}},
                "gaps": {"type": "array", "items": {"type": "string"}},
                "recent_domain_experience": {"type": "string"},
                "career_fit": {
                    "type": "string",
                    "enum": ["Yes", "Lateral", "No"]
                },
                "risk_flags": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["overall_fit", "overall_fit_score", "confidence", "strengths",
                         "gaps", "recent_domain_experience", "career_fit", "risk_flags"]
        }
    }

    try:
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1000,
            temperature=0,
            tools=[tool],
            tool_choice={"type": "tool", "name": "smart_analysis_report"},
            messages=[{"role": "user", "content": prompt}],
        )
        result = message.content[0].input
        result["overall_fit_score"] = _reconcile_score(
            result.get("overall_fit_score", 50), result.get("overall_fit", "Maybe")
        )
        return result
    except Exception as e:
        return {
            "overall_fit": "Maybe",
            "overall_fit_score": 50,
            "confidence": "Low",
            "strengths": [],
            "gaps": [],
            "recent_domain_experience": "Unable to assess",
            "career_fit": "Lateral",
            "risk_flags": [f"Analysis error: {e}"],
        }


def _reconcile_score(score: int, verdict: str) -> int:
    """
    Defensive: clamp the AI's score into the band matching its verdict.
    Prevents any chance of overall_fit='No' with score=90 or vice versa.
    """
    bands = {
        "Strong Yes": (85, 100),
        "Yes":        (70, 84),
        "Maybe":      (50, 69),
        "No":         (0, 49),
    }
    lo, hi = bands.get(verdict, (50, 69))
    try:
        s = int(score)
    except (TypeError, ValueError):
        s = (lo + hi) // 2
    return max(lo, min(hi, s))
