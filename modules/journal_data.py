"""
Data studi kasus dari jurnal:
Applied Sciences 2025, 15(10094)

- Distress diambil dari Table 2
- Segment resurfacing dari Table 6
- Biaya resurfacing dari Table 4
"""

# ============================
# 1. DISTRESS (Tabel 2)
# ============================

# Data: (ID, KM, plus_meter, cost_local)
_DISTRESSES_RAW = [
    (1, 3, 772, 454),
    (2, 10, 529, 210),
    (3, 9, 728, 567),
    (4, 1, 324, 186),
    (5, 7, 212, 435),
    (6, 3, 595, 163),
    (7, 7, 595, 260),
    (8, 1, 107, 589),
    (9, 10, 692, 635),
    (10, 5, 349, 366),
    (11, 11, 516, 410),
    (12, 3, 675, 385),
    (13, 2, 648, 517),
    (14, 6, 479, 210),
    (15, 8, 295, 367),
    (16, 6, 918, 199),
    (17, 11, 183, 594),
    (18, 5, 903, 436),
    (19, 9, 296, 564),
    (20, 10, 132, 200),
]


def _estimate_deduction(cost_local):
    """Pendekatan sederhana: deduction ≈ cost_local / 20"""
    return round(cost_local / 20, 2)


def get_journal_distresses():
    distresses = []
    for idx, km, plus, cost in _DISTRESSES_RAW:
        location = km * 1000 + plus
        deduction = _estimate_deduction(cost)
        distresses.append({
            "id": f"D{idx}",
            "location_m": float(location),
            "deduction": deduction,
            "cost_local": float(cost),
        })
    return distresses


# ============================
# 2. RESURFACING SEGMENTS (Table 4)
# ============================

# Biaya resurfacing berdasarkan panjang (Table 4 dari jurnal)
_COST_BY_LENGTH = {
    5: 6400,
    10: 7700,
    15: 9033,
    20: 10267,
    25: 11333,
    30: 12567,
    35: 15733,
    40: 17000,
    45: 18233,
    50: 19467,
    100: 31000,
    150: 43333,
    200: 56000,
    250: 68000,
    300: 80333,
    350: 93333,
}

# Generate semua possible segments berdasarkan panjang yang tersedia di Table 4
# GA akan bebas pilih kombinasi segmen mana yang optimal
def get_journal_segments():
    """
    Generate segmen resurfacing berdasarkan Table 4.
    Strategi: untuk setiap distress, buat segmen yang bisa cover distress tersebut
    menggunakan HANYA panjang yang efisien (100m, 150m, 200m, dll untuk segment panjang)
    dan panjang kecil untuk spot repair.
    """
    segments = []
    segment_id = 1
    
    # Ambil semua lokasi distress
    distresses = get_journal_distresses()
    distress_locations = [d['location_m'] for d in distresses]
    
    # OPTIMASI: Gunakan hanya panjang yang efisien
    # Panjang kecil (5-50m) untuk spot repair, panjang besar (100-350m) untuk coverage luas
    efficient_lengths = [5, 10, 15, 20, 30, 50, 100, 150, 200, 300]
    
    # Untuk setiap panjang efisien
    for length in efficient_lengths:
        cost = _COST_BY_LENGTH[length]
        
        # Generate segmen yang bisa cover setiap distress
        for distress_loc in distress_locations:
            # Hanya 1 variasi: distress di tengah segmen (paling optimal)
            start = distress_loc - length / 2
            
            # Pastikan segmen tidak keluar dari batas jalan
            if start < 0:
                start = 0
            end = start + length
            if end > 12000:
                start = 12000 - length
                end = 12000
            
            if start >= 0 and end <= 12000:
                # Cek duplikasi dengan tolerance 10 meter
                is_duplicate = False
                for existing in segments:
                    if (abs(existing['start_m'] - start) < 10 and 
                        abs(existing['length'] - length) < 1):
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    segments.append({
                        "id": f"S{segment_id}",
                        "start_m": float(start),
                        "end_m": float(end),
                        "length": float(length),
                        "cost": float(cost),
                    })
                    segment_id += 1
    
    return segments