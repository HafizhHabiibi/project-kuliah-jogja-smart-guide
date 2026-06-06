from flask import Flask
import requests
from bs4 import BeautifulSoup
import mysql.connector
from datetime import datetime
import re
from apscheduler.schedulers.background import BackgroundScheduler
from bs4 import BeautifulSoup

# TAMBAHAN SELENIUM
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = Flask(__name__)

# ==========================
# DATABASE
# ==========================
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="spk_wisata"
    )


# ==========================
# GEMBIRA LOKA
# ==========================
def scrape_gembiraloka():

    print("🔄 Scraping Gembira Loka...")

    url = "https://gembiralokazoo.com/news/gembira-loka-zoo-umumkan-penyesuaian-harga-tiket-mulai-30-maret"

    try:

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=15
        )

        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()

        prices = re.findall(
            r'Rp\.?\s?(\d{1,3}(?:\.\d{3})*)',
            text
        )

        harga_list = []

        for p in prices:
            harga_list.append(
                int(p.replace('.', ''))
            )

        if len(harga_list) > 0:

            harga_tertinggi = max(harga_list)

            db = get_db_connection()
            cursor = db.cursor()

            query = """
            INSERT INTO tiket_wisata
            (
                nama_wisata,
                jenis_tiket,
                harga,
                sumber,
                last_updated
            )
            VALUES (%s,%s,%s,%s,%s)

            ON DUPLICATE KEY UPDATE
            harga=VALUES(harga),
            sumber=VALUES(sumber),
            last_updated=VALUES(last_updated)
            """

            values = (
                "Gembira Loka Zoo",
                "Harga Maksimum",
                harga_tertinggi,
                "Official",
                datetime.now()
            )

            cursor.execute(query, values)
            db.commit()

            cursor.close()
            db.close()

            print(
                f"✅ Gembira Loka Rp{harga_tertinggi}"
            )

        else:
            print("⚠️ Harga Gembira Loka tidak ditemukan")

    except Exception as e:
        print("❌ Error Gembira Loka:", e)


# ==========================
# PRAMBANAN GOERS (SELENIUM)
# ==========================
def scrape_prambanan():

    print("🔄 Scraping Prambanan...")

    url = "https://widget.goersapp.com/venues/schedules/Candi-Prambanan--candiprambanan/2026-05-24"

    try:

        options = Options()

        # sementara jangan headless dulu
        # supaya bisa lihat browser jalan
        # options.add_argument("--headless")

        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")

        driver = webdriver.Chrome(
            service=Service(
                ChromeDriverManager().install()
            ),
            options=options
        )

        wait = WebDriverWait(driver, 40)

        driver.get(url)

        print("⏳ Tunggu Goers render...")

        # tunggu sampai ada teks Rp
        wait.until(
            lambda d:
            "Rp" in d.page_source
            or "IDR" in d.page_source
        )

        time.sleep(5)

        html = driver.page_source

        print("===== DEBUG GOERS SELENIUM =====")
        print(html[:5000])

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        text = soup.get_text()

        prices = re.findall(
            r'(?:Rp|IDR)\s?(\d{1,3}(?:[.,]\d{3})*)',
            text
        )

        harga_list = []

        for p in prices:

            harga = int(
                p.replace('.', '')
                 .replace(',', '')
            )

            harga_list.append(harga)

        print("DEBUG PRICE:", harga_list)

        driver.quit()

        if len(harga_list) > 0:

            harga_tertinggi = max(
                harga_list
            )

            db = get_db_connection()
            cursor = db.cursor()

            query = """
            INSERT INTO tiket_wisata
            (
                nama_wisata,
                jenis_tiket,
                harga,
                sumber,
                last_updated
            )
            VALUES (%s,%s,%s,%s,%s)

            ON DUPLICATE KEY UPDATE
            harga=VALUES(harga),
            sumber=VALUES(sumber),
            last_updated=VALUES(last_updated)
            """

            values = (
                "Candi Prambanan",
                "Harga Maksimum",
                harga_tertinggi,
                "Goers Selenium",
                datetime.now()
            )

            cursor.execute(
                query,
                values
            )

            db.commit()

            cursor.close()
            db.close()

            print(
                f"✅ Prambanan Rp{harga_tertinggi}"
            )

        else:

            print(
                "⚠️ Harga Prambanan tidak ditemukan"
            )

    except Exception as e:

        print(
            "❌ Error Prambanan:",
            e
        )

