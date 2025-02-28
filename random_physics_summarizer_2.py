import requests
from bs4 import BeautifulSoup
import random
import io
import os
from PyPDF2 import PdfReader
import re
from urllib.parse import urljoin
import ssl
import certifi
from flask import Flask, render_template_string
import threading
import webbrowser

# Disable SSL warnings
requests.packages.urllib3.disable_warnings()

def get_feynman_lecture_urls():
    """Get all URLs from Feynman Lectures website."""
    print("Fetching Feynman Lectures URLs...")
    
    # Base URL for constructing full links
    base_url = "https://www.feynmanlectures.caltech.edu"
    
    # URL of the Feynman Lectures Table of Contents
    toc_url = f"{base_url}/II_toc.html"
    
    # Get the webpage content
    response = requests.get(toc_url, verify=False)
    if response.status_code != 200:
        raise Exception(f"Failed to retrieve the Feynman TOC page: {response.status_code}")
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Find all 'a' tags
    links = soup.find_all("a", href=True)
    
    # Extract valid lecture URLs
    urls = []
    for link in links:
        href = link["href"]
        
        # Check if href contains 'Goto'
        match = re.search(r'Goto\((\d+),(\d+)(?:,(\d+))?\)', href)
        if match:
            volume = match.group(1)  # Volume number (1, 2, or 3)
            chapter = match.group(2).zfill(2)  # Chapter number, zero-padded
            section = match.group(3)  # Section number (if available)
            
            # Construct the base lecture URL
            lecture_url = f"{base_url}/{'I' if volume == '1' else 'II' if volume == '2' else 'III'}_{chapter}.html"
            
            # Append section anchor if available
            if section:
                lecture_url += f"#Ch{int(chapter)}-S{int(section)}"
            
            urls.append(lecture_url)
    
    print(f"Found {len(urls)} Feynman lecture URLs")
    return urls

