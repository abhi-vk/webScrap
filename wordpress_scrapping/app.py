import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

# Target website
url = "https://angelinvestments.co.in"
headers = {"User-Agent": "Mozilla/5.0"}

# Create folders to save images and JSON file
image_folder = "7/downloaded_images"
json_folder = "7"

os.makedirs(image_folder, exist_ok=True)  # Ensure image folder exists
os.makedirs(json_folder, exist_ok=True)  # Ensure JSON folder exists

# Fetch the website content
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

# Scraped data storage
scraped_data = {
    "url": url,
    "title": soup.title.string if soup.title else "No Title",
    "content": [],
    "images": []
}

# Extract text content (paragraphs, headings, lists)
for tag in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "li"]):
    text = tag.get_text(strip=True)
    if text:
        scraped_data["content"].append(text)

# Find all image tags (including lazy-loaded images)
img_tags = soup.find_all("img")

for img in img_tags:
    # Get image URL (handles lazy-loaded images)
    img_url = img.get("src") or img.get("data-src") or img.get("data-lazy-src")

    if img_url:
        # Convert relative URLs to absolute
        img_url = urljoin(url, img_url)

        try:
            # Get image data
            img_data = requests.get(img_url, headers=headers).content
            
            # Extract valid filename (remove invalid characters & query params)
            img_filename = re.sub(r'[\\/*?:"<>|]', "", img_url.split("/")[-1].split("?")[0])
            img_name = os.path.join(image_folder, img_filename)

            # Save the image
            with open(img_name, "wb") as img_file:
                img_file.write(img_data)

            print(f"Downloaded: {img_name}")

            # Store image info in JSON
            scraped_data["images"].append({
                "image_url": img_url,
                "saved_as": img_name
            })

        except Exception as e:
            print(f"Failed to download {img_url}: {e}")

# Save data to JSON file in the "1" folder
json_path = os.path.join(json_folder, "scraped_data.json")
with open(json_path, "w", encoding="utf-8") as json_file:
    json.dump(scraped_data, json_file, indent=4, ensure_ascii=False)

print(f"✅ Scraping complete! Data saved in '{json_path}'")
