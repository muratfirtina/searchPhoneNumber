# 🔍 Agentic Phone Number Finder (Telefon Numarası Bulucu)

Şirket telefon numaralarını otomatik olarak bulan, **agentic** (otonom) arama özellikli Python uygulaması.

## ✨ Özellikler

### 🤖 Agentic Arama Modu (YENİ!)
Sistem artık **gerçek bir ajan gibi** çalışır:

1. **Google'da şirketi arar**
2. **Şirketin web sitesini bulur** (örn: `https://www.5starmetal.com.tr/`)
3. **Web sitesine girer**
4. **İletişim sayfasını arar** (`/iletisim`, `/contact`, `/hakkimizda`)
5. **Telefon numarasını çıkarır**

### 📋 Standart Arama Modu
Klasik yöntem:
- Google arama sonuçlarındaki snippet'lerden telefon arar
- Knowledge Graph verilerini kontrol eder
- İlk sonuç URL'lerini tarar

## 🚀 Kurulum

### 1. Gerekli Kütüphaneleri Yükleyin

```bash
pip install -r requirements.txt
```

### 2. SerpAPI Anahtarı Alın

[SerpAPI](https://serpapi.com/) sitesinden ücretsiz API anahtarı alın.

### 3. Ayarları Yapın

`telefon_bulucu.py` dosyasında:

```python
SERPAPI_KEY = "BURAYA_API_KEYİNİ_YAZ"  # API anahtarınızı buraya yazın

# Agentic arama kullanılsın mı?
USE_AGENTIC_SEARCH = True  # True = Agentic, False = Standart

# Excel dosya yolları
INPUT_EXCEL = "/mnt/data/firma_listesi.xlsx"
OUTPUT_EXCEL = "/mnt/data/firma_listesi_sonuclu.xlsx"
```

## 📝 Kullanım

### 1. Excel Dosyasını Hazırlayın

`firma_listesi.xlsx` dosyasına şirket adlarını ekleyin (ilk kolonda):

| Firma Adı |
|-----------|
| 5 STAR METAL OTOMOTİV SANAYİ VE TİCARET LİMİTED ŞİRKETİ |
| ACME İNŞAAT A.Ş. |
| ... |

### 2. Scripti Çalıştırın

```bash
python telefon_bulucu.py
```

### 3. Sonuçları İnceleyin

`firma_listesi_sonuclu.xlsx` dosyasında sonuçları bulacaksınız:

| Firma Adı | Telefon |
|-----------|---------|
| 5 STAR METAL... | 0212 555 12 34 |
| ACME İNŞAAT A.Ş. | +90 216 444 55 66 |

## 🔧 Yapılandırma

### Agentic Search Parametreleri

`agentic_search.py` dosyasında:

```python
searcher = AgenticPhoneSearcher(
    serpapi_key=SERPAPI_KEY,
    timeout=10,        # HTTP timeout (saniye)
    max_pages=5        # Taranacak maksimum sayfa sayısı
)
```

### İletişim Sayfası Pattern'leri

Sistem şu URL pattern'lerini arar:
- `iletisim`, `iletişim`
- `contact`, `contact-us`
- `hakkimizda`, `hakkımızda`
- `about`
- `bize-ulasin`
- `adres`, `address`

Daha fazla pattern eklemek için `agentic_search.py` içindeki `CONTACT_PAGE_PATTERNS` listesini düzenleyin.

## 🎯 Örnek Kullanım

### Standalone Agentic Search

```python
from agentic_search import search_phone_agentic

company = "5 STAR METAL OTOMOTİV SANAYİ VE TİCARET LİMİTED ŞİRKETİ"
api_key = "YOUR_API_KEY"

phone = search_phone_agentic(company, api_key)
print(f"Telefon: {phone}")
```

### Class Kullanımı

```python
from agentic_search import AgenticPhoneSearcher

searcher = AgenticPhoneSearcher("YOUR_API_KEY")
phone = searcher.find_phone_number("ACME İNŞAAT A.Ş.")
```

## 📊 Çıktı Örneği

```
✨ Agentic arama modu aktif (Web sitesi bulup iletişim sayfasına girecek)

🔍 [1/2] Aranıyor: 5 STAR METAL OTOMOTİV SANAYİ VE TİCARET LİMİTED ŞİRKETİ

🔍 Agentic arama başlatılıyor: 5 STAR METAL OTOMOTİV SANAYİ VE TİCARET LİMİTED ŞİRKETİ
   ✓ Web sitesi bulundu: https://www.5starmetal.com.tr/
   📄 Ana sayfa taranıyor...
   📇 2 iletişim sayfası bulundu
   📄 Taranıyor: https://www.5starmetal.com.tr/iletisim
   ✅ Telefon bulundu: 0212 555 12 34
   ✔ Bulundu: 0212 555 12 34
```

## 🔍 Nasıl Çalışır?

### Agentic Search Algoritması

```
┌─────────────────────────────────────────────┐
│  1. Google'da şirket adını ara              │
│     └─ SerpAPI kullanarak arama yap         │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  2. Şirketin web sitesini bul               │
│     └─ Geçerli domain'i tespit et           │
│     └─ PDF, sosyal medya vb. filtrele       │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  3. Ana sayfayı tara                        │
│     └─ Telefon numarası var mı kontrol et   │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  4. İletişim sayfalarını bul                │
│     └─ Tüm linkleri tara                    │
│     └─ Pattern eşleştir (iletisim, contact) │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  5. İletişim sayfalarını tara               │
│     └─ Her sayfayı fetch et                 │
│     └─ BeautifulSoup ile parse et           │
│     └─ Regex ile telefon çıkar              │
└─────────────────────────────────────────────┘
```

## 🛠️ Teknik Detaylar

### Telefon Numarası Regex

```regex
(\+90\s?\d{3}\s?\d{3}\s?\d{2}\s?\d{2}|0\s?\d{3}\s?\d{3}\s?\d{2}\s?\d{2})
```

**Eşleşmeler:**
- `+90 555 123 45 67`
- `0212 555 12 34`
- `+905551234567`
- `02125551234`

### Filtrelenen Domain'ler

Şu siteler otomatik olarak atlanır:
- Sosyal medya: `facebook.com`, `twitter.com`, `instagram.com`, `linkedin.com`, `youtube.com`
- Marketplace: `sahibinden.com`, `hepsiburada.com`, `n11.com`
- Diğer: `wikipedia.org`, `google.com`
- Dosya formatları: `.pdf`, `.doc`, `.xls`

## 📚 Dosya Yapısı

```
searchPhoneNumber/
├── telefon_bulucu.py       # Ana script
├── agentic_search.py       # Agentic arama modülü
├── requirements.txt        # Python bağımlılıkları
├── README.md              # Bu dosya
├── firma_listesi.xlsx     # Input dosyası (şirket listesi)
└── firma_listesi_sonuclu.xlsx  # Output dosyası (sonuçlar)
```

## 🐛 Hata Ayıklama

### API Key Hatası
```
HATA (SerpAPI): Invalid API key
```
**Çözüm:** `SERPAPI_KEY` değişkenini kontrol edin.

### Timeout Hatası
```
⚠ Sayfa okuma hatası: timeout
```
**Çözüm:** `timeout` parametresini artırın (varsayılan: 10 saniye).

### İletişim Sayfası Bulunamadı
```
⚠ İletişim sayfası bulunamadı
```
**Çözüm:** Web sitesi standart dışı URL yapısı kullanıyor olabilir. `CONTACT_PAGE_PATTERNS` listesine yeni pattern'ler ekleyin.

## 📄 Lisans

MIT License

## 🤝 Katkıda Bulunma

Pull request'ler kabul edilir!

## 📧 İletişim

Sorularınız için issue açabilirsiniz.

---

**Not:** Bu araç sadece halka açık bilgileri toplar. Gizlilik politikalarına ve yasal düzenlemelere uygun kullanılmalıdır.
