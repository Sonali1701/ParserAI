# LLM Integration Setup

The ParserAI now supports **optional AI-powered analysis** using Claude API for better accuracy and deeper insights.

## 🚀 How It Works

**Without LLM:**
- ✅ Fast keyword matching (NLP)
- ✅ Works offline, no costs
- ✅ Good for straightforward matches

**With LLM enabled:**
- 🤖 Intelligent contextual understanding
- 📊 Better skill gap analysis
- 📝 Detailed expert assessment
- ⭐ Semantic matching of similar skills
- 💡 Smart recommendations

## ⚙️ Setup (2 Steps)

### Step 1: Get Claude API Key

1. Go to https://console.anthropic.com
2. Sign up or login
3. Go to **API Keys** section
4. Create a new API key
5. Copy the key

### Step 2: Add to Environment

**Option A: Local Testing**
```powershell
$env:ANTHROPIC_API_KEY = "your-api-key-here"
python app.py
```

**Option B: Render Deployment**
1. Go to your Render dashboard
2. Select your app → **Environment**
3. Add new variable:
   - Key: `ANTHROPIC_API_KEY`
   - Value: `your-api-key-here`
4. Deploy

**Option C: .env File**
Create `.env` file in project root:
```
ANTHROPIC_API_KEY=your-api-key-here
```

## 💰 Cost Considerations

- **Claude 3.5 Sonnet:** ~$3 per 1M input tokens, $15 per 1M output tokens
- **Typical analysis:** ~2,000 input tokens + ~500 output tokens = **$0.006 per analysis**
- **Free tier:** If you're building a product, consider:
  - First 1M tokens free (testing)
  - Then very affordable pricing
  - Or implement caching to reduce calls

## 🧪 Test It

```powershell
.\.venv\Scripts\Activate.ps1

# Set your API key
$env:ANTHROPIC_API_KEY = "sk-ant-..."

python app.py
```

Upload a resume & JD. You'll see:
- ✅ Standard analysis (fast)
- ✅ **AI-Powered Deep Analysis** section (if LLM available)

## 🔄 Fallback Behavior

If LLM API fails or key is missing:
- ✅ NLP analysis still works
- ✅ App doesn't crash
- ✅ User gets standard results

## 📈 Product Positioning

**This hybrid approach is production-ready:**
- Use NLP for speed & reliability
- Use LLM for quality & depth
- Best of both worlds
- Cheap to scale

## Next Steps

1. Enable LLM for better results
2. Monitor API costs
3. Add caching for repeated analyses
4. Build batch processing for multiple resumes

