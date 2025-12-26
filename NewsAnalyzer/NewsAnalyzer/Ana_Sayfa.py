"""
ANA SAYFA
Hızlı bakış ve genel özet
"""

import streamlit as st
import sys
from pathlib import Path
import time
from datetime import datetime

sys.path.append(str(Path(__file__).parent))

from scraper.manager import NewsScraper
from database.repository import DatabaseManager
from analyzer.sentiment import NewsAnalyzer
from dashboard.app import DashboardUI

st.set_page_config(
    page_title="News Analyzer",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
  /* Page background */
  .main { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }

  /* Header compact spacing */
  .na-header {
    background: #fff;
    color: #333;
    border-radius: 14px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.07);
    padding: 16px 18px;
    margin: 8px 0;
    border: 1px solid rgba(0,0,0,0.06);
  }
  .na-header h1 { margin: 0; font-size: 24px; font-weight: 700; line-height: 1.2; }
  .na-header p { margin: 4px 0 0; font-size: 13px; color: #666; }

  /* Container spacing */
  .block-container { padding-top: 6px; padding-bottom: 6px; }
  [data-testid="stMetricValue"] { margin-bottom: 0 !important; }
  .css-ocqkz7, .css-1r6slb0, .css-1wivap2 { margin-top: 8px; margin-bottom: 8px; }
  .na-info { margin: 8px 0; }

  /* Metric cards */
  .stMetric {
    background: rgba(255,255,255,0.95);
    padding: 16px;
    border-radius: 12px;
    box-shadow: 0 6px 14px rgba(0,0,0,0.1);
    border-left: 4px solid #667eea;
  }
  .stMetric label { color: #555 !important; }
  .stMetric [data-testid="stMetricValue"] { color: #333 !important; }
  .stMetric [data-testid="stMetricDelta"] { color: #28a745 !important; }

  /* Sidebar */
  [data-testid="stSidebar"] { background-color: #f8f9fa; }
  [data-testid="stSidebar"] .stMarkdown { color: #333; }
  [data-testid="stSidebar"] > div:first-child { padding-top: 2rem; }
  [data-testid="stSidebar"] > div:first-child::before {
    content: "📰 News Analyzer";
    display: block;
    font-size: 1.5rem;
    font-weight: 700;
    color: #667eea;
    text-align: center;
    padding: 1rem 0;
    border-bottom: 2px solid #e0e0e0;
    margin-bottom: 1.5rem;
    position: absolute; top: 0; left: 0; right: 0;
    background: #f8f9fa; z-index: 999;
  }

  /* Buttons */
  .stButton > button { border-radius: 10px; font-weight: 600; transition: all 0.2s; }
  .stButton > button:hover { transform: translateY(-1px); box-shadow: 0 4px 10px rgba(0,0,0,0.15); }

  /* Footer */
  footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ==================== GLOBAL OBJECTS ====================
@st.cache_resource
def init_components():
    """Tüm componentleri başlat"""
    scraper = NewsScraper(max_workers=4)
    db = DatabaseManager('news.db')
    analyzer = NewsAnalyzer()
    ui = DashboardUI()
    return scraper, db, analyzer, ui

            
# Initialize
scraper, db, analyzer, ui = init_components()

# ==================== SIDEBAR ====================
# News Analyzer başlığı CSS ile en üste eklenecek

# Scraping butonu
st.sidebar.markdown("### 🔄 Veri Toplama")

if st.sidebar.button("🚀 YENİ HABERLER ÇEK", use_container_width=True, type="primary"):
    with st.spinner("Haberler çekiliyor... (Threading ile paralel)"):
        # Kişi 1: Scraping
        articles = scraper.scrape_all()

        # Kişi 2: Database'e kaydet
        result = db.insert_articles_bulk(articles)

        st.sidebar.success(f"""
        ✅ **Tamamlandı!**
        - 🔍 Çekilen: {len(articles)} haber
        - ✅ YENİ: {result['saved']} haber
        - 🔄 Duplicate: {result.get('duplicate', 0)} haber
        - ❌ Başarısız: {result['failed']}
        """)

        time.sleep(2)
        st.rerun()

# Test verisi
if st.sidebar.button("🧪 Test Verisi Ekle", use_container_width=True):
    test_articles = [
        {
            'title': 'Breaking: Global Market Surge',
            'url': 'https://example.com/1',
            'source': 'Test Source',
            'sentiment': 0.8,
            'date': datetime.now()
        },
        {
            'title': 'Tech Innovation Breakthrough',
            'url': 'https://example.com/2',
            'source': 'Test Source',
            'sentiment': 0.7,
            'date': datetime.now()
        },
        {
            'title': 'Economic Concerns Rise',
            'url': 'https://example.com/3',
            'source': 'Test Source',
            'sentiment': -0.5,
            'date': datetime.now()
        }
    ]

    result = db.insert_articles_bulk(test_articles)
    st.sidebar.success(f"✅ {result['saved']} test verisi eklendi!")
    time.sleep(1)
    st.rerun()

# Veritabanını temizle
st.sidebar.markdown("---")
if st.sidebar.button("🗑️ VERİTABANINI TEMİZLE", use_container_width=True, type="secondary"):
    db.delete_all_articles()
    st.sidebar.success("✅ Tüm veriler silindi!")
    time.sleep(1)
    st.rerun()

st.sidebar.markdown("---")

# ==================== DATA LOADING ====================
# Kişi 2: Veritabanından veri çek (CACHE YOK - HER ZAMAN GÜNCEL VERİ)
df = db.get_all_articles(limit=1000)

# Kişi 3: Sentiment analizi ekle
if not df.empty:
    df = analyzer.analyze_batch(df)

# Kişi 4: Filtreler
filters = ui.render_sidebar_filters(df)
df_filtered = ui.apply_filters(df.copy(), filters) if not df.empty else df

# ==================== MAIN CONTENT ====================
# Sayfa başlığı (yerel stil)
st.markdown("""
    <div style='text-align: center; padding: 24px; background: white; border-radius: 15px; margin-bottom: 24px; box-shadow: 0 6px 12px rgba(0,0,0,0.15);'>
        <h1 style='margin:0; font-size: 2.2em; color: #333; font-weight: 700; line-height: 1.2;'>📊 News Sentiment Analyzer</h1>
    </div>
""", unsafe_allow_html=True)

# Veri kontrolü
if df_filtered.empty:
    st.warning("⚠️ **Henüz veri yok!**")
    st.info("""
    **Başlamak için:**
    1. Sol menüden **'🚀 YENİ HABERLER ÇEK'** butonuna tıklayın (20-30 sn sürer)
    2. Veya **'🧪 Test Verisi Ekle'** ile demo verisi ekleyin
    """)
    st.stop()

# Kişi 4: Metrics
ui.render_metrics(df_filtered)

st.markdown("---")

# ==================== MAIN DASHBOARD ====================
st.subheader("📊 Hızlı Bakış")
st.info("👈 **Sol menüden farklı sayfaları keşfedin!** Genel Bakış, Trend Analizi, Detay Analiz, Anahtar Kelimeler ve Haberler...")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🎭 Duygu Dağılımı")
    ui.plot_sentiment_pie(df_filtered)

with col2:
    st.markdown("### 📡 Kaynak Dağılımı")
    ui.plot_source_distribution(df_filtered)

st.markdown("---")
st.subheader("📈 Son Trendler")
ui.plot_sentiment_timeline(df_filtered)

# ==================== FOOTER ====================
ui.render_footer()
