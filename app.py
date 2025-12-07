from flask import Flask, render_template, request
from modules.data_parser import DataParser
from modules.genetic_algorithm import GeneticAlgorithm

# === IMPORT DATA JURNAL ===
from modules.journal_data import get_journal_distresses, get_journal_segments

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template(
        "index.html",
        sample_distress="id,location_m,deduction,cost_local\nD1,100,20,400",
        sample_segment="id,start_m,end_m,cost_resurfacing\nS1,0,300,9000",
        result=None,
        params=None,
        error=None
    )


@app.route("/run", methods=["POST"])
def run():
    try:
        # Selalu pakai data jurnal
        distresses = get_journal_distresses()
        segments = get_journal_segments()

        # ===================================================================================
        # PARAMETER GA
        # ===================================================================================

        params = {
            "budget": request.form.get("budget"),
            "pop_size": request.form.get("pop_size"),
            "generations": request.form.get("generations"),
            "crossover_rate": request.form.get("crossover_rate"),
            "mutation_rate": request.form.get("mutation_rate"),
            "use_journal": True,
        }

        # Lambda parameters tidak digunakan lagi, set default
        lambda_budget = 0.5
        lambda_overlap = 1000

        ga = GeneticAlgorithm(
            segments=segments,
            distresses=distresses,
            budget=float(params["budget"]),
            pop_size=int(params["pop_size"]),
            generations=int(params["generations"]),
            crossover_rate=float(params["crossover_rate"]),
            mutation_rate=float(params["mutation_rate"]),
            lambda_budget=lambda_budget,
            lambda_overlap=lambda_overlap,
        )

        result = ga.run()
        
        print(f"GA COMPLETED: {len(result['chosen_segments'])} segments, fitness={result['best_fitness']}")

        return render_template(
            "index.html",
            sample_distress="",
            sample_segment="",
            result=result,
            params=params,
            error=None
        )

    except Exception as e:
        print(f"ERROR in /run: {e}")
        import traceback
        traceback.print_exc()
        return render_template(
            "index.html",
            sample_distress="",
            sample_segment="",
            result=None,
            params=None,
            error=str(e)
        )


if __name__ == "__main__":
    app.run(debug=True)