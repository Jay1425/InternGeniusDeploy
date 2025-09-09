# 🎓 InternGenius - Frontend Demo

This directory contains a simplified version of the InternGenius platform that serves only the frontend UI without any backend dependencies.

## Quick Start

1. Navigate to this directory and set up a virtual environment:
   ```
   cd demo
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

2. Install the minimal requirements:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python app.py
   ```

4. Open your browser and visit: `http://127.0.0.1:5000`

## Structure

This demo contains only the essential files needed to display the UI:

- `app.py` - Simple Flask application
- `requirements.txt` - Minimal dependencies
- `templates/` - HTML templates
- `static/` - CSS, JavaScript, and image assets

## Notes

- This is a frontend-only demo without any backend functionality
- All links will redirect to the home page
- No data persistence or authentication is included