# ==========================
# TAMAN SARI / KRATON
# GLOBALTIX DEBUG SCRAPER
# ==========================
def scrape_tamansari():

    print("🔄 Scraping Taman Sari / Kraton...")

    url = "https://kratonjogja-online.globaltix.com/attraction/kraton-taman-sari-35778"

    try:

        options = Options()

        # sementara NON-headless
        # supaya debugging mudah
        # options.add_argument("--headless")

        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")

        driver = webdriver.Chrome(
            service=Service(
                ChromeDriverManager().install()
            ),
            options=options
        )

        wait = WebDriverWait(driver, 40)

        driver.get(url)

        print("⏳ Tunggu GlobalTix render...")

        # tunggu halaman JS
        time.sleep(10)

        html = driver.page_source

        print("===== DEBUG GLOBALTIX =====")
        print(html[:6000])

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        text = soup.get_text()

        # regex harga
        prices = re.findall(
            r'(?:Rp|IDR)\s?(\d{1,3}(?:[.,]\d{3})*)',
            text
        )

        harga_list = []

        for p in prices:

            harga = int(
                p.replace('.', '')
                 .replace(',', '')
            )

            harga_list.append(harga)

        print(
            "DEBUG PRICE TAMAN SARI:",
            harga_list
        )

        driver.quit()

        if len(harga_list) > 0:

            harga_tertinggi = max(
                harga_list
            )

            db = get_db_connection()
            cursor = db.cursor()

            query = """
            INSERT INTO tiket_wisata
            (
                nama_wisata,
                jenis_tiket,
                harga,
                sumber,
                last_updated
            )
            VALUES (%s,%s,%s,%s,%s)

            ON DUPLICATE KEY UPDATE
            harga=VALUES(harga),
            sumber=VALUES(sumber),
            last_updated=VALUES(last_updated)
            """

            values = (
                "Taman Sari / Kraton",
                "Harga Maksimum",
                harga_tertinggi,
                "GlobalTix Selenium",
                datetime.now()
            )

            cursor.execute(
                query,
                values
            )

            db.commit()

            cursor.close()
            db.close()

            print(
                f"✅ Taman Sari Rp{harga_tertinggi}"
            )

        else:

            print(
                "⚠️ Harga Taman Sari belum ditemukan"
            )

    except Exception as e:

        print(
            "❌ Error Taman Sari:",
            e
        )

# ==========================
# SONOBUDOYO OFFICIAL
# ==========================
def scrape_sonobudoyo():

    print("🔄 Scraping Sonobudoyo...")

    url = "https://sonobudoyo.jogjaprov.go.id/id/information"

    try:

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=15
        )

        soup = BeautifulSoup(
            response.text,
            'html.parser'
        )

        text = soup.get_text(
            " ",
            strip=True
        )

        print("===== DEBUG SONOBUDOYO =====")
        print(text[:3000])

        # Cari semua nominal Rp
        prices = re.findall(
            r'Rp\.?\s?(\d{1,3}(?:\.\d{3})*)',
            text
        )

        print("DEBUG PRICE:", prices)

        harga_list = []

        for p in prices:
            harga_list.append(
                int(
                    p.replace('.', '')
                )
            )

        if len(harga_list) > 0:

            # Ambil harga tertinggi
            harga_tertinggi = max(
                harga_list
            )

            db = get_db_connection()
            cursor = db.cursor()

            query = """
            INSERT INTO tiket_wisata
            (
                nama_wisata,
                jenis_tiket,
                harga,
                sumber,
                last_updated
            )
            VALUES (%s,%s,%s,%s,%s)

            ON DUPLICATE KEY UPDATE
            harga=VALUES(harga),
            sumber=VALUES(sumber),
            last_updated=VALUES(last_updated)
            """

            values = (
                "Museum Sonobudoyo",
                "Harga Maksimum",
                harga_tertinggi,
                "Official",
                datetime.now()
            )

            cursor.execute(
                query,
                values
            )

            db.commit()

            cursor.close()
            db.close()

            print(
                f"✅ Sonobudoyo Rp{harga_tertinggi}"
            )

        else:

            print(
                "⚠️ Harga Sonobudoyo tidak ditemukan"
            )

    except Exception as e:

        print(
            "❌ Error Sonobudoyo:",
            e
        )

