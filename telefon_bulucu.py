import pandas as pd
import re
import requests
from serpapi import GoogleSearch
from agentic_search import AgenticPhoneSearcher

# -----------------------------------
# Ayarlar
# -----------------------------------
SERPAPI_KEY = "BURAYA_API_KEYİNİ_YAZ"  # ← senin API key

INPUT_EXCEL = "/mnt/data/firma_listesi.xlsx"
OUTPUT_EXCEL = "/mnt/data/firma_listesi_sonuclu.xlsx"

# Agentic arama kullanılsın mı? (True = Web sitesi bulup iletişim sayfasına girer)
USE_AGENTIC_SEARCH = True

PHONE_REGEX = re.compile(
    r"(\+90\s?\d{3}\s?\d{3}\s?\d{2}\s?\d{2}|0\s?\d{3}\s?\d{3}\s?\d{2}\s?\d{2})"
)

# -----------------------------------
# SerpAPI Üzerinden Telefon Bulan Fonksiyon
# -----------------------------------
def find_phone_with_serpapi(query):
    try:
        params = {
            "engine": "google",
            "q": query + " telefon",
            "hl": "tr",
            "gl": "tr",
            "api_key": SERPAPI_KEY,
        }

        search = GoogleSearch(params)
        results = search.get_dict()

        # 1) Direct Answers / Knowledge Graph
        if "knowledge_graph" in results:
            kg = results["knowledge_graph"]
            if "phone" in kg:
                return kg["phone"]

        # 2) Organic Results → Titles + Snippets
        if "organic_results" in results:
            for item in results["organic_results"]:
                text = (item.get("title", "") + " " + item.get("snippet", ""))
                match = PHONE_REGEX.search(text)
                if match:
                    return match.group(0)

        # 3) HTML sayfası içinde arama
        if "organic_results" in results:
            for item in results["organic_results"]:
                if "link" in item:
                    try:
                        resp = requests.get(
                            item["link"],
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
        print("HATA (SerpAPI):", e)
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
    agentic_searcher = AgenticPhoneSearcher(SERPAPI_KEY)
    print("✨ Agentic arama modu aktif (Web sitesi bulup iletişim sayfasına girecek)\n")
else:
    print("📋 Standart arama modu aktif (Sadece snippet'lerden arayacak)\n")

for i, row in df.iterrows():
    firma = str(row[firma_col]).strip()
    print(f"🔍 [{i+1}/{len(df)}] Aranıyor: {firma}")

    phone = None

    # Agentic arama kullan
    if USE_AGENTIC_SEARCH and agentic_searcher:
        phone = agentic_searcher.find_phone_number(firma)

    # Agentic arama başarısız olduysa veya kullanılmıyorsa, eski yöntemi dene
    if not phone:
        if USE_AGENTIC_SEARCH:
            print("   ⚠ Agentic arama başarısız, standart aramaya geçiliyor...")
        phone = find_phone_with_serpapi(firma)

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