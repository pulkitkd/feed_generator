# Physics Snapshots

A web-based application that randomly serves snippets from physics textbooks and lectures, including text content, mathematical equations, and associated diagrams. Perfect for physics students, educators, or anyone interested in exploring physics concepts.

## Features

- Extracts content from various physics resources (Feynman Lectures, Brennen's Fluid Dynamics)
- Displays random physics concepts with associated diagrams
- Renders mathematical equations using MathJax
- Provides source attribution and page references
- Clean, modern web interface
- One-click refresh for new content

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/physics-snapshots.git
cd physics-snapshots
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate
```

3. Install required packages:
```bash
pip install flask requests beautifulsoup4 PyMuPDF
```

4. Create a `resources.json` file with your PDF sources:
```json
{
    "lecture_notes": [
        {
            "title": "Your Physics PDF Title",
            "url": "URL to the PDF"
        }
    ]
}
```

## Usage

1. First, process the PDF resources:
```bash
python pdf_pre_processing.py
```
This will:
- Download the specified PDFs
- Extract text and images
- Process and store the content

2. Start the web application:
```bash
python web_display.py
```
The application will:
- Start a local web server
- Automatically open your default browser
- Display random physics content

3. Click "Get New Content" to view different snippets.

## Project Structure

- `pdf_pre_processing.py`: Downloads and processes PDFs
- `fetch_snippet.py`: Handles random content selection
- `web_display.py`: Flask web application
- `resources.json`: Source configuration
- `processed/`: Contains extracted content (generated)
- `pdfs/`: Stores downloaded PDFs (generated)

## Requirements

- Python 3.6+
- Flask
- PyMuPDF (fitz)
- BeautifulSoup4
- Requests

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- The Feynman Lectures on Physics
- Christopher E. Brennen's Fluid Dynamics texts
- MathJax for equation rendering
- Flask web framework 