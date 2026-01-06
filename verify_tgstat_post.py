import httpx
from bs4 import BeautifulSoup

def verify_with_inspection():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Origin': 'https://tgstat.com',
    }
    
    # Test 1: Ratings URL (GET)
    url_ratings = "https://tgstat.com/ratings"
    # Note: /ratings usually requires category, but try /ratings first or specific
    # Try searching for a specific channel directly to see how it looks?
    # Or just use the global search bar on the home page?
    
    print("Testing GET https://tgstat.com/metrics/crypto ... (guessing URL)")
    # 'metrics' or 'channel/@username' 
    
    # Back to Search POST, but inspect result better
    url = "https://tgstat.com/channels/search"
    
    with httpx.Client(headers=headers, follow_redirects=True, timeout=20.0) as client:
        # Step 1: GET
        r_get = client.get(url)
        soup = BeautifulSoup(r_get.text, 'html.parser')
        token = soup.find('input', {'name': '_tgstat_csrk'})['value']
        
        # Step 2: POST
        data = {
            '_tgstat_csrk': token,
            'q': 'crypto',
            'inAbout': '1',
            'page': '1'
        }
        r_post = client.post(url, data=data)
        
        # Parse
        soup_res = BeautifulSoup(r_post.text, 'html.parser')
        
        # Count all 'div's to see what's happening
        print(f"Total divs: {len(soup_res.find_all('div'))}")
        
        # Find any link with 'channel'
        links = soup_res.find_all('a', href=True)
        channel_links = [l['href'] for l in links if '/channel/@' in l['href']]
        print(f"Channel Links found: {len(channel_links)}")
        if channel_links:
            print(f"Sample: {channel_links[:5]}")
            
        # Try to find 'card-body'
        cards = soup_res.find_all('div', class_='card-body')
        print(f"Card bodies: {len(cards)}")
        if cards:
            print(f"First body text: {' '.join(cards[0].get_text().split()[:20])}")

if __name__ == "__main__":
    verify_with_inspection()
