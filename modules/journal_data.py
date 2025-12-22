# modules/journal_data.py

"""
Dataset diambil dari:
Nautiyal, A., & Sharma, S. (2022).
Cost-Optimized Approach for Pavement Maintenance Planning
of Low Volume Rural Roads: A Case Study in Himalayan Region.
International Journal of Pavement Research and Technology.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class Road:
    id: str
    technique: str
    present_pcr: float
    cost: float          # biaya perbaikan (₹) untuk teknik terpilih
    new_pcr: float       # PCR setelah perbaikan


def get_journal_roads() -> List[Road]:
    """
    Mengembalikan list objek Road yang diambil & disederhanakan dari
    Tabel 6 (The optimized selection of maintenance). :contentReference[oaicite:2]{index=2}

    Untuk tugas, subset jalan ini sudah cukup; kalau mau lengkap,
    kamu bisa menambahkan baris lain pakai pola yang sama.
    """

    roads: List[Road] = [
        Road("BIL093", "OG", 1.3,   10488.0, 1.8),
        Road("NL022",  "MS", 2.0,     621.76, 2.6),
        Road("NL023",  "RE", 0.8,   57875.0, 3.0),
        Road("NL026",  "RM", 2.3,    1552.0, 2.53),
        Road("BHL023", "MS", 2.0,    2253.8, 2.6),
        Road("BHL033", "SS", 2.3,    4268.0, 2.53),
        Road("NL028",  "RE", 0.8,   57875.0, 3.0),
        Road("NL035",  "RM", 2.2,     776.0, 2.42),
        Road("NL036",  "RE", 0.8,   92600.0, 3.0),
        Road("NL037",  "RM", 2.3,    1241.6, 2.53),
        Road("NL087",  "RM", 2.3,    1164.0, 2.53),
        Road("NL089",  "RE", 0.8,  185200.0, 3.0),
        Road("NL096",  "RE", 0.8,   98387.0, 3.0),
        # Di jurnal, NL106 tidak dipilih bahkan di 100% budget,
        # tapi kita tetap masukkan sebagai kandidat:
        Road("NL106",  "RE", 0.8,  347250.0, 0.8),  # new PCR sama (tidak direhabilitasi)
        Road("BHL043", "CF", 2.2,     103.01, 2.59),
        Road("BIL047", "SS", 2.0,    4744.4, 2.6),
    ]

    return roads
