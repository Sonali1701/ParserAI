# Resume & JD Parser

A smart tool that analyzes resumes against job descriptions and provides detailed compatibility scores with actionable insights.

## Features

- **Multi-format Support**: Parse PDF, DOCX, and TXT files
- **Smart Extraction**: Automatically extract skills, experience, and education
- **Intelligent Scoring**: Get a comprehensive match score (0-100%)
- **Detailed Analysis**: 
  - Skill match percentage with specific matched/missing skills
  - Experience level comparison
  - Educational background alignment
- **Actionable Insights**: Get recommendations on what the candidate needs to improve
- **Beautiful UI**: Modern, responsive web interface

## Scoring Breakdown

The overall score is calculated using weighted components:
- **Skills Match (50%)**: How many required skills the candidate has
- **Experience Match (30%)**: Years of experience vs. job requirements
- **Education Match (20%)**: Educational background alignment

## Installation

1. Clone the repository:
```bash
git clone <repo-url>
cd ParserAI
```

2. Create a virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate  # On Windows
# or
source .venv/bin/activate  # On macOS/Linux
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Download spacy language model:
```bash
python -m spacy download en_core_web_sm
```

## Usage

1. Start the Flask app:
```bash
python app.py
```

2. Open your browser and go to:
```
http://localhost:5000
```

3. Upload a resume and job description (PDF, DOCX, or TXT)

4. Click "Analyze Now" to get results

## Project Structure

```
ParserAI/
├── app.py                  # Flask application
├── requirements.txt        # Python dependencies
├── parsers/
│   ├── document_parser.py  # Extract text from files
│   └── entity_extractor.py # Extract skills, education, experience
├── scoring/
│   ├── scorer.py          # Calculate match scores
│   └── justifier.py       # Generate explanations
├── templates/
│   └── index.html         # Web interface
└── static/
    ├── style.css          # Styling
    └── script.js          # Frontend logic
```

## How It Works

### 1. Document Parsing
- Extracts text from uploaded resume and JD
- Supports PDF, DOCX, and TXT formats

### 2. Entity Extraction
- Identifies technical skills from predefined lists
- Extracts education details (degrees, fields, GPA)
- Finds years of experience and job titles

### 3. Scoring Algorithm
- Compares candidate skills with JD requirements
- Evaluates experience level alignment
- Assesses educational background match

### 4. Justification Generation
- Provides detailed explanation for each score
- Lists matched and missing skills
- Suggests improvements with priority levels

## Supported Skills

The parser recognizes:
- **Programming Languages**: Python, Java, JavaScript, TypeScript, Go, etc.
- **Web Frameworks**: Django, Flask, React, Angular, Vue, etc.
- **Databases**: SQL, MySQL, PostgreSQL, MongoDB, Redis, etc.
- **Cloud Platforms**: AWS, Azure, Google Cloud, Docker, Kubernetes, etc.
- **Data Tools**: Pandas, NumPy, TensorFlow, PyTorch, Spark, etc.

## Future Enhancements

- [ ] Add more programming languages and frameworks
- [ ] Implement fuzzy matching for better skill detection
- [ ] Add resume/JD templates
- [ ] Export reports as PDF
- [ ] Batch analysis for multiple resumes
- [ ] Integration with LinkedIn profiles
- [ ] Machine learning-based skill extraction

## API Endpoints

### POST /api/analyze
Upload resume and JD for analysis

**Request:**
```
Content-Type: multipart/form-data
- resume: file
- jd: file
```

**Response:**
```json
{
  "success": true,
  "score": {
    "overall_score": 75.5,
    "skill_match": {
      "score": 80,
      "matched": ["python", "react"],
      "missing": ["kubernetes"]
    },
    "experience_match": {
      "score": 70,
      "explanation": "..."
    },
    "education_match": {
      "score": 75,
      "matched_fields": ["computer science"]
    }
  },
  "justification": {
    "fit_level": "Good Fit",
    "summary": "...",
    "skill_analysis": {...},
    "experience_analysis": {...},
    "education_analysis": {...},
    "improvements": [...]
  }
}
```

## Notes

- Maximum file size: 16MB
- Supported formats: PDF, DOCX, TXT
- Scoring is based on keyword matching and pattern recognition
- Results should be used as a preliminary assessment tool

## License

MIT
