# Quick Start Guide

## 🎯 Get Started in 2 Minutes

### Prerequisites
- Python 3.11+
- Claude API Key (free: console.anthropic.com)

### Setup

1. **Clone & Enter Project**
   ```bash
   cd ParserAI
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1  # Windows
   # or
   source .venv/bin/activate     # Mac/Linux
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set API Key**
   Create `.env` file in project root:
   ```
   ANTHROPIC_API_KEY=sk-ant-...your-key...
   ```

5. **Run App**
   ```bash
   python app.py
   ```

6. **Open Browser**
   ```
   http://localhost:5000
   ```

## 📝 Using the Tool

1. **Upload Resume**
   - Click upload area or drag-drop
   - Supports: PDF, DOCX, TXT

2. **Add Job Description**
   - Option A: Upload JD file
   - Option B: Paste JD text

3. **Click "Analyze Now"**

4. **Review Results**
   - Overall match score
   - Detailed skill analysis
   - Experience alignment
   - Expert recommendations
   - Interview talking points
   - Onboarding focus

## 💡 What You Get

- **Match Score** (0-100%)
- **Domain Detection** (healthcare, tech, finance, etc.)
- **Candidate Profile** (extracted intelligently)
- **Skill Analysis** (exact + equivalent + transferable)
- **Experience Assessment** (years + progression)
- **Education Fit** (degree + field alignment)
- **Certification Match** (fuzzy matching)
- **Expert Assessment** (AI-powered analysis)
- **Risk Factors** (what might not work)
- **Upside Factors** (what's great)
- **Interview Talking Points** (what to discuss)
- **Onboarding Focus** (where to train)

## 🔍 Example Scenarios

### Scenario 1: Nurse → L&D Position
- **Result**: 92% match
- **Why**: All certifications matched, exceeds years requirement, domain expertise
- **Recommendation**: Strong Yes - Interview immediately

### Scenario 2: Software Engineer → Product Manager
- **Result**: 68% match
- **Why**: Technical background strong, management experience lighter, leadership potential
- **Recommendation**: Yes - Consider if willing to transition

### Scenario 3: Career Changer → New Industry
- **Result**: 55% match
- **Why**: Transferable skills high, domain knowledge low, trainable
- **Recommendation**: Maybe - Depends on learning ability

## 🎓 Understanding the Score

| Component | Weight (Tech) | What It Measures |
|-----------|---------------|-----------------|
| Skills | 45% | Technical abilities match |
| Experience | 30% | Years + progression fit |
| Education | 15% | Degree + field alignment |
| Certifications | 10% | Required licenses/certs |

*Weights adapt based on job domain*

## ⚙️ Advanced Features

### Domain-Specific Analysis
System automatically detects:
- **Healthcare**: Emphasizes certifications (30%)
- **Tech**: Emphasizes skills (45%)
- **Finance**: Balanced (skills 35%, exp 30%, edu 20%)
- **Sales**: Emphasizes experience (40%)

### Intelligent Matching
- ✅ Recognizes "SQL" = "Database Management"
- ✅ Matches "JavaScript" to "Web Development"
- ✅ Transfers "Project Management" across roles
- ✅ Fuzzy matches certifications (BLS vs BLS-AHA)
- ✅ Detects over-qualification

### Expert Analysis Includes
- Strong areas with explanations
- Weak areas with context
- Career fit assessment
- Cultural indicators
- Risk factors
- Upside potential
- Interview preparation points
- Onboarding recommendations

## 🚀 Deploy to Production

### Option 1: Render (Free Tier)
```bash
git push origin main
# Create new Web Service on render.com
# Connect GitHub repository
# Add ANTHROPIC_API_KEY env variable
# Deploy
```

### Option 2: Docker
```bash
docker build -t parser-ai .
docker run -e ANTHROPIC_API_KEY=sk-ant-... -p 5000:5000 parser-ai
```

### Option 3: Cloud (AWS, Azure, GCP)
- Use CloudRun, App Engine, or Lambda
- Set `ANTHROPIC_API_KEY` environment variable
- Point domain to your deployment

## 📊 Sample Results

### Good Match (92%)
```
Overall: Exceptional Fit
Skills: 95% (all required matched)
Experience: 100% (exceeds requirement)
Education: 100% (degree matched)
Certs: 100% (all present)

Recommendation: Strong Yes
Next Step: Interview immediately
```

### Moderate Match (62%)
```
Overall: Good Fit
Skills: 78% (core skills present)
Experience: 85% (slightly below)
Education: 50% (field relevant)
Certs: 40% (some missing)

Recommendation: Yes, but with caveats
Next Step: Consider with other candidates
```

## 🛠️ Troubleshooting

### "API Key not found"
- Check `.env` file exists
- Verify ANTHROPIC_API_KEY is set
- Restart app after adding key

### "Processing error"
- Check file size < 16MB
- Ensure valid resume/JD format
- Try PDF instead of DOCX

### "Score seems low"
- This is intentional - system is strict
- Check "Missing Skills" section
- Review "Gaps" in analysis
- Certifications heavily weighted in some domains

## 📖 Full Documentation

For more details, see:
- `INTELLIGENT_SYSTEM.md` - Deep dive into architecture
- `ARCHITECTURE.md` - System design
- `README.md` - Features overview
- `LLM_SETUP.md` - LLM configuration

## 🎯 Next Steps

1. **Try with your resume** - Test the system
2. **Analyze competitors** - Compare candidates
3. **Deploy to production** - Share with team
4. **Collect feedback** - Improve over time
5. **Add integrations** - Connect with ATS

---

**Happy analyzing! Your intelligent resume tool is ready.** 🚀
