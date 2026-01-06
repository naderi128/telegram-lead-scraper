"""
Telegram Lead Scraper - Core Scraper Module
Handles Telethon API interactions, SQLite database, and anti-ban measures.
"""

import asyncio
import re
import sqlite3
import random
from datetime import datetime
from typing import Optional, AsyncGenerator, Callable
from pathlib import Path

from telethon import TelegramClient
from telethon.tl.functions.contacts import SearchRequest
from telethon.tl.types import Channel, Chat
from telethon.errors import FloodWaitError, SessionPasswordNeededError


import os
import sqlite3

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = object # Dummy for type hinting if needed or just ignore
    print("[WARNING] Supabase library not installed. Using SQLite only.")

# Supabase configuration
_supabase: Optional['Client'] = None
# SQLite configuration
DB_PATH = Path(__file__).parent / "leads.db"

def init_database(url: Optional[str] = None, key: Optional[str] = None) -> None:
    """
    Initialize Database.
    Priority: Supabase (if keys provided) -> SQLite (local file).
    """
    global _supabase
    
    # 1. Try Supabase
    if not url:
        url = os.environ.get("SUPABASE_URL")
    if not key:
        key = os.environ.get("SUPABASE_KEY")
        
    if SUPABASE_AVAILABLE and url and key:
        try:
            _supabase = create_client(url, key)
            print("✅ Connected to Supabase")
            return
        except Exception as e:
            print(f"Supabase connection error: {e}")
            _supabase = None

    # 2. Fallback to SQLite
    print("[INFO] Supabase credentials not found/failed. Using local SQLite.")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            channel_id INTEGER PRIMARY KEY,
            username TEXT,
            title TEXT,
            category_tag TEXT,
            members_count INTEGER,
            bio_text TEXT,
            admin_contact TEXT,
            scraped_date TEXT
        )
    """)
    conn.commit()
    conn.close()

def upsert_lead(
    channel_id: int,
    username: Optional[str],
    title: str,
    category_tag: str,
    members_count: int,
    bio_text: Optional[str],
    admin_contact: Optional[str]
) -> None:
    """Insert or update a lead record (Supabase or SQLite)."""
    global _supabase
    scraped_date = datetime.now().isoformat()
    
    # 1. Supabase
    if _supabase:
        data = {
            "channel_id": channel_id,
            "username": username,
            "title": title,
            "category_tag": category_tag,
            "members_count": members_count,
            "bio_text": bio_text,
            "admin_contact": admin_contact,
            "scraped_date": scraped_date
        }
        try:
            _supabase.table("leads").upsert(data, on_conflict="channel_id").execute()
        except Exception as e:
            print(f"Supabase upsert error: {e}")
        return

    # 2. SQLite
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO leads (
                channel_id, username, title, category_tag, 
                members_count, bio_text, admin_contact, scraped_date
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(channel_id) DO UPDATE SET
                username = excluded.username,
                title = excluded.title,
                category_tag = excluded.category_tag,
                members_count = excluded.members_count,
                bio_text = excluded.bio_text,
                admin_contact = excluded.admin_contact,
                scraped_date = excluded.scraped_date
        """, (
            channel_id, username, title, category_tag,
            members_count, bio_text, admin_contact, scraped_date
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"SQLite upsert error: {e}")

def get_all_leads() -> list[dict]:
    """Retrieve all leads from Supabase or SQLite."""
    global _supabase
    
    # 1. Supabase
    if _supabase:
        try:
            response = _supabase.table("leads").select("*").order("scraped_date", desc=True).execute()
            return response.data
        except Exception as e:
            print(f"Supabase fetch error: {e}")
            return []

    # 2. SQLite
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM leads ORDER BY scraped_date DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"SQLite fetch error: {e}")
        return []

def get_leads_count() -> int:
    """Get total count of leads."""
    global _supabase
    
    # 1. Supabase
    if _supabase:
        try:
            response = _supabase.table("leads").select("*", count="exact", head=True).execute()
            return response.count
        except Exception:
            return 0

    # 2. SQLite
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM leads")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception:
        return 0




# Anti-ban configuration
MIN_DELAY = 2.0
MAX_DELAY = 5.0

def get_random_delay() -> float:
    """Generate a random delay between MIN_DELAY and MAX_DELAY seconds."""
    return random.uniform(MIN_DELAY, MAX_DELAY)

