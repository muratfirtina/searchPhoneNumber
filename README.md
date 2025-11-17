# Ücretsiz Firma Telefon Bulucu

Excel dosyasındaki firma listesinden telefonlarını otomatik olarak bulan **%100 ücretsiz** Python scripti.

## ✨ Özellikler

- ✅ **SERPAPI'ye bağımlı değil** - Tamamen ücretsiz
- ✅ Web scraping ile Google araması yapıyor
- ✅ Firmaların iletişim sayfalarını da kontrol ediyor
- ✅ Rate limiting ile engellenme riskini en aza indiriyor
- ✅ Rastgele User-Agent kullanarak bot gibi görünmüyor
- ✅ Her aramayı tek tek yapıyor (aynı anda değil)
- ✅ Bulunamayanları işaretliyor

## 📋 Gereksinimler

```bash
pip install -r requirements.txt
```

Veya manuel olarak:

```bash
pip install pandas openpyxl requests beautifulsoup4 lxml
```

## 🚀 Kullanım

1. **firma_listesi.xlsx** dosyasını projeye ekleyin
   - İlk kolon firma adlarını içermeli

2. Scripti çalıştırın:

```bash
python telefon_bulucu.py
```

3. Sonuçlar **firma_listesi_sonuclu.xlsx** dosyasına kaydedilecek

## ⚙️ Ayarlar

`telefon_bulucu.py` dosyasında düzenleyebileceğiniz ayarlar:

```python
INPUT_EXCEL = "firma_listesi.xlsx"      # Giriş dosyası
OUTPUT_EXCEL = "firma_listesi_sonuclu.xlsx"  # Çıkış dosyası
MIN_DELAY = 3  # Minimum bekleme süresi (saniye)
MAX_DELAY = 6  # Maksimum bekleme süresi (saniye)
```

## 🔍 Nasıl Çalışır?

1. **Google Araması**: Her firma için Google'da "firma adı telefon iletişim" araması yapar
2. **URL Tarama**: Bulunan sonuçların web sayfalarını tek tek kontrol eder
3. **İletişim Sayfası**: Ana sayfada bulamazsa iletişim sayfasını arar
4. **Telefon Çıkarma**: Türkiye telefon formatlarını (0xxx xxx xx xx, +90 xxx xxx xx xx) regex ile bulur
5. **Rate Limiting**: Her aramadan sonra 3-6 saniye bekler (engellenme riski azalır)
6. **Rastgele User-Agent**: Her istekte farklı tarayıcı kimliği kullanır

## 📊 Örnek Çıktı

```
============================================================
ÜCRETSİZ FİRMA TELEFON BULUCU
SERPAPI kullanmadan web scraping ile çalışır
============================================================

✔ Excel dosyası okundu: 10 firma bulundu
✔ Firma kolonu: 'Firma Adı'
✔ Rate limiting: 3-6 saniye bekleme

------------------------------------------------------------

[1/10] 🔍 Aranıyor: ABC Teknoloji
   → Google'da aranıyor...
   → 5 sonuç bulundu, kontrol ediliyor...
   → [1/5] Kontrol ediliyor: abcteknoloji.com
   ✔ BULUNDU: 0212 555 12 34
   ⏳ 4.2 saniye bekleniyor...

[2/10] 🔍 Aranıyor: XYZ Ltd
   → Google'da aranıyor...
   → 5 sonuç bulundu, kontrol ediliyor...
   ✖ Bulunamadı
   ⏳ 5.1 saniye bekleniyor...

============================================================
İSTATİSTİKLER
============================================================
Toplam firma: 10
Bulunan: 7 (70.0%)
Bulunamayan: 3 (30.0%)

✔ Sonuçlar kaydedildi: firma_listesi_sonuclu.xlsx
============================================================
İŞLEM TAMAMLANDI!
============================================================
```

## ⚠️ Önemli Notlar

- **Yavaş çalışır**: Her aramadan sonra 3-6 saniye bekler (bu normaldir)
- **%100 başarı garantisi yok**: Bazı firmaların telefonu bulunamayabilir
- **Etik kullanım**: Sadece yasal amaçlar için kullanın
- **Rate limiting**: Ayarları çok düşürürseniz Google sizi engelleyebilir
- **İnternet bağlantısı**: Stabil internet bağlantısı gereklidir

## 🛡️ Anti-Ban Mekanizmaları

1. **Rate Limiting**: Her aramadan sonra 3-6 saniye rastgele bekleme
2. **User-Agent Rotation**: 5 farklı tarayıcı kimliği rotasyonu
3. **Gerçekçi Headers**: Tam HTTP header setleri
4. **Tek Tek Arama**: Paralel değil, sıralı arama
5. **Timeout**: Her istek max 10 saniye

## 📝 Lisans

Bu proje ücretsizdir ve herkes tarafından kullanılabilir.

## 🤝 Katkıda Bulunma

Pull request'ler memnuniyetle karşılanır!

## 📞 Destek

Sorun yaşarsanız issue açabilirsiniz.
