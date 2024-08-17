# @title Original program accessed from https://www.zenrows.com/blog/web-crawler-python#extract-data-into-csv

import requests
from bs4 import BeautifulSoup
import queue
import re
import time
import random
import csv  # Import the csv module

# Initialize the list to store products
products = []

# To store the URLs discovered to visit in a specific order
urls = queue.PriorityQueue()
# High priority
urls.put((0.5, "https://www.scrapingcourse.com/ecommerce/"))

# To store the pages already visited
visited_urls = []

i=1
# Until all pages have been visited
#while not urls.empty():
while i<10:
    # Get the page to visit from the list
    _, current_url = urls.get()

    # Crawling logic
    response = requests.get(current_url)
    soup = BeautifulSoup(response.content, "html.parser")

    visited_urls.append(current_url)

    link_elements = soup.select("a[href]")
    for link_element in link_elements:
        url = link_element['href']

        # Handle relative URLs
        if not url.startswith("http"):
            url = requests.compat.urljoin(current_url, url)

        # If the URL is relative to scrapingcourse.com or any of its subdomains
        if re.match(r"https://(?:.*\.)?scrapingcourse\.com", url):
            # If the URL discovered is new
            if url not in visited_urls and url not in [item[1] for item in urls.queue]:
                # Low priority
                priority_score = 1
                # If it is a pagination page
                if re.match(r"^https://scrapingcourse\.com/ecommerce/page/\d+/?$", url):
                    # High priority
                    priority_score = 0.5
                urls.put((priority_score, url))

    # Pause the script for a random delay between 1 and 3 seconds
    time.sleep(random.uniform(1, 3))

    # If current_url is a product page
    product = {}
    product["url"] = current_url

    # Handle missing elements gracefully
    product["image"] = soup.select_one(".wp-post-image")["src"] if soup.select_one(".wp-post-image") else "N/A"
    product["name"] = soup.select_one(".product_title").text if soup.select_one(".product_title") else "N/A"
    product["price"] = soup.select_one(".price").text if soup.select_one(".price") else "N/A"

    products.append(product)

    i=i+1

# Initialize the CSV output file
with open('products.csv', 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)

    # Write the header
    writer.writerow(["URL", "Image", "Name", "Price"])

    # Populating the CSV
    for product in products:
        writer.writerow(product.values())





# @title Modifications Introduced

# @title 1] Asynchronous requests/multi-threading - Use multi-threading or asynchronous requests (e.g., using libraries like aiohttp or gevent) to speed up the crawling process

!pip install nest-asyncio

import nest_asyncio
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import queue
import re
import random
import csv

# Apply the nest_asyncio patch
nest_asyncio.apply()

# Initialize the list to store products
products = []

# To store the URLs discovered to visit in a specific order
urls = queue.PriorityQueue()
# High priority
urls.put((0.5, "https://www.scrapingcourse.com/ecommerce/"))

# To store the pages already visited
visited_urls = set()

# Function to fetch and parse a page asynchronously
async def fetch_and_parse(session, url):
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            content = await response.text()
            soup = BeautifulSoup(content, "html.parser")
            return soup
    except (aiohttp.ClientError, Exception) as e:
        print(f"Error fetching {url}: {e}")
        return None

# Function to process URLs
async def process_url(session, current_url):
    # Avoid re-visiting URLs
    if current_url in visited_urls:
        return

    soup = await fetch_and_parse(session, current_url)
    if soup is None:
        return

    visited_urls.add(current_url)

    # Find and queue additional URLs
    link_elements = soup.select("a[href]")
    for link_element in link_elements:
        url = link_element['href']

        # Handle relative URLs
        if not url.startswith("http"):
            url = requests.compat.urljoin(current_url, url)

        # If the URL is relative to scrapingcourse.com or any of its subdomains
        if re.match(r"https://(?:.*\.)?scrapingcourse\.com", url):
            # If the URL discovered is new
            if url not in visited_urls and url not in [item[1] for item in urls.queue]:
                # Low priority
                priority_score = 1
                # If it is a pagination page
                if re.match(r"^https://scrapingcourse\.com/ecommerce/page/\d+/?$", url):
                    # High priority
                    priority_score = 0.5
                urls.put((priority_score, url))

    # If current_url is a product page
    product = {
        "url": current_url,
        "image": soup.select_one(".wp-post-image")["src"] if soup.select_one(".wp-post-image") else "N/A",
        "name": soup.select_one(".product_title").text if soup.select_one(".product_title") else "N/A",
        "price": soup.select_one(".price").text if soup.select_one(".price") else "N/A"
    }

    products.append(product)

# Main function to control the asynchronous crawling
async def main():
    async with aiohttp.ClientSession() as session:
        tasks = []
        i = 1
        while i < 10 and not urls.empty():
            _, current_url = urls.get()
            tasks.append(asyncio.create_task(process_url(session, current_url)))
            i += 1

            # Random delay between requests
            await asyncio.sleep(random.uniform(1, 3))

        # Wait for all tasks to complete
        await asyncio.gather(*tasks)

    # Write products to CSV
    with open('products.csv', 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["URL", "Image", "Name", "Price"])
        for product in products:
            writer.writerow(product.values())

# Run the asynchronous crawler
await main()  # Use 'await' instead of 'asyncio.run()' in Jupyter





# @title 2] JavaScript Execution - For pages relying heavily on JavaScript, use headless browsers to render and crawl dynamic content

pip install playwright

!playwright install

import asyncio
from playwright.async_api import async_playwright
import pandas as pd

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # Launch browser in headless mode
        page = await browser.new_page()  # Open a new page

        # Navigate to the URL and wait for network to be idle
        await page.goto('https://www.scrapingcourse.com/ecommerce/', wait_until='networkidle')

        # Wait for the page to load completely
        await page.wait_for_selector('.product_title', timeout=60000)  # Timeout of 60 seconds

        # Extract data
        products = []
        product_elements = await page.query_selector_all('.product')  # Select all products
        for product in product_elements:
            #title = await product.query_selector('.product_title')
            #title = await title.inner_text() if title else 'N/A'  # Extract title
            price = await product.query_selector('.price')
            price = await price.inner_text() if price else 'N/A'  # Extract price
            image = await product.query_selector('.wp-post-image')
            image = await image.get_attribute('src') if image else 'N/A'  # Extract image URL
            products.append({
                'title': title,
                'price': price,
                'image': image
            })

        # Save to CSV
        df = pd.DataFrame(products)
        df.to_csv('products.csv', index=False)  # Save to CSV

        await browser.close()  # Close the browser

# Run the asynchronous function
asyncio.run(main())





