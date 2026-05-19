# Setup Instructions

## Quick Start

### 1. Activate Virtual Environment
```bash
# On Windows PowerShell
.\.venv\Scripts\Activate.ps1

# On Windows Command Prompt
.\.venv\Scripts\activate.bat

# On macOS/Linux
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Download spaCy Language Model
```bash
python -m spacy download en_core_web_sm
```

### 4. Run the Application
```bash
python app.py
```

### 5. Open in Browser
Navigate to: `http://localhost:5000`

## Troubleshooting

### PDF Extraction Issues
If PDF extraction fails, make sure `pdfplumber` is properly installed:
```bash
pip install --upgrade pdfplumber
```

### Port 5000 Already in Use
Change the port in `app.py`:
```python
if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Change 5000 to any available port
```

### File Upload Issues
- Ensure file size is under 16MB
- Use supported formats: PDF, DOCX, TXT
- Check that the `uploads` directory is writable

## Development

### Running Tests
```bash
pytest tests/
```

### Code Quality
```bash
pylint app.py parsers/ scoring/
```

## Production Deployment

For production, use a WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Alternatively, deploy to Render, Heroku, or AWS:
- See deployment guides in the docs folder
