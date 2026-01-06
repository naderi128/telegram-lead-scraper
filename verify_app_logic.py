import sys
from unittest.mock import MagicMock
sys.modules['streamlit'] = MagicMock()
sys.modules['streamlit.set_page_config'] = MagicMock()
sys.modules['streamlit.sidebar'] = MagicMock()
sys.modules['streamlit.session_state'] = {}

# Mock app logic to run scrape function
import asyncio
from app import TgstatScraper

async def verify_scrape():
    print("Initializing TgstatScraper...")
    scraper = TgstatScraper()
    
    print("Testing search_channels...")
    count = 0
    # Use a highly specific keyword we know exists
    keyword = "crypto" 
    
    def debug_callback(msg):
        try:
            print(f"DEBUG: {msg}")
        except UnicodeEncodeError:
            print(f"DEBUG: {msg.encode('ascii', 'ignore').decode()}")

    async for lead in scraper.search_channels(keyword=keyword, limit=3, status_callback=debug_callback):
        print(f"Outcome: Found lead: {lead.get('title')} ({lead.get('username')})")
        count += 1
        
    if count == 0:
        print("Outcome: No leads found. Likely DDG issue or Rate Limit.")
    else:
        print(f"Outcome: Successfully found {count} leads.")

if __name__ == "__main__":
    asyncio.run(verify_scrape())
