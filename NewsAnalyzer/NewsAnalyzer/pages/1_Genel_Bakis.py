"""
GENEL BAKIŞ SAYFASI
Duygu dağılımı ve kaynak analizi
"""

import streamlit as st
import sys
from pathlib import Path

# Proje root'unu path'e ekle
sys.path.append(str(Path(__file__).parent.parent))

from database.repository import DatabaseManager
from analyzer.sentiment import NewsAnalyzer
from dashboard.app import DashboardUI

st.set_page_config(page_title="Genel Bakış", page_icon="📊", layout="wide")

# Custom CSS
# Custom CSS
st.markdown("""
    <style>
    .main {
        background: white;
    }
    h1, h2, h3 {
        color: #555 !important;
    }
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
    [data-testid="stSidebar"] .stMarkdown {
        color: #333;
    }
    
    /* Sidebar başlık en üste */
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 2rem;
    }
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
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        background: #f8f9fa;
        z-index: 999;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize
db = DatabaseManager('news.db')
analyzer = NewsAnalyzer()
ui = DashboardUI()

# Data
df = db.get_all_articles(limit=1000)
if not df.empty:
    df = analyzer.analyze_batch(df)

# Header
st.markdown("""
    <div style='text-align: center; padding: 20px; background: rgba(102, 126, 234, 0.1); border-radius: 15px; margin-bottom: 20px; border: 2px solid rgba(102, 126, 234, 0.3);'>
        <h1 style='margin:0; font-size: 3em; color: #667eea;'>📊 Genel Bakış</h1>
        <p style='color: #555; font-size: 1.2em; margin: 10px 0 0 0;'>Duygu dağılımı ve kaynak analizi</p>
    </div>
""", unsafe_allow_html=True)

if df.empty:
    st.warning("⚠️ Henüz veri yok! Ana sayfadan haber çekin.")
    st.stop()

# Metrics
ui.render_metrics(df)

st.markdown("---")

# Visualizations
col1, col2 = st.columns(2)

with col1:
    st.subheader("🎭 Duygu Dağılımı")
    ui.plot_sentiment_pie(df)

with col2:
    st.subheader("📡 Kaynak Dağılımı")
    ui.plot_source_distribution(df)

st.subheader("📊 Kaynak ve Duygu Karşılaştırması")
ui.plot_source_sentiment_grouped(df)

# Statistics
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Özet İstatistikler")
    stats = analyzer.get_summary_statistics(df)
    st.json(stats)

with col2:
    st.subheader("📊 Kaynak Bazında İstatistikler")
    source_stats = analyzer.sentiment_by_source(df)
    if not source_stats.empty:
        st.dataframe(source_stats, use_container_width=True)
