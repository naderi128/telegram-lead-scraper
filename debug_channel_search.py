import httpx
from bs4 import BeautifulSoup

def debug_channel_search():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    url = "https://tgstat.com/channels/search"
    print(f"Fetching {url}...")
    try:
        response = httpx.get(url, headers=headers, follow_redirects=True, timeout=10.0)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            print(f"Title: {soup.title.string.strip()}")
            
            # Find forms
            forms = soup.find_all('form')
            for i, form in enumerate(forms):
                print(f"Form {i+1}: Action={form.get('action')} Method={form.get('method')}")
                inputs = form.find_all('input')
                for inp in inputs:
                    print(f"  Input: name={inp.get('name')} value={inp.get('value')}")
            
            # Check for 'advanced search' or filter params
            # Maybe I can just pass params to this URL?
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_channel_search()