# @title 3] Retry handling (handling temporary failures or timeouts) and Exception handling (prevent the crawler from crashing on unexpected errors)

import nest_asyncio
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import queue
import re
import random
import csv
import requests
import os
import time

# Apply the nest_asyncio patch
nest_asyncio.apply()

# Initialize the list to store products
products = []

# To store the URLs discovered to visit in a specific order
urls = queue.PriorityQueue()
# High priority
urls.put((0.5, "https://www.scrapingcourse.com/ecommerce/"))

# To store the pages already visited
visited_urls = set()

# Semaphore to limit concurrent tasks
semaphore = asyncio.Semaphore(10)

# Function to fetch and parse a page asynchronously with retry
async def fetch_and_parse(session, url, retries=3, delay=1):
    for attempt in range(retries):
        try:
            async with semaphore:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    response.raise_for_status()
                    content = await response.text()
                    soup = BeautifulSoup(content, "html.parser")
                    return soup
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            print(f"Error fetching {url}: {e}")
            if attempt < retries - 1:
                print(f"Retrying {url} in {delay} seconds...")
                await asyncio.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                print(f"Failed to fetch {url} after {retries} attempts.")
                return None
        except Exception as e:
            print(f"Unexpected error with {url}: {e}")
            return None

# Function to process URLs
async def process_url(session, current_url):
    # Avoid re-visiting URLs
    if current_url in visited_urls:
        return

    soup = await fetch_and_parse(session, current_url)
    if soup is None:
        return

    visited_urls.add(current_url)

    # Find and queue additional URLs
    link_elements = soup.select("a[href]")
    for link_element in link_elements:
        url = link_element['href']

        # Handle relative URLs
        if not url.startswith("http"):
            url = requests.compat.urljoin(current_url, url)

        # If the URL is relative to scrapingcourse.com or any of its subdomains
        if re.match(r"https://(?:.*\.)?scrapingcourse\.com", url):
            # If the URL discovered is new
            if url not in visited_urls and url not in [item[1] for item in urls.queue]:
                # Low priority
                priority_score = 1
                # If it is a pagination page
                if re.match(r"^https://scrapingcourse\.com/ecommerce/page/\d+/?$", url):
                    # High priority
                    priority_score = 0.5
                urls.put((priority_score, url))

    # If current_url is a product page
    product = {
        "url": current_url,
        "image": soup.select_one(".wp-post-image")["src"] if soup.select_one(".wp-post-image") else "N/A",
        "name": soup.select_one(".product_title").text if soup.select_one(".product_title") else "N/A",
        "price": soup.select_one(".price").text if soup.select_one(".price") else "N/A"
    }

    products.append(product)

# Main function to control the asynchronous crawling
async def main():
    async with aiohttp.ClientSession() as session:
        tasks = []
        i = 1
        while i < 10 and not urls.empty():
            _, current_url = urls.get()
            tasks.append(asyncio.create_task(process_url(session, current_url)))
            i += 1

            # Random delay between requests
            await asyncio.sleep(random.uniform(1, 3))

        # Wait for all tasks to complete
        await asyncio.gather(*tasks)

    # Write products to CSV
    csv_file_path = 'products.csv'
    header_written = os.path.exists(csv_file_path)
    with open(csv_file_path, 'a', newline='') as csv_file:
        writer = csv.writer(csv_file)
        if not header_written:
            writer.writerow(["URL", "Image", "Name", "Price"])
        for product in products:
            writer.writerow(product.values())

# Run the asynchronous crawler
await main()  # Use 'await' instead of 'asyncio.run()' in Jupyter





# @title 4] Queue Management - Use scalable queue systems to manage large numbers of URLs

pip install pika

import nest_asyncio
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re
import random
import csv
import requests
import os
import redis
import json

# Apply the nest_asyncio patch
nest_asyncio.apply()

# Initialize Redis
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

# Initialize the list to store products
products = []

# To store the pages already visited
visited_urls = set()

# Semaphore to limit concurrent tasks
semaphore = asyncio.Semaphore(10)

# Function to fetch and parse a page asynchronously with retry
async def fetch_and_parse(session, url, retries=3, delay=1):
    for attempt in range(retries):
        try:
            async with semaphore:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    response.raise_for_status()
                    content = await response.text()
                    soup = BeautifulSoup(content, "html.parser")
                    return soup
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            print(f"Error fetching {url}: {e}")
            if attempt < retries - 1:
                print(f"Retrying {url} in {delay} seconds...")
                await asyncio.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                print(f"Failed to fetch {url} after {retries} attempts.")
                return None
        except Exception as e:
            print(f"Unexpected error with {url}: {e}")
            return None

# Function to process URLs
async def process_url(session, current_url):
    # Avoid re-visiting URLs
    if current_url in visited_urls:
        return

    soup = await fetch_and_parse(session, current_url)
    if soup is None:
        return

    visited_urls.add(current_url)

    # Find and queue additional URLs
    link_elements = soup.select("a[href]")
    for link_element in link_elements:
        url = link_element['href']

        # Handle relative URLs
        if not url.startswith("http"):
            url = requests.compat.urljoin(current_url, url)

        # If the URL is relative to scrapingcourse.com or any of its subdomains
        if re.match(r"https://(?:.*\.)?scrapingcourse\.com", url):
            # If the URL discovered is new
            if url not in visited_urls and not redis_client.sismember('visited_urls', url):
                # Low priority
                priority_score = 1
                # If it is a pagination page
                if re.match(r"^https://scrapingcourse\.com/ecommerce/page/\d+/?$", url):
                    # High priority
                    priority_score = 0.5
                redis_client.zadd('url_queue', {url: priority_score})

    # If current_url is a product page
    product = {
        "url": current_url,
        "image": soup.select_one(".wp-post-image")["src"] if soup.select_one(".wp-post-image") else "N/A",
        "name": soup.select_one(".product_title").text if soup.select_one(".product_title") else "N/A",
        "price": soup.select_one(".price").text if soup.select_one(".price") else "N/A"
    }

    products.append(product)
    redis_client.sadd('visited_urls', current_url)

# Main function to control the asynchronous crawling
async def main():
    async with aiohttp.ClientSession() as session:
        while True:
            url_with_priority = redis_client.zpopmax('url_queue')
            if not url_with_priority:
                break
            url, _ = url_with_priority[0]
            await process_url(session, url)

            # Random delay between requests
            await asyncio.sleep(random.uniform(1, 3))

    # Write products to CSV
    csv_file_path = 'products.csv'
    header_written = os.path.exists(csv_file_path)
    with open(csv_file_path, 'a', newline='') as csv_file:
        writer = csv.writer(csv_file)
        if not header_written:
            writer.writerow(["URL", "Image", "Name", "Price"])
        for product in products:
            writer.writerow(product.values())