def extract_admin_contacts(bio_text: Optional[str]) -> Optional[str]:
    """
    Extract potential admin usernames from bio text.
    Looks for patterns like @username.
    """
    if not bio_text:
        return None
    
    # Regex to match Telegram usernames (@ followed by alphanumeric and underscores)
    pattern = r'@([a-zA-Z][a-zA-Z0-9_]{4,31})'
    matches = re.findall(pattern, bio_text)
    
    if matches:
        # Return comma-separated list of found usernames
        return ", ".join([f"@{m}" for m in matches])
    
    return None

class TelegramScraper:
    """
    Telegram channel/group scraper with anti-ban protection.
    """
    
    def __init__(
        self,
        api_id: int,
        api_hash: str,
        phone: str,
        session_name: str = "telegram_scraper"
    ):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        self.session_path = Path(__file__).parent / f"{session_name}.session"
        self.client: Optional[TelegramClient] = None
        self._request_count = 0
        self._max_requests: Optional[int] = None
    
    def set_max_requests(self, max_requests: Optional[int]) -> None:
        """Set maximum number of requests for this run."""
        self._max_requests = max_requests
        self._request_count = 0
    
    def _check_request_limit(self) -> bool:
        """Check if we've reached the request limit."""
        if self._max_requests is None:
            return True
        return self._request_count < self._max_requests
    
    async def connect(self) -> bool:
        """
        Connect to Telegram and handle authentication.
        Returns True if connected and authorized.
        """
        self.client = TelegramClient(
            str(self.session_path),
            self.api_id,
            self.api_hash
        )
        
        await self.client.connect()
        
        if not await self.client.is_user_authorized():
            return False
        
        return True
    
    async def send_code(self) -> str:
        """Send verification code to phone. Returns phone_code_hash."""
        if self.client is None:
            await self.connect()
        
        result = await self.client.send_code_request(self.phone)
        return result.phone_code_hash
    
    async def sign_in(self, code: str, phone_code_hash: str, password: Optional[str] = None) -> bool:
        """
        Sign in with verification code.
        Returns True if successful.
        """
        try:
            await self.client.sign_in(
                phone=self.phone,
                code=code,
                phone_code_hash=phone_code_hash
            )
            return True
        except SessionPasswordNeededError:
            if password:
                await self.client.sign_in(password=password)
                return True
            else:
                raise ValueError("Two-factor authentication is enabled. Please provide password.")
        except Exception as e:
            raise e
    
    async def disconnect(self) -> None:
        """Disconnect from Telegram."""
        if self.client:
            await self.client.disconnect()
    
    async def search_channels(
        self,
        keyword: str,
        limit: int = 50,
        category_tag: str = "",
        status_callback: Optional[Callable[[str], None]] = None,
        flood_callback: Optional[Callable[[int], None]] = None
    ) -> AsyncGenerator[dict, None]:
        """
        Search for public channels/groups with anti-ban protection.
        
        Args:
            keyword: Search keyword
            limit: Maximum results per keyword
            category_tag: Category to tag the leads with
            status_callback: Callback for status updates
            flood_callback: Callback when FloodWait is encountered
        
        Yields:
            Dict with channel information
        """
        if not self.client:
            raise RuntimeError("Client not connected. Call connect() first.")
        
        try:
            # Apply random delay before search
            delay = get_random_delay()
            if status_callback:
                status_callback(f"⏳ Waiting {delay:.1f}s before searching '{keyword}'...")
            await asyncio.sleep(delay)
            
            # Perform search with FloodWait handling
            try:
                self._request_count += 1
                result = await self.client(SearchRequest(
                    q=keyword,
                    limit=limit
                ))
            except FloodWaitError as e:
                if flood_callback:
                    flood_callback(e.seconds)
                if status_callback:
                    status_callback(f"🚫 FloodWait! Sleeping for {e.seconds} seconds...")
                await asyncio.sleep(e.seconds)
                # Retry after waiting
                result = await self.client(SearchRequest(
                    q=keyword,
                    limit=limit
                ))
            
            # Process results
            entities = result.chats if hasattr(result, 'chats') else []
            
            for entity in entities:
                if not self._check_request_limit():
                    if status_callback:
                        status_callback("⚠️ Max requests limit reached. Stopping.")
                    return
                
                # Only process channels and supergroups
                if not isinstance(entity, (Channel, Chat)):
                    continue
                
                # Get full info with FloodWait handling
                try:
                    delay = get_random_delay()
                    if status_callback:
                        status_callback(f"⏳ Waiting {delay:.1f}s before fetching details...")
                    await asyncio.sleep(delay)
                    
                    self._request_count += 1
                    full_entity = await self.client.get_entity(entity.id)
                    
                    # Try to get full channel info for bio
                    bio_text = None
                    try:
                        if hasattr(entity, 'username') and entity.username:
                            full_info = await self.client.get_entity(f"@{entity.username}")
                            if hasattr(full_info, 'about'):
                                bio_text = full_info.about
                    except:
                        pass
                    
                except FloodWaitError as e:
                    if flood_callback:
                        flood_callback(e.seconds)
                    if status_callback:
                        status_callback(f"🚫 FloodWait! Sleeping for {e.seconds} seconds...")
                    await asyncio.sleep(e.seconds)
                    continue
                except Exception as e:
                    if status_callback:
                        status_callback(f"⚠️ Error fetching entity: {str(e)[:50]}")
                    continue
                
                # Extract info
                channel_id = entity.id
                username = getattr(entity, 'username', None)
                title = getattr(entity, 'title', 'Unknown')
                members_count = getattr(entity, 'participants_count', 0) or 0
                
                # Extract admin contacts from bio
                admin_contact = extract_admin_contacts(bio_text)
                
                # Save to database
                upsert_lead(
                    channel_id=channel_id,
                    username=username,
                    title=title,
                    category_tag=category_tag,
                    members_count=members_count,
                    bio_text=bio_text,
                    admin_contact=admin_contact
                )
                
                yield {
                    'channel_id': channel_id,
                    'username': username,
                    'title': title,
                    'category_tag': category_tag,
                    'members_count': members_count,
                    'bio_text': bio_text,
                    'admin_contact': admin_contact
                }
                
        except FloodWaitError as e:
            if flood_callback:
                flood_callback(e.seconds)
            if status_callback:
                status_callback(f"🚫 FloodWait! Sleeping for {e.seconds} seconds...")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            if status_callback:
                status_callback(f"❌ Error: {str(e)}")
            raise


