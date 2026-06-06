import json
from models import db


class Destination(db.Model):
    __tablename__ = 'destinations'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    photo_url = db.Column(db.String(500), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    price = db.Column(db.Integer, nullable=False)  # dalam Rupiah
    category = db.Column(db.String(50), nullable=False)

    # === PARAMETER 1: NATURE ===
    nature_visual = db.Column(db.Integer, default=3)         # skor 1-5
    nature_activities = db.Column(db.Text, default='[]')     # JSON array
    nature_elements = db.Column(db.Text, default='[]')       # JSON array

    # === PARAMETER 2: CROWD ===
    crowd_review_count = db.Column(db.Integer, default=1)    # skor 1-5
    crowd_rating = db.Column(db.Integer, default=3)          # skor 1-5
    crowd_hashtag = db.Column(db.Integer, default=1)         # skor 1-5
    crowd_activities = db.Column(db.Text, default='[]')      # JSON array
    crowd_facilities = db.Column(db.Text, default='[]')      # JSON array

    # === PARAMETER 3: CULINARY ===
    culinary_facilities = db.Column(db.Text, default='[]')   # JSON array
    culinary_activities = db.Column(db.Text, default='[]')   # JSON array
    culinary_types = db.Column(db.Text, default='[]')        # JSON array

    # === PARAMETER 4: CULTURE ===
    culture_heritage = db.Column(db.Text, default='[]')      # JSON array
    culture_activities = db.Column(db.Text, default='[]')    # JSON array
    culture_elements = db.Column(db.Text, default='[]')      # JSON array

    # === PARAMETER 5: EFFORT ===
    effort_accessibility = db.Column(db.Text, default='[]')  # JSON array
    effort_effort = db.Column(db.Text, default='[]')         # JSON array
    effort_mobility = db.Column(db.Text, default='[]')       # JSON array

    # === SCRAPER HARGA ===
    price_last_scraped = db.Column(db.DateTime, nullable=True)
    price_scrape_status = db.Column(db.String(50), default='PENDING')

    # === SKOR DNA WISATA (MCDM) ===
    score_nature = db.Column(db.Float, default=3.0, nullable=False)
    score_culture = db.Column(db.Float, default=3.0, nullable=False)
    score_culinary = db.Column(db.Float, default=3.0, nullable=False)
    score_crowd = db.Column(db.Float, default=3.0, nullable=False)
    score_effort = db.Column(db.Float, default=3.0, nullable=False)

    # === RELASI CUACA (1-to-1) ===
    weather = db.relationship('DestinationWeather', backref='destination', uselist=False, cascade="all, delete-orphan")

    def _parse_json(self, field):
        """Safely parse a JSON text field to a list."""
        try:
            return json.loads(field) if field else []
        except (json.JSONDecodeError, TypeError):
            return []

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'photo_url': self.photo_url,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'rating': self.rating,
            'price': self.price,
            'category': self.category,
            # Nature
            'nature_visual': self.nature_visual,
            'nature_activities': self._parse_json(self.nature_activities),
            'nature_elements': self._parse_json(self.nature_elements),
            # Crowd
            'crowd_review_count': self.crowd_review_count,
            'crowd_rating': self.crowd_rating,
            'crowd_hashtag': self.crowd_hashtag,
            'crowd_activities': self._parse_json(self.crowd_activities),
            'crowd_facilities': self._parse_json(self.crowd_facilities),
            # Culinary
            'culinary_facilities': self._parse_json(self.culinary_facilities),
            'culinary_activities': self._parse_json(self.culinary_activities),
            'culinary_types': self._parse_json(self.culinary_types),
            # Culture
            'culture_heritage': self._parse_json(self.culture_heritage),
            'culture_activities': self._parse_json(self.culture_activities),
            'culture_elements': self._parse_json(self.culture_elements),
            # Effort
            'effort_accessibility': self._parse_json(self.effort_accessibility),
            'effort_effort': self._parse_json(self.effort_effort),
            'effort_mobility': self._parse_json(self.effort_mobility),
            # Scraper & DNA Scores
            'price_last_scraped': self.price_last_scraped.isoformat() if self.price_last_scraped else None,
            'price_scrape_status': self.price_scrape_status,
            'score_nature': self.score_nature,
            'score_culture': self.score_culture,
            'score_culinary': self.score_culinary,
            'score_crowd': self.score_crowd,
            'score_effort': self.score_effort,
            # Cached Weather Data (Input FIS 1) and output weather_index
            'weather': {
                'temp': self.weather.temp if self.weather else 27.0,
                'rain_1h': self.weather.rain_1h if self.weather else 0.0,
                'clouds_all': self.weather.clouds_all if self.weather else 50,
                'wind_speed': self.weather.wind_speed if self.weather else 2.0,
                'weather_index': self.weather.weather_index if self.weather else 0.5,
                'last_updated': self.weather.last_updated.isoformat() if self.weather and self.weather.last_updated else None
            }
        }

    def __repr__(self):
        return f'<Destination {self.name}>'

    def update_dna_scores(self):
        """Menghitung skor DNA 5-Dimensi (1.0 - 5.0) berdasarkan jawaban kuesioner admin."""
        def calculate_checkbox_score(json_data, max_items=4):
            try:
                items = json.loads(json_data) if json_data else []
            except:
                items = []
            count = len(items)
            return max(1.0, min(5.0, 1.0 + (count * 4.0 / max_items)))

        # 1. NATURE
        visual_score = float(self.nature_visual or 3)
        act_nature = calculate_checkbox_score(self.nature_activities, max_items=6)
        elem_nature = calculate_checkbox_score(self.nature_elements, max_items=5)
        self.score_nature = round((visual_score * 0.5) + (act_nature * 0.25) + (elem_nature * 0.25), 2)

        # 2. CULTURE
        her_culture = calculate_checkbox_score(self.culture_heritage, max_items=4)
        act_culture = calculate_checkbox_score(self.culture_activities, max_items=4)
        elem_culture = calculate_checkbox_score(self.culture_elements, max_items=4)
        self.score_culture = round((her_culture * 0.4) + (act_culture * 0.3) + (elem_culture * 0.3), 2)

        # 3. CULINARY
        fac_culinary = calculate_checkbox_score(self.culinary_facilities, max_items=4)
        act_culinary = calculate_checkbox_score(self.culinary_activities, max_items=4)
        type_culinary = calculate_checkbox_score(self.culinary_types, max_items=4)
        self.score_culinary = round((fac_culinary * 0.4) + (act_culinary * 0.3) + (type_culinary * 0.3), 2)

        # 4. CROWD
        review_score = float(self.crowd_review_count or 1)
        rating_score = float(self.crowd_rating or 3)
        hashtag_score = float(self.crowd_hashtag or 1)
        act_crowd = calculate_checkbox_score(self.crowd_activities, max_items=5)
        fac_crowd = calculate_checkbox_score(self.crowd_facilities, max_items=5)
        self.score_crowd = round(
            (review_score * 0.3) + (rating_score * 0.2) + (hashtag_score * 0.2) + 
            (act_crowd * 0.15) + (fac_crowd * 0.15), 2
        )

        # 5. EFFORT
        acc_effort = calculate_checkbox_score(self.effort_accessibility, max_items=6)
        mob_effort = calculate_checkbox_score(self.effort_mobility, max_items=6)
        diff_effort = calculate_checkbox_score(self.effort_effort, max_items=5)
        self.score_effort = round(max(1.0, min(5.0, 3.0 + diff_effort - (acc_effort * 0.5 + mob_effort * 0.5))), 2)

        # 6. AUTO CATEGORIZATION
        # Tentukan Kategori Otomatis berdasarkan skor tertinggi dari 5 dimensi DNA
        scores = {
            'Alam': self.score_nature,
            'Budaya': self.score_culture,
            'Kuliner': self.score_culinary,
            'Keramaian': self.score_crowd,
            'Petualangan': self.score_effort
        }
        self.category = max(scores, key=scores.get)