# Run the asynchronous crawler
await main()  # Use 'await' instead of 'asyncio.run()' in Jupyter





# @title 5] Hashing - Implement a content deduplication mechanism (e.g., hashing the content) to avoid storing duplicate data.

import nest_asyncio
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import queue
import re
import random
import csv
import requests
import os
import hashlib

# Apply the nest_asyncio patch
nest_asyncio.apply()

# Initialize the list to store products
products = []

# To store the URLs discovered to visit in a specific order
urls = queue.PriorityQueue()
urls.put((0.5, "https://www.scrapingcourse.com/ecommerce/"))

# To store the pages already visited
visited_urls = set()

# Set to store content hashes for deduplication
content_hashes = set()

# Semaphore to limit concurrent tasks
semaphore = asyncio.Semaphore(10)

# Function to hash the content of the page
def hash_content(content):
    return hashlib.md5(content.encode('utf-8')).hexdigest()

# Function to fetch and parse a page asynchronously with retry
async def fetch_and_parse(session, url, retries=3, delay=1):
    for attempt in range(retries):
        try:
            async with semaphore:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    response.raise_for_status()
                    content = await response.text()
                    soup = BeautifulSoup(content, "html.parser")
                    return soup
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            print(f"Error fetching {url}: {e}")
            if attempt < retries - 1:
                print(f"Retrying {url} in {delay} seconds...")
                await asyncio.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                print(f"Failed to fetch {url} after {retries} attempts.")
                return None
        except Exception as e:
            print(f"Unexpected error with {url}: {e}")
            return None

# Function to process URLs
async def process_url(session, current_url):
    if current_url in visited_urls:
        return

    soup = await fetch_and_parse(session, current_url)
    if soup is None:
        return

    # Hash the page content
    page_content = soup.get_text()
    content_hash = hash_content(page_content)

    # Check if the hash is already in the set (deduplication check)
    if content_hash in content_hashes:
        print(f"Duplicate content found at {current_url}, skipping...")
        return

    # Add the hash to the set
    content_hashes.add(content_hash)
    visited_urls.add(current_url)

    # Find and queue additional URLs
    link_elements = soup.select("a[href]")
    for link_element in link_elements:
        url = link_element['href']

        # Handle relative URLs
        if not url.startswith("http"):
            url = requests.compat.urljoin(current_url, url)

        # If the URL is relative to scrapingcourse.com or any of its subdomains
        if re.match(r"https://(?:.*\.)?scrapingcourse\.com", url):
            if url not in visited_urls and url not in [item[1] for item in urls.queue]:
                priority_score = 1
                if re.match(r"^https://scrapingcourse\.com/ecommerce/page/\d+/?$", url):
                    priority_score = 0.5
                urls.put((priority_score, url))

    # If current_url is a product page
    product = {
        "url": current_url,
        "image": soup.select_one(".wp-post-image")["src"] if soup.select_one(".wp-post-image") else "N/A",
        "name": soup.select_one(".product_title").text if soup.select_one(".product_title") else "N/A",
        "price": soup.select_one(".price").text if soup.select_one(".price") else "N/A"
    }

    products.append(product)

# Main function to control the asynchronous crawling
async def main():
    async with aiohttp.ClientSession() as session:
        while not urls.empty():
            _, current_url = urls.get()
            await asyncio.create_task(process_url(session, current_url))
            await asyncio.sleep(random.uniform(1, 3))

    # Write products to CSV
    csv_file_path = 'products.csv'
    header_written = os.path.exists(csv_file_path)
    with open(csv_file_path, 'a', newline='') as csv_file:
        writer = csv.writer(csv_file)
        if not header_written:
            writer.writerow(["URL", "Image", "Name", "Price"])
        for product in products:
            writer.writerow(product.values())

# Run the asynchronous crawler
await main()  # Use 'await' instead of 'asyncio.run()' in Jupyter





# @title 6] Finger printing - Use fingerprinting techniques to identify and filter out duplicate content

pip install simhash

import nest_asyncio
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import queue
import re
import random
import csv
import requests
import os
from simhash import Simhash

# Apply the nest_asyncio patch
nest_asyncio.apply()

# Initialize the list to store products
products = []

# To store the URLs discovered to visit in a specific order
urls = queue.PriorityQueue()
urls.put((0.5, "https://www.scrapingcourse.com/ecommerce/"))

# To store the pages already visited
visited_urls = set()

# Set to store content fingerprints for deduplication
fingerprints = set()

# Semaphore to limit concurrent tasks
semaphore = asyncio.Semaphore(10)

# Function to generate a fingerprint from the content
def generate_fingerprint(content):
    tokens = content.split()
    return Simhash(tokens).value

# Function to fetch and parse a page asynchronously with retry
async def fetch_and_parse(session, url, retries=3, delay=1):
    for attempt in range(retries):
        try:
            async with semaphore:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    response.raise_for_status()
                    content = await response.text()
                    soup = BeautifulSoup(content, "html.parser")
                    return soup
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            print(f"Error fetching {url}: {e}")
            if attempt < retries - 1:
                print(f"Retrying {url} in {delay} seconds...")
                await asyncio.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                print(f"Failed to fetch {url} after {retries} attempts.")
                return None
        except Exception as e:
            print(f"Unexpected error with {url}: {e}")
            return None

# Function to process URLs
async def process_url(session, current_url):
    if current_url in visited_urls:
        return

    soup = await fetch_and_parse(session, current_url)
    if soup is None:
        return

    # Generate a fingerprint from the page content
    page_content = soup.get_text()
    fingerprint = generate_fingerprint(page_content)

    # Check if the fingerprint is already in the set (deduplication check)
    if fingerprint in fingerprints:
        print(f"Duplicate or near-duplicate content found at {current_url}, skipping...")
        return

    # Add the fingerprint to the set
    fingerprints.add(fingerprint)
    visited_urls.add(current_url)

    # Find and queue additional URLs
    link_elements = soup.select("a[href]")
    for link_element in link_elements:
        url = link_element['href']

        # Handle relative URLs
        if not url.startswith("http"):
            url = requests.compat.urljoin(current_url, url)

        # If the URL is relative to scrapingcourse.com or any of its subdomains
        if re.match(r"https://(?:.*\.)?scrapingcourse\.com", url):
            if url not in visited_urls and url not in [item[1] for item in urls.queue]:
                priority_score = 1
                if re.match(r"^https://scrapingcourse\.com/ecommerce/page/\d+/?$", url):
                    priority_score = 0.5
                urls.put((priority_score, url))

    # If current_url is a product page
    product = {
        "url": current_url,
        "image": soup.select_one(".wp-post-image")["src"] if soup.select_one(".wp-post-image") else "N/A",
        "name": soup.select_one(".product_title").text if soup.select_one(".product_title") else "N/A",
        "price": soup.select_one(".price").text if soup.select_one(".price") else "N/A"
    }

    products.append(product)

