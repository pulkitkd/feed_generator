import requests
from bs4 import BeautifulSoup
import random
import webbrowser
import re
import os
import certifi
from urllib.parse import urljoin

def get_feynman_lecture_urls():
    """Get all URLs from Feynman Lectures website."""
    print("Fetching Feynman Lectures URLs...")
    base_url = "https://www.feynmanlectures.caltech.edu"
    toc_url = f"{base_url}/II_toc.html"
    
    response = requests.get(toc_url, verify=certifi.where())
    if response.status_code != 200:
        raise Exception(f"Failed to retrieve the Feynman TOC page: {response.status_code}")
    
    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("a", href=True)
    
    urls = []
    for link in links:
        href = link["href"]
        match = re.search(r'Goto\((\d+),(\d+)(?:,(\d+))?\)', href)
        if match:
            volume = match.group(1)
            chapter = match.group(2).zfill(2)
            section = match.group(3)
            lecture_url = f"{base_url}/{'I' if volume == '1' else 'II' if volume == '2' else 'III'}_{chapter}.html"
            if section:
                lecture_url += f"#Ch{int(chapter)}-S{int(section)}"
            urls.append(lecture_url)
    
    print(f"Found {len(urls)} Feynman lecture URLs")
    return urls

def extract_images(url):
    """Extract all images from a given Feynman Lecture page."""
    print(f"Fetching images from {url}...")
    response = requests.get(url, verify=certifi.where())
    if response.status_code != 200:
        print(f"Failed to fetch page: {response.status_code}")
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    base_url = "https://www.feynmanlectures.caltech.edu"
    images = []
    
    for img in soup.find_all('img'):
        img_url = img.get('src')
        if img_url and not img_url.startswith("data:"):
            full_url = urljoin(base_url, img_url)
            images.append(full_url)
    
    return images

def download_image(image_url):
    """Download the image and save it locally."""
    response = requests.get(image_url, stream=True, verify=certifi.where())
    if response.status_code == 200:
        local_filename = os.path.join("./", os.path.basename(image_url))
        with open(local_filename, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        return local_filename
    else:
        print("Failed to download image.")
        return None

def main():
    urls = get_feynman_lecture_urls()
    if not urls:
        print("No lecture URLs found.")
        return
    
    random_url = random.choice(urls)
    images = extract_images(random_url)
    
    if not images:
        print("No images found on the page.")
        return
    
    random_image = random.choice(images)
    local_image = download_image(random_image)
    
    if local_image:
        print(f"Opening image: {local_image}")
        webbrowser.open(f"file://{os.path.abspath(local_image)}")

if __name__ == "__main__":
    main()