def seed_destinations():
    """Seed database with Yogyakarta tourist destinations."""
    destinations = [
        Destination(
            name='Candi Prambanan',
            description='Kompleks candi Hindu terbesar di Indonesia yang dibangun pada abad ke-9. Candi ini merupakan Situs Warisan Dunia UNESCO dengan arsitektur yang megah dan relief cerita Ramayana yang menakjubkan.',
            photo_url='/static/images/destinations/prambanan.jpg',
            latitude=-7.7520,
            longitude=110.4914,
            rating=4.8,
            price=50000,
            category='Sejarah',
            nature_visual=2,
            nature_activities=json.dumps([]),
            nature_elements=json.dumps(['Vegetasi dominan', 'Sunset/Sunrise']),
            crowd_review_count=5,
            crowd_rating=5,
            crowd_hashtag=5,
            crowd_activities=json.dumps(['Festival/event rutin', 'Live performance', 'Night tourism', 'Wisata keluarga']),
            crowd_facilities=json.dumps(['Area pedestrian', 'Plaza', 'Tempat duduk umum', 'Area foto populer']),
            culinary_facilities=json.dumps(['Restoran', 'Warung makan', 'Pusat oleh-oleh']),
            culinary_activities=json.dumps(['Wisata oleh-oleh']),
            culinary_types=json.dumps(['Makanan tradisional', 'Oleh-oleh khas']),
            culture_heritage=json.dumps(['Situs sejarah', 'Candi', 'Monumen budaya', 'Kawasan heritage', 'Artefak budaya', 'Landmark historis']),
            culture_activities=json.dumps(['Tari tradisional', 'Festival budaya', 'Wisata edukasi sejarah', 'Pertunjukan budaya']),
            culture_elements=json.dumps(['Sejarah', 'Arsitektur tradisional', 'Seni pertunjukan', 'Simbol budaya khas']),
            effort_accessibility=json.dumps(['Jalan beraspal baik', 'Dapat dilalui kendaraan roda 4', 'Dapat diakses bus', 'Memiliki petunjuk arah jelas']),
            effort_effort=json.dumps([]),
            effort_mobility=json.dumps(['Area parkir', 'Transportasi umum', 'Transportasi online', 'Toilet umum', 'Pos informasi', 'Petunjuk arah'])
        ),
        Destination(
            name='Malioboro',
            description='Jantung kota Yogyakarta yang terkenal sebagai surga belanja. Jalan legendaris ini dipenuhi toko-toko batik, kerajinan tangan, dan kuliner khas Jogja yang wajib dicoba setiap pengunjung.',
            photo_url='/static/images/destinations/malioboro.jpg',
            latitude=-7.7925,
            longitude=110.3660,
            rating=4.5,
            price=0,
            category='Belanja',
            nature_visual=1,
            nature_activities=json.dumps(['Joging']),
            nature_elements=json.dumps([]),
            crowd_review_count=5,
            crowd_rating=4,
            crowd_hashtag=5,
            crowd_activities=json.dumps(['Festival/event rutin', 'Live performance', 'Night tourism', 'Pasar wisata', 'Wisata keluarga', 'Street performance', 'Area nongkrong ramai']),
            crowd_facilities=json.dumps(['Area pedestrian', 'Plaza', 'Tempat duduk umum', 'Area nongkrong', 'Area pertunjukan', 'Area kuliner besar', 'Area foto populer', 'Street performance zone']),
            culinary_facilities=json.dumps(['Restoran', 'Warung makan', 'Street food', 'Cafe', 'Pusat oleh-oleh', 'Kuliner khas daerah', 'Pasar kuliner', 'Night culinary area']),
            culinary_activities=json.dumps(['Food hunting', 'Wisata makanan khas', 'Kuliner malam', 'Street food exploration', 'Wisata oleh-oleh', 'Traditional food tasting']),
            culinary_types=json.dumps(['Makanan tradisional', 'Minuman khas', 'Street food khas', 'Oleh-oleh khas', 'Kuliner legendaris', 'Kuliner halal khas']),
            culture_heritage=json.dumps(['Kawasan heritage', 'Landmark historis']),
            culture_activities=json.dumps(['Festival budaya', 'Atraksi tradisional', 'Pertunjukan budaya']),
            culture_elements=json.dumps(['Sejarah', 'Kerajinan lokal', 'Tradisi adat']),
            effort_accessibility=json.dumps(['Jalan beraspal baik', 'Dapat dilalui kendaraan roda 4', 'Dapat diakses bus', 'Tidak memerlukan kendaraan khusus', 'Memiliki petunjuk arah jelas', 'Dekat jalan utama', 'Akses tersedia sepanjang tahun']),
            effort_effort=json.dumps([]),
            effort_mobility=json.dumps(['Area parkir', 'Transportasi umum', 'Transportasi online', 'Jalur pedestrian', 'Toilet umum', 'Pos informasi', 'Petunjuk arah', 'Tempat istirahat'])
        ),
        Destination(
            name='Pantai Parangtritis',
            description='Pantai ikonik di selatan Yogyakarta dengan pemandangan matahari terbenam yang spektakuler. Terkenal dengan legenda Nyi Roro Kidul dan aktivitas seru seperti naik andong di tepi pantai.',
            photo_url='/static/images/destinations/parangtritis.jpg',
            latitude=-8.0253,
            longitude=110.3286,
            rating=4.3,
            price=10000,
            category='Pantai',
            nature_visual=5,
            nature_activities=json.dumps(['Surfing', 'ATV', 'Joging', 'Swimming outdoor']),
            nature_elements=json.dumps(['Pantai', 'Laut', 'Tebing alami', 'Sunset/Sunrise']),
            crowd_review_count=4,
            crowd_rating=4,
            crowd_hashtag=4,
            crowd_activities=json.dumps(['Wisata keluarga', 'Aktivitas wisata alam', 'Area nongkrong ramai']),
            crowd_facilities=json.dumps(['Area pedestrian', 'Tempat duduk umum', 'Area kuliner besar', 'Area foto populer']),
            culinary_facilities=json.dumps(['Warung makan', 'Street food', 'Area makan outdoor']),
            culinary_activities=json.dumps(['Food hunting', 'Street food exploration']),
            culinary_types=json.dumps(['Seafood lokal', 'Street food khas', 'Minuman khas']),
            culture_heritage=json.dumps([]),
            culture_activities=json.dumps([]),
            culture_elements=json.dumps(['Tradisi adat', 'Nilai filosofi lokal']),
            effort_accessibility=json.dumps(['Jalan beraspal baik', 'Dapat dilalui kendaraan roda 4', 'Memiliki petunjuk arah jelas', 'Dekat jalan utama']),
            effort_effort=json.dumps(['Perjalanan > 1 jam']),
            effort_mobility=json.dumps(['Area parkir', 'Transportasi online', 'Toilet umum', 'Petunjuk arah'])
        ),
        Destination(
            name='Keraton Yogyakarta',
            description='Istana resmi Kesultanan Ngayogyakarta Hadiningrat yang masih berfungsi hingga kini. Menyimpan koleksi pusaka, gamelan, dan menampilkan pertunjukan tari klasik Jawa secara rutin.',
            photo_url='/static/images/destinations/keraton.jpg',
            latitude=-7.8052,
            longitude=110.3642,
            rating=4.6,
            price=15000,
            category='Budaya',
            nature_visual=2,
            nature_activities=json.dumps([]),
            nature_elements=json.dumps(['Vegetasi dominan']),
            crowd_review_count=4,
            crowd_rating=5,
            crowd_hashtag=4,
            crowd_activities=json.dumps(['Festival/event rutin', 'Live performance', 'Wisata keluarga', 'Aktivitas komunitas']),
            crowd_facilities=json.dumps(['Area pedestrian', 'Plaza', 'Tempat duduk umum', 'Area pertunjukan', 'Area foto populer']),
            culinary_facilities=json.dumps(['Warung makan', 'Pusat oleh-oleh']),
            culinary_activities=json.dumps(['Wisata oleh-oleh', 'Traditional food tasting']),
            culinary_types=json.dumps(['Makanan tradisional', 'Kuliner legendaris']),
            culture_heritage=json.dumps(['Situs sejarah', 'Bangunan tradisional', 'Museum', 'Keraton', 'Kawasan heritage', 'Arsitektur tradisional', 'Artefak budaya', 'Landmark historis']),
            culture_activities=json.dumps(['Tari tradisional', 'Musik tradisional', 'Festival budaya', 'Ritual adat', 'Pameran budaya', 'Wisata edukasi sejarah', 'Pertunjukan budaya', 'Upacara adat']),
            culture_elements=json.dumps(['Sejarah', 'Arsitektur tradisional', 'Seni pertunjukan', 'Kuliner tradisional', 'Kerajinan lokal', 'Tradisi adat', 'Pakaian adat', 'Nilai filosofi lokal', 'Simbol budaya khas']),
            effort_accessibility=json.dumps(['Jalan beraspal baik', 'Dapat dilalui kendaraan roda 4', 'Dapat diakses bus', 'Tidak memerlukan kendaraan khusus', 'Memiliki petunjuk arah jelas', 'Dekat jalan utama', 'Akses tersedia sepanjang tahun']),
            effort_effort=json.dumps([]),
            effort_mobility=json.dumps(['Area parkir', 'Transportasi umum', 'Transportasi online', 'Jalur pedestrian', 'Toilet umum', 'Pos informasi', 'Petunjuk arah', 'Tempat istirahat'])
        ),
        Destination(
            name='Taman Sari',
            description='Bekas taman kerajaan dan pemandian Kesultanan Yogyakarta yang dibangun pada abad ke-18. Arsitektur unik perpaduan Jawa dan Eropa dengan lorong-lorong bawah tanah yang misterius.',
            photo_url='/static/images/destinations/tamansari.jpg',
            latitude=-7.8100,
            longitude=110.3593,
            rating=4.4,
            price=15000,
            category='Sejarah',
            nature_visual=3,
            nature_activities=json.dumps([]),
            nature_elements=json.dumps(['Vegetasi dominan']),
            crowd_review_count=4,
            crowd_rating=4,
            crowd_hashtag=4,
            crowd_activities=json.dumps(['Wisata keluarga', 'Aktivitas komunitas']),
            crowd_facilities=json.dumps(['Area pedestrian', 'Area foto populer']),
            culinary_facilities=json.dumps(['Warung makan', 'Street food', 'Cafe']),
            culinary_activities=json.dumps(['Food hunting', 'Street food exploration']),
            culinary_types=json.dumps(['Makanan tradisional', 'Street food khas']),
            culture_heritage=json.dumps(['Situs sejarah', 'Bangunan tradisional', 'Kawasan heritage', 'Arsitektur tradisional', 'Artefak budaya', 'Landmark historis']),
            culture_activities=json.dumps(['Wisata edukasi sejarah']),
            culture_elements=json.dumps(['Sejarah', 'Arsitektur tradisional', 'Nilai filosofi lokal']),
            effort_accessibility=json.dumps(['Jalan beraspal baik', 'Dapat dilalui kendaraan roda 4', 'Tidak memerlukan kendaraan khusus', 'Dekat jalan utama', 'Akses tersedia sepanjang tahun']),
            effort_effort=json.dumps(['Harus berjalan kaki jauh']),
            effort_mobility=json.dumps(['Area parkir', 'Transportasi online', 'Jalur pedestrian', 'Toilet umum', 'Petunjuk arah'])
        ),
        Destination(
            name='Candi Borobudur',
            description='Candi Buddha terbesar di dunia dan keajaiban arsitektur abad ke-9. Memiliki lebih dari 2.600 panel relief dan 504 arca Buddha. Sunrise di Borobudur adalah pengalaman yang tak terlupakan.',
            photo_url='/static/images/destinations/borobudur.jpg',
            latitude=-7.6079,
            longitude=110.2038,
            rating=4.9,
            price=50000,
            category='Sejarah',
            nature_visual=3,
            nature_activities=json.dumps([]),
            nature_elements=json.dumps(['Gunung', 'Vegetasi dominan', 'Sunset/Sunrise']),
            crowd_review_count=5,
            crowd_rating=5,
            crowd_hashtag=5,
            crowd_activities=json.dumps(['Festival/event rutin', 'Live performance', 'Night tourism', 'Wisata keluarga']),
            crowd_facilities=json.dumps(['Area pedestrian', 'Plaza', 'Tempat duduk umum', 'Area kuliner besar', 'Area foto populer']),
            culinary_facilities=json.dumps(['Restoran', 'Warung makan', 'Pusat oleh-oleh']),
            culinary_activities=json.dumps(['Wisata oleh-oleh']),
            culinary_types=json.dumps(['Makanan tradisional', 'Oleh-oleh khas']),
            culture_heritage=json.dumps(['Situs sejarah', 'Candi', 'Monumen budaya', 'Kawasan heritage', 'Artefak budaya', 'Landmark historis']),
            culture_activities=json.dumps(['Festival budaya', 'Wisata edukasi sejarah', 'Pertunjukan budaya']),
            culture_elements=json.dumps(['Sejarah', 'Arsitektur tradisional', 'Nilai filosofi lokal', 'Simbol budaya khas']),
            effort_accessibility=json.dumps(['Jalan beraspal baik', 'Dapat dilalui kendaraan roda 4', 'Dapat diakses bus', 'Memiliki petunjuk arah jelas']),
            effort_effort=json.dumps(['Perjalanan > 1 jam', 'Memerlukan stamina fisik']),
            effort_mobility=json.dumps(['Area parkir', 'Transportasi umum', 'Transportasi online', 'Toilet umum', 'Pos informasi', 'Petunjuk arah', 'Tempat istirahat'])
        ),
        Destination(
            name='Pantai Indrayanti',
            description='Pantai berpasir putih dengan air laut biru jernih di Gunungkidul. Dilengkapi kafe-kafe tepi pantai yang instagramable dan cocok untuk bersantai menikmati panorama laut selatan.',
            photo_url='/static/images/destinations/indrayanti.jpg',
            latitude=-8.1514,
            longitude=110.6119,
            rating=4.5,
            price=10000,
            category='Pantai',
            nature_visual=5,
            nature_activities=json.dumps(['Snorkeling', 'Swimming outdoor', 'Joging']),
            nature_elements=json.dumps(['Pantai', 'Laut', 'Tebing alami', 'Sunset/Sunrise']),
            crowd_review_count=4,
            crowd_rating=4,
            crowd_hashtag=4,
            crowd_activities=json.dumps(['Wisata keluarga', 'Aktivitas wisata alam', 'Area nongkrong ramai']),
            crowd_facilities=json.dumps(['Tempat duduk umum', 'Area nongkrong', 'Area kuliner besar', 'Area foto populer']),
            culinary_facilities=json.dumps(['Restoran', 'Warung makan', 'Cafe', 'Area makan outdoor']),
            culinary_activities=json.dumps(['Food hunting', 'Cafe hopping']),
            culinary_types=json.dumps(['Seafood lokal', 'Minuman khas']),
            culture_heritage=json.dumps([]),
            culture_activities=json.dumps([]),
            culture_elements=json.dumps([]),
            effort_accessibility=json.dumps(['Jalan beraspal baik', 'Dapat dilalui kendaraan roda 4', 'Memiliki petunjuk arah jelas']),
            effort_effort=json.dumps(['Perjalanan > 1 jam', 'Jalan sempit']),
            effort_mobility=json.dumps(['Area parkir', 'Transportasi online', 'Toilet umum', 'Petunjuk arah'])
        ),
        Destination(
            name='Hutan Pinus Mangunan',
            description='Hutan pinus yang asri di perbukitan Mangunan dengan udara sejuk dan pemandangan menakjubkan. Spot foto favorit dengan gardu pandang yang menghadap lembah hijau nan memukau.',
            photo_url='/static/images/destinations/mangunan.jpg',
            latitude=-7.9337,
            longitude=110.4047,
            rating=4.3,
            price=5000,
            category='Alam',
            nature_visual=5,
            nature_activities=json.dumps(['Hiking', 'Camping', 'Bersepeda', 'Joging']),
            nature_elements=json.dumps(['Gunung', 'Hutan', 'Vegetasi dominan', 'Sunset/Sunrise']),
            crowd_review_count=3,
            crowd_rating=4,
            crowd_hashtag=3,
            crowd_activities=json.dumps(['Wisata keluarga', 'Aktivitas wisata alam']),
            crowd_facilities=json.dumps(['Tempat duduk umum', 'Area foto populer']),
            culinary_facilities=json.dumps(['Warung makan', 'Area makan outdoor']),
            culinary_activities=json.dumps(['Food hunting']),
            culinary_types=json.dumps(['Minuman khas']),
            culture_heritage=json.dumps([]),
            culture_activities=json.dumps([]),
            culture_elements=json.dumps([]),
            effort_accessibility=json.dumps(['Jalan beraspal baik', 'Dapat dilalui kendaraan roda 4', 'Memiliki petunjuk arah jelas']),
            effort_effort=json.dumps(['Perjalanan > 1 jam', 'Medan tidak rata', 'Memerlukan stamina fisik']),
            effort_mobility=json.dumps(['Area parkir', 'Transportasi online', 'Toilet umum', 'Petunjuk arah', 'Tempat istirahat'])
        ),
        Destination(
            name='Goa Jomblang',
            description='Gua vertikal spektakuler dengan fenomena cahaya surga (heaven light) yang menembus ke dasar gua. Petualangan menuruni kedalaman 60 meter untuk menyaksikan keajaiban alam yang langka.',
            photo_url='/static/images/destinations/jomblang.jpg',
            latitude=-8.0456,
            longitude=110.6394,
            rating=4.7,
            price=500000,
            category='Alam',
            nature_visual=5,
            nature_activities=json.dumps(['Hiking', 'Panjat tebing']),
            nature_elements=json.dumps(['Hutan', 'Tebing alami', 'Vegetasi dominan']),
            crowd_review_count=3,
            crowd_rating=5,
            crowd_hashtag=4,
            crowd_activities=json.dumps(['Aktivitas wisata alam']),
            crowd_facilities=json.dumps(['Area foto populer']),
            culinary_facilities=json.dumps([]),
            culinary_activities=json.dumps([]),
            culinary_types=json.dumps([]),
            culture_heritage=json.dumps([]),
            culture_activities=json.dumps([]),
            culture_elements=json.dumps([]),
            effort_accessibility=json.dumps(['Jalan beraspal baik', 'Dapat dilalui kendaraan roda 4']),
            effort_effort=json.dumps(['Perjalanan > 1 jam', 'Memerlukan trekking', 'Memerlukan pendakian', 'Medan tidak rata', 'Memerlukan stamina fisik', 'Memerlukan guide/operator']),
            effort_mobility=json.dumps(['Area parkir', 'Toilet umum', 'Pos informasi'])
        ),
        Destination(
            name='Museum Ullen Sentalu',
            description='Museum budaya Jawa terbaik di lereng Gunung Merapi. Menyimpan koleksi batik, foto, dan artefak kerajaan Jawa dengan penyajian yang interaktif dan memikat setiap pengunjung.',
            photo_url='/static/images/destinations/ullensentalu.jpg',
            latitude=-7.5977,
            longitude=110.4230,
            rating=4.6,
            price=40000,
            category='Budaya',
            nature_visual=4,
            nature_activities=json.dumps([]),
            nature_elements=json.dumps(['Gunung', 'Vegetasi dominan']),
            crowd_review_count=3,
            crowd_rating=5,
            crowd_hashtag=3,
            crowd_activities=json.dumps(['Wisata keluarga']),
            crowd_facilities=json.dumps(['Area pedestrian', 'Tempat duduk umum']),
            culinary_facilities=json.dumps(['Cafe']),
            culinary_activities=json.dumps(['Traditional food tasting']),
            culinary_types=json.dumps(['Makanan tradisional', 'Minuman khas']),
            culture_heritage=json.dumps(['Situs sejarah', 'Museum', 'Arsitektur tradisional', 'Artefak budaya']),
            culture_activities=json.dumps(['Pameran budaya', 'Wisata edukasi sejarah']),
            culture_elements=json.dumps(['Sejarah', 'Arsitektur tradisional', 'Kerajinan lokal', 'Tradisi adat', 'Pakaian adat', 'Nilai filosofi lokal']),
            effort_accessibility=json.dumps(['Jalan beraspal baik', 'Dapat dilalui kendaraan roda 4', 'Memiliki petunjuk arah jelas']),
            effort_effort=json.dumps(['Perjalanan > 1 jam']),
            effort_mobility=json.dumps(['Area parkir', 'Transportasi online', 'Toilet umum', 'Pos informasi', 'Petunjuk arah'])
        ),
        Destination(
            name='Tebing Breksi',
            description='Bekas tambang batu kapur yang disulap menjadi destinasi wisata memukau dengan pahatan relief raksasa di dinding tebing. Menawarkan panorama kota Yogyakarta dari ketinggian.',
            photo_url='/static/images/destinations/breksi.jpg',
            latitude=-7.7703,
            longitude=110.5039,
            rating=4.2,
            price=10000,
            category='Alam',
            nature_visual=4,
            nature_activities=json.dumps(['Hiking', 'Joging']),
            nature_elements=json.dumps(['Tebing alami', 'Vegetasi dominan', 'Sunset/Sunrise']),
            crowd_review_count=3,
            crowd_rating=3,
            crowd_hashtag=3,
            crowd_activities=json.dumps(['Wisata keluarga', 'Aktivitas wisata alam', 'Area nongkrong ramai']),
            crowd_facilities=json.dumps(['Tempat duduk umum', 'Area nongkrong', 'Area foto populer']),
            culinary_facilities=json.dumps(['Warung makan', 'Street food', 'Area makan outdoor']),
            culinary_activities=json.dumps(['Food hunting', 'Street food exploration']),
            culinary_types=json.dumps(['Street food khas', 'Minuman khas']),
            culture_heritage=json.dumps(['Landmark historis']),
            culture_activities=json.dumps([]),
            culture_elements=json.dumps([]),
            effort_accessibility=json.dumps(['Jalan beraspal baik', 'Dapat dilalui kendaraan roda 4', 'Memiliki petunjuk arah jelas']),
            effort_effort=json.dumps(['Medan tidak rata', 'Memerlukan stamina fisik']),
            effort_mobility=json.dumps(['Area parkir', 'Transportasi online', 'Toilet umum', 'Petunjuk arah'])
        ),
        Destination(
            name='HeHa Sky View',
            description='Destinasi wisata modern di dataran tinggi dengan restoran, spot foto instagramable, dan pemandangan kota Yogyakarta yang menakjubkan terutama saat malam hari dengan gemerlap lampu kota.',
            photo_url='/static/images/destinations/hehaskyview.jpg',
            latitude=-7.7956,
            longitude=110.4483,
            rating=4.1,
            price=20000,
            category='Hiburan',
            nature_visual=3,
            nature_activities=json.dumps([]),
            nature_elements=json.dumps(['Vegetasi dominan', 'Sunset/Sunrise']),
            crowd_review_count=4,
            crowd_rating=3,
            crowd_hashtag=4,
            crowd_activities=json.dumps(['Night tourism', 'Gathering', 'Wisata keluarga', 'Area nongkrong ramai']),
            crowd_facilities=json.dumps(['Plaza', 'Tempat duduk umum', 'Area nongkrong', 'Area kuliner besar', 'Area foto populer', 'Area hiburan']),
            culinary_facilities=json.dumps(['Restoran', 'Cafe', 'Food court', 'Area makan outdoor']),
            culinary_activities=json.dumps(['Cafe hopping', 'Kuliner malam']),
            culinary_types=json.dumps(['Makanan modern lokal', 'Minuman khas', 'Dessert lokal']),
            culture_heritage=json.dumps([]),
            culture_activities=json.dumps([]),
            culture_elements=json.dumps([]),
            effort_accessibility=json.dumps(['Jalan beraspal baik', 'Dapat dilalui kendaraan roda 4', 'Memiliki petunjuk arah jelas', 'Akses tersedia sepanjang tahun']),
            effort_effort=json.dumps([]),
            effort_mobility=json.dumps(['Area parkir', 'Transportasi online', 'Toilet umum', 'Petunjuk arah', 'Tempat istirahat'])
        ),
    ]

    for dest in destinations:
        existing = Destination.query.filter_by(name=dest.name).first()
        if not existing:
            dest.update_dna_scores()
            db.session.add(dest)

    db.session.commit()