# Main function to control the asynchronous crawling
async def main():
    async with aiohttp.ClientSession() as session:
        while not urls.empty():
            _, current_url = urls.get()
            await asyncio.create_task(process_url(session, current_url))
            await asyncio.sleep(random.uniform(1, 3))

    # Write products to CSV
    csv_file_path = 'products.csv'
    header_written = os.path.exists(csv_file_path)
    with open(csv_file_path, 'a', newline='') as csv_file:
        writer = csv.writer(csv_file)
        if not header_written:
            writer.writerow(["URL", "Image", "Name", "Price"])
        for product in products:
            writer.writerow(product.values())

# Run the asynchronous crawler
await main()  # Use 'await' instead of 'asyncio.run()' in Jupyter





# @title 7] Real-time Monitoring - Set up real-time monitoring to track the crawler’s progress and identify any issues quickly

import requests
from bs4 import BeautifulSoup
import queue
import re
import time
import random
import csv
import logging
from logging.handlers import RotatingFileHandler

# Set up logging with rotation
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler = RotatingFileHandler('crawler.log', maxBytes=1000000, backupCount=5)
log_handler.setFormatter(log_formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)
logger.addHandler(console_handler)

# Initialize the list to store products
products = []

# To store the URLs discovered to visit in a specific order
urls = queue.PriorityQueue()
urls.put((0.5, "https://www.scrapingcourse.com/ecommerce/"))

# To store the pages already visited
visited_urls = []

# Retry settings
max_retries = 3
retry_delay = 2

# Initialize counters
pages_visited = 0
products_scraped = 0

