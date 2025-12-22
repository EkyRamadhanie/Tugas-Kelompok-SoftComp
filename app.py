# app.py

from flask import Flask, render_template, request

from modules.journal_data import get_journal_roads
from modules.genetic_algorithm import GeneticAlgorithm

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    """
    Halaman awal: tampilkan form sederhana (budget %, parameter GA).
    """
    roads = get_journal_roads()
    total_budget = sum(r.cost for r in roads)
    
    return render_template(
        "index.html",
        roads=roads,
        total_budget=total_budget,
        result=None,
        params={
            "budget_ratio": 1.0,
            "population_size": 50,
            "generations": 200,
            "crossover_rate": 0.8,
            "mutation_rate": 0.02,
        },
        error=None,
    )


@app.route("/run", methods=["POST"])
def run():
    try:
        # ambil parameter dari form (kalau field tidak ada, pakai default)
        budget_ratio = float(request.form.get("budget_ratio", "1.0"))
        population_size = int(request.form.get("population_size", "50"))
        generations = int(request.form.get("generations", "200"))
        crossover_rate = float(request.form.get("crossover_rate", "0.8"))
        mutation_rate = float(request.form.get("mutation_rate", "0.02"))

        roads = get_journal_roads()
        total_budget = sum(r.cost for r in roads)

        ga = GeneticAlgorithm(
            roads=roads,
            budget_ratio=budget_ratio,
            population_size=population_size,
            generations=generations,
            crossover_rate=crossover_rate,
            mutation_rate=mutation_rate,
        )

        result = ga.run()
        result_dict = GeneticAlgorithm.result_to_dict(result)
        
        # Debug: Print result
        print("\n=== GA RESULT ===")
        print(f"Total Delta PCR: {result_dict.get('total_delta_pcr', 'N/A')}")
        print(f"Selected Roads: {len(result_dict.get('selected', []))}")
        print(f"Budget Used: {result_dict.get('total_cost', 0):.0f} / {result_dict.get('budget_limit', 0):.0f}")
        print("=================\n")

        return render_template(
            "index.html",
            roads=roads,
            total_budget=total_budget,
            result=result_dict,
            params={
                "budget_ratio": budget_ratio,
                "population_size": population_size,
                "generations": generations,
                "crossover_rate": crossover_rate,
                "mutation_rate": mutation_rate,
            },
            error=None,
        )

    except Exception as e:
        roads = get_journal_roads()
        total_budget = sum(r.cost for r in roads)
        return render_template(
            "index.html",
            roads=roads,
            total_budget=total_budget,
            result=None,
            params=None,
            error=str(e),
        )


if __name__ == "__main__":
    app.run(debug=True)