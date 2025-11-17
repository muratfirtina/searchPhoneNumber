"""
Agentic Phone Number Search Module
===================================
Bu modül şirket web sitelerini ve Türk telefon rehberi sitelerini tarayarak
telefon numaralarını çıkarır.

Çalışma Mantığı:
1. Türk telefon rehberi sitelerinde ara (tdrehber.com, telefonnumarasi.org.tr, bulurum.com)
2. DuckDuckGo'da şirket adını ara (TAMAMEN ÜCRETSİZ, API KEY GEREKMİYOR!)
3. Şirketin resmi web sitesini bul
4. Web sitesinde iletişim/contact sayfalarını ara
5. Telefon numaralarını çıkar
"""

import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from typing import Optional, List, Dict
from ddgs import DDGS


class AgenticPhoneSearcher:
    """Agentic telefon numarası arama sınıfı - TAMAMEN ÜCRETSİZ!"""

    # Türk telefon numarası regex pattern (çok esnek - tüm formatları yakalar)
    # Validation _clean_phone_number'da yapılacak
    PHONE_REGEX = re.compile(
        r"(?:\+90\s?|0\s?)?[\s\(]?\d{3}[\s\)]?\s?\d{1,4}\s?\d{0,4}\s?\d{0,2}"
    )

    # İletişim sayfası URL pattern'leri (Türkçe ve İngilizce)
    CONTACT_PAGE_PATTERNS = [
        'iletisim',
        'contact',
        'hakkimizda',
        'about',
        'bize-ulasin',
        'contact-us',
        'iletişim',
        'hakkımızda',
        'adres',
        'address',
        'kundenservice',
        'impressum'
    ]

    # Türk telefon rehberi siteleri
    PHONE_DIRECTORY_SITES = [
        'tdrehber.com',
        'telefonnumarasi.org.tr',
        'bulurum.com'
    ]

    def __init__(self, timeout: int = 10, max_pages: int = 5):
        """
        Args:
            timeout: HTTP request timeout (saniye)
            max_pages: Taranacak maksimum sayfa sayısı

        NOT: API KEY GEREKMİYOR! Tamamen ücretsiz DuckDuckGo kullanılıyor.
        """
        self.timeout = timeout
        self.max_pages = max_pages
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def find_phone_number(self, company_name: str) -> Optional[str]:
        """
        Verilen şirket adı için telefon numarası bul

        Arama Stratejisi:
        1. Şirketin kendi web sitesini bul ve iletişim sayfalarını tara
        2. DuckDuckGo genel arama sonuçlarından ara

        Args:
            company_name: Şirket adı

        Returns:
            Bulunan telefon numarası veya None
        """
        print(f"\n🔍 Agentic arama başlatılıyor: {company_name}")

        # NOT: Telefon rehberi araması devre dışı - yanlış sonuçlar veriyordu
        # Direkt şirketin web sitesine gidiyoruz

        # 1. Şirketin web sitesini bul
        website_url = self._find_company_website(company_name)
        if website_url:
            print(f"   ✓ Web sitesi bulundu: {website_url}")

            # 2. İletişim sayfalarını bul ve tara
            phone = self._search_website_for_phone(website_url, company_name)
            if phone:
                print(f"   ✅ Telefon bulundu: {phone}")
                return phone

        print("   ❌ Telefon bulunamadı")
        return None

    def _search_phone_directories(self, company_name: str) -> Optional[str]:
        """
        Türk telefon rehberi sitelerinde şirket ara

        Args:
            company_name: Şirket adı

        Returns:
            Bulunan telefon numarası veya None
        """
        # DuckDuckGo ile rehber sitelerinde ara
        try:
            with DDGS() as ddgs:
                # Telefon rehberi sitelerinde ara
                for directory_site in self.PHONE_DIRECTORY_SITES:
                    try:
                        search_query = f"site:{directory_site} {company_name}"
                        results = list(ddgs.text(
                            search_query,
                            region='tr-tr',
                            safesearch='off',
                            max_results=3
                        ))

                        if results:
                            print(f"      → {directory_site} kontrol ediliyor...")

                        # Bulunan sayfaları tara
                        for result in results:
                            link = result.get('href', '') or result.get('link', '')
                            if link and directory_site in link:
                                phone = self._extract_phone_from_page(link)
                                if phone:
                                    print(f"      ✓ {directory_site} üzerinde bulundu")
                                    return phone

                    except Exception as e:
                        continue

        except Exception as e:
            print(f"   ⚠ Telefon rehberi arama hatası: {e}")

        return None

    def _find_company_website(self, company_name: str) -> Optional[str]:
        """
        DuckDuckGo arama sonuçlarından şirketin web sitesini bul
        TAMAMEN ÜCRETSİZ - API KEY GEREKMİYOR!

        Args:
            company_name: Şirket adı

        Returns:
            Web sitesi URL'i veya None
        """
        try:
            # DuckDuckGo ile arama yap
            with DDGS() as ddgs:
                results = list(ddgs.text(
                    company_name,
                    region='tr-tr',
                    safesearch='off',
                    max_results=5
                ))

            # Sonuçlardan web sitesi bul
            for result in results:
                link = result.get('href', '') or result.get('link', '')

                # Geçerli bir web sitesi URL'i mi kontrol et
                if self._is_valid_website_url(link):
                    return link

            return None

        except Exception as e:
            print(f"   ⚠ DuckDuckGo arama hatası: {e}")
            return None

    def _is_valid_website_url(self, url: str) -> bool:
        """
        URL'in geçerli bir şirket web sitesi olup olmadığını kontrol et
        (PDF, sosyal medya, vb. olmayan)

        Args:
            url: Kontrol edilecek URL

        Returns:
            True ise geçerli web sitesi
        """
        if not url:
            return False

        # PDF, DOC gibi dosyaları atla
        if url.lower().endswith(('.pdf', '.doc', '.docx', '.xls', '.xlsx')):
            return False

        # Sosyal medya, marketplace vb. siteleri atla
        # ANCAK telefon rehberi sitelerini KABUL ET
        excluded_domains = [
            'facebook.com', 'twitter.com', 'instagram.com', 'linkedin.com',
            'youtube.com', 'sahibinden.com', 'hepsiburada.com', 'n11.com',
            'wikipedia.org', 'google.com'
        ]

        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        # Telefon rehberi siteleri her zaman geçerlidir
        for directory_site in self.PHONE_DIRECTORY_SITES:
            if directory_site in domain:
                return True

        # Diğer excluded domain'leri kontrol et
        for excluded in excluded_domains:
            if excluded in domain:
                return False

        return True

    def _search_website_for_phone(self, base_url: str, company_name: str) -> Optional[str]:
        """
        Web sitesini tara ve telefon numarası bul

        Args:
            base_url: Ana web sitesi URL'i
            company_name: Şirket adı (log için)

        Returns:
            Bulunan telefon numarası veya None
        """
        # Önce ana sayfaya bak
        print(f"   📄 Ana sayfa taranıyor...")
        phone = self._extract_phone_from_page(base_url)
        if phone:
            return phone

        # İletişim sayfalarını bul ve tara
        contact_pages = self._find_contact_pages(base_url)

        if contact_pages:
            print(f"   📇 {len(contact_pages)} iletişim sayfası bulundu")
            for page_url in contact_pages[:self.max_pages]:
                print(f"   📄 Taranıyor: {page_url}")
                phone = self._extract_phone_from_page(page_url)
                if phone:
                    return phone
        else:
            print("   ⚠ İletişim sayfası bulunamadı")

        return None

    def _find_contact_pages(self, base_url: str) -> List[str]:
        """
        Web sitesinde iletişim sayfalarını bul
        Gelişmiş tespit: menu, footer, navigation ve tüm linkler

        Args:
            base_url: Ana web sitesi URL'i

        Returns:
            İletişim sayfası URL'leri listesi
        """
        contact_pages = []

        try:
            response = self.session.get(base_url, timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'lxml')

            # Öncelikli alanlar: menu, footer, nav
            priority_areas = soup.find_all(['nav', 'footer', 'menu', 'header'])

            # Önce öncelikli alanlardaki linkleri tara
            for area in priority_areas:
                for link in area.find_all('a', href=True):
                    href = link['href'].lower()
                    link_text = link.get_text().lower()

                    # İletişim sayfası pattern'i var mı kontrol et (href veya link text'te)
                    for pattern in self.CONTACT_PAGE_PATTERNS:
                        if pattern in href or pattern in link_text:
                            # Relative URL'i absolute'a çevir
                            full_url = urljoin(base_url, link['href'])

                            if full_url not in contact_pages and base_url in full_url:
                                contact_pages.append(full_url)
                            break

            # Sonra tüm linkleri tara
            for link in soup.find_all('a', href=True):
                href = link['href'].lower()
                link_text = link.get_text().lower()

                # İletişim sayfası pattern'i var mı kontrol et
                for pattern in self.CONTACT_PAGE_PATTERNS:
                    if pattern in href or pattern in link_text:
                        # Relative URL'i absolute'a çevir
                        full_url = urljoin(base_url, link['href'])

                        if full_url not in contact_pages and base_url in full_url:
                            contact_pages.append(full_url)
                        break

        except Exception as e:
            print(f"   ⚠ İletişim sayfası bulma hatası: {e}")

        return contact_pages

    def _extract_phone_from_page(self, url: str) -> Optional[str]:
        """
        Belirtilen sayfadan telefon numarası çıkar
        Gelişmiş tespit: tel: linkleri, özel class'lar, contact alanları

        Args:
            url: Sayfa URL'i

        Returns:
            Bulunan telefon numarası veya None
        """
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'lxml')

            # 1. Önce tel: linklerini kontrol et (en güvenilir)
            tel_links = soup.find_all('a', href=re.compile(r'^tel:', re.I))
            for link in tel_links:
                href = link.get('href', '')
                # tel: kısmını kaldır ve temizle
                phone_text = href.replace('tel:', '').replace('Tel:', '')
                match = self.PHONE_REGEX.search(phone_text)
                if match:
                    cleaned = self._clean_phone_number(match.group(0))
                    if cleaned:  # Geçerli numara mı kontrol et
                        return cleaned

            # 2. Telefon ile ilgili class/id'lere sahip elementleri ara
            phone_keywords = ['phone', 'tel', 'telefon', 'contact', 'iletisim']
            for keyword in phone_keywords:
                # Class içinde anahtar kelime olanları bul
                elements = soup.find_all(class_=re.compile(keyword, re.I))
                for elem in elements:
                    text = elem.get_text()
                    match = self.PHONE_REGEX.search(text)
                    if match:
                        cleaned = self._clean_phone_number(match.group(0))
                        if cleaned:
                            return cleaned

                # ID içinde anahtar kelime olanları bul
                elements = soup.find_all(id=re.compile(keyword, re.I))
                for elem in elements:
                    text = elem.get_text()
                    match = self.PHONE_REGEX.search(text)
                    if match:
                        cleaned = self._clean_phone_number(match.group(0))
                        if cleaned:
                            return cleaned

            # 3. "Tel:", "Telefon:", "Phone:" gibi etiketlerin yanındaki numaraları ara
            text_content = soup.get_text()
            phone_label_pattern = r'(?:tel|telefon|phone|gsm|fax|faks)[\s:]+' + self.PHONE_REGEX.pattern
            match = re.search(phone_label_pattern, text_content, re.IGNORECASE)
            if match:
                phone_match = self.PHONE_REGEX.search(match.group(0))
                if phone_match:
                    cleaned = self._clean_phone_number(phone_match.group(0))
                    if cleaned:
                        return cleaned

            # 4. Contact/iletişim section'larını ara
            contact_sections = soup.find_all(['section', 'div'],
                class_=re.compile(r'contact|iletisim|iletişim', re.I))
            for section in contact_sections:
                text = section.get_text()
                match = self.PHONE_REGEX.search(text)
                if match:
                    cleaned = self._clean_phone_number(match.group(0))
                    if cleaned:
                        return cleaned

            # 5. Genel arama - tüm sayfa
            match = self.PHONE_REGEX.search(response.text)
            if match:
                cleaned = self._clean_phone_number(match.group(0))
                if cleaned:
                    return cleaned

            return None

        except Exception as e:
            # Sessizce hata ver, çok fazla log kalabalığı olmasın
            if "timeout" not in str(e).lower():
                print(f"   ⚠ Sayfa okuma hatası: {str(e)[:50]}")
            return None

    def _clean_phone_number(self, phone: str) -> str:
        """
        Telefon numarasını temizle, doğrula ve formatla

        Args:
            phone: Ham telefon numarası

        Returns:
            Temizlenmiş telefon numarası veya None (geçersizse)
        """
        if not phone:
            return None

        # Sadece rakamları al (tüm özel karakterleri kaldır)
        numbers = re.sub(r'[^\d]', '', phone)

        # Türk telefon numarası validasyonu
        # Yerli format: 11 hane (0XXX YYY YY YY)
        # - 0 (ön ek)
        # - XXX (3 haneli alan kodu: TÜM Türkiye şehirleri)
        #   Geçerli ilk rakamlar: 2, 3, 4, 5, 8
        #   Geçersiz: 0, 1, 6, 7, 9
        # - YYY YY YY (7 haneli numara)
        # Uluslararası: 12 hane (90XXX YYY YY YY)

        # Uzunluk kontrolü
        if len(numbers) < 10 or len(numbers) > 12:
            return None

        # 1. 11 haneli yerli numara (0XXX YYY YY YY)
        if len(numbers) == 11 and numbers.startswith('0'):
            area_code = numbers[1:4]  # XXX kısmı

            # TÜM Türk alan kodları kontrolü
            # Geçerli ilk rakamlar: 2 (Marmara), 3 (İç Anadolu/Akdeniz),
            #                       4 (Doğu/Güneydoğu), 5 (Mobil), 8 (Özel servisler)
            if area_code[0] not in ['2', '3', '4', '5', '8']:
                return None

            # Format: 0XXX YYY YY YY
            return f"{numbers[0:4]} {numbers[4:7]} {numbers[7:9]} {numbers[9:11]}"

        # 2. 10 haneli (eksik 0 ön eki - nadiren)
        elif len(numbers) == 10:
            # İlk 3 hane alan kodu olabilir
            area_code = numbers[0:3]
            if area_code[0] in ['2', '3', '4', '5', '8']:
                # 0 ekleyip 11 hane yap
                numbers = '0' + numbers
                return f"{numbers[0:4]} {numbers[4:7]} {numbers[7:9]} {numbers[9:11]}"
            return None

        # 3. 12 haneli uluslararası (90XXX YYY YY YY)
        elif len(numbers) == 12 and numbers.startswith('90'):
            area_code = numbers[2:5]  # XXX kısmı

            # Alan kodu kontrolü - TÜM Türk şehirleri
            if area_code[0] not in ['2', '3', '4', '5', '8']:
                return None

            # Format: +90 XXX YYY YY YY
            return f"+90 {numbers[2:5]} {numbers[5:8]} {numbers[8:10]} {numbers[10:12]}"

        else:
            # Geçersiz format
            return None


# Standalone kullanım için yardımcı fonksiyon
def search_phone_agentic(company_name: str) -> Optional[str]:
    """
    Agentic arama ile telefon numarası bul (standalone fonksiyon)
    TAMAMEN ÜCRETSİZ - API KEY GEREKMİYOR!

    Args:
        company_name: Şirket adı

    Returns:
        Bulunan telefon numarası veya None
    """
    searcher = AgenticPhoneSearcher()
    return searcher.find_phone_number(company_name)


if __name__ == "__main__":
    # Test - API KEY GEREKMİYOR!
    test_company = "5 STAR METAL OTOMOTİV SANAYİ VE TİCARET LİMİTED ŞİRKETİ"

    print("🆓 TAMAMEN ÜCRETSİZ ARAMA - API KEY GEREKMİYOR!")
    result = search_phone_agentic(test_company)
    print(f"\n{'='*50}")
    print(f"Şirket: {test_company}")
    print(f"Sonuç: {result if result else 'Bulunamadı'}")
    print(f"{'='*50}")
