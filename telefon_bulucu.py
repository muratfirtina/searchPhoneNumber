import pandas as pd
import re
import requests
from ddgs import DDGS
from agentic_search import AgenticPhoneSearcher

# -----------------------------------
# Ayarlar
# -----------------------------------
# 🆓 TAMAMEN ÜCRETSİZ! API KEY GEREKMİYOR!

INPUT_EXCEL = "/mnt/data/firma_listesi.xlsx"
OUTPUT_EXCEL = "/mnt/data/firma_listesi_sonuclu.xlsx"

# Agentic arama kullanılsın mı? (True = Web sitesi bulup iletişim sayfasına girer)
USE_AGENTIC_SEARCH = True

PHONE_REGEX = re.compile(
    r"(?:\+90|0)?[\s\(\-]?\d{3}[\s\)\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}"
)

# -----------------------------------
# DuckDuckGo ile Standart Telefon Arama
# 🆓 TAMAMEN ÜCRETSİZ - API KEY GEREKMİYOR!
# -----------------------------------
def find_phone_with_duckduckgo(query):
    """
    DuckDuckGo ile basit arama yap (snippet'lerden telefon ara)
    Fallback fonksiyon - Agentic arama başarısız olursa kullanılır
    """
    try:
        # DuckDuckGo ile arama
        with DDGS() as ddgs:
            results = list(ddgs.text(
                keywords=query + " telefon",
                region='tr-tr',
                safesearch='off',
                max_results=5
            ))

        # 1) Snippet'lerden telefon ara
        for result in results:
            title = result.get('title', '')
            body = result.get('body', '')
            text = title + " " + body

            match = PHONE_REGEX.search(text)
            if match:
                return match.group(0)

        # 2) URL'lerden telefon ara
        for result in results:
            link = result.get('href', '') or result.get('link', '')
            if link:
                try:
                    resp = requests.get(
                        link,
                        timeout=8,
                        headers={"User-Agent": "Mozilla/5.0"},
                    )
                    match = PHONE_REGEX.search(resp.text)
                    if match:
                        return match.group(0)
                except:
                    pass

        return None

    except Exception as e:
        print(f"   ⚠ DuckDuckGo hatası: {e}")
        return None


# -----------------------------------
# Excel Okuma
# -----------------------------------
df = pd.read_excel(INPUT_EXCEL)

firma_col = df.columns[0]  # İlk kolon firma adıysa
telefon_col = "Telefon"

if telefon_col not in df.columns:
    df[telefon_col] = ""


# -----------------------------------
# Firma Liste Tarama
# -----------------------------------

# Agentic searcher'ı başlat (eğer kullanılacaksa)
agentic_searcher = None
if USE_AGENTIC_SEARCH:
    agentic_searcher = AgenticPhoneSearcher()  # API KEY GEREKMİYOR!
    print("🆓 ✨ TAMAMEN ÜCRETSİZ Agentic arama modu aktif!")
    print("   (Web sitesi bulup iletişim sayfasına girecek)\n")
else:
    print("🆓 📋 TAMAMEN ÜCRETSİZ Standart arama modu aktif!")
    print("   (Sadece snippet'lerden arayacak)\n")

for i, row in df.iterrows():
    firma = str(row[firma_col]).strip()
    print(f"🔍 [{i+1}/{len(df)}] Aranıyor: {firma}")

    phone = None

    # Agentic arama kullan
    if USE_AGENTIC_SEARCH and agentic_searcher:
        phone = agentic_searcher.find_phone_number(firma)

    # Agentic arama başarısız olduysa veya kullanılmıyorsa, standart DuckDuckGo aramayı dene
    if not phone:
        if USE_AGENTIC_SEARCH:
            print("   ⚠ Agentic arama başarısız, standart aramaya geçiliyor...")
        phone = find_phone_with_duckduckgo(firma)

    if phone:
        print(f"   ✔ Bulundu: {phone}")
        df.loc[i, telefon_col] = phone
    else:
        print(f"   ✖ Bulunamadı")
        df.loc[i, telefon_col] = "Bulunamadı"

    print()  # Boş satır ekle


# -----------------------------------
# Sonuç Kaydetme
# -----------------------------------
df.to_excel(OUTPUT_EXCEL, index=False)
print("\n✔ İşlem tamamlandı!")
print("Dosya kaydedildi:", OUTPUT_EXCEL)