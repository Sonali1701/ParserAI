from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import tempfile
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from parsers.document_parser import extract_text
from parsers.entity_extractor import extract_all_entities
from scoring.scorer import score_candidate
from scoring.justifier import generate_justification

# Optional LLM support
try:
    from llm.claude_analyzer import extract_with_llm, generate_detailed_analysis, is_llm_enabled
    LLM_AVAILABLE = is_llm_enabled()
except (ImportError, Exception):
    LLM_AVAILABLE = False

app = Flask(__name__)
CORS(app)

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _reshape_llm_output(llm_data: dict) -> dict:
    """Reshape LLM output to match NLP entity extractor format"""
    all_skills = llm_data.get('skills', [])
    certs = llm_data.get('certifications', [])
    specialties = llm_data.get('specialties', [])

    # Combine all relevant items into skills dict
    combined_skills = {
        'nursing_certifications': certs,
        'specialty_skills': specialties,
        'clinical_procedures': all_skills[:5],
        'emr_systems': [s for s in all_skills if any(x in s.lower() for x in ['epic', 'meditech', 'cerner', 'charting', 'ehr'])],
        'soft_skills': [s for s in all_skills if any(x in s.lower() for x in ['communication', 'teamwork', 'leadership', 'patient care'])],
        'other_skills': all_skills[5:] if len(all_skills) > 5 else []
    }

    return {
        'skills': combined_skills,
        'education': {
            'degrees': llm_data.get('education_degrees', []),
            'fields': llm_data.get('education_fields', []),
            'gpa': None
        },
        'experience': {
            'years': llm_data.get('years_experience', 0),
            'companies': [],
            'positions': []
        },
        'certifications': certs,
        'raw_text': ''
    }


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Analyze resume against JD with intelligent, domain-aware matching"""
    try:
        if 'resume' not in request.files or 'jd' not in request.files:
            return jsonify({'error': 'Both resume and JD files are required'}), 400

        resume_file = request.files['resume']
        jd_file = request.files['jd']

        if not resume_file or not jd_file:
            return jsonify({'error': 'Files are empty'}), 400

        if not allowed_file(resume_file.filename) or not allowed_file(jd_file.filename):
            return jsonify({'error': 'Invalid file format. Allowed: PDF, DOCX, TXT'}), 400

        # Save uploaded files temporarily
        with tempfile.TemporaryDirectory() as temp_dir:
            resume_path = os.path.join(temp_dir, secure_filename(resume_file.filename))
            jd_path = os.path.join(temp_dir, secure_filename(jd_file.filename))

            resume_file.save(resume_path)
            jd_file.save(jd_path)

            # Extract text
            resume_text = extract_text(resume_path)
            jd_text = extract_text(jd_path)

            if not LLM_AVAILABLE:
                raise ValueError("LLM features are required for intelligent analysis. Please set ANTHROPIC_API_KEY.")

            # Use intelligent extraction
            from llm.requirement_extractor import extract_requirements, extract_candidate_profile
            from llm.semantic_matcher import detect_domain, find_equivalent_skills, analyze_experience_relevance, generate_smart_analysis
            from scoring.intelligent_scorer import calculate_semantic_match, categorize_fit

            # Extract structured data
            jd_requirements = extract_requirements(jd_text)
            candidate_profile = extract_candidate_profile(resume_text)

            # Detect domain for domain-specific analysis
            domain = detect_domain(resume_text, jd_text)

            # Find equivalent and transferable skills
            skill_analysis = find_equivalent_skills(
                candidate_profile.get("core_competencies", []) + candidate_profile.get("technical_skills", []),
                jd_requirements.get("required_skills", [])
            )

            # Analyze experience relevance
            exp_analysis = analyze_experience_relevance(
                {
                    "years": candidate_profile.get("years_relevant_experience", 0),
                    "positions": [w.get("title", "") for w in candidate_profile.get("work_history", [])[:3]],
                    "companies": [w.get("company", "") for w in candidate_profile.get("work_history", [])[:3]],
                },
                {
                    "years": jd_requirements.get("required_experience_years", 0),
                    "level": jd_requirements.get("role_level", "mid"),
                },
                domain
            )

            # Calculate algorithmic per-category scores (used for transparency tiles)
            score_result = calculate_semantic_match(candidate_profile, jd_requirements, domain, skill_analysis)

            # AI does the holistic assessment, sees the algorithmic breakdown, and
            # returns the authoritative overall_fit + overall_fit_score
            smart_analysis = generate_smart_analysis(resume_text, jd_text, score_result)

            # Use AI's holistic score as the headline. This guarantees the score
            # always lives in the band of the AI's verdict (Strong Yes 85-100, etc).
            ai_score = smart_analysis.get("overall_fit_score")
            if isinstance(ai_score, (int, float)):
                score_result["overall_score"] = round(float(ai_score), 2)

            # Fit category comes from the AI verdict so the badge and score agree
            fit_category = categorize_fit(
                score_result["overall_score"], domain,
                verdict=smart_analysis.get("overall_fit"),
            )

            return jsonify({
                'success': True,
                'score': score_result,
                'candidate_profile': candidate_profile,
                'jd_requirements': jd_requirements,
                'domain': domain,
                'fit_category': fit_category,
                'skill_analysis': skill_analysis,
                'experience_analysis': exp_analysis,
                'smart_analysis': smart_analysis,
                'using_intelligent_system': True
            }), 200

    except ValueError as e:
        return jsonify({'error': f'Configuration error: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Processing error: {str(e)}'}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug, port=port, host='0.0.0.0')
