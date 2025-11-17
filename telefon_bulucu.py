import pandas as pd
import re
import requests
from bs4 import BeautifulSoup
import time
import random
from urllib.parse import urljoin, urlparse

# -----------------------------------
# Ayarlar
# -----------------------------------
INPUT_EXCEL = "firma_listesi.xlsx"
OUTPUT_EXCEL = "firma_listesi_sonuclu.xlsx"

# Gelişmiş telefon regex (Türkiye formatları)
PHONE_REGEX = re.compile(
    r"(\+?\s*90\s*[\(\s]?\d{3}[\)\s]?\s*\d{3}\s*\d{2}\s*\d{2}|0\s*[\(\s]?\d{3}[\)\s]?\s*\d{3}\s*\d{2}\s*\d{2})"
)

# Rate limiting ayarları (engellenmeyi önlemek için)
MIN_DELAY = 3  # saniye
MAX_DELAY = 6  # saniye

# User-Agent listesi (bot gibi görünmemek için)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

# İletişim sayfası anahtar kelimeleri
CONTACT_KEYWORDS = ['iletisim', 'contact', 'hakkimizda', 'about', 'bize-ulasin', 'contact-us']


def get_random_headers():
    """Rastgele User-Agent döndürür"""
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }


def search_google(query, num_results=5):
    """
    Google'da arama yapar ve sonuç URL'lerini döndürür
    SERPAPI yerine doğrudan web scraping kullanır
    """
    try:
        search_url = f"https://www.google.com/search?q={requests.utils.quote(query)}&hl=tr&gl=tr"

        response = requests.get(search_url, headers=get_random_headers(), timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        links = []

        # Google arama sonuçlarından linkleri çıkar
        for g in soup.find_all('div', class_='g'):
            anchors = g.find_all('a')
            for anchor in anchors:
                link = anchor.get('href')
                if link and link.startswith('http'):
                    links.append(link)
                    if len(links) >= num_results:
                        break
            if len(links) >= num_results:
                break

        # Alternatif yöntem: cite etiketlerinden URL'leri al
        if not links:
            for cite in soup.find_all('cite'):
                url = cite.text
                if url and not url.startswith('http'):
                    url = 'https://' + url
                if url:
                    links.append(url)
                    if len(links) >= num_results:
                        break

        return links[:num_results]

    except Exception as e:
        print(f"   ⚠ Google arama hatası: {e}")
        return []


def extract_phone_from_text(text):
    """Metinden telefon numarası çıkarır"""
    if not text:
        return None

    match = PHONE_REGEX.search(text)
    if match:
        phone = match.group(0)
        # Telefonu temizle
        phone = re.sub(r'\s+', ' ', phone).strip()
        return phone
    return None


def find_contact_page(base_url, soup):
    """
    Ana sayfadan iletişim sayfası linkini bulmaya çalışır
    """
    contact_urls = []

    try:
        for link in soup.find_all('a', href=True):
            href = link.get('href', '').lower()
            text = link.get_text('', strip=True).lower()

            # İletişim sayfası olabilecek linkleri bul
            for keyword in CONTACT_KEYWORDS:
                if keyword in href or keyword in text:
                    full_url = urljoin(base_url, link['href'])
                    if full_url not in contact_urls:
                        contact_urls.append(full_url)
                        break

            if len(contact_urls) >= 3:  # En fazla 3 iletişim sayfası kontrol et
                break

    except Exception as e:
        print(f"   ⚠ İletişim sayfası arama hatası: {e}")

    return contact_urls


def scrape_phone_from_url(url, check_contact_page=True):
    """
    Verilen URL'den telefon numarası çıkarmaya çalışır
    İletişim sayfasını da kontrol edebilir
    """
    try:
        response = requests.get(url, headers=get_random_headers(), timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # 1) Ana sayfadan telefon ara
        phone = extract_phone_from_text(response.text)
        if phone:
            return phone

        # 2) İletişim sayfasını kontrol et
        if check_contact_page:
            contact_pages = find_contact_page(url, soup)
            for contact_url in contact_pages:
                try:
                    time.sleep(1)  # Kısa bir bekleme
                    contact_response = requests.get(contact_url, headers=get_random_headers(), timeout=10)
                    contact_response.raise_for_status()

                    phone = extract_phone_from_text(contact_response.text)
                    if phone:
                        return phone
                except:
                    continue

        return None

    except Exception as e:
        print(f"   ⚠ URL scraping hatası ({url}): {e}")
        return None


def find_phone_free(query):
    """
    SERPAPI kullanmadan ücretsiz olarak telefon numarası bulur
    """
    try:
        print(f"   → Google'da aranıyor...")

        # Google'da ara
        urls = search_google(query + " telefon iletişim", num_results=5)

        if not urls:
            print(f"   ⚠ Arama sonucu bulunamadı")
            return None

        print(f"   → {len(urls)} sonuç bulundu, kontrol ediliyor...")

        # Her URL'yi kontrol et
        for i, url in enumerate(urls, 1):
            print(f"   → [{i}/{len(urls)}] Kontrol ediliyor: {urlparse(url).netloc}")

            phone = scrape_phone_from_url(url, check_contact_page=True)

            if phone:
                return phone

            # Sonraki URL'ye geçmeden önce bekle (rate limiting)
            if i < len(urls):
                time.sleep(random.uniform(1, 2))

        return None

    except Exception as e:
        print(f"   ✖ Hata: {e}")
        return None


# -----------------------------------
# Excel Okuma
# -----------------------------------
def main():
    print("=" * 60)
    print("ÜCRETSİZ FİRMA TELEFON BULUCU")
    print("SERPAPI kullanmadan web scraping ile çalışır")
    print("=" * 60)
    print()

    try:
        df = pd.read_excel(INPUT_EXCEL)
        print(f"✔ Excel dosyası okundu: {len(df)} firma bulundu")
    except FileNotFoundError:
        print(f"✖ HATA: '{INPUT_EXCEL}' dosyası bulunamadı!")
        return
    except Exception as e:
        print(f"✖ HATA: Excel dosyası okunamadı: {e}")
        return

    firma_col = df.columns[0]  # İlk kolon firma adı
    telefon_col = "Telefon"

    if telefon_col not in df.columns:
        df[telefon_col] = ""

    print(f"✔ Firma kolonu: '{firma_col}'")
    print(f"✔ Rate limiting: {MIN_DELAY}-{MAX_DELAY} saniye bekleme")
    print()
    print("-" * 60)

    # -----------------------------------
    # Firma Liste Tarama
    # -----------------------------------
    toplam = len(df)
    bulunan = 0
    bulunamayan = 0

    for i, row in df.iterrows():
        firma = str(row[firma_col]).strip()

        print()
        print(f"[{i+1}/{toplam}] 🔍 Aranıyor: {firma}")

        # Ücretsiz yöntemle telefon bul
        phone = find_phone_free(firma)

        if phone:
            print(f"   ✔ BULUNDU: {phone}")
            df.loc[i, telefon_col] = phone
            bulunan += 1
        else:
            print(f"   ✖ Bulunamadı")
            df.loc[i, telefon_col] = "Bulunamadı"
            bulunamayan += 1

        # Her aramadan sonra rate limiting (engellenmeyi önlemek için)
        if i < toplam - 1:  # Son firmadan sonra beklemeye gerek yok
            wait_time = random.uniform(MIN_DELAY, MAX_DELAY)
            print(f"   ⏳ {wait_time:.1f} saniye bekleniyor...")
            time.sleep(wait_time)

    # -----------------------------------
    # Sonuç Kaydetme
    # -----------------------------------
    print()
    print("=" * 60)
    print("İSTATİSTİKLER")
    print("=" * 60)
    print(f"Toplam firma: {toplam}")
    print(f"Bulunan: {bulunan} ({bulunan/toplam*100:.1f}%)")
    print(f"Bulunamayan: {bulunamayan} ({bulunamayan/toplam*100:.1f}%)")
    print()

    try:
        df.to_excel(OUTPUT_EXCEL, index=False)
        print(f"✔ Sonuçlar kaydedildi: {OUTPUT_EXCEL}")
    except Exception as e:
        print(f"✖ HATA: Dosya kaydedilemedi: {e}")

    print("=" * 60)
    print("İŞLEM TAMAMLANDI!")
    print("=" * 60)


if __name__ == "__main__":
    main()