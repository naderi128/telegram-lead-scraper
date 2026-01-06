from duckduckgo_search import DDGS

def verify_broad():
    queries = [
        'tgstat crypto channel',
        'site:tgstat.com crypto',
        'site:tgstat.ru crypto'
    ]
    
    for q in queries:
        print(f"--- Query: {q} ---")
        try:
            results = DDGS().text(q, max_results=10)
            if results:
                for r in results:
                    print(f"Title: {r.get('title')}")
                    print(f"URL: {r.get('href')}")
            else:
                print("No results.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    verify_broad()
