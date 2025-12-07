import random
import time
import copy


class GeneticAlgorithm:

    def __init__(
        self,
        segments,
        distresses,
        budget,
        pop_size,
        generations,
        crossover_rate,
        mutation_rate,
        lambda_budget,
        lambda_overlap
    ):
        # === RESET RANDOM SETIAP RUN ===
        random.seed(time.time())

        # === SIMPAN DATA ===
        self.segments = segments
        self.distresses = distresses
        self.budget = budget

        self.pop_size = pop_size
        self.generations = generations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.lambda_budget = lambda_budget
        self.lambda_overlap = lambda_overlap

        # === RESET STATE GA ===
        self.population = []
        self.best_solution = None
        self.best_fitness = float("-inf")
        
        # === CACHE untuk speed up ===
        self._fitness_cache = {}

        # === INISIALISASI POPULASI ===
        self._init_population()

    # ----------------------------------------------------------------------
    # INISIALISASI POPULASI
    # ----------------------------------------------------------------------
    def _init_population(self):
        self.population = []
        chromosome_length = len(self.segments)

        # Generate random population dengan density rendah
        for _ in range(self.pop_size):
            chrom = []
            for _ in range(chromosome_length):
                # 5% chance gene = 1
                if random.random() < 0.05:
                    chrom.append(1)
                else:
                    chrom.append(0)
            
            self.population.append(chrom)

    # ----------------------------------------------------------------------
    # HITUNG TOTAL BIAYA CHROMOSOME (RESURFACING + LOCAL REPAIR)
    # ----------------------------------------------------------------------
    def _compute_total_cost(self, chrom):
        total = 0
        
        # 1. Biaya resurfacing
        repaired_by_resurfacing = set()
        for gene, seg in zip(chrom, self.segments):
            if gene == 1:
                total += seg["cost"]
                # Track distress yang di-cover resurfacing
                for d in self.distresses:
                    if seg["start_m"] <= d["location_m"] <= seg["end_m"]:
                        repaired_by_resurfacing.add(d["id"])
        
        # 2. Biaya local repair untuk yang tidak di-cover resurfacing
        for d in self.distresses:
            if d["id"] not in repaired_by_resurfacing:
                total += d["cost_local"]
        
        return total

    # ----------------------------------------------------------------------
    # HITUNG MANFAAT (TOTAL DEDUCTION REPAIRED)
    # ----------------------------------------------------------------------
    def _compute_benefit(self, chrom):

        repaired_by_resurfacing = set()

        # 1. Resurfacing coverage
        for gene, seg in zip(chrom, self.segments):
            if gene == 1:  # segmen terpilih
                for d in self.distresses:
                    if seg["start_m"] <= d["location_m"] <= seg["end_m"]:
                        repaired_by_resurfacing.add(d["id"])

        # 2. Hitung benefit dari resurfacing + local repair
        total_benefit = 0
        for d in self.distresses:
            # Semua distress diperbaiki (resurfacing atau local repair)
            total_benefit += d["deduction"]

        return total_benefit

    # ----------------------------------------------------------------------
    # HITUNG PENALTI OVERLAP
    # ----------------------------------------------------------------------
    def _compute_overlap_penalty(self, chrom):
        penalty = 0
        chosen_segments = [
            seg for gene, seg in zip(chrom, self.segments) if gene == 1
        ]

        # Bandingkan semua pasangan segmen
        for i in range(len(chosen_segments)):
            for j in range(i + 1, len(chosen_segments)):
                s1 = chosen_segments[i]
                s2 = chosen_segments[j]

                if not (s1["end_m"] < s2["start_m"] or s2["end_m"] < s1["start_m"]):
                    penalty += self.lambda_overlap

        return penalty

    # ----------------------------------------------------------------------
    # HITUNG FITNESS
    # ----------------------------------------------------------------------
    def _fitness(self, chrom):
        # Check cache first
        chrom_tuple = tuple(chrom)
        if chrom_tuple in self._fitness_cache:
            return self._fitness_cache[chrom_tuple]
        
        cost = self._compute_total_cost(chrom)
        benefit = self._compute_benefit(chrom)

        # Cek overlap dulu - invalid solution
        overlap_penalty = self._compute_overlap_penalty(chrom)
        if overlap_penalty > 0:
            self._fitness_cache[chrom_tuple] = 0
            return 0

        # Over budget = invalid solution
        if cost > self.budget:
            self._fitness_cache[chrom_tuple] = 0
            return 0
        
        # Hitung jumlah distress yang diperbaiki via resurfacing
        repaired_by_resurfacing = 0
        for d in self.distresses:
            for gene, seg in zip(chrom, self.segments):
                if gene == 1 and seg["start_m"] <= d["location_m"] <= seg["end_m"]:
                    repaired_by_resurfacing += 1
                    break
        
        # Semua distress diperbaiki (resurfacing + local repair)
        total_repaired = len(self.distresses)
        
        # Fitness components:
        # 1. Benefit (total deduction) - semua diperbaiki, jadi benefit maksimal
        # 2. Minimize cost - lebih sedikit biaya lebih bagus
        # 3. Prefer resurfacing jika ekonomis (bonus untuk resurfacing)
        
        # Fitness = benefit - (cost penalty) + (resurfacing bonus)
        cost_penalty = cost / 1000  # Normalize cost
        resurfacing_bonus = repaired_by_resurfacing * 20  # Bonus untuk setiap resurfacing
        
        fitness = (benefit * 10) - cost_penalty + resurfacing_bonus

        # Cache result
        self._fitness_cache[chrom_tuple] = fitness
        return fitness

    # ----------------------------------------------------------------------
    # SELECTION (TOURNAMENT)
    # ----------------------------------------------------------------------
    def _select_parent(self):
        k = 3  # tournament size
        best = None
        best_fit = float("-inf")

        for _ in range(k):
            chrom = random.choice(self.population)
            fit = self._fitness(chrom)
            if fit > best_fit:
                best_fit = fit
                best = chrom

        return copy.deepcopy(best)

    # ----------------------------------------------------------------------
    # CROSSOVER (SINGLE POINT)
    # ----------------------------------------------------------------------
    def _crossover(self, p1, p2):
        if random.random() > self.crossover_rate:
            return copy.deepcopy(p1), copy.deepcopy(p2)

        point = random.randint(1, len(p1) - 1)

        c1 = p1[:point] + p2[point:]
        c2 = p2[:point] + p1[point:]

        return c1, c2

    # ----------------------------------------------------------------------
    # MUTATION
    # ----------------------------------------------------------------------
    def _mutate(self, chrom):
        # Standard bit-flip mutation
        for i in range(len(chrom)):
            if random.random() < self.mutation_rate:
                chrom[i] = 1 - chrom[i]
        
        return chrom
    
    # ----------------------------------------------------------------------
    # REPAIR: Perbaiki solusi yang over budget dan overlap
    # ----------------------------------------------------------------------
    def _repair(self, chrom):
        """Hapus segmen dengan efisiensi terendah sampai tidak over budget dan no overlap"""
        
        # Step 1: Fix overlaps first
        max_iter_overlap = 50
        for _ in range(max_iter_overlap):
            overlap_penalty = self._compute_overlap_penalty(chrom)
            if overlap_penalty == 0:
                break
            
            # Find overlapping segments
            chosen_segs_idx = [i for i, g in enumerate(chrom) if g == 1]
            found_overlap = False
            
            for i in chosen_segs_idx:
                if found_overlap:
                    break
                for j in chosen_segs_idx:
                    if i >= j:
                        continue
                    s1 = self.segments[i]
                    s2 = self.segments[j]
                    
                    # Check overlap
                    if not (s1["end_m"] <= s2["start_m"] or s2["end_m"] <= s1["start_m"]):
                        # Remove the more expensive one
                        if s1["cost"] > s2["cost"]:
                            chrom[i] = 0
                        else:
                            chrom[j] = 0
                        found_overlap = True
                        break
        
        # Step 2: Fix budget
        cost = self._compute_total_cost(chrom)
        if cost <= self.budget:
            return chrom
        
        # Build list of active segments dengan efisiensi
        active_segments = []
        for i, (gene, seg) in enumerate(zip(chrom, self.segments)):
            if gene == 1:
                # Hitung efisiensi
                covered_deduction = 0
                for d in self.distresses:
                    if seg["start_m"] <= d["location_m"] <= seg["end_m"]:
                        covered_deduction += d["deduction"]
                
                efficiency = covered_deduction / seg["cost"] if seg["cost"] > 0 else 0
                active_segments.append((i, efficiency, seg["cost"]))
        
        # Sort by efficiency ascending (worst first)
        active_segments.sort(key=lambda x: x[1])
        
        # Hapus segmen dengan efisiensi terendah sampai budget OK
        for idx, eff, seg_cost in active_segments:
            chrom[idx] = 0
            cost -= seg_cost
            if cost <= self.budget:
                break
        
        return chrom

    # ----------------------------------------------------------------------
    # EVALUATE BEST SOLUTION
    # ----------------------------------------------------------------------
    def _update_best(self):
        for chrom in self.population:
            fit = self._fitness(chrom)
            if fit > self.best_fitness:
                self.best_fitness = fit
                self.best_solution = copy.deepcopy(chrom)

    # ----------------------------------------------------------------------
    # RUN GA
    # ----------------------------------------------------------------------
    def run(self):

        # RESET STATE SETIAP RUN
        random.seed(time.time())
        self.best_fitness = float("-inf")
        self.best_solution = None
        self._init_population()

        # LOOP GENERATION
        for _ in range(self.generations):
            new_population = []

            # Buat populasi baru
            while len(new_population) < self.pop_size:
                p1 = self._select_parent()
                p2 = self._select_parent()

                c1, c2 = self._crossover(p1, p2)

                c1 = self._mutate(c1)
                c2 = self._mutate(c2)
                
                # REPAIR: perbaiki solusi yang over budget
                c1 = self._repair(c1)
                c2 = self._repair(c2)

                new_population.append(c1)
                if len(new_population) < self.pop_size:
                    new_population.append(c2)

            self.population = new_population
            self._update_best()

        # KEMBALIKAN RESULT
        return self._build_result()

    # ----------------------------------------------------------------------
    # BANGUN OUTPUT UNTUK UI
    # ----------------------------------------------------------------------
    def _build_result(self):

        chosen_segments = []
        total_cost = 0

        for gene, seg in zip(self.best_solution, self.segments):
            if gene == 1:
                chosen_segments.append({
                    "id": seg["id"],
                    "start_m": seg["start_m"],
                    "end_m": seg["end_m"],
                    "length": seg["length"],
                    "cost": seg["cost"]
                })
                total_cost += seg["cost"]

        # Status distress dengan metode repair
        distress_status = []
        resurfacing_cost_total = 0
        local_repair_cost_total = 0
        
        for d in self.distresses:
            repaired = False
            method = "None"
            cost_used = 0

            # Cek apakah termasuk resurfacing
            for gene, seg in zip(self.best_solution, self.segments):
                if gene == 1 and seg["start_m"] <= d["location_m"] <= seg["end_m"]:
                    repaired = True
                    method = "Resurfacing"
                    # Cost untuk resurfacing sudah di-track di chosen_segments
                    cost_used = seg["cost"]  # Ini share cost dengan distress lain di segmen yang sama
                    resurfacing_cost_total += d["cost_local"]  # Track biaya local yang disave
                    break

            # Kalau tidak masuk resurfacing → pakai local repair
            if not repaired:
                repaired = True
                method = "Local Repair"
                cost_used = d["cost_local"]
                local_repair_cost_total += d["cost_local"]

            distress_status.append({
                "id": d["id"],
                "location_m": d["location_m"],
                "deduction": d["deduction"],
                "cost_local": d["cost_local"],
                "repaired": repaired,
                "method": method,
                "cost_used": cost_used
            })

        # Hitung total cost termasuk local repair
        total_cost_with_local = total_cost + local_repair_cost_total
        
        # Count metode
        resurfacing_count = sum(1 for d in distress_status if d["method"] == "Resurfacing")
        local_repair_count = sum(1 for d in distress_status if d["method"] == "Local Repair")
        
        return {
            "best_fitness": round(self.best_fitness, 3),
            "best_solution": self.best_solution,
            "chosen_segments": chosen_segments,
            "total_cost": total_cost_with_local,
            "resurfacing_cost": total_cost,
            "local_repair_cost": local_repair_cost_total,
            "budget": self.budget,
            "total_benefit": self._compute_benefit(self.best_solution),
            "distress_status": distress_status,
            "resurfacing_count": resurfacing_count,
            "local_repair_count": local_repair_count
        }