# ==========================
# WADUK SERMO OFFICIAL
# ==========================
def scrape_waduk_sermo():

    print("🔄 Scraping Waduk Sermo...")

    url = "https://waduksermo.com/karcis-masuk-waduk-sermo/"

    try:

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=15
        )

        soup = BeautifulSoup(
            response.text,
            'html.parser'
        )

        text = soup.get_text(
            " ",
            strip=True
        )

        # DEBUG
        print("===== DEBUG WADUK SERMO =====")
        print(text[:3000])

        # Cari semua nominal Rp
        prices = re.findall(
            r'Rp\.?\s?(\d{1,3}(?:\.\d{3})*)',
            text
        )

        print(
            "DEBUG PRICE:",
            prices
        )

        harga_list = []

        for p in prices:

            harga_list.append(
                int(
                    p.replace('.', '')
                )
            )

        if len(harga_list) > 0:

            # ambil harga tertinggi
            harga_tertinggi = max(
                harga_list
            )

            db = get_db_connection()
            cursor = db.cursor()

            query = """
            INSERT INTO tiket_wisata
            (
                nama_wisata,
                jenis_tiket,
                harga,
                sumber,
                last_updated
            )
            VALUES (%s,%s,%s,%s,%s)

            ON DUPLICATE KEY UPDATE
            harga=VALUES(harga),
            sumber=VALUES(sumber),
            last_updated=VALUES(last_updated)
            """

            values = (
                "Waduk Sermo",
                "Harga Maksimum",
                harga_tertinggi,
                "Official",
                datetime.now()
            )

            cursor.execute(
                query,
                values
            )

            db.commit()

            cursor.close()
            db.close()

            print(
                f"✅ Waduk Sermo Rp{harga_tertinggi}"
            )

        else:

            print(
                "⚠️ Harga Waduk Sermo tidak ditemukan"
            )

    except Exception as e:

        print(
            "❌ Error Waduk Sermo:",
            e
        )

# ==========================
# HEHA SKY VIEW
# ==========================
def scrape_heha():

    print("🔄 Scraping HeHa Sky View...")

    url = "https://id.trip.com/travel-guide/attraction/patuk/heha-sky-view-142511061/?locale=id-ID&curr=IDR"

    try:

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=20
        )

        soup = BeautifulSoup(
            response.text,
            'html.parser'
        )

        text = soup.get_text(
            " ",
            strip=True
        )

        print("===== DEBUG HEHA =====")
        print(text[:4000])

        # Ambil angka setelah "Mulai dari"
        prices = re.findall(
            r'Mulai dari\s+(\d+(?:\.\d+)?)',
            text
        )

        print("DEBUG RAW PRICE:", prices)

        harga_list = []

        for p in prices:

            harga = int(
                float(p)
            )

            # filter supaya bukan angka random
            if 5000 <= harga <= 500000:
                harga_list.append(harga)

        print(
            "DEBUG CLEAN PRICE:",
            harga_list
        )

        if harga_list:

            harga_tertinggi = max(
                harga_list
            )

            db = get_db_connection()
            cursor = db.cursor()

            query = """
            INSERT INTO tiket_wisata
            (
                nama_wisata,
                jenis_tiket,
                harga,
                sumber,
                last_updated
            )
            VALUES (%s,%s,%s,%s,%s)

            ON DUPLICATE KEY UPDATE
            harga=VALUES(harga),
            sumber=VALUES(sumber),
            last_updated=VALUES(last_updated)
            """

            values = (
                "HeHa Sky View",
                "Harga Maksimum",
                harga_tertinggi,
                "Trip.com",
                datetime.now()
            )

            cursor.execute(
                query,
                values
            )

            db.commit()

            cursor.close()
            db.close()

            print(
                f"✅ HeHa Rp{harga_tertinggi}"
            )

        else:

            print(
                "⚠️ Harga HeHa tidak ditemukan"
            )

    except Exception as e:

        print(
            "❌ Error HeHa:",
            e
        )

