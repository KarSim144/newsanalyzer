"""
DATA MODELS - Strong typing with dataclasses
Tüm modüller arasında tutarlı veri yapısı
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class NewsArticle:
    """
    Haber makalesi için güçlü veri modeli
    
    Attributes:
        title: Makale başlığı
        url: Makale URL'si
        source: Haber kaynağı (BBC, CNN, Al Jazeera, NPR)
        sentiment: Duygu analizi skoru (-1.0 ~ +1.0)
        date: Çekiliş tarihi
        sentiment_label: Duygu etiketi (Positive/Negative/Neutral) - Optional
    """
    
    title: str
    url: str
    source: str
    sentiment: float
    date: datetime = field(default_factory=datetime.now)
    sentiment_label: Optional[str] = None
    
    def __post_init__(self):
        """Validasyon sonrası işlemler"""
        if not -1.0 <= self.sentiment <= 1.0:
            raise ValueError(f"Sentiment must be between -1.0 and 1.0, got {self.sentiment}")
        
        if not self.title or len(self.title) < 5:
            raise ValueError(f"Title must be at least 5 characters, got '{self.title}'")
        
        valid_sources = {'BBC News', 'CNN', 'Al Jazeera', 'NPR'}
        if self.source not in valid_sources:
            raise ValueError(f"Source must be one of {valid_sources}, got '{self.source}'")
    
    def to_dict(self) -> dict:
        """Convert to dictionary format"""
        return {
            'title': self.title,
            'url': self.url,
            'source': self.source,
            'sentiment': self.sentiment,
            'sentiment_label': self.sentiment_label,
            'date': self.date
        }
    
    def categorize_sentiment(self) -> None:
        """Sentiment skoru etiketi olarak kategorize et"""
        if self.sentiment > 0.1:
            self.sentiment_label = 'Positive'
        elif self.sentiment < -0.1:
            self.sentiment_label = 'Negative'
        else:
            self.sentiment_label = 'Neutral'
    
    def __str__(self) -> str:
        """String representation"""
        return f"NewsArticle(title='{self.title[:30]}...', source='{self.source}', sentiment={self.sentiment:.2f})"
    
    def __repr__(self) -> str:
        """Developer representation"""
        return f"NewsArticle(title={self.title!r}, source={self.source!r}, sentiment={self.sentiment})"
