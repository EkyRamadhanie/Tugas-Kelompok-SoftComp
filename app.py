"""
Road Maintenance Optimizer - Genetic Algorithm
Main Flask Application

Aplikasi web untuk optimasi pemeliharaan jalan menggunakan Algoritma Genetika
"""

from flask import Flask, request, render_template
import sys
import os

# Tambahkan folder modules ke path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

from genetic_algorithm import GeneticAlgorithm
from data_parser import DataParser

# =========================
# FLASK APP INITIALIZATION
# =========================

app = Flask(__name__)

# =========================
# DATA CONTOH DEFAULT
# =========================

SAMPLE_DISTRESS_CSV = """id,location_m,deduction,cost_local
D1,100,20,400
D2,250,15,350
D3,420,30,600
D4,600,10,200
D5,780,25,500
"""

SAMPLE_SEGMENT_CSV = """id,start_m,end_m,cost_resurfacing
S1,0,300,9000
S2,300,700,14000
S3,650,900,11000
"""

# =========================
# ROUTES
# =========================

@app.route("/", methods=["GET"])
def index():
    """
    Halaman utama - Tampilkan form input
    """
    return render_template(
        'index.html',
        sample_distress="",
        sample_segment="",
        result=None,
        error=None
    )


@app.route("/run", methods=["POST"])
def run():
    """
    Endpoint untuk menjalankan optimasi GA
    """
    try:
        # Ambil data CSV dari form
        distress_csv = request.form.get("distress_csv", "")
        segment_csv = request.form.get("segment_csv", "")
        
        # Debug: print data yang diterima
        print("=" * 60)
        print("RECEIVED DATA:")
        print("Distress CSV length:", len(distress_csv))
        print("Segment CSV length:", len(segment_csv))
        print("Distress CSV:\n", distress_csv[:200] if distress_csv else "EMPTY")
        print("Segment CSV:\n", segment_csv[:200] if segment_csv else "EMPTY")
        print("=" * 60)
        
        # Tolak jika kosong agar tidak fallback ke default
        if not distress_csv.strip() or not segment_csv.strip():
            error_msg = "Data input kosong. Isi lewat form atau CSV sebelum menjalankan analisis."
            return render_template(
                'index.html',
                sample_distress=distress_csv,
                sample_segment=segment_csv,
                result=None,
                error=error_msg
            )
        
        # Parse CSV menjadi data struktur
        parser = DataParser()
        distresses = parser.parse_distress(distress_csv)
        segments = parser.parse_segments(segment_csv)
        
        print(f"Parsed {len(distresses)} distresses and {len(segments)} segments")
        print("=" * 60)
        
        # Ambil parameter GA dari form
        budget = float(request.form.get("budget", "150000"))
        pop_size = int(request.form.get("pop_size", "50"))
        generations = int(request.form.get("generations", "100"))
        crossover_rate = float(request.form.get("crossover_rate", "0.8"))
        mutation_rate = float(request.form.get("mutation_rate", "0.05"))
        lambda_budget = float(request.form.get("lambda_budget", "0.5"))
        lambda_overlap = float(request.form.get("lambda_overlap", "1000"))
        
        # Jalankan Algoritma Genetika
        ga = GeneticAlgorithm(
            segments=segments,
            distresses=distresses,
            budget=budget,
            pop_size=pop_size,
            generations=generations,
            crossover_rate=crossover_rate,
            mutation_rate=mutation_rate,
            lambda_budget=lambda_budget,
            lambda_overlap=lambda_overlap
        )
        
        result = ga.run()
        
        # Ambil semua parameter form
        params = {
            'budget': request.form.get("budget", "150000"),
            'pop_size': request.form.get("pop_size", "50"),
            'generations': request.form.get("generations", "100"),
            'crossover_rate': request.form.get("crossover_rate", "0.8"),
            'mutation_rate': request.form.get("mutation_rate", "0.05"),
            'lambda_budget': request.form.get("lambda_budget", "0.5"),
            'lambda_overlap': request.form.get("lambda_overlap", "1000")
        }
        
        # Tampilkan hasil dengan data yang sudah diinput
        return render_template(
            'index.html',
            sample_distress=distress_csv,
            sample_segment=segment_csv,
            result=result,
            params=params,
            error=None
        )
    
    except Exception as e:
        # Jika ada error, tampilkan pesan error
        distress_csv = request.form.get("distress_csv", "")
        segment_csv = request.form.get("segment_csv", "")
        return render_template(
            'index.html',
            sample_distress=distress_csv,
            sample_segment=segment_csv,
            result=None,
            error=str(e)
        )


# =========================
# MAIN - Jalankan Server
# =========================

if __name__ == "__main__":
    print("=" * 60)
    print("  Starting Road Maintenance Optimizer")
    print("=" * 60)
    print("\n  >> Open your browser at: http://127.0.0.1:5000")
    print("  >> Press CTRL+C to stop the server\n")
    print("=" * 60)
    app.run(debug=True)