# ==========================
# DOLANDESO BORO
# ==========================
def scrape_dolandeso():

    print("🔄 Scraping DolaNDeso...")

    url = "https://www.dolandesoboro.com/#pricing"

    try:

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=20
        )

        soup = BeautifulSoup(
            response.text,
            'html.parser'
        )

        text = soup.get_text(
            " ",
            strip=True
        )

        print("===== DEBUG DOLANDESO =====")
        print(text[:5000])

        # cari format Rp85k / Rp 130k
        prices_k = re.findall(
            r'Rp\s?(\d+)\s?k',
            text,
            re.IGNORECASE
        )

        print(
            "DEBUG RAW PRICE:",
            prices_k
        )

        harga_list = []

        for p in prices_k:

            harga = int(p) * 1000

            if 10000 <= harga <= 1000000:
                harga_list.append(harga)

        print(
            "DEBUG CLEAN PRICE:",
            harga_list
        )

        if harga_list:

            harga_tertinggi = max(
                harga_list
            )

            db = get_db_connection()
            cursor = db.cursor()

            query = """
            INSERT INTO tiket_wisata
            (
                nama_wisata,
                jenis_tiket,
                harga,
                sumber,
                last_updated
            )
            VALUES (%s,%s,%s,%s,%s)

            ON DUPLICATE KEY UPDATE
            harga=VALUES(harga),
            sumber=VALUES(sumber),
            last_updated=VALUES(last_updated)
            """

            values = (
                "DolaNDeso Boro",
                "Harga Maksimum",
                harga_tertinggi,
                "Official Website",
                datetime.now()
            )

            cursor.execute(
                query,
                values
            )

            db.commit()

            cursor.close()
            db.close()

            print(
                f"✅ DolaNDeso Rp{harga_tertinggi}"
            )

        else:

            print(
                "⚠️ Harga DolaNDeso tidak ditemukan"
            )

    except Exception as e:

        print(
            "❌ Error DolaNDeso:",
            e
        )

# ==========================
# MUSEUM GUNUNGAPI MERAPI
# ==========================
def scrape_merapi():

    print("🔄 Scraping Museum Gunungapi Merapi...")

    url = "https://mgm.slemankab.go.id/harga-tiket/"

    try:

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=20
        )

        soup = BeautifulSoup(
            response.text,
            'html.parser'
        )

        text = soup.get_text(
            " ",
            strip=True
        )

        print("===== DEBUG MERAPI =====")
        print(text[:5000])

        # cari Rp 5.000 / Rp. 10.000
        prices = re.findall(
            r'Rp\.?\s?(\d{1,3}(?:\.\d{3})*)',
            text
        )

        print(
            "DEBUG RAW PRICE:",
            prices
        )

        harga_list = []

        for p in prices:

            harga = int(
                p.replace('.', '')
            )

            if 1000 <= harga <= 500000:
                harga_list.append(
                    harga
                )

        print(
            "DEBUG CLEAN PRICE:",
            harga_list
        )

        if harga_list:

            harga_tertinggi = max(
                harga_list
            )

            db = get_db_connection()
            cursor = db.cursor()

            query = """
            INSERT INTO tiket_wisata
            (
                nama_wisata,
                jenis_tiket,
                harga,
                sumber,
                last_updated
            )
            VALUES (%s,%s,%s,%s,%s)

            ON DUPLICATE KEY UPDATE
            harga=VALUES(harga),
            sumber=VALUES(sumber),
            last_updated=VALUES(last_updated)
            """

            values = (
                "Museum Gunungapi Merapi",
                "Harga Maksimum",
                harga_tertinggi,
                "Official MGM",
                datetime.now()
            )

            cursor.execute(
                query,
                values
            )

            db.commit()

            cursor.close()
            db.close()

            print(
                f"✅ Museum Merapi Rp{harga_tertinggi}"
            )

        else:

            print(
                "⚠️ Harga Museum Merapi tidak ditemukan"
            )

    except Exception as e:

        print(
            "❌ Error Museum Merapi:",
            e
        )