import httpx
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

# ... [Keep existing functions and TelegramScraper] ...

class TgstatScraper:
    """
    Scraper for tgstat.com using DuckDuckGo for discovery and httpx for content.
    """
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://tgstat.com/',
            'X-Requested-With': 'XMLHttpRequest', # Crucial for search to work
        }
    
    async def search_channels(
        self,
        keyword: str,
        limit: int = 50,
        category_tag: str = "",
        status_callback: Optional[Callable[[str], None]] = None
    ) -> AsyncGenerator[dict, None]:
        """
        Search for channels via DDG pointing to tgstat.com, then scrape details.
        """
        if status_callback:
            status_callback(f"🔎 searching for '{keyword}' via DuckDuckGo...")
            
    async def _get_ddg_results(self, query: str, limit: int) -> list:
        try:
            return DDGS().text(query, max_results=limit)
        except Exception:
            return []

    async def _search_direct_tgstat(self, keyword: str, limit: int) -> list:
        """
        Fallback: Try to search directly on tgstat.com using their form.
        """
        results = []
        url_search = "https://tgstat.com/channels/search"
        
        try:
            async with httpx.AsyncClient(headers=self.headers, follow_redirects=True, timeout=20.0) as client:
                # 1. GET to get token
                r_get = await client.get(url_search)
                if r_get.status_code != 200:
                    return []
                
                soup = BeautifulSoup(r_get.text, 'html.parser')
                token_input = soup.find('input', {'name': '_tgstat_csrk'})
                if not token_input:
                    return []
                token = token_input['value']
                
                # 2. POST
                data = {
                    '_tgstat_csrk': token,
                    'q': keyword,
                    'inAbout': '1',
                    'page': '1'
                }
                
                # Add delay
                await asyncio.sleep(random.uniform(2.0, 4.0))
                
                r_post = await client.post(url_search, data=data)
                if r_post.status_code != 200:
                    return []
                
                # Parse JSON response
                try:
                    json_data = r_post.json()
                    html_content = json_data.get('html', '')
                    soup_res = BeautifulSoup(html_content, 'html.parser')
                except:
                    # Fallback if not JSON (though it should be with the header)
                    soup_res = BeautifulSoup(r_post.text, 'html.parser')
                
                # Parse cards
                links = soup_res.find_all('a', href=True)
                for l in links:
                    href = l['href']
                    # Matches: https://tgstat.com/channel/@username/stat or similar
                    if '/channel/@' in href or '/channel/' in href:
                         # Clean URL to get base channel URL
                         if '/stat' in href:
                             href = href.replace('/stat', '')
                         
                         if href not in results:
                             results.append(href)
                             if len(results) >= limit:
                                 break
        except Exception:
            pass
            
        return results

    async def search_channels(
        self,
        keyword: str,
        limit: int = 50,
        category_tag: str = "",
        status_callback: Optional[Callable[[str], None]] = None,
        flood_callback: Optional[Callable[[int], None]] = None
    ) -> AsyncGenerator[dict, None]:
        """
        Search for channels via DDG pointing to tgstat.com, then scrape details.
        """
        found_urls = set()
        
        # Strategy 1: Specific DDG
        if status_callback:
            status_callback(f"🔎 Strategy 1: DDG Site Search for '{keyword}'...")
        
        ddg_results = await self._get_ddg_results(f'site:tgstat.com/channel "{keyword}"', limit)
        if ddg_results:
             for res in ddg_results:
                 found_urls.add(res.get('href', ''))
        
        # Strategy 2: Broad DDG
        if len(found_urls) < 5:
            if status_callback:
                status_callback(f"🔎 Strategy 2: Broad DDG Search...")
            ddg_results_broad = await self._get_ddg_results(f'tgstat "{keyword}" channel', limit)
            for res in ddg_results_broad:
                href = res.get('href', '')
                if 'tgstat.com/channel/' in href and href not in found_urls:
                    found_urls.add(href)

        # Strategy 3: Direct POST (Fallback)
        if hasattr(self, '_search_direct_tgstat') and len(found_urls) < 3:
             if status_callback:
                status_callback(f"🔎 Strategy 3: Direct Tgstat Search...")
             direct_urls = await self._search_direct_tgstat(keyword, limit)
             for href in direct_urls:
                 if href not in found_urls:
                     found_urls.add(href)

        if not found_urls:
            if status_callback:
                status_callback(f"⚠️ No results found for '{keyword}' via any strategy")
            return
            
        if status_callback:
             status_callback(f"✅ Found {len(found_urls)} potential URLs. Scraping details...")

        count = 0
        for url in found_urls:
            if count >= limit:
                break
                
            if status_callback:
                status_callback(f"Processing: {url}...")
                
            try:
                # Random delay
                delay = get_random_delay()
                await asyncio.sleep(delay)
                
                # Scrape page
                async with httpx.AsyncClient(follow_redirects=True, timeout=15.0) as client:
                    resp = await client.get(url, headers=self.headers)
                    
                if resp.status_code != 200:
                    continue
                    
                # Parse Content
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                # Extract Data
                # Title
                title = "Unknown"
                h1 = soup.find('h1')
                if h1:
                    title = h1.get_text(strip=True)
                else:
                    # Title might be in metadata
                    meta_title = soup.find('meta', property='og:title')
                    if meta_title:
                        title = meta_title.get('content')
                
                # Username
                username = None
                if '@' in url:
                    username = url.split('@')[-1].split('/')[0]
                
                # Fallback username finding
                if not username:
                     # Try finding t.me link
                     tme_link = soup.find('a', href=re.compile(r't\.me/'))
                     if tme_link:
                         username = tme_link['href'].split('t.me/')[-1].strip('/')
                
                if not username:
                    # Skip if no username found (crucial for leads)
                    continue

                # Members Count
                members_count = 0
                # Try to find specific stat block
                # Usually a number followed by "subscribers" or in a 'position-relative' block
                text_content = soup.get_text()
                sub_matches = re.findall(r'([\d\s]+)\s+subscribers', text_content, re.IGNORECASE)
                if sub_matches:
                    try:
                        # Take the first one that looks like a number
                        members_count = int(sub_matches[0].replace(' ', '').strip())
                    except:
                        pass
                
                # Bio
                bio_text = ""
                meta_desc = soup.find('meta', {'name': 'description'})
                if meta_desc:
                    bio_text = meta_desc.get('content', '')
                
                # Admin Contact
                admin_contact = extract_admin_contacts(bio_text)
                
                # ID Generation
                channel_id = abs(hash(username)) % (10**10)

                # Save
                upsert_lead(
                    channel_id=channel_id,
                    username=username,
                    title=title,
                    category_tag=category_tag,
                    members_count=members_count,
                    bio_text=bio_text,
                    admin_contact=admin_contact
                )
                
                yield {
                    'channel_id': channel_id,
                    'username': username,
                    'title': title,
                    'category_tag': category_tag,
                    'members_count': members_count,
                    'bio_text': bio_text,
                    'admin_contact': admin_contact
                }
                
                count += 1
                    
            except Exception as e:
                # Log but continue
                pass

