# 📱 Telegram Lead Scraper

A powerful web application for discovering and scraping Telegram channels using Tgstat.com data.

## 🌟 Features

- **🔍 Multi-Strategy Search:** Uses category pages, ratings, and DuckDuckGo as fallbacks
- **🌐 Bilingual Support:** Persian and English interface with Persian keyword mapping
- **🛡️ Safe Mode:** Filters out VPN, adult, gambling, and inappropriate channels
- **📂 15+ Categories:** Crypto, Tech, News, Business, Education, and more
- **🇮🇷 Region Selection:** Choose between Iranian and International channels
- **📊 Data Export:** Export leads to CSV for further analysis
- **☁️ Cloud Ready:** Deploy on Streamlit Cloud with Supabase database

---

## 🚀 Quick Start

### Option 1: Run Locally

```bash
# Clone the repository
git clone https://github.com/naderi128/telegram-lead-scraper.git
cd telegram-lead-scraper

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

### Option 2: Use Online (Streamlit Cloud)

Visit: [Your Streamlit App URL]

---

## 📖 How It Works

### Search Strategy

The scraper uses multiple strategies to find channels:

```
┌─────────────────────────────────────────────────────────────┐
│  Strategy 1: Category Page Scraping                        │
│  ├── Matches keyword to category (e.g., "crypto" → /crypto)│
│  └── Scrapes tgstat.com/{category} or ir.tgstat.com/{cat}  │
├─────────────────────────────────────────────────────────────┤
│  Strategy 2: Ratings Page                                   │
│  └── Scrapes top channels from ratings page                │
├─────────────────────────────────────────────────────────────┤
│  Strategy 3: DuckDuckGo Search (Fallback)                   │
│  └── Searches "site:tgstat.com/channel {keyword}"          │
├─────────────────────────────────────────────────────────────┤
│  Strategy 4: Direct Tgstat POST (Last Resort)              │
│  └── Direct search API (may require auth on cloud)         │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
User Input → Keyword Processing → Strategy Selection → Scraping → Filtering → Database → Display
     │              │                    │                │           │          │
     │              │                    │                │           │          └── Results Table
     │              │                    │                │           └── Safe Mode Filter
     │              │                    │                └── Parse HTML for channel data
     │              │                    └── Choose best strategy based on results
     │              └── Convert Persian keywords to English slugs
     └── Category, Keywords, Region, Safe Mode
```

---

## 🎮 Using the App

### Step 1: Configure Search

| Setting | Description |
|---------|-------------|
| **📂 Category** | Select from 15+ categories or enter custom keywords |
| **🔤 Keywords** | Comma-separated keywords (English or Persian) |
| **🌐 Region** | 🌍 International (tgstat.com) or 🇮🇷 Iranian (ir.tgstat.com) |
| **🛡️ Safe Mode** | Filter inappropriate channels (VPN, adult, gambling) |
| **Limit** | Maximum channels per keyword (5-100) |

### Step 2: Start Scraping

1. Click **"🔎 Start Scraping"**
2. Watch the Activity Log for progress
3. Results appear in the table below

### Step 3: Export Data

- Click **"📥 Download CSV"** to export all leads
- Data includes: Username, Title, Members, Bio, Admin Contact

---

## 🌍 Supported Categories

| Category | Slug | Persian |
|----------|------|---------|
| Crypto | `crypto` | ارز دیجیتال، کریپتو، بیتکوین |
| Technology | `tech` | تکنولوژی، برنامه نویسی |
| News | `news` | اخبار، خبر |
| Business | `business` | کسب و کار، استارتاپ |
| Education | `education` | آموزش، یادگیری |
| Entertainment | `entertainment` | سرگرمی، تفریح |
| Music | `music` | موسیقی، آهنگ |
| Sport | `sport` | ورزش، فوتبال |
| Design | `design` | طراحی، گرافیک |
| Food | `food` | غذا، آشپزی |
| Travel | `travel` | سفر، گردشگری |
| Fashion | `fashion` | مد، لباس |
| Health | `health` | سلامت، پزشکی |
| Games | `games` | بازی، گیم |

---

## 🛡️ Safe Mode Filters

When **Safe Mode** is enabled, channels containing these keywords are blocked:

| Category | Blocked Keywords |
|----------|------------------|
| VPN/Proxy | vpn, proxy, فیلترشکن, v2ray |
| Adult | adult, 18+, xxx, سکس |
| Gambling | casino, gambling, bet, شرط بندی, قمار |
| Hacking | hack, crack, هک, کرک |

---

## 🔤 Persian Keyword Support

Type in Persian, the app converts automatically:

```
کریپتو    →  crypto
بیتکوین   →  crypto
تکنولوژی  →  tech
آموزش     →  education
ورزش      →  sport
موسیقی    →  music
...and more
```

---

## ☁️ Deployment

### Streamlit Cloud

1. Push code to GitHub
2. Connect repo to [share.streamlit.io](https://share.streamlit.io)
3. Add secrets in Streamlit Cloud dashboard:

```toml
# .streamlit/secrets.toml
SUPABASE_URL = "your-supabase-url"
SUPABASE_KEY = "your-supabase-key"
```

### Supabase Setup

Create a table with this schema:

```sql
CREATE TABLE leads (
    id SERIAL PRIMARY KEY,
    channel_id BIGINT UNIQUE,
    username TEXT NOT NULL,
    title TEXT,
    category_tag TEXT,
    members_count INTEGER DEFAULT 0,
    bio_text TEXT,
    admin_contact TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## 📁 Project Structure

```
telegram-lead-scraper/
├── app.py              # Main Streamlit application
├── scraper.py          # TgstatScraper class and utilities
├── database.py         # SQLite/Supabase database functions
├── requirements.txt    # Python dependencies
├── .streamlit/
│   └── secrets.toml    # Secrets (not in git)
└── README.md           # This file
```

---

## ⚠️ Known Limitations

1. **Cloud IP Blocking:** Tgstat may block requests from cloud server IPs (Streamlit Cloud). Category pages work better than direct search.

2. **Rate Limiting:** DuckDuckGo may rate-limit requests. The app handles this with delays.

3. **Authentication:** Some Tgstat features require login from cloud environments.

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| 0 results found | Try different keywords or categories |
| "Authentication Required" | Use category pages instead of search |
| DDG returns 0 | DDG may be rate-limiting; wait and retry |
| App crashes | Check Streamlit Cloud logs |

---

## 📝 License

MIT License - Feel free to use and modify.

---

## 👨‍💻 Author

Created with ❤️ by [Naderi128](https://github.com/naderi128)