# ==========================
# SKE CITY PARK
# ==========================
def scrape_ske():

    print("🔄 Scraping SKE City Park...")

    url = "https://skecitypark.com/tickets"

    driver = None

    try:

        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        import time

        options = Options()

        options.add_argument(
            "--headless=new"
        )
        options.add_argument(
            "--disable-gpu"
        )
        options.add_argument(
            "--no-sandbox"
        )
        options.add_argument(
            "--window-size=1920,1080"
        )

        driver = webdriver.Chrome(
            options=options
        )

        driver.get(url)

        print(
            "⏳ Tunggu SKE render..."
        )

        time.sleep(8)

        html = driver.page_source

        print(
            "===== DEBUG SKE ====="
        )
        print(
            html[:5000]
        )

        soup = BeautifulSoup(
            html,
            'html.parser'
        )

        text = soup.get_text(
            " ",
            strip=True
        )

        print(
            "===== DEBUG TEXT SKE ====="
        )
        print(
            text[:4000]
        )

        # Rp100.000 / Rp 35.000
        prices = re.findall(
            r'Rp\.?\s?(\d{1,3}(?:[.,]\d{3})*)',
            text
        )

        print(
            "DEBUG RAW PRICE:",
            prices
        )

        harga_list = []

        for p in prices:

            harga = int(
                p.replace('.', '')
                 .replace(',', '')
            )

            # filter harga masuk akal
            if 5000 <= harga <= 1000000:
                harga_list.append(
                    harga
                )

        print(
            "DEBUG CLEAN PRICE:",
            harga_list
        )

        if harga_list:

            harga_tertinggi = max(
                harga_list
            )

            db = get_db_connection()
            cursor = db.cursor()

            query = """
            INSERT INTO tiket_wisata
            (
                nama_wisata,
                jenis_tiket,
                harga,
                sumber,
                last_updated
            )
            VALUES (%s,%s,%s,%s,%s)

            ON DUPLICATE KEY UPDATE
            harga=VALUES(harga),
            sumber=VALUES(sumber),
            last_updated=VALUES(last_updated)
            """

            values = (
                "SKE City Park",
                "Harga Maksimum",
                harga_tertinggi,
                "Official Website",
                datetime.now()
            )

            cursor.execute(
                query,
                values
            )

            db.commit()

            cursor.close()
            db.close()

            print(
                f"✅ SKE City Park Rp{harga_tertinggi}"
            )

        else:

            print(
                "⚠️ Harga SKE tidak ditemukan"
            )

    except Exception as e:

        print(
            "❌ Error SKE:",
            e
        )

    finally:

        if driver:
            driver.quit()

# ==========================
# JEEP MERAPI TOUR
# ==========================
def scrape_jeep_merapi():

    print("🔄 Scraping Jeep Merapi Tour...")

    url = "https://jeepmerapitour.com/"

    try:

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=20
        )

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        text = soup.get_text(
            separator=" ",
            strip=True
        )

        # DEBUG
        print("===== DEBUG JEEP MERAPI =====")
        print(text[:4000])

        # Cari harga Rp
        prices = re.findall(
            r'Rp\.?\s?(\d{1,3}(?:[.,]\d{3})+)',
            text
        )

        print("DEBUG PRICE:", prices)

        harga_list = []

        for p in prices:

            clean = (
                p.replace('.', '')
                 .replace(',', '')
            )

            try:
                angka = int(clean)

                # Filter harga masuk akal
                if 10000 <= angka <= 5000000:
                    harga_list.append(angka)

            except:
                pass

        print("DEBUG CLEAN PRICE:", harga_list)

        if len(harga_list) > 0:

            harga_tertinggi = max(harga_list)

            db = get_db_connection()
            cursor = db.cursor()

            query = """
            INSERT INTO tiket_wisata
            (
                nama_wisata,
                jenis_tiket,
                harga,
                sumber,
                last_updated
            )
            VALUES (%s,%s,%s,%s,%s)

            ON DUPLICATE KEY UPDATE
            harga=VALUES(harga),
            sumber=VALUES(sumber),
            last_updated=VALUES(last_updated)
            """

            values = (
                "Jeep Merapi Tour",
                "Harga Maksimum",
                harga_tertinggi,
                "jeepmerapitour.com",
                datetime.now()
            )

            cursor.execute(
                query,
                values
            )

            db.commit()

            cursor.close()
            db.close()

            print(
                f"✅ Jeep Merapi Rp{harga_tertinggi}"
            )

        else:

            print(
                "⚠️ Harga Jeep Merapi tidak ditemukan"
            )

    except Exception as e:

        print(
            "❌ Error Jeep Merapi:",
            e
        )


