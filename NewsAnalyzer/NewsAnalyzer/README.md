# 📰 News Sentiment Analyzer

**Gerçek zamanlı haber duygu analizi ve görselleştirme platformu**

BBC, CNN, Al Jazeera ve NPR gibi kaynaklardan otomatik haber çekimi yapan, sentiment analizi gerçekleştiren ve interaktif dashboard ile sonuçları görselleştiren Python uygulaması.

---

## 🚀 Hızlı Başlangıç

```bash
# 1. Repository'yi klonla
git clone <repo-url>
cd NewsAnalyzer

# 2. Bağımlılıkları yükle
pip install -r requirements.txt

# 3. Uygulamayı çalıştır
streamlit run Ana_Sayfa.py
```

**URL**: http://localhost:8501

---

## 📁 Proje Yapısı

```
NewsAnalyzer/
│
├── Ana_Sayfa.py             # Ana giriş noktası
├── models.py                # Veri modelleri (NewsArticle)
├── requirements.txt         # Python bağımlılıkları
├── news.db                  # SQLite veritabanı
│
├── scraper/                 # Web Scraping Modülü
│   ├── __init__.py
│   └── manager.py           # Threading ile paralel scraping
│
├── database/                # Database Modülü
│   ├── __init__.py
│   └── repository.py        # SQLite CRUD operasyonları
│
├── analyzer/                # Sentiment Analysis Modülü
│   ├── __init__.py
│   └── sentiment.py         # TextBlob NLP analizi
│
├── dashboard/               # UI & Visualization Modülü
│   ├── __init__.py
│   └── app.py              # Dashboard bileşenleri
│
└── pages/                   # Streamlit sayfaları
    ├── 1_Genel_Bakis.py    # Duygu dağılımı ve kaynak analizi
    ├── 2_Trend_Analizi.py  # Zaman içinde trend grafikleri
    ├── 3_Anahtar_Kelimeler.py  # Kelime bulutu ve trend kelimeler
    └── 4_Haberler.py       # Tüm haberlerin listesi
```

---

## 🎯 Özellikler

### 🔍 Veri Toplama
- **4 Haber Kaynağı**: BBC News, CNN, Al Jazeera, NPR
- **Paralel Scraping**: ThreadPoolExecutor ile 4 worker thread
- **Otomatik Duplicate Kontrolü**: URL bazlı tekrar önleme
- **Real-time Scraping**: Her tıklamada güncel haberler

### 🧠 Analiz
- **Sentiment Analysis**: TextBlob ile duygu skoru (-1 ile +1 arası)
- **Otomatik Etiketleme**: Positive, Neutral, Negative
- **Kaynak Bazında İstatistikler**: Her kaynağın sentiment ortalaması
- **Trend Kelimeleri**: En sık geçen anahtar kelimeler
- **Zaman Serisi Analizi**: Günlük sentiment trendleri

### 📊 Görselleştirme
- **Ana Dashboard**: KPI metrikleri (toplam haber, ortalama duygu, kaynak sayısı)
- **Pie Chart**: Sentiment dağılımı (Pozitif/Nötr/Negatif)
- **Bar Charts**: Kaynak bazında haber sayısı ve sentiment karşılaştırması
- **Timeline**: Zaman içinde sentiment değişimi
- **Box Plot**: Kaynak bazında sentiment dağılımı
- **Kelime Bulutu**: En popüler anahtar kelimeler
- **Haber Listesi**: Filtrelenebilir ve sıralanabilir tam liste

### 🎛️ Filtreler
- **Kaynak Filtresi**: Belirli haber kaynaklarını seç
- **Tarih Aralığı**: İstediğin tarih aralığını filtrele
- **Sentiment Filtresi**: Pozitif, Nötr veya Negatif haberleri göster
- **Sıralama**: Sentiment değerine göre artan/azalan

---

## 🛠️ Teknolojiler

| Kategori | Teknoloji | Versiyon | Kullanım |
|----------|-----------|----------|----------|
| **Language** | Python | 3.13+ | Ana dil |
| **UI Framework** | Streamlit | 1.31.1 | Web arayüzü |
| **Database** | SQLite | 3.x | Veri saklama |
| **Web Scraping** | BeautifulSoup4 | 4.12.2 | HTML parsing |
| **HTTP** | Requests | 2.31.0 | Web istekleri |
| **NLP** | TextBlob | 0.17.1 | Sentiment analizi |
| **Visualization** | Plotly | 5.18.0 | İnteraktif grafikler |
| **Data Processing** | Pandas | 2.1.3 | DataFrame operasyonları |
| **Threading** | concurrent.futures | stdlib | Paralel scraping |

---

## 📐 Mimari

### Veri Akışı

