# Jogja Smart Guide (JSG)

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![Flask Version](https://img.shields.io/badge/flask-3.1.1-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](#)

**Jogja Smart Guide** adalah platform panduan pariwisata cerdas berbasis web yang dirancang khusus untuk membantu wisatawan menjelajahi keindahan Yogyakarta. Aplikasi ini mengintegrasikan data preferensi personal pengguna, informasi cuaca *real-time* via API, estimasi jarak dinamis, dan sistem penilaian terstruktur untuk menyajikan rekomendasi tempat wisata yang dipersonalisasi.

Platform ini dibangun menggunakan arsitektur MVC (Model-View-Controller) yang kokoh, dengan backend berbasis **Flask** dan frontend interaktif menggunakan **Vanilla CSS & JS** dengan desain modern bertema *glassmorphism*.

---

## Fitur Utama

### 1. Dashboard Wisata Cerdas
*   **Pencarian & Penyaringan**: Cari destinasi berdasarkan nama atau deskripsi, serta filter instan berdasarkan 6 kategori utama: **Sejarah, Alam, Pantai, Budaya, Belanja, dan Hiburan**.
*   **Pengurutan Fleksibel**: Urutkan destinasi berdasarkan rating tertinggi, harga tiket termurah/termahal, abjad nama, atau acak (default).
*   **Widget Cuaca Real-Time**: Integrasi langsung dengan **OpenWeatherMap API** untuk menampilkan data curah hujan 1 jam terakhir, suhu (°C), ketebalan awan (%), dan kecepatan angin (m/s) di lokasi destinasi wisata tersebut secara dinamis.
*   **Fallback Cuaca Pintar**: Jika API Key cuaca belum diatur, sistem secara otomatis mengaktifkan mode simulasi cuaca dinamis yang tampak nyata untuk menjaga estetika UI.
*   **Estimasi Jarak Dinamis**: Memanfaatkan **HTML5 Geolocation API** untuk menghitung jarak nyata dari posisi pengguna ke lokasi astronomis destinasi (menggunakan rumus *Haversine*). Dilengkapi dengan titik pusat kota (Jalan Malioboro) sebagai *fallback* jika akses lokasi tidak diizinkan.

### 2. Personalisasi & Profil Wisatawan
*   Wisatawan terdaftar dapat mengelola profil mereka dan menentukan bobot preferensi pribadi (skala 1-5) untuk 5 dimensi penilaian wisata:
    1.  **Nature (Alam)**: Kebutuhan akan keasrian alam dan panorama lanskap.
    2.  **Culture (Budaya)**: Ketertarikan pada sejarah, tradisi, seni, dan bangunan adat.
    3.  **Culinary (Kuliner)**: Kebutuhan terhadap fasilitas kuliner khas dan aktivitas *food hunting*.
    4.  **Crowd (Kepadatan)**: Tingkat toleransi terhadap keramaian dan ketersediaan fasilitas publik di tempat ramai.
    5.  **Effort (Upaya Fisik)**: Preferensi kenyamanan aksesibilitas jalan dan tingkat stamina yang dibutuhkan.

### 3. Backoffice Admin (CRUD Panel)
*   **Manajemen Destinasi**: Panel khusus bagi Administrator untuk menambah, mengubah, dan menghapus destinasi wisata (Full CRUD).
*   **Unggah Foto Aman**: Sistem penanganan berkas unggahan foto destinasi yang terlindungi, lengkap dengan validasi ekstensi gambar (`png`, `jpg`, `jpeg`, `gif`, `webp`) dan penamaan otomatis berbasis *timestamp* untuk mencegah konflik nama berkas.
*   **Penilaian 5-Dimensi Lengkap**: Form admin menyediakan pengisian skor numerik (1-5) dan *multi-select* tag JSON untuk masing-masing dari 5 parameter wisata demi menghasilkan data rekomendasi yang sangat akurat.
*   **Dashboard Statistik**: Menampilkan ringkasan jumlah destinasi, jumlah kategori, dan total pengguna terdaftar.

---

## Struktur Direktori Project

Aplikasi ini menggunakan struktur direktori yang modular dan teratur:

```text
project-kuliah-jogja-smart-guide/
│
├── app.py
├── config.py
├── requirements.txt
│
├── controllers/
│   ├── __init__.py
│   ├── admin_controller.py
│   ├── auth_controller.py
│   ├── dashboard_controller.py
│   └── profile_controller.py
│
├── models/
│   ├── __init__.py
│   ├── user.py
│   └── destination.py
│
├── static/
│   ├── css/
│   │   └── style.css
│   ├── images/
│   │   ├── destinations/
│   │   ├── hero-bg.png
│   │   └── logo.png
│   └── js/
│       ├── main.js
│       ├── landing.js
│       ├── auth.js
│       ├── dashboard.js
│       ├── profile.js
│       └── admin.js
│
├── templates/
│   ├── base.html
│   ├── admin_base.html
│   ├── landing.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── profile.html
│   ├── admin_dashboard.html
│   └── admin_destination_form.html
│
└── instance/
    └── jogja_smart_guide.db
```

---

## Spesifikasi Teknologi

*   **Backend**: Python 3.x, Flask 3.1.1
*   **Database**: SQLite (SQLAlchemy ORM) untuk fleksibilitas dan instalasi cepat tanpa server database eksternal.
*   **Autentikasi**: Flask-Login (manajemen sesi pengguna) & Werkzeug (keamanan kriptografi password).
*   **API Cuaca**: OpenWeatherMap API (Current Weather Data).
*   **Desain UI/UX**:
    *   **Typography**: Inter (modern sans-serif) & Playfair Display (premium serif untuk judul).
    *   **Icons**: Google Material Icons.
    *   **Styling**: Vanilla CSS3 dengan arsitektur variabel warna modern (sistem HSL), efek *blur-glassmorphic*, tata letak fleksibel (CSS Grid & Flexbox), dan animasi transisi halus (`@keyframes`).
    *   **Interaktivitas**: Vanilla JavaScript (ES6+) modern tanpa dependensi berat (jQuery/Bootstrap JS).

---

## Panduan Instalasi & Menjalankan Aplikasi

Ikuti langkah-langkah berikut untuk menjalankan project ini di komputer lokal Anda:

### 1. Prasyarat
Pastikan Anda sudah menginstal **Python 3.8 atau versi di atasnya** dan **Git** di komputer Anda.

### 2. Kloning Repositori
Buka terminal/command prompt, lalu jalankan perintah:
```bash
git clone https://github.com/HafizhHabiibi/project-kuliah-jogja-smart-guide.git
cd project-kuliah-jogja-smart-guide
```

### 3. Buat dan Aktifkan Virtual Environment
Sangat disarankan menggunakan virtual environment agar pustaka project tidak mengganggu sistem global Anda.

*   **Di Windows (PowerShell / CMD):**
    ```powershell
    python -m venv venv
    .\venv\Scripts\activate
    ```
*   **Di macOS / Linux:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

### 4. Instal Dependensi
Instal seluruh pustaka Python yang dibutuhkan dengan menjalankan perintah berikut:
```bash
pip install -r requirements.txt
```

### 5. Konfigurasi Kunci API Cuaca (Opsional)
Aplikasi ini secara bawaan menggunakan data cuaca dinamis *dummy* yang disimulasikan dengan indah. Jika Anda ingin mengaktifkan data cuaca *real-time* asli dari **OpenWeatherMap**, ikuti langkah ini:
1.  Dapatkan API Key gratis di [OpenWeatherMap](https://openweathermap.org/api).
2.  Buka berkas `config.py` dan ubah nilai `YOUR_API_KEY_HERE` menjadi kunci API Anda:
    ```python
    OPENWEATHERMAP_API_KEY = os.environ.get('OPENWEATHERMAP_API_KEY') or 'KUNCI_API_ANDA_DI_SINI'
    ```
    *Atau Anda juga dapat mengaturnya melalui environment variable dengan nama `OPENWEATHERMAP_API_KEY`.*

### 6. Menjalankan Server Lokal
Jalankan aplikasi Flask dengan mengeksekusi berkas `app.py`:
```bash
python app.py
```
Setelah berhasil dijalankan, buka peramban (browser) Anda lalu akses tautan berikut:
**[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## Akun Bawaan (Default Credentials)

Saat aplikasi pertama kali dijalankan, sistem secara otomatis melakukan inisialisasi basis data SQLite (`instance/jogja_smart_guide.db`), melakukan *seeding* **12 destinasi wisata ikonik Yogyakarta** (seperti Candi Prambanan, Malioboro, Keraton, Pantai Parangtritis, Goa Jomblang, dll.), serta membuat **satu akun Administrator utama**:

*   **Email**: `admin@jogjasmartguide.com`
*   **Password**: `admin123`
*   **Peran**: Administrator (memiliki akses penuh ke panel pengelolaan destinasi di `/admin`)

*Catatan: Anda dapat mendaftarkan akun baru melalui halaman **Register** untuk bertindak sebagai wisatawan biasa (non-admin) untuk menguji fitur preferensi.*

---

## Detail Parameter Wisata (5-Dimensi)

Rekomendasi cerdas aplikasi ini bekerja berdasarkan pencocokan data preferensi user dengan data penilaian destinasi yang disimpan dalam 5 dimensi utama:

| Parameter | Sub-Kriteria di Database | Deskripsi Fungsi |
| :--- | :--- | :--- |
| **Nature (Alam)** | `nature_visual` (1-5)<br>`nature_activities` (JSON)<br>`nature_elements` (JSON) | Mengukur seberapa alami objek wisata tersebut (visual pemandangan, vegetasi dominan, aktivitas alam seperti hiking/camping). |
| **Crowd (Keramaian)** | `crowd_review_count` (1-5)<br>`crowd_rating` (1-5)<br>`crowd_hashtag` (1-5)<br>`crowd_activities` & `facilities` (JSON) | Mengukur tingkat kepopuleran dan kepadatan tempat wisata (jumlah kunjungan, ketersediaan area pedestrian, spot foto populer). |
| **Culinary (Kuliner)** | `culinary_facilities` (JSON)<br>`culinary_activities` (JSON)<br>`culinary_types` (JSON) | Menilai variasi hidangan kuliner di sekitar destinasi (street food khas, restoran tradisional, pusat oleh-oleh). |
| **Culture (Budaya)** | `culture_heritage` (JSON)<br>`culture_activities` (JSON)<br>`culture_elements` (JSON) | Menilai kedalaman nilai adat dan sejarah di lokasi (museum, candi, tari tradisional, upacara adat). |
| **Effort (Upaya)** | `effort_accessibility` (JSON)<br>`effort_effort` (JSON)<br>`effort_mobility` (JSON) | Menilai kemudahan akses perjalanan (kondisi jalan, ketersediaan parkir bus, stamina fisik yang dibutuhkan). |

---

## Keunggulan Desain UI/UX
*   **Sistem HSL Tailored Color**: Menggunakan palet warna HSL terkurasi yang harmonis, memberikan transisi kontras yang lembut dan tidak melelahkan mata.
*   **Responsive Grid Layout**: Layout halaman beradaptasi sempurna di berbagai resolusi layar, baik ponsel cerdas, tablet, maupun komputer desktop.
*   **Micro-Animations**: Efek hover yang dinamis, kartu destinasi dengan transisi `translateY`, serta indikator pemuatan cuaca skeleton yang elegan meningkatkan kepuasan interaksi pengguna (*micro-interactions*).
*   **Glassmorphic Elements**: Mengaburkan elemen latar belakang (`backdrop-filter`) untuk memberikan efek kedalaman premium yang estetis pada modal detail dan navigasi.

---

## Lisensi
Proyek ini dilisensikan di bawah **MIT License**. Anda bebas menggunakan, memodifikasi, dan menyebarkan kode ini untuk keperluan edukasi dan pengembangan pariwisata.

---
*Dibuat untuk kemajuan Pariwisata Yogyakarta.*
