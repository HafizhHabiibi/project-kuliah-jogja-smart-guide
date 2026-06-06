"""
=============================================================
  LOGIKA PERHITUNGAN JARAK SEMI-REALTIME MENGGUNAKAN OSRM API
=============================================================

PENJELASAN API YANG DIGUNAKAN:
--------------------------------
  > OSRM (Open Source Routing Machine)
    - URL Endpoint : https://router.project-osrm.org/route/v1/driving/{lng1},{lat1};{lng2},{lat2}
    - Method       : GET
    - Auth         : Tidak butuh API Key (gratis & open source)
    - Response     : JSON berisi distance (meter) dan duration (detik)
    - PENTING      : Urutan koordinat adalah LONGITUDE dulu, baru LATITUDE

CARA KERJA SEMI-REALTIME:
--------------------------
  1. Lokasi user diperbarui setiap interval tertentu (misalnya setiap 5 detik).
  2. Untuk setiap update lokasi, sistem memanggil OSRM API ke semua destinasi.
  3. Hasilnya ditampilkan ke terminal secara langsung (live update).

MENJALANKAN:
------------
  $ pip install requests
  $ python logika.py

=============================================================
"""

import requests
import time
import math


# ------------------------------------------------------------------
# DAFTAR DESTINASI WISATA (Nama -> Koordinat)
# Format: {"nama": (latitude, longitude)}
# ------------------------------------------------------------------
DESTINASI_WISATA = {
    "Monumen Nasional (Monas)":         (-6.175392,  106.827153),
    "Taman Impian Jaya Ancol":          (-6.121435,  106.830208),
    "Taman Mini Indonesia Indah (TMII)": (-6.302446,  106.895155),
    "Kebun Binatang Ragunan":           (-6.312778,  106.820278),
    "Kota Tua Jakarta":                 (-6.137641,  106.813301),
}


# ------------------------------------------------------------------
# SIMULASI LOKASI USER (Semi-Realtime)
# Di aplikasi nyata, ini digantikan oleh GPS device / Geolocation API.
# Di sini kita simulasikan user yang bergerak perlahan dari titik awal.
# ------------------------------------------------------------------
SIMULASI_LOKASI_AWAL = (-6.194900, 106.823000)  # Bundaran HI, Jakarta


def simulasikan_pergerakan(langkah: int, lat_awal: float, lng_awal: float):
    """
    Mensimulasikan lokasi user yang bergerak sedikit setiap iterasi.
    Bergerak ke arah timur laut secara bertahap.
    
    Args:
        langkah (int): Iterasi ke-berapa (dipakai untuk menggeser koordinat).
        lat_awal (float): Latitude awal user.
        lng_awal (float): Longitude awal user.
    
    Returns:
        tuple: (latitude_terkini, longitude_terkini)
    """
    # Bergerak 0.001 derajat per langkah (~111 meter ke utara, ~111m ke timur)
    lat_terkini = lat_awal + (langkah * 0.001)
    lng_terkini = lng_awal + (langkah * 0.0008)
    return round(lat_terkini, 6), round(lng_terkini, 6)


