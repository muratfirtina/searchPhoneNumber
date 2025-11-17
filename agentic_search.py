"""
Agentic Phone Number Search Module
===================================
Bu modül şirket web sitelerini bulup, iletişim sayfalarını tarayarak
telefon numaralarını çıkarır.

Çalışma Mantığı:
1. DuckDuckGo'da şirket adını ara (TAMAMEN ÜCRETSİZ, API KEY GEREKMİYOR!)
2. Şirketin resmi web sitesini bul
3. Web sitesinde iletişim/contact sayfalarını ara
4. Telefon numaralarını çıkar
"""

import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from typing import Optional, List, Dict
from duckduckgo_search import DDGS


class AgenticPhoneSearcher:
    """Agentic telefon numarası arama sınıfı - TAMAMEN ÜCRETSİZ!"""

    # Türk telefon numarası regex pattern
    PHONE_REGEX = re.compile(
        r"(\+90\s?\d{3}\s?\d{3}\s?\d{2}\s?\d{2}|0\s?\d{3}\s?\d{3}\s?\d{2}\s?\d{2})"
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
        'address'
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

        Args:
            company_name: Şirket adı

        Returns:
            Bulunan telefon numarası veya None
        """
        print(f"\n🔍 Agentic arama başlatılıyor: {company_name}")

        # 1. Şirketin web sitesini bul
        website_url = self._find_company_website(company_name)
        if not website_url:
            print("   ⚠ Web sitesi bulunamadı")
            return None

        print(f"   ✓ Web sitesi bulundu: {website_url}")

        # 2. İletişim sayfalarını bul ve tara
        phone = self._search_website_for_phone(website_url, company_name)

        if phone:
            print(f"   ✅ Telefon bulundu: {phone}")
        else:
            print("   ❌ Telefon bulunamadı")

        return phone

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
                    keywords=company_name,
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
        excluded_domains = [
            'facebook.com', 'twitter.com', 'instagram.com', 'linkedin.com',
            'youtube.com', 'sahibinden.com', 'hepsiburada.com', 'n11.com',
            'wikipedia.org', 'google.com'
        ]

        parsed = urlparse(url)
        domain = parsed.netloc.lower()

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

            # Tüm linkleri tara
            for link in soup.find_all('a', href=True):
                href = link['href'].lower()

                # İletişim sayfası pattern'i var mı kontrol et
                for pattern in self.CONTACT_PAGE_PATTERNS:
                    if pattern in href:
                        # Relative URL'i absolute'a çevir
                        full_url = urljoin(base_url, link['href'])

                        if full_url not in contact_pages:
                            contact_pages.append(full_url)
                        break

        except Exception as e:
            print(f"   ⚠ İletişim sayfası bulma hatası: {e}")

        return contact_pages

    def _extract_phone_from_page(self, url: str) -> Optional[str]:
        """
        Belirtilen sayfadan telefon numarası çıkar

        Args:
            url: Sayfa URL'i

        Returns:
            Bulunan telefon numarası veya None
        """
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            # HTML'den telefon numarası ara
            match = self.PHONE_REGEX.search(response.text)
            if match:
                return self._clean_phone_number(match.group(0))

            # Daha temiz arama için BeautifulSoup kullan
            soup = BeautifulSoup(response.content, 'lxml')

            # Telefon numarası içerebilecek tag'leri ara
            for tag in soup.find_all(['p', 'span', 'div', 'a', 'li']):
                text = tag.get_text()
                match = self.PHONE_REGEX.search(text)
                if match:
                    return self._clean_phone_number(match.group(0))

            return None

        except Exception as e:
            print(f"   ⚠ Sayfa okuma hatası ({url}): {e}")
            return None

    def _clean_phone_number(self, phone: str) -> str:
        """
        Telefon numarasını temizle ve formatla

        Args:
            phone: Ham telefon numarası

        Returns:
            Temizlenmiş telefon numarası
        """
        # Boşlukları kaldır ve standart formata getir
        cleaned = re.sub(r'\s+', ' ', phone.strip())
        return cleaned


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
