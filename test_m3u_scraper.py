# test_m3u_scraper.py

import requests
from bs4 import BeautifulSoup

# Function to scrape m3u links

def scrape_m3u_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    m3u_links = []

    # Find all links with m3u extension
    for link in soup.find_all('a'):
        href = link.get('href')
        if href and href.endswith('.m3u'):
            m3u_links.append(href)

    return m3u_links

# Test the function
if __name__ == '__main__':
    test_url = 'https://streamsports99.su'
    links = scrape_m3u_links(test_url)
    print('Found m3u links:', links)