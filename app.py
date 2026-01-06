"""
Telegram Lead Scraper & Manager
A robust, safe, and user-friendly Streamlit application for scraping Telegram channels/groups.
"""

import streamlit as st
import pandas as pd
import asyncio
import random
from datetime import datetime
from typing import Optional

from scraper import (
    TelegramScraper,
    TgstatScraper,
    get_all_leads,
    get_leads_count,
    init_database,
    upsert_lead
)

# Page configuration
st.set_page_config(
    page_title="Telegram Lead Scraper",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

def init_session_state():
    """Initialize session state variables."""
    defaults = {
        'api_id': '',
        'api_hash': '',
        'phone': '',
        'authenticated': False,
        'phone_code_hash': None,
        'phone_code_hash': None,
        'scraper': None,
        'scraper_type': 'Tgstat Scraper', # Default to Tgstat
        'scraping_in_progress': False,
        'status_messages': [],
        'flood_wait_count': 0,
        'demo_mode': False
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def load_css():
    """Load custom CSS."""
    st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
        }
        .status-box {
            padding: 1rem;
            border-radius: 0.5rem;
            background-color: #1e1e1e;
            border: 1px solid #333;
            margin: 0.5rem 0;
        }
        .stProgress > div > div > div > div {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        }
        .footer {
            text-align: center;
            color: #666;
            margin-top: 2rem;
            font-size: 0.8rem;
        }
        .author-tag {
            color: #764ba2;
            font-weight: bold;
        }
    </style>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Render sidebar with configuration options."""
    st.sidebar.markdown("## ⚙️ Configuration")
    
    # API Credentials
    st.sidebar.markdown("### 🔐 Telegram API Credentials")
    st.sidebar.caption("Get these from [my.telegram.org](https://my.telegram.org)")
    
    api_id = st.sidebar.text_input(
        "API ID",
        value=st.session_state.api_id,
        type="default"
    )
    
    api_hash = st.sidebar.text_input(
        "API Hash",
        value=st.session_state.api_hash,
        type="password"
    )
    
    phone = st.sidebar.text_input(
        "Phone Number",
        value=st.session_state.phone,
        placeholder="+1234567890"
    )
    
    # Update session state
    st.session_state.api_id = api_id
    st.session_state.api_hash = api_hash
    st.session_state.api_hash = api_hash
    st.session_state.phone = phone
    
    # Scraper Method
    st.sidebar.markdown("### 🛠️ Scraper Settings")
    scraper_type = st.sidebar.selectbox(
        "Scraping Method",
        ["Tgstat Scraper (Web)", "Telegram API (Direct)"],
        index=0 if st.session_state.scraper_type == "Tgstat Scraper (Web)" else 1
    )
    st.session_state.scraper_type = scraper_type
    
    # Authentication status
    st.sidebar.markdown("---")
    if st.session_state.authenticated:
        st.sidebar.success("✅ Authenticated")
    else:
        st.sidebar.warning("⚠️ Not authenticated")
    
    # Demo Mode
    st.sidebar.markdown("---")
    demo_mode = st.sidebar.checkbox("🎮 Demo Mode", value=st.session_state.demo_mode, help="Run without API credentials using mock data")
    st.session_state.demo_mode = demo_mode
    
    # Anti-ban settings
    st.sidebar.markdown("### 🛡️ Safety Settings")
    
    max_requests = st.sidebar.slider(
        "Max Requests (0 = unlimited)",
        min_value=0,
        max_value=200,
        value=50,
        step=10
    )
    
    return {
        'api_id': api_id,
        'api_hash': api_hash,
        'phone': phone,
        'max_requests': max_requests if max_requests > 0 else None,
        'demo_mode': demo_mode,
        'scraper_type': scraper_type,
        'supabase_url': st.secrets.get("SUPABASE_URL"),
        'supabase_key': st.secrets.get("SUPABASE_KEY")
    }


def render_search_params():
    """Render search parameters section."""
    st.markdown("### 🔍 Search Parameters")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        keywords = st.text_area(
            "Keywords (comma-separated)",
            placeholder="crypto, trading, forex, bitcoin",
            value="crypto, forex" if st.session_state.get('demo_mode', False) else ""
        )
    
    with col2:
        limit_per_keyword = st.slider(
            "Limit per Keyword",
            min_value=5,
            max_value=100,
            value=20,
            step=5
        )
        
        category_tag = st.text_input(
            "Category Tag",
            placeholder="e.g., Crypto",
            value="Demo" if st.session_state.get('demo_mode', False) else ""
        )
    
    return {
        'keywords': [k.strip() for k in keywords.split(',') if k.strip()],
        'limit': limit_per_keyword,
        'category_tag': category_tag
    }


async def authenticate_user(config: dict) -> bool:
    """Handle user authentication flow."""
    if config.get('demo_mode'):
        st.session_state.authenticated = True
        return True

    # If using Tgstat, authentication is simulated/not needed for now
    if "Tgstat" in config.get('scraper_type', ''):
        st.session_state.authenticated = True
        st.session_state.scraper = TgstatScraper()
        return True


    try:
        api_id = int(config['api_id'])
    except (ValueError, TypeError):
        st.error("❌ Invalid API ID. Please enter a valid number.")
        return False
    
    scraper = TelegramScraper(
        api_id=api_id,
        api_hash=config['api_hash'],
        phone=config['phone']
    )
    
    connected = await scraper.connect()
    
    if connected:
        st.session_state.authenticated = True
        st.session_state.scraper = scraper
        return True
    else:
        # Need to send code
        phone_code_hash = await scraper.send_code()
        st.session_state.phone_code_hash = phone_code_hash
        st.session_state.scraper = scraper
        return False


async def sign_in_user(code: str, password: Optional[str] = None) -> bool:
    """Sign in with verification code."""
    scraper = st.session_state.scraper
    if not scraper:
        return False
    
    try:
        success = await scraper.sign_in(
            code=code,
            phone_code_hash=st.session_state.phone_code_hash,
            password=password
        )
        if success:
            st.session_state.authenticated = True
        return success
    except Exception as e:
        st.error(f"❌ {str(e)}")
        return False


async def run_scraper(config: dict, search_params: dict, progress_bar, status_text):
    """Run the scraping process."""
    if config.get('demo_mode'):
        # Mock scraping logic
        st.session_state.scraping_in_progress = True
        st.session_state.status_messages = []
        
        status_text.markdown("**Status:** 🎮 Running in Demo Mode...")
        
        keywords = search_params['keywords']
        if not keywords:
            keywords = ["demo_crypto", "demo_forex"]
            
        total_steps = len(keywords) * 5 # Simulate 5 results per keyword
        current_step = 0
        
        try:
            for keyword in keywords:
                msg = f"🔎 Searching for '{keyword}'..."
                st.session_state.status_messages.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
                status_text.markdown(f"**Status:** {msg}")
                await asyncio.sleep(1.5)
                
                # Generate fake results
                for i in range(5):
                    await asyncio.sleep(0.8)
                    current_step += 1
                    progress = min(current_step / total_steps, 0.95)
                    progress_bar.progress(progress, text=f"Processing '{keyword}'...")
                    
                    channel_id = random.randint(1000000000, 9999999999)
                    username = f"{keyword}_{i}"
                    title = f"Demo {keyword.title()} Channel {i+1}"
                    
                    mock_lead = {
                        'channel_id': channel_id,
                        'username': username,
                        'title': title,
                        'category_tag': search_params['category_tag'],
                        'members_count': random.randint(1000, 50000),
                        'bio_text': f"This is a demo channel for {keyword}. Contact @admin_{username}",
                        'admin_contact': f"@admin_{username}"
                    }
                    
                    # Save to DB
                    upsert_lead(**mock_lead)
                    
                    msg_found = f"✅ Found: {title}..."
                    st.session_state.status_messages.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg_found}")
            
            progress_bar.progress(1.0, text="Complete!")
            status_text.markdown("**Status:** 🎉 Scraping complete!")
            st.session_state.status_messages.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🎉 Scraping complete!")
            
        finally:
            st.session_state.scraping_in_progress = False
        return

    # Real scraping logic
    scraper = st.session_state.scraper
    if not scraper:
        # Re-init if missing
        if "Tgstat" in config.get('scraper_type', ''):
             scraper = TgstatScraper()
             st.session_state.scraper = scraper
        else:
            st.error("❌ Scraper not initialized")
            return

    
    # Set max requests limit if applicable
    if hasattr(scraper, 'set_max_requests'):
        scraper.set_max_requests(config['max_requests'])
    
    keywords = search_params['keywords']
    total_keywords = len(keywords)
    
    if total_keywords == 0:
        st.warning("⚠️ Please enter at least one keyword")
        return
    
    st.session_state.scraping_in_progress = True
    st.session_state.status_messages = []
    st.session_state.flood_wait_count = 0
    
    results = []
    
    def status_callback(message: str):
        st.session_state.status_messages.append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        status_text.markdown(f"**Status:** {message}")
    
    def flood_callback(seconds: int):
        st.session_state.flood_wait_count += 1
    
    try:
        for i, keyword in enumerate(keywords):
            progress = (i / total_keywords)
            progress_bar.progress(progress, text=f"Searching: {keyword}")
            
            status_callback(f"🔎 Searching for '{keyword}'...")
            
            async for lead in scraper.search_channels(
                keyword=keyword,
                limit=search_params['limit'],
                category_tag=search_params['category_tag'],
                status_callback=status_callback,
                flood_callback=flood_callback
            ):
                results.append(lead)
                status_callback(f"✅ Found: {lead['title'][:30]}...")
        
        progress_bar.progress(1.0, text="Complete!")
        status_callback(f"🎉 Scraping complete! Found {len(results)} leads.")
        
    except Exception as e:
        status_callback(f"❌ Error: {str(e)}")
        st.error(f"Scraping error: {str(e)}")
    finally:
        st.session_state.scraping_in_progress = False


def render_results():
    """Render results section with data table and export options."""
    st.markdown("---")
    st.markdown("### 📊 Stored Leads")
    
    # Get leads from database
    leads = get_all_leads()
    
    if not leads:
        st.info("📭 No leads in database yet. Start scraping to collect leads!")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(leads)
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Leads", len(df))
    with col2:
        with_admins = df[df['admin_contact'].notna() & (df['admin_contact'] != '')].shape[0]
        st.metric("With Admin Contacts", with_admins)
    with col3:
        categories = df['category_tag'].nunique()
        st.metric("Categories", categories)
    with col4:
        if 'flood_wait_count' in st.session_state:
            st.metric("FloodWait Events", st.session_state.flood_wait_count)
    
    # Display data table
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "channel_id": st.column_config.NumberColumn("Channel ID", format="%d"),
            "username": st.column_config.TextColumn("Username"),
            "title": st.column_config.TextColumn("Title"),
            "category_tag": st.column_config.TextColumn("Category"),
            "members_count": st.column_config.NumberColumn("Members", format="%d"),
            "bio_text": st.column_config.TextColumn("Bio", width="large"),
            "admin_contact": st.column_config.TextColumn("Admin Contacts", width="medium"),
            "scraped_date": st.column_config.TextColumn("Scraped At"),
        }
    )
    
    # Export section
    st.markdown("### 📥 Export Data")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        export_columns = st.multiselect(
            "Select columns to export",
            options=df.columns.tolist(),
            default=['username', 'title', 'category_tag', 'members_count', 'admin_contact']
        )
    
    with col2:
        if export_columns:
            export_df = df[export_columns]
            csv_data = export_df.to_csv(index=False)
            
            st.download_button(
                label="📥 Download CSV",
                data=csv_data,
                file_name=f"telegram_leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )


def main():
    """Main application entry point."""
    init_session_state()
    # init_database moved after config load
    load_css()
    
    # Header
    st.markdown('<h1 class="main-header">📱 Telegram Lead Scraper</h1>', unsafe_allow_html=True)
    st.markdown("Safely scrape and manage Telegram channel/group leads with anti-ban protection.")
    
    # Sidebar configuration
    config = render_sidebar()

    # Initialize DB (with Supabase secrets if available)
    init_database(config.get('supabase_url'), config.get('supabase_key'))
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["🔓 Authentication", "🔍 Scraper", "📊 Data"])
    
    with tab1:
        st.markdown("### 🔐 Connect to Telegram")
        
        if st.session_state.authenticated:
            st.success("✅ You are authenticated and ready to scrape!")
            if st.button("🔓 Disconnect"):
                st.session_state.authenticated = False
                st.session_state.scraper = None
                st.rerun()
        else:
            # Check if credentials are provided
            if not config['api_id'] or not config['api_hash'] or not config['phone']:
                if not config['demo_mode']:
                    st.warning("⚠️ Please fill in your API credentials in the sidebar.")
            else:
                if st.session_state.phone_code_hash:
                    # Code entry form
                    st.info("📲 A verification code has been sent to your Telegram app.")
                    
                    code = st.text_input("Enter verification code", max_chars=10)
                    password = st.text_input("2FA Password (if enabled)", type="password")
                    
                    if st.button("✅ Verify Code"):
                        with st.spinner("Verifying..."):
                            success = asyncio.run(sign_in_user(code, password if password else None))
                            if success:
                                st.success("✅ Successfully authenticated!")
                                st.rerun()
                else:
                    if st.button("🔑 Connect to Telegram"):
                        with st.spinner("Connecting..."):
                            already_auth = asyncio.run(authenticate_user(config))
                            if already_auth:
                                st.success("✅ Already authenticated!")
                                st.rerun()
                            else:
                                if not st.session_state.authenticated:
                                    st.info("📲 Check your Telegram for verification code.")
                                    st.rerun()
    
    with tab2:
        st.markdown("### 🔍 Scraper")
        
        if not st.session_state.authenticated:
            st.warning("⚠️ Please fill in your API credentials in the sidebar.")
        else:
            search_params = render_search_params()
            
            st.markdown("---")
            
            # Status area
            status_placeholder = st.empty()
            progress_bar = st.progress(0, text="Ready to scrape")
            status_text = st.empty()
            
            # Log area
            with st.expander("📜 Activity Log", expanded=False):
                log_area = st.empty()
                if st.session_state.status_messages:
                    log_area.text("\n".join(st.session_state.status_messages[-20:]))
            
            col1, col2 = st.columns([1, 3])
            with col1:
                start_button = st.button(
                    "🚀 Start Scraping",
                    disabled=st.session_state.scraping_in_progress,
                    use_container_width=True
                )
            
            if start_button:
                asyncio.run(run_scraper(config, search_params, progress_bar, status_text))
                st.rerun()
    
    with tab3:
        render_results()
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div class="footer">
            ⚠️ Use responsibly. Respect Telegram's Terms of Service. | <span class="author-tag">Made by Naderi128</span>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
