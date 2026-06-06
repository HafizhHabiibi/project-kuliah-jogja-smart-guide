# utils/fuzzy_engine.py
"""
Fuzzy Inference System (FIS) Mamdani - Tahap 1 (Indeks Cuaca)
Calculates the weather index W_env (0.0 to 1.0) based on Suhu, Curah Hujan, Kecepatan Angin, Tutupan Awan.
"""

# ==========================================
# 1. FUNGSI KEANGGOTAAN INPUT (MEMBERSHIP FUNCTIONS)
# ==========================================

# A. Curah Hujan (0 s/d 12 mm/jam)
def mu_rain_tidak_hujan(x):
    if x <= 0.5:
        return 1.0
    elif 0.5 < x < 1.5:
        return (1.5 - x) / (1.5 - 0.5)
    else:
        return 0.0

def mu_rain_ringan(x):
    if x <= 0.5 or x >= 6.0:
        return 0.0
    elif 0.5 < x <= 3.0:
        return (x - 0.5) / (3.0 - 0.5)
    else:
        return (6.0 - x) / (6.0 - 3.0)

def mu_rain_sedang(x):
    if x <= 4.0 or x >= 11.0:
        return 0.0
    elif 4.0 < x <= 7.5:
        return (x - 4.0) / (7.5 - 4.0)
    else:
        return (11.0 - x) / (11.0 - 7.5)

def mu_rain_lebat(x):
    if x <= 9.0:
        return 0.0
    elif 9.0 < x < 12.0:
        return (x - 9.0) / (12.0 - 9.0)
    else:
        return 1.0


# B. Kecepatan Angin (0 s/d 10 m/s)
def mu_wind_aman(x):
    if x <= 6.0:
        return 1.0
    elif 6.0 < x < 10.0:
        return (10.0 - x) / (10.0 - 6.0)
    else:
        return 0.0

def mu_wind_bahaya(x):
    if x <= 6.0:
        return 0.0
    elif 6.0 < x < 10.0:
        return (x - 6.0) / (10.0 - 6.0)
    else:
        return 1.0


# C. Suhu Udara (20 s/d 30 °C)
def mu_temp_sejuk(x):
    if x <= 20.0:
        return 1.0
    elif 20.0 < x < 24.0:
        return (24.0 - x) / (24.0 - 20.0)
    else:
        return 0.0

def mu_temp_nyaman(x):
    if x <= 20.0 or x >= 30.0:
        return 0.0
    elif 20.0 < x <= 25.0:
        return (x - 20.0) / (25.0 - 20.0)
    else:
        return (30.0 - x) / (30.0 - 25.0)

def mu_temp_panas(x):
    if x <= 26.0:
        return 0.0
    elif 26.0 < x < 30.0:
        return (x - 26.0) / (30.0 - 26.0)
    else:
        return 1.0


# D. Tutupan Awan (1 s/d 100 %)
def mu_cloud_cerah(x):
    if x <= 15.0:
        return 1.0
    elif 15.0 < x < 50.0:
        return (50.0 - x) / (50.0 - 15.0)
    else:
        return 0.0

def mu_cloud_normal(x):
    if x <= 15.0 or x >= 85.0:
        return 0.0
    elif 15.0 < x <= 50.0:
        return (x - 15.0) / (50.0 - 15.0)
    else:
        return (85.0 - x) / (85.0 - 50.0)

def mu_cloud_mendung(x):
    if x <= 50.0:
        return 0.0
    elif 50.0 < x < 85.0:
        return (x - 50.0) / (85.0 - 50.0)
    else:
        return 1.0


# ==========================================
# 2. FUNGSI KEANGGOTAAN OUTPUT (CONSEQUENT)
# ==========================================

# Indeks Cuaca (0.0 s/d 1.0)
def mu_out_buruk(z):
    if z <= 0.2:
        return 1.0
    elif 0.2 < z < 0.4:
        return (0.4 - z) / (0.4 - 0.2)
    else:
        return 0.0

def mu_out_cukup(z):
    if z <= 0.2 or z >= 0.8:
        return 0.0
    elif 0.2 < z <= 0.5:
        return (z - 0.2) / (0.5 - 0.2)
    else:
        return (0.8 - z) / (0.8 - 0.5)

