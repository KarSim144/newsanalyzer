"""
ANALYZER MODULE - Sentiment Analysis & Data Processing
Kişi 3: Sentiment Analysis ve Data Processing sorumlusu
Bu modül haberlerin duygu analizini ve veri işlemlerini yapar
"""

import pandas as pd
from textblob import TextBlob
from collections import Counter
import re
from typing import List, Dict, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NewsAnalyzer:
    """Haber analiz sınıfı"""

    def __init__(self):
        """Analiz sınıfını başlat"""
        self.stop_words = {
            'this', 'that', 'with', 'from', 'have', 'been', 'more',
            'will', 'says', 'after', 'could', 'would', 'about', 'their',
            'said', 'also', 'when', 'where', 'what', 'which', 'there'
        }

    def analyze_sentiment(self, text: str) -> Dict[str, any]:
        """
        Tek bir metinin duygu analizini yap

        Args:
            text (str): Analiz edilecek metin

        Returns:
            Dict: {'score': float, 'label': str, 'subjectivity': float}
        """
        if not text or len(text.strip()) == 0:
            return {
                'score': 0.0,
                'label': 'Neutral',
                'subjectivity': 0.0
            }

        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity  # -1 (negatif) ile +1 (pozitif)
            subjectivity = blob.sentiment.subjectivity  # 0 (objektif) ile 1 (subjektif)

            # Etiketleme
            if polarity > 0.1:
                label = 'Positive'
            elif polarity < -0.1:
                label = 'Negative'
            else:
                label = 'Neutral'

            return {
                'score': round(polarity, 3),
                'label': label,
                'subjectivity': round(subjectivity, 3)
            }
        except Exception as e:
            logger.error(f"Sentiment analizi hatası: {e}")
            return {'score': 0.0, 'label': 'Neutral', 'subjectivity': 0.0}

    def analyze_batch(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Toplu haber analizi - DataFrame'e sentiment bilgileri ekle

        Args:
            df (pd.DataFrame): Haber verileri

        Returns:
            pd.DataFrame: Sentiment bilgileri eklenmiş DataFrame
        """
        if df.empty:
            return df

        logger.info(f"📊 {len(df)} haber analiz ediliyor...")

        # Sentiment label ekle
        df['sentiment_label'] = df['sentiment'].apply(
            lambda x: 'Positive' if x > 0.1 else ('Negative' if x < -0.1 else 'Neutral')
        )

        logger.info("✅ Analiz tamamlandı")
        return df

    def extract_keywords(self, text: str, top_n: int = 10) -> List[Tuple[str, int]]:
        """
        Metinden anahtar kelimeleri çıkar

        Args:
            text (str): Analiz edilecek metin
            top_n (int): Döndürülecek kelime sayısı

        Returns:
            List[Tuple[str, int]]: [(kelime, frekans), ...]
        """
        if not text:
            return []

        # Temizle ve tokenize et
        text = text.lower()
        words = re.findall(r'\b\w{4,}\b', text)

        # Stop words filtrele
        words = [word for word in words if word not in self.stop_words]

        # Frekans hesapla
        word_freq = Counter(words)

        return word_freq.most_common(top_n)

    def get_trending_topics(self, df: pd.DataFrame, top_n: int = 20) -> List[Tuple[str, int]]:
        """
        DataFrame'den trend konuları çıkar

        Args:
            df (pd.DataFrame): Haber verileri
            top_n (int): Döndürülecek konu sayısı

        Returns:
            List[Tuple[str, int]]: [(kelime, frekans), ...]
        """
        if df.empty or 'title' not in df.columns:
            return []

        # Tüm başlıkları birleştir
        all_text = ' '.join(df['title'].tolist())

        return self.extract_keywords(all_text, top_n)

    def sentiment_by_source(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Kaynak bazında sentiment istatistikleri

        Args:
            df (pd.DataFrame): Haber verileri

        Returns:
            pd.DataFrame: Kaynak bazında istatistikler
        """
        if df.empty or 'source' not in df.columns:
            return pd.DataFrame()

        stats = df.groupby('source').agg({
            'sentiment': ['mean', 'std', 'count'],
            'sentiment_label': lambda x: x.value_counts().to_dict()
        }).round(3)

        return stats

    def sentiment_over_time(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Zaman içinde sentiment trendi

        Args:
            df (pd.DataFrame): Haber verileri (date column'u olmalı)

        Returns:
            pd.DataFrame: Günlük sentiment ortalamaları
        """
        if df.empty or 'date' not in df.columns:
            return pd.DataFrame()

        # Tarihi düzelt
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])

        if df.empty:
            return pd.DataFrame()

        # Günlük grup
        df['day'] = df['date'].dt.date

        daily_stats = df.groupby('day').agg({
            'sentiment': 'mean',
            'id': 'count'
        }).rename(columns={'id': 'article_count'}).round(3)

        return daily_stats

    def get_sentiment_distribution(self, df: pd.DataFrame) -> Dict[str, int]:
        """
        Sentiment dağılımını hesapla

        Args:
            df (pd.DataFrame): Haber verileri

        Returns:
            Dict: {'Positive': count, 'Neutral': count, 'Negative': count}
        """
        if df.empty or 'sentiment_label' not in df.columns:
            return {'Positive': 0, 'Neutral': 0, 'Negative': 0}

        distribution = df['sentiment_label'].value_counts().to_dict()

        # Eksik olanları ekle
        for label in ['Positive', 'Neutral', 'Negative']:
            if label not in distribution:
                distribution[label] = 0

        return distribution

    def calculate_readability(self, text: str) -> Dict[str, any]:
        """
        Metnin okunabilirlik metriklerini hesapla

        Args:
            text (str): Analiz edilecek metin

        Returns:
            Dict: Okunabilirlik metrikleri
        """
        if not text:
            return {
                'avg_word_length': 0,
                'sentence_count': 0,
                'word_count': 0
            }

        sentences = text.split('.')
        words = text.split()

        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0

        return {
            'avg_word_length': round(avg_word_length, 2),
            'sentence_count': len(sentences),
            'word_count': len(words)
        }

    def get_summary_statistics(self, df: pd.DataFrame) -> Dict:
        """
        Genel özet istatistikler

        Args:
            df (pd.DataFrame): Haber verileri

        Returns:
            Dict: Özet istatistikler
        """
        if df.empty:
            return {}

        return {
            'total_articles': len(df),
            'avg_sentiment': round(df['sentiment'].mean(), 3) if 'sentiment' in df.columns else 0,
            'sources_count': df['source'].nunique() if 'source' in df.columns else 0,
            'sentiment_distribution': self.get_sentiment_distribution(df),
            'date_range': {
                'min': df['date'].min() if 'date' in df.columns else None,
                'max': df['date'].max() if 'date' in df.columns else None
            }
        }

    def filter_by_sentiment(self, df: pd.DataFrame, sentiment_type: str) -> pd.DataFrame:
        """
        Sentiment'e göre filtrele

        Args:
            df (pd.DataFrame): Haber verileri
            sentiment_type (str): 'Positive', 'Neutral', veya 'Negative'

        Returns:
            pd.DataFrame: Filtrelenmiş veriler
        """
        if df.empty or 'sentiment_label' not in df.columns:
            return pd.DataFrame()

        return df[df['sentiment_label'] == sentiment_type].copy()

    def get_top_positive_news(self, df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
        """
        En pozitif haberleri getir

        Args:
            df (pd.DataFrame): Haber verileri
            n (int): Haber sayısı

        Returns:
            pd.DataFrame: En pozitif haberler
        """
        if df.empty or 'sentiment' not in df.columns:
            return pd.DataFrame()

        return df.nlargest(n, 'sentiment')

    def get_top_negative_news(self, df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
        """
        En negatif haberleri getir

        Args:
            df (pd.DataFrame): Haber verileri
            n (int): Haber sayısı

        Returns:
            pd.DataFrame: En negatif haberler
        """
        if df.empty or 'sentiment' not in df.columns:
            return pd.DataFrame()

        return df.nsmallest(n, 'sentiment')


# Test fonksiyonu
if __name__ == "__main__":
    analyzer = NewsAnalyzer()

    print("=" * 50)
    print("ANALYZER MODÜLÜ TEST")
    print("=" * 50)

    # Test metni
    test_texts = [
        "Breaking news: Great economic growth announced today!",
        "Terrible disaster strikes the region",
        "Meeting held to discuss future plans"
    ]

    print("\n📊 Sentiment Analizi:")
    for text in test_texts:
        result = analyzer.analyze_sentiment(text)
        print(f"\n'{text}'")
        print(f"   → {result['label']} ({result['score']})")

    # Test DataFrame
    test_df = pd.DataFrame({
        'title': test_texts,
        'sentiment': [0.8, -0.7, 0.0],
        'source': ['BBC', 'CNN', 'NPR']
    })

    # Batch analiz
    test_df = analyzer.analyze_batch(test_df)
    print(f"\n✅ Batch analiz tamamlandı")
    print(test_df[['title', 'sentiment_label']])

    # Trending topics
    keywords = analyzer.get_trending_topics(test_df, top_n=5)
    print(f"\n🔑 Anahtar Kelimeler:")
    for word, count in keywords:
        print(f"   {word}: {count}")