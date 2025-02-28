from flask import Flask, render_template_string, send_from_directory
from fetch_snippet import fetch_random_snippet
from pathlib import Path
import re
import webbrowser
import threading
import time

app = Flask(__name__)

# Get the base directory
BASE_DIR = Path(__file__).parent.absolute()

# HTML template with modern styling and MathJax support
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Physics Snapshots</title>
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 10px;
        }
        .header-container {
            text-align: center;
            margin-bottom: 30px;
        }
        .content {
            margin-bottom: 20px;
        }
        .metadata {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 20px;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 5px;
        }
        .paragraph {
            text-align: justify;
            padding: 20px;
            background-color: #fff;
            border-left: 4px solid #3498db;
            margin-bottom: 20px;
        }
        .image-container {
            text-align: center;
            margin: 20px 0;
        }
        .image-wrapper {
            margin: 20px 0;
        }
        img {
            max-width: 100%;
            height: auto;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            margin-bottom: 10px;
        }
        .image-caption {
            font-size: 0.9em;
            color: #666;
            margin-top: 8px;
            padding: 0 20px;
            font-style: italic;
        }
        .refresh-btn {
            display: inline-block;
            padding: 8px 20px;
            background-color: #3498db;
            color: white;
            text-align: center;
            text-decoration: none;
            border-radius: 5px;
            transition: background-color 0.3s;
            font-size: 0.9em;
            margin-top: 10px;
        }
        .refresh-btn:hover {
            background-color: #2980b9;
        }
        .source-link {
            color: #3498db;
            text-decoration: none;
        }
        .source-link:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header-container">
            <h1>Physics Snapshots</h1>
            <a href="/" class="refresh-btn">Get New Content</a>
        </div>
        
        <div class="metadata">
            <strong>Source:</strong> 
            <a href="{{ snippet.source_url }}" target="_blank" class="source-link">{{ snippet.pdf_title }}</a>
            <br>
            <strong>Page:</strong> {{ snippet.page_number }}
        </div>

        <div class="content">
            <div class="paragraph">
                {{ snippet.paragraph }}
            </div>

            {% if snippet.images %}
                <div class="image-container">
                    {% for image in snippet.images %}
                        <div class="image-wrapper">
                            <img src="{{ url_for('serve_image', filename=image.path) }}" alt="Physics diagram">
                            <div class="image-caption">{{ image.caption }}</div>
                        </div>
                    {% endfor %}
                </div>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    snippet = fetch_random_snippet()
    if not snippet:
        return "Error: Could not fetch content. Please make sure content.json is available."
    return render_template_string(HTML_TEMPLATE, snippet=snippet)

@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory(BASE_DIR, filename)

def open_browser():
    """Open browser after a short delay"""
    time.sleep(1.5)
    webbrowser.open('http://127.0.0.1:5000/')

if __name__ == '__main__':
    # Open browser in a separate thread
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Run the Flask app
    app.run(debug=True) 