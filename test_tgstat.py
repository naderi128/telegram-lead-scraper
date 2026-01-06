import httpx
from bs4 import BeautifulSoup

def test_tgstat():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Try probing for channel specific search
    urls = [
        "https://tgstat.com/search?q=crypto&type=channels",
        "https://tgstat.com/search?q=crypto&peer_type=channel",
        "https://tgstat.com/search/channels?q=crypto"
    ]
    
    for url in urls:
        print(f"Testing {url}...")
        try:
            response = httpx.get(url, headers=headers, follow_redirects=True, timeout=10.0)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                title = soup.title.string.strip()
                print(f"  Title: {title}")
                
                # Check if it says 'posts' or 'channels'
                if "channel" in title.lower():
                    print("  -> Possible CHANNEL search match!")
                
                # Look for results
                cards = soup.find_all('div', class_='card')
                print(f"  Cards found: {len(cards)}")
                
                # Print first card text snippet
                if cards:
                    print(f"  First card snippet: {cards[0].get_text()[:100].strip().replace('\n', ' ')}")
                    
        except Exception as e:
            print(f"  Error: {e}")
        print("-" * 20)

if __name__ == "__main__":
    test_tgstat()