# ==========================
# TEBING BREKSI
# ==========================
def scrape_tebing_breksi():
    try:
        print("🔄 Scraping Tebing Breksi...")

        url = "https://tebingbreksi.com/formulir-reservasi/"

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, headers=headers, timeout=20)

        soup = BeautifulSoup(response.text, "html.parser")

        text = soup.get_text(" ", strip=True)

        print("===== DEBUG TEBING BREKSI =====")
        print(text[:5000])

        harga = re.findall(r'Rp\s?([\d\.]+)', text)

        print("DEBUG RAW PRICE:", harga)

        harga_bersih = []

        for h in harga:
            try:
                nilai = int(h.replace(".", ""))
                harga_bersih.append(nilai)
            except:
                pass

        print("DEBUG CLEAN PRICE:", harga_bersih)

        if harga_bersih:

            harga_tertinggi = max(harga_bersih)

            db = get_db_connection()
            cursor = db.cursor()

            query = """
            INSERT INTO tiket_wisata
            (
                nama_wisata,
                jenis_tiket,
                harga,
                sumber,
                last_updated
            )
            VALUES (%s,%s,%s,%s,%s)

            ON DUPLICATE KEY UPDATE
            harga=VALUES(harga),
            sumber=VALUES(sumber),
            last_updated=VALUES(last_updated)
            """

            values = (
                "Tebing Breksi",
                "Harga Maksimum",
                harga_tertinggi,
                "Official Website",
                datetime.now()
            )

            cursor.execute(query, values)
            db.commit()

            cursor.close()
            db.close()

            print(f"✅ Tebing Breksi Rp{harga_tertinggi}")

        print("⚠️ Harga Tebing Breksi tidak ditemukan")
        return None

    except Exception as e:
        print("❌ Error Tebing Breksi:", e)
        return None


# ==========================
# PANTAI TIMANG
# ==========================
def scrape_pantai_timang():

    print("🔄 Scraping Pantai Timang...")

    url = "https://pantaitimang.com/paket-wisata-timang/"

    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, headers=headers, timeout=20)

        soup = BeautifulSoup(response.text, "html.parser")

        text = soup.get_text(" ", strip=True)

        print("===== DEBUG PANTAI TIMANG =====")
        print(text[:5000])

        # ambil semua format Rp 100.000 / Rp100000 / Rp 100.000,-
        prices = re.findall(
            r'Rp\.?\s?(\d{1,3}(?:[.\,]\d{3})*)',
            text
        )

        print("DEBUG RAW PRICE:", prices)

        harga_list = []

        for p in prices:
            try:
                harga = int(p.replace(".", "").replace(",", ""))

                # filter harga masuk akal wisata
                if 10000 <= harga <= 10000000:
                    harga_list.append(harga)

            except:
                pass

        print("DEBUG CLEAN PRICE:", harga_list)

        if len(harga_list) > 0:

            harga_tertinggi = max(harga_list)

            db = get_db_connection()
            cursor = db.cursor()

            query = """
            INSERT INTO tiket_wisata
            (
                nama_wisata,
                jenis_tiket,
                harga,
                sumber,
                last_updated
            )
            VALUES (%s,%s,%s,%s,%s)

            ON DUPLICATE KEY UPDATE
            harga=VALUES(harga),
            sumber=VALUES(sumber),
            last_updated=VALUES(last_updated)
            """

            values = (
                "Pantai Timang",
                "Paket Wisata / Harga Maksimum",
                harga_tertinggi,
                "Official Website",
                datetime.now()
            )

            cursor.execute(query, values)
            db.commit()

            cursor.close()
            db.close()

            print(f"✅ Pantai Timang Rp{harga_tertinggi}")

        else:
            print("⚠️ Harga Pantai Timang tidak ditemukan")

    except Exception as e:
        print("❌ Error Pantai Timang:", e)


