"""
Add mock data to the leads database for UI demonstration.
"""

import sqlite3
from datetime import datetime, timedelta
import random
from pathlib import Path

DB_PATH = Path(__file__).parent / "leads.db"

# Mock data
MOCK_LEADS = [
    {
        "channel_id": 1001234567,
        "username": "cryptosignals_pro",
        "title": "🚀 Crypto Signals Pro",
        "category_tag": "Crypto",
        "members_count": 45200,
        "bio_text": "Best crypto signals! Contact admin: @crypto_admin_john for VIP access. Premium signals daily 📈",
        "admin_contact": "@crypto_admin_john"
    },
    {
        "channel_id": 1002345678,
        "username": "forex_masters_ir",
        "title": "Forex Masters Iran 💹",
        "category_tag": "Forex",
        "members_count": 28500,
        "bio_text": "آموزش حرفه‌ای فارکس | مدیر: @forex_master_ali | پشتیبانی: @support_forex",
        "admin_contact": "@forex_master_ali, @support_forex"
    },
    {
        "channel_id": 1003456789,
        "username": "bitcoin_whale_alerts",
        "title": "🐋 Bitcoin Whale Alerts",
        "category_tag": "Crypto",
        "members_count": 156000,
        "bio_text": "Real-time whale movements! Admin @whale_tracker_bot",
        "admin_contact": "@whale_tracker_bot"
    },
    {
        "channel_id": 1004567890,
        "username": "trading_academy_fa",
        "title": "آکادمی ترید فارسی",
        "category_tag": "Education",
        "members_count": 67800,
        "bio_text": "آموزش رایگان ترید | تماس با ما: @trading_academy_admin | ثبت‌نام دوره: @course_register",
        "admin_contact": "@trading_academy_admin, @course_register"
    },
    {
        "channel_id": 1005678901,
        "username": "nft_drops_daily",
        "title": "NFT Drops Daily 🎨",
        "category_tag": "NFT",
        "members_count": 34200,
        "bio_text": "Daily NFT drops and mints. DM @nft_hunter for collaborations",
        "admin_contact": "@nft_hunter"
    },
    {
        "channel_id": 1006789012,
        "username": "defi_yields",
        "title": "DeFi Yield Farming 🌾",
        "category_tag": "DeFi",
        "members_count": 22100,
        "bio_text": "Best APY farms curated. Contact: @defi_analyst",
        "admin_contact": "@defi_analyst"
    },
    {
        "channel_id": 1007890123,
        "username": "altcoin_gems",
        "title": "💎 Altcoin Gems Hunter",
        "category_tag": "Crypto",
        "members_count": 89500,
        "bio_text": "Finding 100x gems before they pump! VIP: @altcoin_vip_access | Support: @gems_support",
        "admin_contact": "@altcoin_vip_access, @gems_support"
    },
    {
        "channel_id": 1008901234,
        "username": "stock_market_iran",
        "title": "بورس ایران 📊",
        "category_tag": "Stock",
        "members_count": 112000,
        "bio_text": "تحلیل بورس تهران | ادمین: @bourse_analyst | پشتیبانی: @bourse_support",
        "admin_contact": "@bourse_analyst, @bourse_support"
    },
    {
        "channel_id": 1009012345,
        "username": "meme_coins_pumps",
        "title": "🐸 Meme Coins Pumps",
        "category_tag": "Crypto",
        "members_count": 41300,
        "bio_text": "PEPE, DOGE, SHIB and more! Contact @meme_lord for calls",
        "admin_contact": "@meme_lord"
    },
    {
        "channel_id": 1010123456,
        "username": "gold_trading_signals",
        "title": "Gold & Silver Trading 🥇",
        "category_tag": "Commodities",
        "members_count": 18900,
        "bio_text": "XAUUSD signals with 90% accuracy. Premium: @gold_premium_admin",
        "admin_contact": "@gold_premium_admin"
    },
]


def add_mock_data():
    """Insert mock data into database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            channel_id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            title TEXT,
            category_tag TEXT,
            members_count INTEGER,
            bio_text TEXT,
            admin_contact TEXT,
            scraped_date TEXT
        )
    """)
    
    # Insert mock data
    for i, lead in enumerate(MOCK_LEADS):
        # Randomize scraped date within last 3 days
        days_ago = random.randint(0, 3)
        hours_ago = random.randint(0, 23)
        scraped_date = (datetime.now() - timedelta(days=days_ago, hours=hours_ago)).isoformat()
        
        cursor.execute("""
            INSERT OR REPLACE INTO leads (
                channel_id, username, title, category_tag,
                members_count, bio_text, admin_contact, scraped_date
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            lead["channel_id"],
            lead["username"],
            lead["title"],
            lead["category_tag"],
            lead["members_count"],
            lead["bio_text"],
            lead["admin_contact"],
            scraped_date
        ))
    
    conn.commit()
    conn.close()
    print(f"[OK] Added {len(MOCK_LEADS)} mock leads to database!")


if __name__ == "__main__":
    add_mock_data()