def mu_out_baik(z):
    if z <= 0.6:
        return 0.0
    elif 0.6 < z < 0.8:
        return (z - 0.6) / (0.8 - 0.6)
    else:
        return 1.0


# ==========================================
# 3. KEPUTUSAN INFERENSI FUZZY
# ==========================================

def calculate_weather_index(temp, rain, clouds, wind):
    """
    Fuzzy Mamdani Tahap 1
    Returns weather index W_env between 0.0 (Worst) and 1.0 (Best)
    """
    # Batasi input agar tidak melampaui batas semesta pembicaraan
    temp = max(20.0, min(30.0, float(temp)))
    rain = max(0.0, min(12.0, float(rain)))
    clouds = max(1.0, min(100.0, float(clouds)))
    wind = max(0.0, min(10.0, float(wind)))

    # Keanggotaan Input
    r_th = mu_rain_tidak_hujan(rain)
    r_r = mu_rain_ringan(rain)
    r_s = mu_rain_sedang(rain)
    r_l = mu_rain_lebat(rain)

    w_am = mu_wind_aman(wind)
    w_bh = mu_wind_bahaya(wind)

    t_sj = mu_temp_sejuk(temp)
    t_ny = mu_temp_nyaman(temp)
    t_pn = mu_temp_panas(temp)

    c_cr = mu_cloud_cerah(clouds)
    c_nr = mu_cloud_normal(clouds)
    c_md = mu_cloud_mendung(clouds)

    # Evaluasi Rules (Mamdani Antecedent implication)
    # R1: Hujan Lebat -> Buruk
    rule1 = r_l

    # R2: Angin Bahaya -> Buruk
    rule2 = w_bh

    # R3: Hujan Sedang & Angin Aman & Suhu Sejuk & Awan Mendung -> Buruk
    rule3 = min(r_s, w_am, t_sj, c_md)

    # R4: Hujan Sedang & Angin Aman & Suhu Nyaman & Awan Mendung -> Buruk
    rule4 = min(r_s, w_am, t_ny, c_md)

    # R5: Hujan Sedang & Angin Aman & Suhu Panas & Awan Normal -> Cukup
    rule5 = min(r_s, w_am, t_pn, c_nr)

    # R6: Hujan Ringan & Angin Aman & Suhu Sejuk & Awan Mendung -> Cukup
    rule6 = min(r_r, w_am, t_sj, c_md)

    # R7: Hujan Ringan & Angin Aman & Suhu Nyaman & Awan Normal -> Cukup
    rule7 = min(r_r, w_am, t_ny, c_nr)

    # R8: Hujan Ringan & Angin Aman & Suhu Panas & Awan Cerah -> Cukup
    rule8 = min(r_r, w_am, t_pn, c_cr)

    # R9: Tidak Hujan & Angin Aman & Suhu Panas & Awan Cerah -> Baik
    rule9 = min(r_th, w_am, t_pn, c_cr)

    # R10: Tidak Hujan & Angin Aman & Suhu Sejuk & Awan Cerah -> Baik
    rule10 = min(r_th, w_am, t_sj, c_cr)

    # R11: Tidak Hujan & Angin Aman & Suhu Nyaman & Awan Normal -> Baik
    rule11 = min(r_th, w_am, t_ny, c_nr)

    # R12: Tidak Hujan & Angin Aman & Suhu Nyaman & Awan Cerah -> Baik
    rule12 = min(r_th, w_am, t_ny, c_cr)

    # Agregasi Output (MAX)
    aggr_buruk = max(rule1, rule2, rule3, rule4)
    aggr_cukup = max(rule5, rule6, rule7, rule8)
    aggr_baik = max(rule9, rule10, rule11, rule12)

    # Defuzzifikasi menggunakan Metode Centroid (Center of Gravity)
    # Membagi rentang 0.0 - 1.0 menjadi 100 sampel
    num_samples = 100
    step_size = 1.0 / num_samples
    
    sum_numerator = 0.0
    sum_denominator = 0.0

    for i in range(num_samples + 1):
        z = i * step_size
        
        # Potong area consequent dengan nilai agregat (MIN)
        val_buruk = min(aggr_buruk, mu_out_buruk(z))
        val_cukup = min(aggr_cukup, mu_out_cukup(z))
        val_baik = min(aggr_baik, mu_out_baik(z))
        
        # Gabungkan area potong (MAX)
        aggregated_membership = max(val_buruk, val_cukup, val_baik)
        
        sum_numerator += z * aggregated_membership
        sum_denominator += aggregated_membership

    # Fallback ke 0.5 jika denominator = 0 (tidak ada rule yang aktif, kondisi tidak lazim)
    if sum_denominator == 0.0:
        return 0.5
        
    return round(sum_numerator / sum_denominator, 4)


