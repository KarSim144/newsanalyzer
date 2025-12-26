"""
DATABASE MODULE - SQLite Operations
Kişi 2: Database sorumlusu
Bu modül veritabanı CRUD operasyonlarını yönetir
"""

import sqlite3
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
from contextlib import contextmanager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """SQLite veritabanı yöneticisi"""

    def __init__(self, db_path='news.db'):
        """
        Args:
            db_path (str): Veritabanı dosyası yolu
        """
        self.db_path = db_path
        self.init_database()

    @contextmanager
    def get_connection(self):
        """
        Context manager ile güvenli bağlantı yönetimi
        Otomatik commit ve rollback
        """
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row  # Dict-like access
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Veritabanı hatası: {e}")
            raise
        finally:
            conn.close()

    def init_database(self):
        """Veritabanı ve tabloları oluştur"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Articles tablosu
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    url TEXT UNIQUE,
                    source TEXT NOT NULL,
                    sentiment REAL,
                    date TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # İndeksler (performans için)
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_source ON articles(source)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_date ON articles(date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sentiment ON articles(sentiment)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_url ON articles(url)')

            logger.info("✅ Veritabanı hazır")

    def insert_article(self, article) -> Optional[int]:
        """
        Tek bir haber ekle (Duplicate URL'leri atla)

        Args:
            article: NewsArticle dataclass veya Dict

        Returns:
            Optional[int]: Eklenen kaydın ID'si (duplicate ise None)
        """
        try:
            # NewsArticle dataclass ise dict'e çevir
            if hasattr(article, 'to_dict'):
                article_dict = article.to_dict()
            else:
                article_dict = article

            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # URL duplicate kontrolü
                url = article_dict.get('url')
                if url:
                    cursor.execute('SELECT id FROM articles WHERE url = ?', (url,))
                    if cursor.fetchone():
                        return None  # Duplicate, ekleme
                
                cursor.execute('''
                    INSERT INTO articles (title, url, source, sentiment, date)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    article_dict.get('title'),
                    url,
                    article_dict.get('source'),
                    article_dict.get('sentiment'),
                    article_dict.get('date', datetime.now())
                ))
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Veritabanı hatası: {e}")
            return None

    def insert_articles_bulk(self, articles: List) -> Dict[str, int]:
        """
        Toplu haber ekleme (Duplicate kontrolü ile)

        Args:
            articles (List): NewsArticle dataclass listesi veya Dict listesi

        Returns:
            Dict: {'saved': int, 'failed': int, 'duplicate': int}
        """
        saved = 0
        failed = 0
        duplicate = 0

        for article in articles:
            result = self.insert_article(article)
            if result is None:
                # None dönerse duplicate veya hata
                duplicate += 1
            elif result:
                saved += 1
            else:
                failed += 1

        logger.info(f"✅ {saved} YENİ haber kaydedildi, {duplicate} duplicate atlandı, {failed} başarısız")
        return {'saved': saved, 'failed': failed, 'duplicate': duplicate}

    def get_all_articles(self,
                         source: Optional[str] = None,
                         limit: int = 1000) -> pd.DataFrame:
        """
        Tüm haberleri getir

        Args:
            source (str, optional): Belirli bir kaynağı filtrele
            limit (int): Maksimum kayıt sayısı

        Returns:
            pd.DataFrame: Haber verileri
        """
        with self.get_connection() as conn:
            query = "SELECT * FROM articles"
            params = []

            if source:
                query += " WHERE source = ?"
                params.append(source)

            query += " ORDER BY date DESC LIMIT ?"
            params.append(limit)

            df = pd.read_sql_query(query, conn, params=params)

            # Tarih formatını düzelt
            if not df.empty and 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce')

            return df

    def get_article_by_id(self, article_id: int) -> Optional[Dict]:
        """
        ID'ye göre tek bir haber getir

        Args:
            article_id (int): Haber ID

        Returns:
            Optional[Dict]: Haber bilgileri
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM articles WHERE id = ?", (article_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_article(self, article_id: int, updates: Dict) -> bool:
        """
        Haberi güncelle

        Args:
            article_id (int): Haber ID
            updates (Dict): Güncellenecek alanlar

        Returns:
            bool: Başarı durumu
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Dinamik UPDATE query
                fields = ', '.join([f"{k} = ?" for k in updates.keys()])
                values = list(updates.values()) + [article_id]

                cursor.execute(f"UPDATE articles SET {fields} WHERE id = ?", values)

                logger.info(f"✅ Haber {article_id} güncellendi")
                return True
        except Exception as e:
            logger.error(f"Güncelleme hatası: {e}")
            return False

    def delete_article(self, article_id: int) -> bool:
        """
        Haberi sil

        Args:
            article_id (int): Haber ID

        Returns:
            bool: Başarı durumu
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM articles WHERE id = ?", (article_id,))
                logger.info(f"✅ Haber {article_id} silindi")
                return True
        except Exception as e:
            logger.error(f"Silme hatası: {e}")
            return False

    def delete_all_articles(self) -> bool:
        """
        Tüm haberleri sil

        Returns:
            bool: Başarı durumu
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM articles")
                count = cursor.rowcount
                logger.info(f"✅ {count} haber silindi")
                return True
        except Exception as e:
            logger.error(f"Silme hatası: {e}")
            return False

    def get_statistics(self) -> Dict:
        """
        Genel istatistikleri getir

        Returns:
            Dict: İstatistik bilgileri
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Toplam haber
            cursor.execute("SELECT COUNT(*) as total FROM articles")
            total = cursor.fetchone()['total']

            # Kaynak dağılımı
            cursor.execute("""
                SELECT source, COUNT(*) as count 
                FROM articles 
                GROUP BY source
            """)
            sources = {row['source']: row['count'] for row in cursor.fetchall()}

            # Ortalama sentiment
            cursor.execute("SELECT AVG(sentiment) as avg_sentiment FROM articles")
            avg_sentiment = cursor.fetchone()['avg_sentiment'] or 0

            # Tarih aralığı
            cursor.execute("SELECT MIN(date) as min_date, MAX(date) as max_date FROM articles")
            date_row = cursor.fetchone()

            return {
                'total_articles': total,
                'sources': sources,
                'avg_sentiment': round(avg_sentiment, 3),
                'date_range': {
                    'min': date_row['min_date'],
                    'max': date_row['max_date']
                }
            }

    def search_articles(self, keyword: str, limit: int = 50) -> pd.DataFrame:
        """
        Anahtar kelime ile ara

        Args:
            keyword (str): Arama kelimesi
            limit (int): Maksimum sonuç

        Returns:
            pd.DataFrame: Bulunan haberler
        """
        with self.get_connection() as conn:
            query = """
                SELECT * FROM articles 
                WHERE title LIKE ? 
                ORDER BY date DESC 
                LIMIT ?
            """
            df = pd.read_sql_query(query, conn, params=(f'%{keyword}%', limit))

            if not df.empty:
                df['date'] = pd.to_datetime(df['date'], errors='coerce')

            return df

    def export_to_csv(self, filename='news_export.csv'):
        """
        Verileri CSV'ye aktar

        Args:
            filename (str): Çıktı dosyası
        """
        df = self.get_all_articles()
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        logger.info(f"✅ {len(df)} haber {filename} dosyasına aktarıldı")

    def get_sources(self) -> List[str]:
        """
        Veritabanındaki tüm kaynakları getir

        Returns:
            List[str]: Kaynak listesi
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT source FROM articles")
            return [row['source'] for row in cursor.fetchall()]


# Test fonksiyonu
if __name__ == "__main__":
    db = DatabaseManager('test_news.db')

    print("=" * 50)
    print("DATABASE MODÜLÜ TEST")
    print("=" * 50)

    # Test verisi ekle
    test_articles = [
        {
            'title': 'Test Haber 1',
            'url': 'https://example.com/1',
            'source': 'Test Source',
            'sentiment': 0.5,
            'date': datetime.now()
        },
        {
            'title': 'Test Haber 2',
            'url': 'https://example.com/2',
            'source': 'Test Source',
            'sentiment': -0.3,
            'date': datetime.now()
        }
    ]

    # Ekle
    result = db.insert_articles_bulk(test_articles)
    print(f"\n✅ {result['saved']} haber eklendi")

    # İstatistikler
    stats = db.get_statistics()
    print(f"\n📊 İstatistikler:")
    print(f"   Toplam: {stats['total_articles']}")
    print(f"   Kaynaklar: {stats['sources']}")
    print(f"   Avg Sentiment: {stats['avg_sentiment']}")

    # Tüm haberleri getir
    df = db.get_all_articles()
    print(f"\n📰 {len(df)} haber getirildi")

    # Temizle
    db.delete_all_articles()
    print("\n🗑️  Test veritabanı temizlendi")