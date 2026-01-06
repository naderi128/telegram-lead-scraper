# 📱 Telegram Lead Scraper

A powerful web application for discovering and scraping Telegram channels using Tgstat.com data.

> ⚠️ **توجه:** این ابزار از هیچ هوش مصنوعی برای پیدا کردن کانال‌ها استفاده نمی‌کند. فقط از **وب اسکرپینگ** صفحات عمومی Tgstat.com استفاده می‌کند.

## 🌟 Features

- **🔍 Multi-Strategy Search:** Uses category pages, ratings, and DuckDuckGo as fallbacks
- **🌐 Bilingual Support:** Persian and English interface with Persian keyword mapping
- **🛡️ Safe Mode:** Filters 100+ blocked keywords (VPN, adult, gambling, drugs, scams)
- **📂 15+ Categories:** Crypto, Tech, News, Business, Education, and more
- **🇮🇷 Region Selection:** Choose between Iranian and International channels
- **📊 Data Export:** Export leads to CSV for further analysis
- **☁️ Cloud Ready:** Deploy on Streamlit Cloud with Supabase database
- **� Anti-Ban Protection:** Smart rate limiting to avoid IP blocking

---

## �️ How It Works (Technical Details)

### این اسکریپر چگونه کار می‌کند؟

این ابزار **هیچ هوش مصنوعی ندارد**. فقط از روش‌های زیر استفاده می‌کند:

```
┌──────────────────────────────────────────────────────────────────────┐
│  1. Web Scraping (وب اسکرپینگ)                                        │
│     ├── HTTP GET request به صفحات Tgstat.com                          │
│     └── Parse HTML با BeautifulSoup برای استخراج لینک کانال‌ها         │
├──────────────────────────────────────────────────────────────────────┤
│  2. DuckDuckGo Search (جستجوی داک داک گو)                              │
│     ├── Query: "site:tgstat.com/channel {keyword}"                   │
│     └── خروجی: لیست URL های صفحات کانال                               │
├──────────────────────────────────────────────────────────────────────┤
│  3. Data Extraction (استخراج داده)                                    │
│     ├── Title: از تگ <h1> یا <meta og:title>                          │
│     ├── Username: از URL (مثال: tgstat.com/channel/@username)        │
│     ├── Subscribers: از متن صفحه (regex: "\d+ subscribers")          │
│     └── Bio: از تگ <meta name="description">                         │
└──────────────────────────────────────────────────────────────────────┘
```

### Search Strategies (استراتژی‌های جستجو)

| # | Strategy | توضیح | موفقیت |
|---|----------|-------|--------|
| 1 | Category Page | مستقیم از `tgstat.com/{category}` | ✅ بالا |
| 2 | Ratings Page | از صفحه رتبه‌بندی کانال‌ها | ✅ بالا |
| 3 | DuckDuckGo | جستجوی `site:tgstat.com` | ⚠️ متوسط |
| 4 | Direct POST | فرم سرچ Tgstat | ❌ بلاک شده روی کلود |

### Data Collected (داده‌های استخراج شده)

| Field | Source | توضیح |
|-------|--------|-------|
| `username` | URL parsing | شناسه کانال (مثل @channel) |
| `title` | HTML `<h1>` tag | نام کانال |
| `members_count` | Text regex | تعداد اعضا |
| `bio_text` | Meta description | توضیحات کانال |
| `admin_contact` | Bio parsing | اطلاعات تماس ادمین |
| `channel_id` | Hash of username | شناسه یونیک |

---

## 🔒 Anti-Ban Protection (محافظت از بن شدن)

این اسکریپر از چندین روش برای جلوگیری از بن شدن استفاده می‌کند:

### 1. Random Delays (تاخیر تصادفی)
```python
# بین هر درخواست 2 تا 5 ثانیه صبر می‌کند
delay = random.uniform(2.0, 5.0)
await asyncio.sleep(delay)
```

### 2. Realistic Headers (هدرهای واقعی)
```python
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)...',
    'Accept': 'text/html,application/xhtml+xml...',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://tgstat.com/',
}
```

### 3. Request Limiting (محدودیت درخواست)
- حداکثر 100 کانال در هر جستجو
- تاخیر بین هر صفحه
- خودداری از درخواست‌های همزمان

### ⚠️ توصیه‌ها:
- از VPN استفاده نکنید (IP شما تغییر می‌کند)
- بیش از 50 کانال در هر جستجو نگیرید
- بین جستجوها 1-2 دقیقه صبر کنید
- از حالت Demo استفاده نکنید

---

## 🛡️ Safe Mode Filters (فیلتر محتوای نامناسب)

وقتی **Safe Mode** فعال است، کانال‌هایی با کلمات زیر فیلتر می‌شوند:

### کلمات ممنوعه (100+ کلمه)

| دسته | کلمات انگلیسی | کلمات فارسی |
|------|---------------|-------------|
| **VPN/فیلترشکن** | vpn, proxy, v2ray, vmess, vless, shadowsock, wireguard | فیلترشکن, فیلتر شکن, وی پی ان, پروکسی, کانفیگ رایگان |
| **بزرگسال/18+** | adult, 18+, xxx, porn, sex, nude, nsfw, onlyfans | سکس, سکسی, بزرگسال, فیلم سوپر, پورن |
| **قمار/شرط‌بندی** | casino, gambling, bet, poker, slot, jackpot, roulette | شرط بندی, کازینو, قمار, بازی انفجار, پیش بینی |
| **هک/کرک** | hack, crack, exploit, malware, phishing | هک, کرک, نفوذ, دزدی اطلاعات, ربات هک |
| **مواد مخدر** | drug, weed, marijuana, cocaine, heroin | مواد, مخدر, گل, حشیش, شیشه, تریاک |
| **کلاهبرداری** | scam, fraud, ponzi, pyramid, mlm | کلاهبرداری, پانزی, هرمی, سود تضمینی |
| **اسلحه** | gun, weapon | اسلحه, سلاح, تفنگ |
| **جعل مدارک** | fake id, fake document | مدرک جعلی, گواهی جعلی |

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