# =====================================================================
# FUZZY INFERENCE SYSTEM (FIS) TAHAP 2 (SKOR REKOMENDASI)
# =====================================================================

# ---------------------------------------------------------------------
# A. MEMBERSHIP FUNCTIONS INPUT 1: Cosine Similarity Preferensi User (-1 s/d 1)
# ---------------------------------------------------------------------
def mu_cs_tidak_cocok(x):
    if x <= -0.3:
        return 1.0
    elif -0.3 < x < 0.0:
        return (0.0 - x) / 0.3
    else:
        return 0.0

def mu_cs_cukup_cocok(x):
    if x <= -0.2 or x >= 0.4:
        return 0.0
    elif -0.2 < x <= 0.0:
        return (x - (-0.2)) / 0.2
    else:
        return (0.4 - x) / 0.4

def mu_cs_cocok(x):
    if x <= 0.2 or x >= 0.8:
        return 0.0
    elif 0.2 < x <= 0.5:
        return (x - 0.2) / 0.3
    else:
        return (0.8 - x) / 0.3

def mu_cs_sangat_cocok(x):
    if x <= 0.6:
        return 0.0
    elif 0.6 < x < 0.8:
        return (x - 0.6) / 0.2
    else:
        return 1.0


# ---------------------------------------------------------------------
# B. MEMBERSHIP FUNCTIONS INPUT 2: Kondisi Cuaca (0.0 s/d 1.0)
# ---------------------------------------------------------------------
def mu_weather_buruk(x):
    return mu_out_buruk(x)

def mu_weather_cukup(x):
    return mu_out_cukup(x)

def mu_weather_baik(x):
    return mu_out_baik(x)


# ---------------------------------------------------------------------
# C. MEMBERSHIP FUNCTIONS INPUT 3: Harga Tiket Masuk & Parkir (Rp 0 s/d Rp 150.000)
# ---------------------------------------------------------------------
def mu_price_murah(x):
    if x <= 10000.0:
        return 1.0
    elif 10000.0 < x < 25000.0:
        return (25000.0 - x) / 15000.0
    else:
        return 0.0

def mu_price_terjangkau(x):
    if x <= 15000.0 or x >= 65000.0:
        return 0.0
    elif 15000.0 < x <= 40000.0:
        return (x - 15000.0) / 25000.0
    else:
        return (65000.0 - x) / 25000.0

def mu_price_mahal(x):
    if x <= 50000.0:
        return 0.0
    elif 50000.0 < x < 80000.0:
        return (x - 50000.0) / 30000.0
    else:
        return 1.0


# ---------------------------------------------------------------------
# D. MEMBERSHIP FUNCTIONS INPUT 4: Jarak Geografis (0 s/d 100 km)
# ---------------------------------------------------------------------
def mu_dist_dekat(x):
    if x <= 5.0:
        return 1.0
    elif 5.0 < x < 15.0:
        return (15.0 - x) / 10.0
    else:
        return 0.0

def mu_dist_sedang(x):
    if x <= 10.0 or x >= 45.0:
        return 0.0
    elif 10.0 < x <= 25.0:
        return (x - 10.0) / 15.0
    else:
        return (45.0 - x) / 20.0

def mu_dist_jauh(x):
    if x <= 35.0:
        return 0.0
    elif 35.0 < x < 60.0:
        return (x - 35.0) / 25.0
    else:
        return 1.0


# ---------------------------------------------------------------------
# E. MEMBERSHIP FUNCTIONS OUTPUT: Skor Rekomendasi (0 s/d 100)
# ---------------------------------------------------------------------
def mu_recommend_std(z):
    if z <= 15.0:
        return 1.0
    elif 15.0 < z < 25.0:
        return (25.0 - z) / 10.0
    else:
        return 0.0