i = 1
while i < 10:
    _, current_url = urls.get()

    retries = 0
    success = False
    while retries < max_retries and not success:
        try:
            response = requests.get(current_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            success = True
        except requests.exceptions.RequestException as e:
            retries += 1
            logger.warning(f"Error fetching {current_url}: {e}. Retrying {retries}/{max_retries}...")
            time.sleep(retry_delay)

    if not success:
        logger.error(f"Failed to fetch {current_url} after {max_retries} retries.")
        continue

    visited_urls.append(current_url)
    pages_visited += 1

    link_elements = soup.select("a[href]")
    for link_element in link_elements:
        url = link_element['href']
        if not url.startswith("http"):
            url = requests.compat.urljoin(current_url, url)

        if re.match(r"https://(?:.*\.)?scrapingcourse\.com", url):
            if url not in visited_urls and url not in [item[1] for item in urls.queue]:
                priority_score = 1
                if re.match(r"^https://scrapingcourse\.com/ecommerce/page/\d+/?$", url):
                    priority_score = 0.5
                urls.put((priority_score, url))

    time.sleep(random.uniform(1, 3))

    product = {
        "url": current_url,
        "image": soup.select_one(".wp-post-image")["src"] if soup.select_one(".wp-post-image") else "N/A",
        "name": soup.select_one(".product_title").text if soup.select_one(".product_title") else "N/A",
        "price": soup.select_one(".price").text if soup.select_one(".price") else "N/A"
    }

    products.append(product)
    products_scraped += 1
    logger.info(f"Scraped product: {product['name']} from {current_url}")

    if i % 5 == 0:  # Output a progress summary every 5 iterations
        logger.info(f"Progress Summary: {pages_visited} pages visited, {products_scraped} products scraped, {urls.qsize()} URLs remaining in the queue")

    i += 1

# Initialize the CSV output file
with open('products.csv', 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["URL", "Image", "Name", "Price"])
    for product in products:
        writer.writerow(product.values())

logger.info("Scraping completed. Products saved to products.csv")





# @title 8] Throttle Requests - Adjust crawling speed based on the target site's load to avoid getting blocked

import requests
from bs4 import BeautifulSoup
import queue
import re
import time
import random
import csv
import logging
from logging.handlers import RotatingFileHandler

# Set up logging with rotation
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler = RotatingFileHandler('crawler.log', maxBytes=1000000, backupCount=5)
log_handler.setFormatter(log_formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)
logger.addHandler(console_handler)

# Initialize the list to store products
products = []

# To store the URLs discovered to visit in a specific order
urls = queue.PriorityQueue()
urls.put((0.5, "https://www.scrapingcourse.com/ecommerce/"))

# To store the pages already visited
visited_urls = []

# Retry settings
max_retries = 3
retry_delay = 2

# Throttling settings
min_delay = 1  # Minimum delay in seconds
max_delay = 5  # Maximum delay in seconds
current_delay = min_delay  # Start with the minimum delay

# Initialize counters
pages_visited = 0
products_scraped = 0

i = 1
while i < 10:
    _, current_url = urls.get()

    retries = 0
    success = False
    start_time = time.time()  # Track the request start time
    while retries < max_retries and not success:
        try:
            response = requests.get(current_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            success = True
        except requests.exceptions.RequestException as e:
            retries += 1
            logger.warning(f"Error fetching {current_url}: {e}. Retrying {retries}/{max_retries}...")
            time.sleep(retry_delay)

    if not success:
        logger.error(f"Failed to fetch {current_url} after {max_retries} retries.")
        continue

    # Calculate the response time and adjust the delay accordingly
    response_time = time.time() - start_time
    if response_time > 2:  # If the response time exceeds 2 seconds, increase the delay
        current_delay = min(current_delay + 1, max_delay)
    else:
        current_delay = max(current_delay - 1, min_delay)

    logger.info(f"Response time: {response_time:.2f}s, adjusting delay to: {current_delay}s")

    visited_urls.append(current_url)
    pages_visited += 1

    link_elements = soup.select("a[href]")
    for link_element in link_elements:
        url = link_element['href']
        if not url.startswith("http"):
            url = requests.compat.urljoin(current_url, url)

        if re.match(r"https://(?:.*\.)?scrapingcourse\.com", url):
            if url not in visited_urls and url not in [item[1] for item in urls.queue]:
                priority_score = 1
                if re.match(r"^https://scrapingcourse\.com/ecommerce/page/\d+/?$", url):
                    priority_score = 0.5
                urls.put((priority_score, url))

    # Throttle the requests by pausing based on the adjusted delay
    time.sleep(current_delay)

    product = {
        "url": current_url,
        "image": soup.select_one(".wp-post-image")["src"] if soup.select_one(".wp-post-image") else "N/A",
        "name": soup.select_one(".product_title").text if soup.select_one(".product_title") else "N/A",
        "price": soup.select_one(".price").text if soup.select_one(".price") else "N/A"
    }

    products.append(product)
    products_scraped += 1
    logger.info(f"Scraped product: {product['name']} from {current_url}")

    if i % 5 == 0:  # Output a progress summary every 5 iterations
        logger.info(f"Progress Summary: {pages_visited} pages visited, {products_scraped} products scraped, {urls.qsize()} URLs remaining in the queue")

    i += 1

# Initialize the CSV output file
with open('products.csv', 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["URL", "Image", "Name", "Price"])
    for product in products:
        writer.writerow(product.values())

logger.info("Scraping completed. Products saved to products.csv")





# @title 9] User agent managament - Rotate user agents to mimic different browsers and reduce the chances of getting blocked

import requests
from bs4 import BeautifulSoup
import queue
import re
import time
import random
import csv
import logging
from logging.handlers import RotatingFileHandler

# Set up logging with rotation
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler = RotatingFileHandler('crawler.log', maxBytes=1000000, backupCount=5)
log_handler.setFormatter(log_formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)
logger.addHandler(console_handler)

# User agent list for rotation
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
]

# Initialize the list to store products
products = []

# To store the URLs discovered to visit in a specific order
urls = queue.PriorityQueue()
urls.put((0.5, "https://www.scrapingcourse.com/ecommerce/"))

# To store the pages already visited
visited_urls = []

# Retry settings
max_retries = 3
retry_delay = 2

# Throttling settings
min_delay = 1  # Minimum delay in seconds
max_delay = 5  # Maximum delay in seconds
current_delay = min_delay  # Start with the minimum delay

# Initialize counters
pages_visited = 0
products_scraped = 0

i = 1
while i < 10:
    _, current_url = urls.get()

    retries = 0
    success = False
    start_time = time.time()  # Track the request start time

    # Rotate user agents
    user_agent = random.choice(user_agents)
    headers = {"User-Agent": user_agent}

    while retries < max_retries and not success:
        try:
            response = requests.get(current_url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            success = True
        except requests.exceptions.RequestException as e:
            retries += 1
            logger.warning(f"Error fetching {current_url} with {user_agent}: {e}. Retrying {retries}/{max_retries}...")
            time.sleep(retry_delay)

    if not success:
        logger.error(f"Failed to fetch {current_url} after {max_retries} retries.")
        continue

    # Calculate the response time and adjust the delay accordingly
    response_time = time.time() - start_time
    if response_time > 2:  # If the response time exceeds 2 seconds, increase the delay
        current_delay = min(current_delay + 1, max_delay)
    else:
        current_delay = max(current_delay - 1, min_delay)

    logger.info(f"Response time: {response_time:.2f}s, adjusting delay to: {current_delay}s")

    visited_urls.append(current_url)
    pages_visited += 1

    link_elements = soup.select("a[href]")
    for link_element in link_elements:
        url = link_element['href']
        if not url.startswith("http"):
            url = requests.compat.urljoin(current_url, url)

        if re.match(r"https://(?:.*\.)?scrapingcourse\.com", url):
            if url not in visited_urls and url not in [item[1] for item in urls.queue]:
                priority_score = 1
                if re.match(r"^https://scrapingcourse\.com/ecommerce/page/\d+/?$", url):
                    priority_score = 0.5
                urls.put((priority_score, url))

    # Throttle the requests by pausing based on the adjusted delay
    time.sleep(current_delay)

    product = {
        "url": current_url,
        "image": soup.select_one(".wp-post-image")["src"] if soup.select_one(".wp-post-image") else "N/A",
        "name": soup.select_one(".product_title").text if soup.select_one(".product_title") else "N/A",
        "price": soup.select_one(".price").text if soup.select_one(".price") else "N/A"
    }

    products.append(product)
    products_scraped += 1
    logger.info(f"Scraped product: {product['name']} from {current_url}")

    if i % 5 == 0:  # Output a progress summary every 5 iterations
        logger.info(f"Progress Summary: {pages_visited} pages visited, {products_scraped} products scraped, {urls.qsize()} URLs remaining in the queue")

    i += 1

# Initialize the CSV output file
with open('products.csv', 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["URL", "Image", "Name", "Price"])
    for product in products:
        writer.writerow(product.values())

logger.info("Scraping completed. Products saved to products.csv")





# @title 10] Key word filtering - prioritize or exclude certain pages based on their content

import requests
from bs4 import BeautifulSoup
import queue
import re
import time
import random
import csv
import logging
from logging.handlers import RotatingFileHandler

# Set up logging with rotation
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler = RotatingFileHandler('crawler.log', maxBytes=1000000, backupCount=5)
log_handler.setFormatter(log_formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)
logger.addHandler(console_handler)

# User agent list for rotation
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
]

# Keywords for filtering
include_keywords = ["sale", "discount", "offer"]
exclude_keywords = ["out of stock", "expired"]

# Initialize the list to store products
products = []

# To store the URLs discovered to visit in a specific order
urls = queue.PriorityQueue()
urls.put((0.5, "https://www.scrapingcourse.com/ecommerce/"))

# To store the pages already visited
visited_urls = []

# Retry settings
max_retries = 3
retry_delay = 2

# Throttling settings
min_delay = 1  # Minimum delay in seconds
max_delay = 5  # Maximum delay in seconds
current_delay = min_delay  # Start with the minimum delay

# Initialize counters
pages_visited = 0
products_scraped = 0

i = 1
while i < 10:
    _, current_url = urls.get()

    retries = 0
    success = False
    start_time = time.time()  # Track the request start time

    # Rotate user agents
    user_agent = random.choice(user_agents)
    headers = {"User-Agent": user_agent}

    while retries < max_retries and not success:
        try:
            response = requests.get(current_url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            success = True
        except requests.exceptions.RequestException as e:
            retries += 1
            logger.warning(f"Error fetching {current_url} with {user_agent}: {e}. Retrying {retries}/{max_retries}...")
            time.sleep(retry_delay)

    if not success:
        logger.error(f"Failed to fetch {current_url} after {max_retries} retries.")
        continue

    # Calculate the response time and adjust the delay accordingly
    response_time = time.time() - start_time
    if response_time > 2:  # If the response time exceeds 2 seconds, increase the delay
        current_delay = min(current_delay + 1, max_delay)
    else:
        current_delay = max(current_delay - 1, min_delay)

    logger.info(f"Response time: {response_time:.2f}s, adjusting delay to: {current_delay}s")

    visited_urls.append(current_url)
    pages_visited += 1

    # Keyword filtering
    page_text = soup.get_text().lower()

    if any(keyword in page_text for keyword in exclude_keywords):
        logger.info(f"Skipping {current_url} due to exclusion keywords.")
        continue

    if not any(keyword in page_text for keyword in include_keywords):
        logger.info(f"Skipping {current_url} as it does not contain inclusion keywords.")
        continue

    link_elements = soup.select("a[href]")
    for link_element in link_elements:
        url = link_element['href']
        if not url.startswith("http"):
            url = requests.compat.urljoin(current_url, url)

        if re.match(r"https://(?:.*\.)?scrapingcourse\.com", url):
            if url not in visited_urls and url not in [item[1] for item in urls.queue]:
                priority_score = 1
                if re.match(r"^https://scrapingcourse\.com/ecommerce/page/\d+/?$", url):
                    priority_score = 0.5
                urls.put((priority_score, url))

    # Throttle the requests by pausing based on the adjusted delay
    time.sleep(current_delay)

    product = {
        "url": current_url,
        "image": soup.select_one(".wp-post-image")["src"] if soup.select_one(".wp-post-image") else "N/A",
        "name": soup.select_one(".product_title").text if soup.select_one(".product_title") else "N/A",
        "price": soup.select_one(".price").text if soup.select_one(".price") else "N/A"
    }

    products.append(product)
    products_scraped += 1
    logger.info(f"Scraped product: {product['name']} from {current_url}")

    if i % 5 == 0:  # Output a progress summary every 5 iterations
        logger.info(f"Progress Summary: {pages_visited} pages visited, {products_scraped} products scraped, {urls.qsize()} URLs remaining in the queue")

    i += 1

# Initialize the CSV output file
with open('products.csv', 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["URL", "Image", "Name", "Price"])
    for product in products:
        writer.writerow(product.values())

logger.info("Scraping completed. Products saved to products.csv")





# @title 11] Adaptive Crawling - heuristic method to adaptively decide which pages to crawl next based on their relevance or importance

import requests
from bs4 import BeautifulSoup
import queue
import re
import time
import random
import csv
import logging
from logging.handlers import RotatingFileHandler

# Set up logging with rotation
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler = RotatingFileHandler('crawler.log', maxBytes=1000000, backupCount=5)
log_handler.setFormatter(log_formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)
logger.addHandler(console_handler)

# User agent list for rotation
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
]

# Keywords for filtering
include_keywords = ["sale", "discount", "offer"]
exclude_keywords = ["out of stock", "expired"]

# Initialize the list to store products
products = []

# To store the URLs discovered to visit in a specific order
urls = queue.PriorityQueue()
urls.put((0.5, "https://www.scrapingcourse.com/ecommerce/"))

# To store the pages already visited
visited_urls = []

# Retry settings
max_retries = 3
retry_delay = 2

# Throttling settings
min_delay = 1  # Minimum delay in seconds
max_delay = 5  # Maximum delay in seconds
current_delay = min_delay  # Start with the minimum delay

# Initialize counters
pages_visited = 0
products_scraped = 0

# Feature extraction for relevance scoring
def extract_features(soup):
    text = soup.get_text().lower()
    word_count = len(text.split())
    include_count = sum(text.count(keyword) for keyword in include_keywords)
    exclude_count = sum(text.count(keyword) for keyword in exclude_keywords)
    return word_count, include_count, exclude_count

# Scoring function to decide page relevance
def score_page(word_count, include_count, exclude_count):
    score = include_count * 10 - exclude_count * 20 + word_count * 0.1
    return score

i = 1
while i < 10:
    _, current_url = urls.get()

    retries = 0
    success = False
    start_time = time.time()  # Track the request start time

    # Rotate user agents
    user_agent = random.choice(user_agents)
    headers = {"User-Agent": user_agent}

    while retries < max_retries and not success:
        try:
            response = requests.get(current_url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            success = True
        except requests.exceptions.RequestException as e:
            retries += 1
            logger.warning(f"Error fetching {current_url} with {user_agent}: {e}. Retrying {retries}/{max_retries}...")
            time.sleep(retry_delay)

    if not success:
        logger.error(f"Failed to fetch {current_url} after {max_retries} retries.")
        continue

    # Calculate the response time and adjust the delay accordingly
    response_time = time.time() - start_time
    if response_time > 2:  # If the response time exceeds 2 seconds, increase the delay
        current_delay = min(current_delay + 1, max_delay)
    else:
        current_delay = max(current_delay - 1, min_delay)

    logger.info(f"Response time: {response_time:.2f}s, adjusting delay to: {current_delay}s")

    visited_urls.append(current_url)
    pages_visited += 1

    # Feature extraction and scoring
    word_count, include_count, exclude_count = extract_features(soup)
    relevance_score = score_page(word_count, include_count, exclude_count)

    logger.info(f"Page relevance score for {current_url}: {relevance_score}")

    # If relevance score is below a certain threshold, skip the page
    if relevance_score < 10:
        logger.info(f"Skipping {current_url} due to low relevance score.")
        continue

    link_elements = soup.select("a[href]")
    for link_element in link_elements:
        url = link_element['href']
        if not url.startswith("http"):
            url = requests.compat.urljoin(current_url, url)

        if re.match(r"https://(?:.*\.)?scrapingcourse\.com", url):
            if url not in visited_urls and url not in [item[1] for item in urls.queue]:
                priority_score = 1 / (relevance_score + 1)  # Inverse of the relevance score for prioritization
                if re.match(r"^https://scrapingcourse\.com/ecommerce/page/\d+/?$", url):
                    priority_score = 0.5
                urls.put((priority_score, url))

    # Throttle the requests by pausing based on the adjusted delay
    time.sleep(current_delay)

    product = {
        "url": current_url,
        "image": soup.select_one(".wp-post-image")["src"] if soup.select_one(".wp-post-image") else "N/A",
        "name": soup.select_one(".product_title").text if soup.select_one(".product_title") else "N/A",
        "price": soup.select_one(".price").text if soup.select_one(".price") else "N/A"
    }

    products.append(product)
    products_scraped += 1
    logger.info(f"Scraped product: {product['name']} from {current_url}")

    if i % 5 == 0:  # Output a progress summary every 5 iterations
        logger.info(f"Progress Summary: {pages_visited} pages visited, {products_scraped} products scraped, {urls.qsize()} URLs remaining in the queue")

    i += 1

# Initialize the CSV output file
with open('products.csv', 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["URL", "Image", "Name", "Price"])
    for product in products:
        writer.writerow(product.values())

logger.info("Scraping completed. Products saved to products.csv")





# @title 12] CAPTCHA Handling - Implement solutions for handling CAPTCHAs

import requests
from bs4 import BeautifulSoup
import queue
import re
import time
import random
import csv
import logging
from logging.handlers import RotatingFileHandler

# Set up logging with rotation
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler = RotatingFileHandler('crawler.log', maxBytes=1000000, backupCount=5)
log_handler.setFormatter(log_formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)
logger.addHandler(console_handler)

# User agent list for rotation
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
]

# CAPTCHA API key (replace with your actual key)
captcha_api_key = 'your_2captcha_api_key'

# Initialize the list to store products
products = []

# To store the URLs discovered to visit in a specific order
urls = queue.PriorityQueue()
urls.put((0.5, "https://www.scrapingcourse.com/ecommerce/"))

# To store the pages already visited
visited_urls = []

# Retry settings
max_retries = 3
retry_delay = 2

# Throttling settings
min_delay = 1  # Minimum delay in seconds
max_delay = 5  # Maximum delay in seconds
current_delay = min_delay  # Start with the minimum delay

# Initialize counters
pages_visited = 0
products_scraped = 0

# Function to solve CAPTCHA using 2Captcha
def solve_captcha(captcha_url):
    # Step 1: Request CAPTCHA solving
    response = requests.post(
        'http://2captcha.com/in.php',
        data={
            'key': captcha_api_key,
            'method': 'userrecaptcha',
            'googlekey': 'your_google_site_key',  # Replace with the actual Google reCAPTCHA site key
            'pageurl': captcha_url,
            'json': 1
        }
    )
    request_result = response.json()
    if request_result['status'] == 1:
        captcha_id = request_result['request']
        # Step 2: Wait for CAPTCHA solving
        for _ in range(20):
            time.sleep(5)
            result = requests.get(
                'http://2captcha.com/res.php',
                params={
                    'key': captcha_api_key,
                    'action': 'get',
                    'id': captcha_id,
                    'json': 1
                }
            ).json()
            if result['status'] == 1:
                return result['request']
    raise Exception("CAPTCHA solving failed")

# Feature extraction for relevance scoring
def extract_features(soup):
    text = soup.get_text().lower()
    word_count = len(text.split())
    include_count = sum(text.count(keyword) for keyword in include_keywords)
    exclude_count = sum(text.count(keyword) for keyword in exclude_keywords)
    return word_count, include_count, exclude_count

# Scoring function to decide page relevance
def score_page(word_count, include_count, exclude_count):
    score = include_count * 10 - exclude_count * 20 + word_count * 0.1
    return score

i = 1
while i < 10:
    _, current_url = urls.get()

    retries = 0
    success = False
    start_time = time.time()  # Track the request start time

    # Rotate user agents
    user_agent = random.choice(user_agents)
    headers = {"User-Agent": user_agent}

    while retries < max_retries and not success:
        try:
            response = requests.get(current_url, headers=headers)
            if 'captcha' in response.url.lower():  # Check if CAPTCHA is detected
                captcha_solution = solve_captcha(current_url)
                # Include CAPTCHA solution in the request if needed
                response = requests.get(current_url, headers=headers, params={'captcha_solution': captcha_solution})
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            success = True
        except requests.exceptions.RequestException as e:
            retries += 1
            logger.warning(f"Error fetching {current_url} with {user_agent}: {e}. Retrying {retries}/{max_retries}...")
            time.sleep(retry_delay)

    if not success:
        logger.error(f"Failed to fetch {current_url} after {max_retries} retries.")
        continue

    # Calculate the response time and adjust the delay accordingly
    response_time = time.time() - start_time
    if response_time > 2:  # If the response time exceeds 2 seconds, increase the delay
        current_delay = min(current_delay + 1, max_delay)
    else:
        current_delay = max(current_delay - 1, min_delay)

    logger.info(f"Response time: {response_time:.2f}s, adjusting delay to: {current_delay}s")

    visited_urls.append(current_url)
    pages_visited += 1

    # Feature extraction and scoring
    word_count, include_count, exclude_count = extract_features(soup)
    relevance_score = score_page(word_count, include_count, exclude_count)

    logger.info(f"Page relevance score for {current_url}: {relevance_score}")

    # If relevance score is below a certain threshold, skip the page
    if relevance_score < 10:
        logger.info(f"Skipping {current_url} due to low relevance score.")
        continue

    link_elements = soup.select("a[href]")
    for link_element in link_elements:
        url = link_element['href']
        if not url.startswith("http"):
            url = requests.compat.urljoin(current_url, url)

        if re.match(r"https://(?:.*\.)?scrapingcourse\.com", url):
            if url not in visited_urls and url not in [item[1] for item in urls.queue]:
                priority_score = 1 / (relevance_score + 1)  # Inverse of the relevance score for prioritization
                if re.match(r"^https://scrapingcourse\.com/ecommerce/page/\d+/?$", url):
                    priority_score = 0.5
                urls.put((priority_score, url))

    # Throttle the requests by pausing based on the adjusted delay
    time.sleep(current_delay)

    product = {
        "url": current_url,
        "image": soup.select_one(".wp-post-image")["src"] if soup.select_one(".wp-post-image") else "N/A",
        "name": soup.select_one(".product_title").text if soup.select_one(".product_title") else "N/A",
        "price": soup.select_one(".price").text if soup.select_one(".price") else "N/A"
    }

    products.append(product)
    products_scraped += 1
    logger.info(f"Scraped product: {product['name']} from {current_url}")

    if i % 5 == 0:  # Output a progress summary every 5 iterations
        logger.info(f"Progress Summary: {pages_visited} pages visited, {products_scraped} products scraped, {urls.qsize()} URLs remaining in the queue")

    i += 1

# Initialize the CSV output file
with open('products.csv', 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["URL", "Image", "Name", "Price"])
    for product in products:
        writer.writerow(product.values())

logger.info("Scraping completed. Products saved to products.csv")





# @title 13] Proxy server rotation - To avoid IP bans and distribute requests across different IPs

import requests
from bs4 import BeautifulSoup
import queue
import re
import time
import random
import csv

# Initialize the list to store products
products = []

# To store the URLs discovered to visit in a specific order
urls = queue.PriorityQueue()
urls.put((0.5, "https://www.scrapingcourse.com/ecommerce/"))

# To store the pages already visited
visited_urls = set()

# User-Agent rotation
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:91.0) Gecko/20100101 Firefox/91.0",
]

