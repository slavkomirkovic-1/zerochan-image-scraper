#!/usr/bin/python3

# Web Scraping
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.request import urlopen, Request
from urllib.parse import quote_plus
from re import findall

# File management
from os.path import exists
from os import mkdir

def download_image(url : str) -> None:
    
    '''
        Download the image that was supplied in the url
    '''

    image_name = ".".join(url.split(".")[-2::])
    with open(f"images/{image_name}", "wb") as f:
        try:
            f.write(urlopen(url).read())
        except:
            download_image(url=url)

if not exists("images/"):
    mkdir("images/")

print("Please type what you are looking for")
choice = str(input("> ")).replace(" ","+")

if "http" not in choice:
    # Chosing what we want to scrape
    req = Request(f"https://www.zerochan.net/suggest?q={quote_plus(choice)}&limit=50")
    req.add_header("User-Agent","Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36")
    items = [(x.strip("\n").split("|")[0])for x in urlopen(req).read().decode().split("\n")]
    for index, value in enumerate(items):
        if value:
            print(f"{index+1}. {value}")
    item = int(input("> ")) - 1
    url = f"https://www.zerochan.net/{quote_plus(items[item])}?q={quote_plus(items[item])}"
else:
    url = choice
    if "&p" in url:
        url = url.split("&p")[0]

# Image scraping
regular_expression_no_pages = r"page \d+.+?(\d+).+Zerochan"
p_number = 1
max_p = None

try:
    req.full_url = f"{url}&p={p_number}"
except:
    req = Request(f"{url}&p={p_number}")
    req.add_header("User-Agent","Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36")
response = urlopen(req).read().decode()

number_of_pages = int(findall(r"page.\d+.+?(\d+)", response)[0])
while p_number <= number_of_pages:

    req.full_url = f"{url}&p={p_number}"
    response = urlopen(req).read().decode()

    image_names = findall(r'href=.(.+)">?<s.class=.tiny download"', response)

    if len(image_names) == 0:
        break 

    # I find 2 to be sweet spot but you can change to any number you like.
    with ThreadPoolExecutor(max_workers=2) as executioner:
        futures = {executioner.submit(download_image, image):image for image in image_names}
        for future in as_completed(futures):
            url = futures[future]
            try:
                data = future.result()
            except Exception as f:
                print(f)
                pass

    p_number += 1