# ------------------------------------------------------------------
# FUNGSI INTI: MEMANGGIL OSRM API
# ------------------------------------------------------------------
def hitung_jarak_osrm(lat_user: float, lng_user: float,
                       lat_tujuan: float, lng_tujuan: float) -> dict:
    """
    Memanggil OSRM Routing API untuk menghitung jarak dan waktu tempuh
    melalui jalan raya (bukan garis lurus/haversine).

    Args:
        lat_user (float)   : Latitude posisi user saat ini.
        lng_user (float)   : Longitude posisi user saat ini.
        lat_tujuan (float) : Latitude destinasi wisata.
        lng_tujuan (float) : Longitude destinasi wisata.

    Returns:
        dict: {
            "jarak_meter"  : float,   -> Jarak rute jalan (meter)
            "jarak_km"     : float,   -> Jarak rute jalan (km, 2 desimal)
            "durasi_detik" : float,   -> Estimasi waktu (detik)
            "durasi_menit" : int,     -> Estimasi waktu (menit, dibulatkan)
            "status"       : str      -> "ok" atau "error"
        }

    CATATAN FORMAT URL:
        OSRM menggunakan format: {LONGITUDE},{LATITUDE} (bukan lat,lng!)
        Urutan: [titik_asal];[titik_tujuan]
    """
    # ⬇️ Format URL: longitude dulu, baru latitude
    osrm_url = (
        f"https://router.project-osrm.org/route/v1/driving/"
        f"{lng_user},{lat_user};{lng_tujuan},{lat_tujuan}"
        f"?overview=false&steps=false"
    )

    try:
        response = requests.get(osrm_url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("code") == "Ok" and data.get("routes"):
            route      = data["routes"][0]
            jarak_m    = route["distance"]      # dalam meter
            durasi_dtk = route["duration"]      # dalam detik

            return {
                "jarak_meter"  : jarak_m,
                "jarak_km"     : round(jarak_m / 1000, 2),
                "durasi_detik" : durasi_dtk,
                "durasi_menit" : math.ceil(durasi_dtk / 60),
                "status"       : "ok"
            }
        else:
            return {"status": "error", "pesan": f"OSRM code: {data.get('code')}"}

    except requests.exceptions.Timeout:
        return {"status": "error", "pesan": "Request timeout (>10 detik)"}
    except requests.exceptions.RequestException as e:
        return {"status": "error", "pesan": str(e)}


# ------------------------------------------------------------------
# FUNGSI FALLBACK: HAVERSINE (Jarak Garis Lurus)
# Dipakai kalau OSRM tidak bisa dihubungi (offline/error)
# ------------------------------------------------------------------
def hitung_jarak_haversine(lat1: float, lng1: float,
                            lat2: float, lng2: float) -> float:
    """
    Menghitung jarak garis lurus (as the crow flies) antara dua titik
    menggunakan formula Haversine. Hasilnya dalam kilometer.

    Ini adalah FALLBACK jika OSRM API tidak tersedia.
    Haversine tidak mempertimbangkan jalan, macet, atau belokan.

    Args:
        lat1, lng1: Koordinat titik pertama.
        lat2, lng2: Koordinat titik kedua.

    Returns:
        float: Jarak dalam kilometer.
    """
    R = 6371  # Jari-jari bumi dalam km

    phi1    = math.radians(lat1)
    phi2    = math.radians(lat2)
    d_phi   = math.radians(lat2 - lat1)
    d_lambda = math.radians(lng2 - lng1)

    a = math.sin(d_phi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return round(R * c, 2)


# ------------------------------------------------------------------
# FUNGSI TAMPILAN: PRINT HASIL KE TERMINAL
# ------------------------------------------------------------------
def tampilkan_hasil(iterasi: int, lat_user: float, lng_user: float, hasil: dict):
    """
    Menampilkan hasil perhitungan jarak ke terminal dalam format tabel rapi.
    """
    print(f"\n{'='*65}")
    print(f"  ITERASI #{iterasi}  |  Lokasi User: ({lat_user}, {lng_user})")
    print(f"{'='*65}")
    print(f"  {'Destinasi':<35} {'Jarak':>10} {'Waktu':>10}")
    print(f"  {'-'*57}")

    for nama, info in hasil.items():
        if info["status"] == "ok":
            jarak_str  = f"{info['jarak_km']} km"
            durasi_str = f"{info['durasi_menit']} mnt"
        else:
            jarak_str  = "ERROR"
            durasi_str = info.get("pesan", "-")[:10]

        print(f"  {nama:<35} {jarak_str:>10} {durasi_str:>10}")

    print(f"{'='*65}")


# ------------------------------------------------------------------
# FUNGSI UTAMA: LOOP SEMI-REALTIME
# ------------------------------------------------------------------
def jalankan_semi_realtime(jumlah_iterasi: int = 5, interval_detik: int = 6):
    """
    Menjalankan loop semi-realtime untuk memantau jarak user ke semua
    destinasi wisata. Setiap interval, lokasi user diperbarui dan
    OSRM dipanggil ulang.

    Args:
        jumlah_iterasi (int): Berapa kali update dilakukan.
        interval_detik (int): Jeda antar update (dalam detik).
    """
    lat_awal, lng_awal = SIMULASI_LOKASI_AWAL

    print("\n" + "="*65)
    print("  PELACAK JARAK SEMI-REALTIME --- OSRM API")
    print("  Simulasi user bergerak dari Bundaran HI, Jakarta")
    print("="*65)
    print(f"\n  Total update : {jumlah_iterasi}x")
    print(f"  Interval     : setiap {interval_detik} detik")
    print(f"  Metode       : OSRM API (jalan raya) + Haversine (fallback)")
    print(f"\n  Memulai pelacakan...\n")

    for i in range(1, jumlah_iterasi + 1):
        # 1. Perbarui lokasi user (simulasi GPS update)
        lat_user, lng_user = simulasikan_pergerakan(i - 1, lat_awal, lng_awal)

        hasil_semua = {}

        # 2. Hitung jarak ke setiap destinasi wisata via OSRM
        for nama_dest, (lat_dest, lng_dest) in DESTINASI_WISATA.items():
            hasil = hitung_jarak_osrm(lat_user, lng_user, lat_dest, lng_dest)

            # Jika OSRM gagal, gunakan haversine sebagai fallback
            if hasil["status"] == "error":
                jarak_fallback = hitung_jarak_haversine(lat_user, lng_user,
                                                         lat_dest, lng_dest)
                hasil = {
                    "jarak_km"     : jarak_fallback,
                    "durasi_menit" : "-",
                    "status"       : "ok",
                    "catatan"      : "haversine (fallback)"
                }

            hasil_semua[nama_dest] = hasil

        # 3. Tampilkan hasil ke terminal
        tampilkan_hasil(i, lat_user, lng_user, hasil_semua)

        # 4. Tunggu sebelum iterasi berikutnya (kecuali iterasi terakhir)
        if i < jumlah_iterasi:
            print(f"\n  [TUNGGU]  Update berikutnya dalam {interval_detik} detik...", end="\r")
            time.sleep(interval_detik)

    print("\n\n  [SELESAI] Sesi pelacakan selesai.\n")


# ------------------------------------------------------------------
# ENTRY POINT
# ------------------------------------------------------------------
if __name__ == "__main__":
    jalankan_semi_realtime(
        jumlah_iterasi=5,   # Ubah angka ini untuk lebih banyak update
        interval_detik=6    # Ubah angka ini untuk interval antar update
    )