# Proxy list
proxies_list = [
    {"http": "http://proxy1.example.com:port", "https": "https://proxy1.example.com:port"},
    {"http": "http://proxy2.example.com:port", "https": "https://proxy2.example.com:port"},
    # Add more proxies as needed
]

def get_random_user_agent():
    return random.choice(user_agents)

def get_random_proxy():
    return random.choice(proxies_list)

i = 1
while not urls.empty() and i < 10:
    priority, current_url = urls.get()

    try:
        headers = {"User-Agent": get_random_user_agent()}
        proxy = get_random_proxy()
        response = requests.get(current_url, headers=headers, proxies=proxy, timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses
        soup = BeautifulSoup(response.content, "html.parser")
    except requests.RequestException as e:
        print(f"Request failed for {current_url}: {e}")
        continue

    visited_urls.add(current_url)

    link_elements = soup.select("a[href]")
    for link_element in link_elements:
        url = link_element['href']

        # Handle relative URLs
        if not url.startswith("http"):
            url = requests.compat.urljoin(current_url, url)

        # If the URL is relative to scrapingcourse.com or any of its subdomains
        if re.match(r"https://(?:.*\.)?scrapingcourse\.com", url):
            if url not in visited_urls and url not in [item[1] for item in urls.queue]:
                priority_score = 1
                if re.match(r"^https://scrapingcourse\.com/ecommerce/page/\d+/?$", url):
                    priority_score = 0.5
                urls.put((priority_score, url))

    # Pause the script for a random delay between 1 and 3 seconds
    time.sleep(random.uniform(1, 3))

    # Extract product information
    product = {
        "url": current_url,
        "image": soup.select_one(".wp-post-image")["src"] if soup.select_one(".wp-post-image") else "N/A",
        "name": soup.select_one(".product_title").text.strip() if soup.select_one(".product_title") else "N/A",
        "price": soup.select_one(".price").text.strip() if soup.select_one(".price") else "N/A"
    }

    products.append(product)
    i += 1

# Write data to CSV
with open('products.csv', 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["URL", "Image", "Name", "Price"])

    for product in products:
        writer.writerow([product["url"], product["image"], product["name"], product["price"]])





# @title 14] Efficient Storage - Use efficient storage systems like MongoDB handling large volumes of crawled data

pip install pymongo

import requests
from bs4 import BeautifulSoup
import queue
import re
import time
import random
from pymongo import MongoClient

# Initialize MongoDB client and database
client = MongoClient('mongodb://localhost:27017/')
db = client['web_scraper']
collection = db['products']

# To store the URLs discovered to visit in a specific order
urls = queue.PriorityQueue()
urls.put((0.5, "https://www.scrapingcourse.com/ecommerce/"))

# To store the pages already visited
visited_urls = set()

# User-Agent rotation
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:91.0) Gecko/20100101 Firefox/91.0",
]

