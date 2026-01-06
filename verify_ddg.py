from duckduckgo_search import DDGS
import httpx
from bs4 import BeautifulSoup
import time

def verify_ddg_mock():
    # 1. Search
    query = 'site:tgstat.com/channel "crypto"'
    print(f"Searching for: {query}")
    
    # Standard DDGS usage
    results = DDGS().text(query, max_results=5)
    
    found_urls = []
    if results:
        for res in results:
            url = res.get('href')
            print(f"Found URL: {url}")
            if 'tgstat.com/channel/' in url:
                found_urls.append(url)
    
    if not found_urls:
        print("No channel URLs found.")
        return

    # 2. Scrape one page
    target_url = found_urls[0]
    print(f"Scraping {target_url}...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
    
    try:
        r = httpx.get(target_url, headers=headers, follow_redirects=True, timeout=10.0)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            
            title = soup.title.string.strip() if soup.title else "No Title"
            print(f"Title: {title}")
            
            # Try to find specific details
            # Username often in h1 or header
            # Members count usually in a stat box
            
            # Just dump some text to see if we got content
            body_text = soup.body.get_text() if soup.body else ""
            print(f"Body text snippet: {' '.join(body_text.split()[:50])}...")
            
            # Find participants count
            # Often has 'subscribers' or 'members'
            
    except Exception as e:
        print(f"Error scraping page: {e}")

if __name__ == "__main__":
    verify_ddg_mock()
