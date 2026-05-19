# Deploy to Render (Free Tier)

## Prerequisites
- GitHub account
- Render account (free at render.com)

## Steps

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit - ParserAI"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ParserAI.git
git push -u origin main
```

### 2. Create Account & Deploy
1. Go to https://render.com
2. Sign up with GitHub
3. Click "New +" → "Web Service"
4. Select your ParserAI repository
5. Configure:
   - **Name**: parser-ai
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: Free

### 3. Deploy
- Click "Create Web Service"
- Wait for build to complete (2-3 minutes)
- Your app will be live at: `https://parser-ai.onrender.com`

## Important Notes

**Free Tier Limitations:**
- App spins down after 15 min of inactivity (first request will be slow)
- Limited RAM/CPU
- Can handle small file uploads (< 10MB)
- Best for testing/development

**For Production:**
- Use Paid tier ($7+/month)
- No spin-down after inactivity
- Better performance

## Troubleshooting

**Build fails?**
- Check build logs in Render dashboard
- Ensure all dependencies are in `requirements.txt`

**Large file uploads fail?**
- Reduce `MAX_CONTENT_LENGTH` in `app.py`:
  ```python
  app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB instead of 16MB
  ```

**App crashes?**
- Check logs: Dashboard → Your app → Logs
- May be spaCy model size issue on free tier

## Alternative: Docker on Render

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN python -m spacy download en_core_web_sm
COPY . .
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:10000"]
```

Then deploy using "Docker" environment instead of Python.