def get_random_user_agent():
    return random.choice(user_agents)

i = 1
while not urls.empty() and i < 10:
    priority, current_url = urls.get()

    try:
        headers = {"User-Agent": get_random_user_agent()}
        response = requests.get(current_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
    except requests.RequestException as e:
        print(f"Request failed for {current_url}: {e}")
        continue

    visited_urls.add(current_url)

    link_elements = soup.select("a[href]")
    for link_element in link_elements:
        url = link_element['href']
        if not url.startswith("http"):
            url = requests.compat.urljoin(current_url, url)
        if re.match(r"https://(?:.*\.)?scrapingcourse\.com", url):
            if url not in visited_urls and url not in [item[1] for item in urls.queue]:
                priority_score = 1
                if re.match(r"^https://scrapingcourse\.com/ecommerce/page/\d+/?$", url):
                    priority_score = 0.5
                urls.put((priority_score, url))

    time.sleep(random.uniform(1, 3))

    product = {
        "url": current_url,
        "image": soup.select_one(".wp-post-image")["src"] if soup.select_one(".wp-post-image") else "N/A",
        "name": soup.select_one(".product_title").text.strip() if soup.select_one(".product_title") else "N/A",
        "price": soup.select_one(".price").text.strip() if soup.select_one(".price") else "N/A"
    }

    # Insert product into MongoDB
    collection.insert_one(product)
    i += 1





# @title 15] Data Cleaning - To ensure the stored data is relevant and free of noise

import requests
from bs4 import BeautifulSoup
import queue
import re
import time
import random
import csv

# Initialize the list to store products
products = []

# To store the URLs discovered to visit in a specific order
urls = queue.PriorityQueue()
urls.put((0.5, "https://www.scrapingcourse.com/ecommerce/"))

# To store the pages already visited
visited_urls = set()

# A set to track seen product URLs to avoid duplicates
seen_product_urls = set()

i = 1
while i < 10 and not urls.empty():
    _, current_url = urls.get()

    if current_url in visited_urls:
        continue

    try:
        # Crawling logic
        response = requests.get(current_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        visited_urls.add(current_url)

        link_elements = soup.select("a[href]")
        for link_element in link_elements:
            url = link_element['href']

            # Handle relative URLs
            if not url.startswith("http"):
                url = requests.compat.urljoin(current_url, url)

            # If the URL is relative to scrapingcourse.com or any of its subdomains
            if re.match(r"https://(?:.*\.)?scrapingcourse\.com", url):
                if url not in visited_urls and url not in [item[1] for item in urls.queue]:
                    priority_score = 1
                    if re.match(r"^https://scrapingcourse\.com/ecommerce/page/\d+/?$", url):
                        priority_score = 0.5
                    urls.put((priority_score, url))

        # Pause the script for a random delay between 1 and 3 seconds
        time.sleep(random.uniform(1, 3))

        # If current_url is a product page
        if current_url in seen_product_urls:
            continue

        product = {}
        product["url"] = current_url

        # Handle missing elements gracefully
        product["image"] = soup.select_one(".wp-post-image")["src"] if soup.select_one(".wp-post-image") else "N/A"
        product["name"] = soup.select_one(".product_title").text.strip() if soup.select_one(".product_title") else "N/A"
        product["price"] = soup.select_one(".price").text.strip() if soup.select_one(".price") else "N/A"

        # Data Cleaning
        # Remove unwanted characters from price, if necessary
        product["price"] = re.sub(r'[^\d.,]', '', product["price"])

        # Skip empty products
        if all(value == "N/A" for value in product.values()):
            continue

        products.append(product)
        seen_product_urls.add(current_url)

    except requests.RequestException as e:
        print(f"Request failed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

    i += 1

# Initialize the CSV output file
with open('products.csv', 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)

    # Write the header
    writer.writerow(["URL", "Image", "Name", "Price"])

    # Populating the CSV
    for product in products:
        writer.writerow(product.values())