1. **Kullanıcı "YENİ HABERLER ÇEK" butonuna tıklar**
2. `NewsScraper` 4 kaynaktan paralel olarak haber çeker (Threading)
3. Her haber `NewsArticle` dataclass olarak oluşturulur
4. `DatabaseManager` haberleri SQLite'a kaydeder (duplicate kontrolü ile)
5. `NewsAnalyzer` haberlere sentiment skoru ve etiket ekler
6. `DashboardUI` verileri Plotly grafikleri ile görselleştirir
7. Kullanıcı filtreleri değiştirerek verileri keşfeder

---

## 📊 Veritabanı Şeması

```sql
CREATE TABLE articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    url TEXT UNIQUE,
    source TEXT NOT NULL,
    sentiment REAL,
    date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- İndeksler (Performans)
CREATE INDEX idx_source ON articles(source);
CREATE INDEX idx_date ON articles(date);
CREATE INDEX idx_sentiment ON articles(sentiment);
CREATE INDEX idx_url ON articles(url);
```

---

## 🧪 Kullanım

### 1. Ana Sayfa
- Dashboard'a genel bakış
- Toplam haber sayısı, ortalama sentiment, kaynak dağılımı
- Son trendleri gösteren grafikler
- **YENİ HABERLER ÇEK** butonu ile veri toplama

### 2. Genel Bakış
- Duygu dağılımı (Pie chart)
- Kaynak dağılımı (Bar chart)
- Kaynak ve duygu karşılaştırması
- Özet istatistikler

### 3. Trend Analizi
- Zaman içinde sentiment değişimi
- Günlük haber sayısı
- Box plot ve histogram grafikleri
- İlişki analizi

### 4. Anahtar Kelimeler
- En popüler 20 kelime (Bar chart)
- Kelime bulutu görselleştirmesi
- Kelime frekansları

### 5. Haberler
- Tüm haberlerin tam listesi
- Sentiment'e göre sıralama (↑/↓)
- Her haber için:
  - Başlık
  - Kaynak
  - Tarih
  - Sentiment skoru
  - Direkt link
- Sayfalama (20 haber/sayfa)

---

## 🎨 Özelleştirme

### Yeni Haber Kaynağı Ekleme

`scraper/manager.py` içine yeni scraping fonksiyonu ekle:

```python
def scrape_yeni_kaynak(self) -> List[NewsArticle]:
    articles = []
    try:
        url = "https://yeni-kaynak.com"
        response = requests.get(url, headers=self.headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Scraping mantığı...
        
        return articles
    except Exception as e:
        logger.error(f"Hata: {e}")
        return articles
```

Sonra `scrape_all()` metoduna ekle:

```python
scraping_functions = [
    self.scrape_bbc,
    self.scrape_cnn,
    self.scrape_aljazeera,
    self.scrape_npr,
    self.scrape_yeni_kaynak  # Yeni!
]
```

---

## 🐛 Sorun Giderme

### Scraping başarısız oluyor
- İnternet bağlantınızı kontrol edin
- Haber siteleri HTML yapısını değiştirmiş olabilir
- User-Agent header'ını güncelleyin

### Veritabanı hatası
- `news.db` dosyasını silin, otomatik yeniden oluşturulacak
- SQLite kurulu olduğundan emin olun

### Streamlit çalışmıyor
- Port 8501 meşgul olabilir: `streamlit run Ana_Sayfa.py --server.port 8502`
- Bağımlılıkları yeniden yükleyin: `pip install -r requirements.txt --force-reinstall`

---

## 📈 Gelecek Geliştirmeler

- [ ] Daha fazla haber kaynağı (Reuters, The Guardian, vb.)
- [ ] Gelişmiş NLP (BERT, Transformer modeller)
- [ ] Çoklu dil desteği
- [ ] Notification sistemi (yeni haberler için)
- [ ] API endpoint'leri
- [ ] Docker containerization
- [ ] Otomatik scraping scheduler (cron job)
- [ ] Export özellikleri (CSV, PDF rapor)

---

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/yeni-ozellik`)
3. Değişikliklerinizi commit edin (`git commit -m 'Yeni özellik eklendi'`)
4. Branch'inizi push edin (`git push origin feature/yeni-ozellik`)
5. Pull Request oluşturun

---

## 📝 Lisans

MIT License - Eğitim amaçlı proje

---

## 👥 Ekip

Bu proje modüler bir mimari ile geliştirilmiştir:

- **Modül 1**: Web Scraping & Threading
- **Modül 2**: Database Operations
- **Modül 3**: Sentiment Analysis & NLP
- **Modül 4**: Dashboard & Visualization

---

**Son Güncelleme**: 11 Aralık 2025