# ==========================
# PANTAI PARANGTRITIS (TRAVELSPROMO)
# ==========================
def scrape_parangtritis():

    print("🔄 Scraping Pantai Parangtritis (Travelspromo)...")

    url = "https://travelspromo.com/htm-wisata/pantai-parangtritis-bantul/"

    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, headers=headers, timeout=20)

        soup = BeautifulSoup(response.text, "html.parser")

        text = soup.get_text(" ", strip=True)

        print("===== DEBUG PARANGTRITIS =====")
        print(text[:5000])

        # Ambil semua format Rp10.000 / Rp 10.000 / Rp 15.000,-
        prices = re.findall(
            r'Rp\.?\s?(\d{1,3}(?:[.\,]\d{3})*)',
            text
        )

        print("DEBUG RAW PRICE:", prices)

        harga_list = []

        for p in prices:
            try:
                harga = int(p.replace(".", "").replace(",", ""))

                # filter harga wajar tiket wisata
                if 5000 <= harga <= 1000000:
                    harga_list.append(harga)

            except:
                pass

        print("DEBUG CLEAN PRICE:", harga_list)

        if len(harga_list) > 0:

            harga_final = min(harga_list)

            print("DEBUG FINAL PRICE:", harga_final)

            db = get_db_connection()
            cursor = db.cursor()

            query = """
            INSERT INTO tiket_wisata
            (
                nama_wisata,
                jenis_tiket,
                harga,
                sumber,
                last_updated
            )
            VALUES (%s,%s,%s,%s,%s)

            ON DUPLICATE KEY UPDATE
            harga=VALUES(harga),
            sumber=VALUES(sumber),
            last_updated=VALUES(last_updated)
            """

            values = (
                "Pantai Parangtritis",
                "Tiket Masuk",
                harga_final,
                "Travelspromo",
                datetime.now()
            )

            cursor.execute(query, values)
            db.commit()

            cursor.close()
            db.close()

            print(f"✅ Parangtritis Rp{harga_final}")

        else:
            print("⚠️ Harga Parangtritis tidak ditemukan")

    except Exception as e:
        print("❌ Error Parangtritis:", e)


# ==========================
# PANTAI GLAGAH (TRAVELSPROMO)
# ==========================
def scrape_pantai_glagah():

    print("🔄 Scraping Pantai Glagah (Travelspromo)...")

    url = "https://travelspromo.com/htm-wisata/pantai-glagah-kulon-progo/"

    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, headers=headers, timeout=20)

        soup = BeautifulSoup(response.text, "html.parser")

        text = soup.get_text(" ", strip=True)

        print("===== DEBUG PANTAI GLAGAH =====")
        print(text[:5000])

        # ambil semua format Rp6.000 / Rp 10.000 / Rp 295.000
        prices = re.findall(
            r'Rp\.?\s?(\d{1,3}(?:[.\,]\d{3})*)',
            text
        )

        print("DEBUG RAW PRICE:", prices)

        harga_list = []

        for p in prices:
            try:
                harga = int(p.replace(".", "").replace(",", ""))

                # filter harga tiket masuk wajar
                if 3000 <= harga <= 50000:
                    harga_list.append(harga)

            except:
                pass

        print("DEBUG CLEAN PRICE:", harga_list)

        if len(harga_list) > 0:

            # tiket masuk = paling kecil (bukan paket)
            harga_final = min(harga_list)

            print("DEBUG FINAL PRICE:", harga_final)

            db = get_db_connection()
            cursor = db.cursor()

            query = """
            INSERT INTO tiket_wisata
            (
                nama_wisata,
                jenis_tiket,
                harga,
                sumber,
                last_updated
            )
            VALUES (%s,%s,%s,%s,%s)

            ON DUPLICATE KEY UPDATE
            harga=VALUES(harga),
            sumber=VALUES(sumber),
            last_updated=VALUES(last_updated)
            """

            values = (
                "Pantai Glagah",
                "Tiket Masuk",
                harga_final,
                "Travelspromo",
                datetime.now()
            )

            cursor.execute(query, values)
            db.commit()

            cursor.close()
            db.close()

            print(f"✅ Pantai Glagah Rp{harga_final}")

        else:
            print("⚠️ Harga Pantai Glagah tidak ditemukan")

    except Exception as e:
        print("❌ Error Pantai Glagah:", e)

# ==========================
# SCRAPE ALL
# ==========================
def scrape_all():

    scrape_gembiraloka()
    scrape_prambanan()
    scrape_tamansari()
    scrape_sonobudoyo()
    scrape_waduk_sermo()
    scrape_heha()
    scrape_dolandeso()
    scrape_merapi()
    scrape_ske()
    scrape_jeep_merapi()
    scrape_tebing_breksi()
    scrape_pantai_timang()
    scrape_parangtritis()
    scrape_pantai_glagah()


# ==========================
# SCHEDULER
# ==========================
scheduler = BackgroundScheduler()

scheduler.add_job(
    scrape_all,
    'interval',
    hours=24
)

if not scheduler.running:
    scheduler.start()


# ==========================
# ROUTE
# ==========================
@app.route("/")
def home():
    return "SPK Scraper Jalan 🚀"


@app.route("/scrape")
def manual_scrape():

    scrape_all()

    return "Scraping semua wisata dijalankan!"


if __name__ == "__main__":
    app.run(debug=False)