def get_brennen_textbook_urls():
    """Get all URLs from Brennen's fluid dynamics textbook."""
    print("Fetching Brennen's fluid dynamics textbook URLs...")
    
    base_url = "http://brennen.caltech.edu/fluidbook/"
    response = requests.get(base_url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch Brennen index page: {response.status_code}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    
    # Find all link tags
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        # Skip external links and anchors
        if href.startswith('http') or href.startswith('#'):
            continue
        # Build full URL
        full_url = urljoin(base_url, href)
        links.append(full_url)
    
    print(f"Found {len(links)} Brennen textbook URLs")
    return links

def get_random_resource_url():
    """Randomly choose between Feynman lectures and Brennen textbook, then return a random URL."""
    print("Gathering all resource URLs...")
    
    # Get URLs from both resources
    feynman_urls = get_feynman_lecture_urls()
    brennen_urls = get_brennen_textbook_urls()
    
    # Choose which resource to use
    resource_choice = random.choice(["feynman", "brennen"])
    
    if resource_choice == "feynman":
        print("Randomly selected: Feynman Lectures")
        return random.choice(feynman_urls), "feynman"
    else:
        print("Randomly selected: Brennen's Fluid Dynamics Textbook")
        return random.choice(brennen_urls), "brennen"

def is_pdf_url(url):
    """Check if a URL points to a PDF file."""
    return url.lower().endswith('.pdf')

def download_pdf(url):
    """Download a PDF file from a URL."""
    print(f"Downloading PDF from {url}...")
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to download PDF: {response.status_code}")
    return io.BytesIO(response.content)

def extract_text_from_pdf(pdf_file):
    """Extract text content from a PDF file."""
    print("Extracting text from PDF...")
    try:
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

def fetch_html_content(url, resource_type):
    """Fetch and extract text from an HTML page."""
    print(f"Fetching HTML content from {url}...")
    
    # Handle SSL verification differently for Feynman lectures
    verify = True
    if resource_type == "feynman":
        verify = False
    
    response = requests.get(url, verify=verify)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch HTML content: {response.status_code}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.extract()
    
    # For Feynman lectures, we should focus on the main content area
    if resource_type == "feynman":
        main_content = soup.find('div', class_='content')
        if main_content:
            text = main_content.get_text(separator=' ', strip=True)
        else:
            text = soup.get_text(separator=' ', strip=True)
    else:
        # Get text from the main content for Brennen's textbook
        text = soup.get_text(separator=' ', strip=True)
    
    # Clean up the text (remove excessive whitespace)
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = ' '.join(chunk for chunk in chunks if chunk)
    
    return text

def clean_text(text):
    """Clean and prepare text for summarization."""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def summarize_with_mistral(text, url, resource_type, api_key):
    """Use Mistral AI API to summarize the text."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # Truncate text if too long (Mistral may have token limits)
    max_chars = 8000
    truncated_text = text[:max_chars] if len(text) > max_chars else text
    
    # Adjust system prompt based on the resource type
    if resource_type == "feynman":
        system_prompt = "You are a helpful assistant specializing in physics. Provide a concise summary of the following text from a Feynman Lecture."
    else:
        system_prompt = "You are a helpful assistant specializing in fluid dynamics. Provide a concise summary of the following text from a fluid dynamics textbook."
    
    payload = {
        "model": "mistral-large-latest",
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": f"Please summarize the following text from {'a Feynman Lecture' if resource_type == 'feynman' else 'a fluid dynamics textbook'} (URL: {url}). Focus on the key concepts, equations, and their significance: \n\n{truncated_text}"
            }
        ],
        "temperature": 0.5
    }
    
    print("Sending text to Mistral AI for summarization...")
    response = requests.post(
        "https://api.mistral.ai/v1/chat/completions",
        headers=headers,
        json=payload
    )
    
    if response.status_code != 200:
        raise Exception(f"Mistral API error: {response.status_code} - {response.text}")
    
    response_data = response.json()
    summary = response_data["choices"][0]["message"]["content"]
    
    return summary

def create_web_app():
    """Create a Flask web app to display the results"""
    app = Flask(__name__)
    
    # Global variables to store the summaries
    app.summaries = []
    app.status = "Initializing..."
    
    @app.route('/')
    def home():
        return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Physics Content Summarizer</title>
            <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
            <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
            <script>
            MathJax = {
                tex: { inlineMath: [['$', '$'], ['\\(', '\\)']] }
            };
            document.addEventListener("DOMContentLoaded", function() {
                if (window.MathJax) {
                    window.MathJax.typeset();
                }
            });
            </script>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 20px;
                    max-width: 1000px;
                    margin: 0 auto;
                }
                h1 {
                    color: #2c3e50;
                    border-bottom: 2px solid #3498db;
                    padding-bottom: 10px;
                }
                .resource-info {
                    background-color: #f8f9fa;
                    border-left: 4px solid #3498db;
                    padding: 10px 15px;
                    margin: 20px 0;
                }
                .summary {
                    background-color: #f8f9fa;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    padding: 15px;
                    margin: 20px 0;
                }
                .status {
                    color: #e74c3c;
                    font-style: italic;
                }
                .header {
                    margin-bottom: 20px;
                }
                a {
                    color: #3498db;
                    text-decoration: none;
                }
                a:hover {
                    text-decoration: underline;
                }
                .summary-container {
                    margin-bottom: 40px;
                    border-bottom: 1px dashed #ccc;
                    padding-bottom: 20px;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Physics Content Summarizer</h1>
            </div>
            
            {% if status != "Complete" %}
                <p class="status">{{ status }}</p>
            {% endif %}
            
            {% if summaries %}
                {% for summary_data in summaries %}
                    <div class="summary-container">
                        <div class="resource-info">
                            <h2>{{ summary_data.resource_type }}</h2>
                            <p>Source: <a href="{{ summary_data.url }}" target="_blank">{{ summary_data.url }}</a></p>
                        </div>
                        
                        <h2>Summary</h2>
                        <div class="summary mathjax">
                            {{ summary_data.summary | safe }}
                        </div>
                    </div>
                {% endfor %}
            {% endif %}
        </body>
        </html>
        ''', 
        summaries=[
            {
                "resource_type": s["resource_type"],
                "url": s["url"],
                "summary": s["summary"].replace('\n', '<br>')
            } for s in app.summaries
        ],
        status=app.status
        )
    
    return app

def update_status(app, status):
    """Update the status in the web app"""
    app.status = status

def add_summary(app, resource_type, url, summary):
    """Add a new summary to the web app"""
    app.summaries.append({
        "resource_type": resource_type,
        "url": url,
        "summary": summary
    })

def start_browser(port):
    """Open the browser after a short delay"""
    webbrowser.open(f'http://127.0.0.1:{port}/')

# Modified main function to generate 3 summaries
def main():
    # Create and start the web app
    app = create_web_app()
    port = 5000
    
    # Start the Flask app in a separate thread
    flask_thread = threading.Thread(target=lambda: app.run(debug=False, port=port))
    flask_thread.daemon = True
    flask_thread.start()
    
    # Open browser after a short delay
    threading.Timer(1.5, start_browser, args=[port]).start()
    
    # Get Mistral AI API key from environment variable
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        update_status(app, "Error: MISTRAL_API_KEY environment variable not set")
        return
    
    # Generate 3 summaries
    for summary_num in range(1, 4):
        update_status(app, f"Generating summary {summary_num} of 3...")
        
        # Try up to 3 times for each summary
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                update_status(app, f"Summary {summary_num}: Attempt {attempt+1} - Selecting random resource...")
                
                # Get a random resource URL
                random_url, resource_type = get_random_resource_url()
                resource_name = 'Feynman Lectures' if resource_type == 'feynman' else 'Brennen Fluid Dynamics'
                
                update_status(app, f"Summary {summary_num}: Fetching content from {resource_name}...")
                
                # Extract content based on file type
                if is_pdf_url(random_url):
                    pdf_file = download_pdf(random_url)
                    content = extract_text_from_pdf(pdf_file)
                else:
                    content = fetch_html_content(random_url, resource_type)
                
                # If we got meaningful content, proceed
                if content and len(content) > 200:  # Require at least 200 chars
                    cleaned_content = clean_text(content)
                    
                    update_status(app, f"Summary {summary_num}: Summarizing {len(cleaned_content)} characters of text...")
                    
                    # Create a shorter summary for the multiple view
                    summary = summarize_with_mistral(cleaned_content, random_url, resource_type, api_key)
                    
                    # Add the summary to the web app
                    add_summary(app, resource_name, random_url, summary)
                    
                    # Success, break the attempt loop
                    break
                else:
                    update_status(app, f"Summary {summary_num}: Attempt {attempt+1} failed: Content too short or empty")
            except Exception as e:
                update_status(app, f"Summary {summary_num}: Attempt {attempt+1} failed: {str(e)}")
                if attempt == max_attempts - 1:
                    # Add an error message as a summary if all attempts fail
                    add_summary(app, 
                               "Error", 
                               "#", 
                               f"Failed to generate summary {summary_num} after {max_attempts} attempts.")
    
    update_status(app, "Complete")
    
    # Keep the main thread alive
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Server shutdown.")

if __name__ == "__main__":
    main()


