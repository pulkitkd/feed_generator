import requests
from bs4 import BeautifulSoup
import random
import io
import os
from PyPDF2 import PdfReader
import re
from urllib.parse import urljoin
import mimetypes

def get_textbook_index_page():
    """Fetch the main index page of the fluid dynamics textbook."""
    base_url = "http://brennen.caltech.edu/fluidbook/"
    response = requests.get(base_url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch index page: {response.status_code}")
    return response.text

def extract_links(html_content, base_url):
    """Extract all links from the HTML content and return full URLs."""
    soup = BeautifulSoup(html_content, 'html.parser')
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
    
    return links

def get_random_page_url(links):
    """Select a random link from the list of links."""
    if not links:
        raise Exception("No links found in the textbook index")
    
    return random.choice(links)

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

def fetch_html_content(url):
    """Fetch and extract text from an HTML page."""
    print(f"Fetching HTML content from {url}...")
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch HTML content: {response.status_code}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.extract()
    
    # Get text from the main content
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

def summarize_with_mistral(text, url, api_key):
    """Use Mistral AI API to summarize the text."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # Truncate text if too long (Mistral may have token limits)
    max_chars = 8000
    truncated_text = text[:max_chars] if len(text) > max_chars else text
    
    payload = {
        "model": "mistral-large-latest",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant specializing in fluid dynamics. Provide a concise summary of the following text from a fluid dynamics textbook."
            },
            {
                "role": "user",
                "content": f"Please summarize the following text from a fluid dynamics textbook page (URL: {url}). Focus on the key concepts, equations, and their significance: \n\n{truncated_text}"
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

def main():
    base_url = "http://brennen.caltech.edu/fluidbook/"
    
    # Get Mistral AI API key from environment variable
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        raise Exception("MISTRAL_API_KEY environment variable not set")
    
    print("Fetching fluid dynamics textbook index...")
    index_html = get_textbook_index_page()
    
    print("Extracting links from the textbook...")
    all_links = extract_links(index_html, base_url)
    print(f"Found {len(all_links)} links in the textbook")
    
    # Try up to 5 times to get a valid page
    max_attempts = 5
    for attempt in range(max_attempts):
        try:
            # Get a random page URL
            random_url = get_random_page_url(all_links)
            print(f"Selected random page: {random_url}")
            
            # Extract content based on file type
            if is_pdf_url(random_url):
                pdf_file = download_pdf(random_url)
                content = extract_text_from_pdf(pdf_file)
            else:
                content = fetch_html_content(random_url)
            
            # If we got meaningful content, proceed
            if content and len(content) > 200:  # Require at least 200 chars
                cleaned_content = clean_text(content)
                print(f"Extracted {len(cleaned_content)} characters of text")
                
                summary = summarize_with_mistral(cleaned_content, random_url, api_key)
                
                # Display results
                print("\n" + "="*80)
                print(f"RANDOM PAGE URL: {random_url}")
                print("="*80)
                print("\nSUMMARY:")
                print(summary)
                print("="*80)
                
                # Success, exit loop
                break
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            if attempt == max_attempts - 1:
                print("All attempts failed to find a valid page to summarize.")
                raise

if __name__ == "__main__":
    main()