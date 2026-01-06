import httpx

def probe_tags():
    keywords = ["crypto", "bitcoin"]
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Try different URL patterns
    patterns = [
        "https://tgstat.com/tag/{}", 
        "https://tgstat.com/tags/{}", 
        "https://tgstat.com/search?q={}",
        "https://eu.tgstat.com/search?q={}" # Try EU mirror?
    ]
    
    for kw in keywords:
        for pat in patterns:
            url = pat.format(kw)
            print(f"Checking {url}...")
            try:
                r = httpx.get(url, headers=headers, follow_redirects=True, timeout=5.0)
                print(f"Status: {r.status_code}")
                if r.status_code == 200:
                    if "channel" in r.text or "t.me/" in r.text:
                        print("  -> Found 'channel' or 't.me' in response!")
                        # Print title
                        if "<title>" in r.text:
                             print(f"  Title: {r.text.split('<title>')[1].split('</title>')[0]}")
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    probe_tags()
