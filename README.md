# 🔍 Agentic Phone Number Finder (Telefon Numarası Bulucu)

🆓 **TAMAMEN ÜCRETSİZ** - API KEY GEREKMİYOR!

Şirket telefon numaralarını otomatik olarak bulan, **agentic** (otonom) arama özellikli Python uygulaması.

## 🆓 Neden Bu Araç?

- ✅ **TAMAMEN ÜCRETSİZ** - Hiçbir API key veya ücretli servis gerekmez
- ✅ **DuckDuckGo Kullanır** - Açık ve ücretsiz arama motoru
- ✅ **Akıllı Web Scraping** - Gerçek web sitelerini ziyaret eder
- ✅ **Sınırsız Kullanım** - Hiçbir API limiti yok

## ✨ Özellikler

### 🤖 Agentic Arama Modu (YENİ!)
Sistem artık **gerçek bir ajan gibi** çalışır ve **çok kaynaklı** arama yapar:

**Adım 1: Türk Telefon Rehberleri** 📚
- `tdrehber.com` sitesinde ara
- `telefonnumarasi.org.tr` sitesinde ara
- `bulurum.com` sitesinde ara

**Adım 2: Şirket Web Sitesi** 🌐
1. **DuckDuckGo'da şirketi arar** (ücretsiz!)
2. **Şirketin web sitesini bulur** (örn: `https://www.5starmetal.com.tr/`)
3. **Web sitesine girer**
4. **İletişim sayfasını arar** - Gelişmiş tespit:
   - Menu, footer, navigation alanlarına öncelik verir
   - `/iletisim`, `/contact`, `/hakkimizda` sayfalarını bulur
   - Link text'lerini de kontrol eder
5. **Telefon numarasını akıllıca çıkarır**:
   - `tel:` linklerini kontrol eder
   - Telefon class/ID'li elementleri bulur
   - "Tel:", "Telefon:" etiketlerini tanır
   - Contact section'larını önceliklendirir

### 📋 Standart Arama Modu
Klasik yöntem:
- DuckDuckGo arama sonuçlarındaki snippet'lerden telefon arar
- İlk sonuç URL'lerini tarar
- Fallback olarak kullanılır

## 🚀 Kurulum

### 1. Gerekli Kütüphaneleri Yükleyin

```bash
pip install -r requirements.txt
```

**Hepsi bu kadar! API key gerekmez!** 🎉

### 2. Ayarları Yapın (İsteğe Bağlı)

`telefon_bulucu.py` dosyasında:

```python
# Agentic arama kullanılsın mı?
USE_AGENTIC_SEARCH = True  # True = Agentic, False = Standart

# Excel dosya yolları
INPUT_EXCEL = "/mnt/data/firma_listesi.xlsx"
OUTPUT_EXCEL = "/mnt/data/firma_listesi_sonuclu.xlsx"
```

**NOT:** Hiçbir API anahtarı veya kayıt gerekmez!

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
    timeout=10,        # HTTP timeout (saniye)
    max_pages=5        # Taranacak maksimum sayfa sayısı
)
# API KEY GEREKMİYOR! 🆓
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

### Standalone Agentic Search - 🆓 API KEY GEREKMİYOR!

```python
from agentic_search import search_phone_agentic

company = "5 STAR METAL OTOMOTİV SANAYİ VE TİCARET LİMİTED ŞİRKETİ"

# API KEY GEREKMİYOR! Direkt kullanın:
phone = search_phone_agentic(company)
print(f"Telefon: {phone}")
```

### Class Kullanımı - 🆓 API KEY GEREKMİYOR!

```python
from agentic_search import AgenticPhoneSearcher

# API KEY GEREKMİYOR!
searcher = AgenticPhoneSearcher()
phone = searcher.find_phone_number("ACME İNŞAAT A.Ş.")
```

## 📊 Çıktı Örneği

```
🆓 ✨ TAMAMEN ÜCRETSİZ Agentic arama modu aktif!
   (Web sitesi bulup iletişim sayfasına girecek)

🔍 [1/2] Aranıyor: 5 STAR METAL OTOMOTİV SANAYİ VE TİCARET LİMİTED ŞİRKETİ

🔍 Agentic arama başlatılıyor: 5 STAR METAL OTOMOTİV SANAYİ VE TİCARET LİMİTED ŞİRKETİ
   📚 Telefon rehberi sitelerinde aranıyor...
      → tdrehber.com kontrol ediliyor...
      → telefonnumarasi.org.tr kontrol ediliyor...
      ✓ telefonnumarasi.org.tr üzerinde bulundu
   ✅ Telefon rehberinde bulundu: 0212 555 12 34
   ✔ Bulundu: 0212 555 12 34
```

**Veya web sitesinden bulma:**

```
🔍 Agentic arama başlatılıyor: ACME İNŞAAT A.Ş.
   📚 Telefon rehberi sitelerinde aranıyor...
      → tdrehber.com kontrol ediliyor...
   ✓ Web sitesi bulundu: https://www.acmeinsaat.com.tr/
   📄 Ana sayfa taranıyor...
   📇 3 iletişim sayfası bulundu
   📄 Taranıyor: https://www.acmeinsaat.com.tr/iletisim
   ✅ Telefon bulundu: 0216 444 55 66
```

## 🔍 Nasıl Çalışır?

### Agentic Search Algoritması

```
┌─────────────────────────────────────────────┐
│  1. Türk Telefon Rehberlerinde Ara          │
│     ├─ tdrehber.com                         │
│     ├─ telefonnumarasi.org.tr               │
│     └─ bulurum.com                          │
│  BULUNDU MU? → EVET: DÖNDÜR ✅               │
└─────────────────────────────────────────────┘
                    ↓ HAYIR
┌─────────────────────────────────────────────┐
│  2. DuckDuckGo'da şirket adını ara          │
│     └─ TAMAMEN ÜCRETSİZ - API KEY YOK!      │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  3. Şirketin web sitesini bul               │
│     └─ Geçerli domain'i tespit et           │
│     └─ PDF, sosyal medya vb. filtrele       │
│     └─ Telefon rehberi sitelerini KABUL ET  │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  4. Ana sayfayı akıllıca tara               │
│     ├─ tel: linklerini kontrol et           │
│     ├─ Telefon class/ID'leri ara            │
│     ├─ "Tel:", "Telefon:" etiketleri bul    │
│     └─ Contact section'larına bak           │
│  BULUNDU MU? → EVET: DÖNDÜR ✅               │
└─────────────────────────────────────────────┘
                    ↓ HAYIR
┌─────────────────────────────────────────────┐
│  5. İletişim sayfalarını bul (Gelişmiş)    │
│     ├─ Menu/Footer/Nav öncelikli tara       │
│     ├─ Link text'lerini de kontrol et       │
│     └─ Pattern eşleştir (iletisim, contact) │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  6. İletişim sayfalarını akıllıca tara      │
│     ├─ tel: linkleri (en güvenilir)         │
│     ├─ Telefon class/ID'li elementler       │
│     ├─ "Tel:", "Telefon:" etiketleri        │
│     ├─ Contact section'lar                  │
│     └─ Genel regex tarama                   │
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

**ÖNEMLİ:** Telefon rehberi siteleri (`tdrehber.com`, `telefonnumarasi.org.tr`, `bulurum.com`) **ASLA** filtrelenmez ve her zaman taranır!

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

### DuckDuckGo Bağlantı Hatası
```
⚠ DuckDuckGo arama hatası: ...
```
**Çözüm:** İnternet bağlantınızı kontrol edin. DuckDuckGo erişilebilir olmalı.

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
