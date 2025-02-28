import requests
from bs4 import BeautifulSoup
import re

# Base URL for constructing full links
base_url = "https://www.feynmanlectures.caltech.edu"

# URL of the Feynman Lectures Table of Contents
toc_url = f"{base_url}/II_toc.html"
# toc_url = base_url

# Get the webpage content
response = requests.get(toc_url, verify=False)
if response.status_code == 200:
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

    # Print extracted URLs
    for url in urls:
        print(url)
else:
    print("Failed to retrieve the page.")
