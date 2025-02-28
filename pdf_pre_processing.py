import os
import json
import random
import requests
import fitz  # PyMuPDF
from bs4 import BeautifulSoup
import base64
from pathlib import Path

# Get the base directory (where the script is located)
BASE_DIR = Path(__file__).parent.absolute()

# Load resources file
with open(BASE_DIR / "resources.json", "r") as file:
    resources = json.load(file)

lecture_notes = resources.get("lecture_notes", [])

# Create storage directories
(BASE_DIR / "pdfs").mkdir(exist_ok=True)
(BASE_DIR / "processed").mkdir(exist_ok=True)
(BASE_DIR / "processed" / "images").mkdir(exist_ok=True)

def download_pdf(title, url):
    """Download the PDF if not already present."""
    pdf_path = BASE_DIR / "pdfs" / f"{title}.pdf"
    if not pdf_path.exists():
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(pdf_path, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
        print(f"Downloaded: {title}")
    return pdf_path

def extract_caption(page, image_bbox):
    """Try to extract caption for an image based on text near it."""
    try:
        # Look for text below the image (within 50 points)
        caption_area = fitz.Rect(
            image_bbox.x0,
            image_bbox.y1,
            image_bbox.x1,
            image_bbox.y1 + 50
        )
        caption_text = page.get_text("text", clip=caption_area).strip()
        
        # If caption starts with "Figure" or "Fig.", keep it
        if caption_text.lower().startswith(("figure", "fig")):
            return caption_text
        
        # Look for text above the image
        caption_area = fitz.Rect(
            image_bbox.x0,
            max(0, image_bbox.y0 - 50),
            image_bbox.x1,
            image_bbox.y0
        )
        caption_text = page.get_text("text", clip=caption_area).strip()
        
        if caption_text.lower().startswith(("figure", "fig")):
            return caption_text
        
        return "Caption not available"
    except:
        return "Caption not available"

def save_image(image_data, title, page_num, img_num):
    """Save image to file and return the file path."""
    # Replace spaces with underscores in the title
    safe_title = title.replace(" ", "_")
    image_path = BASE_DIR / "processed" / "images" / f"{safe_title}_page{page_num}_img{img_num}.png"
    with open(image_path, "wb") as f:
        f.write(image_data)
    return image_path

def extract_content(pdf_path, title):
    """Extracts text snippets and images from a PDF."""
    doc = fitz.open(pdf_path)
    extracted_data = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")
        images = page.get_images(full=True)
        
        paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 20]
        if len(paragraphs) > 0:
            paragraph = random.choice(paragraphs[:15])  # Limit paragraph size
        else:
            paragraph = None
        
        image_data = []
        for img_index, img in enumerate(images):
            xref = img[0]
            base_image = doc.extract_image(xref)
            
            # Get image location on page
            image_list = page.get_images(full=True)
            for img_info in image_list:
                if img_info[0] == xref:
                    image_bbox = page.get_image_bbox(img_info)
                    break
            else:
                image_bbox = None
            
            # Extract caption if we found the image location
            caption = extract_caption(page, image_bbox) if image_bbox else "Caption not available"
            
            image_path = save_image(
                base_image["image"],
                title,
                page_num + 1,
                img_index + 1
            )
            # Store relative path instead of absolute path
            rel_path = str(image_path.relative_to(BASE_DIR))
            image_data.append({
                "path": rel_path,
                "caption": caption
            })
        
        extracted_data.append({
            "page": page_num + 1,
            "paragraph": paragraph,
            "images": image_data  # Now contains both paths and captions
        })
    
    return extracted_data

def process_pdfs():
    """Processes all PDFs and stores the extracted content."""
    processed_data = {}
    
    for note in lecture_notes:
        title, url = note["title"], note["url"]
        pdf_path = download_pdf(title, url)
        extracted_content = extract_content(pdf_path, title)
        processed_data[title] = extracted_content
    
    output_path = BASE_DIR / "processed" / "content.json"
    with open(output_path, "w", encoding='utf-8') as file:
        json.dump(processed_data, file, indent=4, ensure_ascii=False)
    
    print("Processing complete. Extracted data stored.")

if __name__ == "__main__":
    process_pdfs()

