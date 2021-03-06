import os
import requests
from bs4 import BeautifulSoup
from collections import deque
from typing import Deque, Tuple
from enum import Enum

INDEX_URL = "https://introcomputing.org/"
SAVE_FOLDER = "./static/"

# if save folder is not exist, create it
if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)
    
downloaded = set()
downloaded.add(INDEX_URL)

# download the index page
index_html = requests.get(INDEX_URL)

# save the index page
with open(SAVE_FOLDER + "index.html", "wb") as f:
    f.write(index_html.content)

class FileType(Enum):
    HTML = "html"
    IMAGE = "image"
    CSS = "css"
    JS = "js"

files_to_download: Deque[Tuple[FileType, str]] = deque()

def process_html(file_content):
    # we get bytes, so we need to decode it
    file_content = file_content.decode("utf-8")
    # parse the file
    file_soup = BeautifulSoup(file_content, "html.parser")

    # add any links to the list of files to download
    for link in file_soup.find_all("a"):
        link_url = link.get("href")

        # is this url a relative link?
        if not link_url.startswith("http"):
            # add the link to the list of files to download
            files_to_download.append((FileType.HTML, link_url))
            
    # add any images to the list of files to download
    for img in file_soup.find_all("img"):
        img_url = img.get("src")

        # is this url a relative link?
        if img_url and not img_url.startswith("http"):
            # add the link to the list of files to download
            files_to_download.append((FileType.IMAGE, img_url))

    # add any css files to the list of files to download
    for link in file_soup.find_all("link"):
        link_url = link.get("href")

        # is this url a relative link?
        if link_url and not link_url.startswith("http"):
            # add the link to the list of files to download
            files_to_download.append((FileType.CSS, link_url))

    # add any js files to the list of files to download
    for script in file_soup.find_all("script"):
        script_url = script.get("src")
        
        if not script_url:
            continue

        # is this url a relative link?
        if not script_url.startswith("http"):
            # add the link to the list of files to download
            files_to_download.append((FileType.JS, script_url))
            
        if script_url.startswith("http") and not script_url.startswith("https"):
            # change the url to https
            script_url = script_url.replace("http", "https", 1)
            script["src"] = script_url
            
    return file_soup.prettify("utf-8")
            
# initalize the list of files to download
process_html(index_html.content)

# ok we will now download all the files
while len(files_to_download) > 0:
    # get the next file to download
    file_type, file_url = files_to_download.popleft()
    
    print(f"Downloading {file_url}")
    
    if file_url in downloaded:
        continue
    
    downloaded.add(file_url)

    # download the file
    file_html = requests.get(INDEX_URL + file_url)
    file_content = file_html.content
    
    if file_type == FileType.HTML:
        file_content = process_html(file_content)

    # save the file
    with open(SAVE_FOLDER + file_url, "wb") as f:
        f.write(file_content)

