import httpx
from bs4 import BeautifulSoup

def debug_tgstat():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    urls = [
        "https://tgstat.com/search", 
        "https://tgstat.com/channels"
    ]
    
    for url in urls:
        print(f"Fetching {url}...")
        try:
            response = httpx.get(url, headers=headers, follow_redirects=True, timeout=10.0)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find all forms
                forms = soup.find_all('form')
                print(f"Found {len(forms)} forms.")
                for i, form in enumerate(forms):
                    action = form.get('action', 'No Action')
                    method = form.get('method', 'No Method')
                    print(f"  Form {i+1}: Action={action} Method={method}")
                    # Inputs
                    inputs = form.find_all('input')
                    for inp in inputs:
                        print(f"    Input: name={inp.get('name')} type={inp.get('type')}")

                # Find all links with 'channel' in href
                links = soup.find_all('a', href=True)
                channel_links = [l['href'] for l in links if 'channel' in l['href']]
                print(f"Found {len(channel_links)} links with 'channel'.")
                if channel_links:
                     print(f"Sample: {channel_links[:3]}")

        except Exception as e:
            print(f"Error: {e}")
        print("-" * 20)

if __name__ == "__main__":
    debug_tgstat()