def mu_recommend_td(z):
    if z <= 20.0 or z >= 50.0:
        return 0.0
    elif 20.0 < z <= 35.0:
        return (z - 20.0) / 15.0
    else:
        return (50.0 - z) / 15.0

def mu_recommend_cd(z):
    if z <= 40.0 or z >= 70.0:
        return 0.0
    elif 40.0 < z <= 55.0:
        return (z - 40.0) / 15.0
    else:
        return (70.0 - z) / 15.0

def mu_recommend_d(z):
    if z <= 60.0 or z >= 90.0:
        return 0.0
    elif 60.0 < z <= 75.0:
        return (z - 60.0) / 15.0
    else:
        return (90.0 - z) / 15.0

def mu_recommend_sd(z):
    if z <= 80.0:
        return 0.0
    elif 80.0 < z < 90.0:
        return (z - 80.0) / 10.0
    else:
        return 1.0


# ---------------------------------------------------------------------
# F. INFERENSI FUZZY MAMDANI TAHAP 2
# ---------------------------------------------------------------------
def calculate_recommendation_score(cosine_sim, weather_idx, price, distance):
    """
    Fuzzy Mamdani Tahap 2
    Calculates dynamic Recommendation Score (SR) between 0.0 (Worst) and 100.0 (Best).
    
    Inputs:
        cosine_sim (float) : Cosine similarity between user prefs and dest DNA (-1.0 to 1.0)
        weather_idx (float): Weather Environment Index from Stage 1 FIS (0.0 to 1.0)
        price (float)      : Ticket + parking price in IDR (0 to 150,000)
        distance (float)   : Distance in kilometers (0 to 100)
    """
    # Batasi input agar tidak melampaui batas semesta pembicaraan
    cosine_sim = max(-1.0, min(1.0, float(cosine_sim)))
    weather_idx = max(0.0, min(1.0, float(weather_idx)))
    price = max(0.0, min(150000.0, float(price)))
    distance = max(0.0, min(100.0, float(distance)))

    # 1. Derajat Keanggotaan Input
    cs_tc = mu_cs_tidak_cocok(cosine_sim)
    cs_cc = mu_cs_cukup_cocok(cosine_sim)
    cs_c = mu_cs_cocok(cosine_sim)
    cs_sc = mu_cs_sangat_cocok(cosine_sim)

    w_b = mu_weather_buruk(weather_idx)
    w_c = mu_weather_cukup(weather_idx)
    w_bk = mu_weather_baik(weather_idx)

    p_m = mu_price_murah(price)
    p_t = mu_price_terjangkau(price)
    p_mh = mu_price_mahal(price)

    d_dk = mu_dist_dekat(distance)
    d_sd = mu_dist_sedang(distance)
    d_jh = mu_dist_jauh(distance)

    # 2. Evaluasi Rules (Mamdani Inference)
    
    # R1: Cosine Tidak Cocok -> STD (Mewakili 27 aturan pruning)
    rule1 = cs_tc

    # R2: Cosine Cukup Cocok & Cuaca Buruk -> STD
    rule2 = min(cs_cc, w_b)

    # R3: Cosine Cocok & Cuaca Buruk & Tiket Mahal & Jarak Jauh -> STD
    rule3 = min(cs_c, w_b, p_mh, d_jh)

    # R4: Cosine Cocok & Cuaca Buruk & Tiket Terjangkau & Jarak Sedang -> TD
    rule4 = min(cs_c, w_b, p_t, d_sd)

    # R5: Cosine Sangat Cocok & Cuaca Buruk & Tiket Gratis/Murah & Jarak Dekat -> TD
    rule5 = min(cs_sc, w_b, p_m, d_dk)

    # R6: Cosine Cukup Cocok & Cuaca Cukup & Tiket Mahal & Jarak Jauh -> TD
    rule6 = min(cs_cc, w_c, p_mh, d_jh)

    # R7: Cosine Cukup Cocok & Cuaca Cukup & Tiket Terjangkau & Jarak Sedang -> CD
    rule7 = min(cs_cc, w_c, p_t, d_sd)

    # R8: Cosine Cukup Cocok & Cuaca Baik & Tiket Gratis/Murah & Jarak Dekat -> CD
    rule8 = min(cs_cc, w_bk, p_m, d_dk)

    # R9: Cosine Cocok & Cuaca Cukup & Tiket Mahal & Jarak Jauh -> TD
    rule9 = min(cs_c, w_c, p_mh, d_jh)

    # R10: Cosine Cocok & Cuaca Cukup & Tiket Terjangkau & Jarak Sedang -> CD
    rule10 = min(cs_c, w_c, p_t, d_sd)

    # R11: Cosine Cocok & Cuaca Cukup & Tiket Gratis/Murah & Jarak Dekat -> D
    rule11 = min(cs_c, w_c, p_m, d_dk)

    # R12: Cosine Cocok & Cuaca Baik & Tiket Mahal & Jarak Jauh -> CD
    rule12 = min(cs_c, w_bk, p_mh, d_jh)

    # R13: Cosine Cocok & Cuaca Baik & Tiket Terjangkau & Jarak Sedang -> D
    rule13 = min(cs_c, w_bk, p_t, d_sd)

    # R14: Cosine Cocok & Cuaca Baik & Tiket Gratis/Murah & Jarak Dekat -> SD
    rule14 = min(cs_c, w_bk, p_m, d_dk)

    # R15: Cosine Sangat Cocok & Cuaca Cukup & Tiket Mahal & Jarak Jauh -> CD
    rule15 = min(cs_sc, w_c, p_mh, d_jh)

    # R16: Cosine Sangat Cocok & Cuaca Cukup & Tiket Terjangkau & Jarak Sedang -> D
    rule16 = min(cs_sc, w_c, p_t, d_sd)

    # R17: Cosine Sangat Cocok & Cuaca Cukup & Tiket Gratis/Murah & Jarak Dekat -> SD
    rule17 = min(cs_sc, w_c, p_m, d_dk)

    # R18: Cosine Sangat Cocok & Cuaca Baik & Tiket Mahal & Jarak Jauh -> D
    rule18 = min(cs_sc, w_bk, p_mh, d_jh)

    # R19: Cosine Sangat Cocok & Cuaca Baik & Tiket Terjangkau & Jarak Sedang -> SD
    rule19 = min(cs_sc, w_bk, p_t, d_sd)

    # R20: Cosine Sangat Cocok & Cuaca Baik & Tiket Gratis/Murah & Jarak Dekat -> SD
    rule20 = min(cs_sc, w_bk, p_m, d_dk)

    # Agregasi Area Consequent (MAX)
    aggr_std = max(rule1, rule2, rule3)
    aggr_td  = max(rule4, rule5, rule6, rule9)
    aggr_cd  = max(rule7, rule8, rule10, rule12, rule15)
    aggr_d   = max(rule11, rule13, rule16, rule18)
    aggr_sd  = max(rule14, rule17, rule19, rule20)

    # 3. Defuzzifikasi Centroid (COG)
    # Rentang output Skor Rekomendasi (0 s/d 100). Kita bagi menjadi 100 sampel (step = 1.0)
    num_samples = 100
    step_size = 100.0 / num_samples
    
    sum_numerator = 0.0
    sum_denominator = 0.0

    for i in range(num_samples + 1):
        z = i * step_size
        
        # Potong area keanggotaan consequent dengan tingkat keaktifan aturan (MIN)
        val_std = min(aggr_std, mu_recommend_std(z))
        val_td  = min(aggr_td, mu_recommend_td(z))
        val_cd  = min(aggr_cd, mu_recommend_cd(z))
        val_d   = min(aggr_d, mu_recommend_d(z))
        val_sd  = min(aggr_sd, mu_recommend_sd(z))
        
        # Gabungkan daerah potongan (MAX)
        aggregated_membership = max(val_std, val_td, val_cd, val_d, val_sd)
        
        sum_numerator += z * aggregated_membership
        sum_denominator += aggregated_membership

    # Fallback ke 50.0 jika tidak ada rule yang aktif (kondisi ekstrem)
    if sum_denominator == 0.0:
        return 50.0
        
    return round(sum_numerator / sum_denominator, 2)

