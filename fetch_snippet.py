import json
import random
from pathlib import Path

# Get the base directory
BASE_DIR = Path(__file__).parent.absolute()

# Load pre-processed content
def load_processed_data():
    with open(BASE_DIR / "processed" / "content.json", "r") as file:
        return json.load(file)

def fetch_random_snippet():
    """Selects a random PDF, then a random paragraph from it."""
    data = load_processed_data()
    if not data:
        print("No processed data available.")
        return None
    
    pdf_title = random.choice(list(data.keys()))
    pdf_entries = data[pdf_title]
    if not pdf_entries:
        print(f"No data found for {pdf_title}.")
        return None
    
    entry = random.choice(pdf_entries)
    page_num = entry["page"]
    paragraph = entry.get("paragraph", "No text available.")
    images = entry.get("images", [])  # Now contains both paths and captions
    
    # Retrieve the source URL
    with open(BASE_DIR / "resources.json", "r") as file:
        resources = json.load(file)
    
    source_url = next((note["url"] for note in resources["lecture_notes"] if note["title"] == pdf_title), "Unknown")
    
    return {
        "pdf_title": pdf_title,
        "page_number": page_num,
        "paragraph": paragraph,
        "images": images,
        "source_url": source_url
    }

if __name__ == "__main__":
    snippet = fetch_random_snippet()
    if snippet:
        print("Random Snippet:")
        print(f"Title: {snippet['pdf_title']}")
        print(f"Page: {snippet['page_number']}")
        print(f"Text: {snippet['paragraph']}")
        print("\nImages:")
        for image in snippet['images']:
            print(f"- Path: {image['path']}")
            print(f"  Caption: {image['caption']}")
