"""
Module untuk Algoritma Genetika (GA)
Optimasi Pemeliharaan Jalan dengan Resurfacing dan Local Repair
"""

import random


class GeneticAlgorithm:
    """
    Class untuk menjalankan Algoritma Genetika
    """
    
    def __init__(self, segments, distresses, budget, 
                 pop_size=50, generations=100,
                 crossover_rate=0.8, mutation_rate=0.05,
                 lambda_budget=0.5, lambda_overlap=1000.0):
        """
        Inisialisasi parameter GA
        """
        self.segments = segments
        self.distresses = distresses
        self.budget = budget
        self.pop_size = pop_size
        self.generations = generations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.lambda_budget = lambda_budget
        self.lambda_overlap = lambda_overlap
        
        # Panjang kromosom = jumlah segmen + jumlah kerusakan
        self.genome_length = len(segments) + len(distresses)
        
        # Tracking solusi terbaik
        self.best_chromosome = None
        self.best_fitness = float("-inf")
        self.best_cost = 0.0
        self.best_benefit = 0.0
    
    @staticmethod
    def segments_overlap(seg_a, seg_b):
        """
        Cek apakah dua segmen saling overlap
        """
        return max(seg_a["start_m"], seg_b["start_m"]) < min(seg_a["end_m"], seg_b["end_m"])
    
    def compute_fitness(self, chromosome):
        """
        Hitung fitness, cost, dan benefit dari kromosom
        """
        n_seg = len(self.segments)
        
        # Decode kromosom
        seg_bits = chromosome[:n_seg]
        loc_bits = chromosome[n_seg:]
        
        # Hitung biaya segmen dan overlap
        total_cost = 0.0
        chosen_seg_idx = [i for i, g in enumerate(seg_bits) if g == 1]
        
        for i in chosen_seg_idx:
            total_cost += self.segments[i]["cost"]
        
        # Hitung overlap
        overlap_count = 0
        for i in range(len(chosen_seg_idx)):
            for j in range(i + 1, len(chosen_seg_idx)):
                s1 = self.segments[chosen_seg_idx[i]]
                s2 = self.segments[chosen_seg_idx[j]]
                if self.segments_overlap(s1, s2):
                    overlap_count += 1
        
        # Evaluasi perbaikan kerusakan
        total_benefit = 0.0
        for idx, d in enumerate(self.distresses):
            loc = d["location_m"]
            deduction = d["deduction"]
            cost_local = d["cost_local"]
            
            # Cek apakah tercakup dalam segmen resurfacing
            covered_by_seg = False
            for s_idx in chosen_seg_idx:
                s = self.segments[s_idx]
                if s["start_m"] <= loc <= s["end_m"]:
                    covered_by_seg = True
                    break
            
            repaired = False
            if covered_by_seg:
                repaired = True
            else:
                if loc_bits[idx] == 1:
                    repaired = True
                    total_cost += cost_local
            
            if repaired:
                total_benefit += deduction
        
        # Hitung penalti dan fitness
        overshoot = max(0.0, total_cost - self.budget)
        penalty_budget = self.lambda_budget * overshoot
        penalty_overlap = self.lambda_overlap * overlap_count
        
        fitness = total_benefit - penalty_budget - penalty_overlap
        
        return fitness, total_cost, total_benefit
    
    def init_population(self):
        """
        Inisialisasi populasi dengan bit random
        """
        return [[random.randint(0, 1) for _ in range(self.genome_length)] 
                for _ in range(self.pop_size)]
    
    def tournament_selection(self, population, fitnesses, k=3):
        """
        Tournament selection untuk memilih parent
        """
        best = None
        best_fit = None
        for _ in range(k):
            idx = random.randint(0, len(population) - 1)
            if (best is None) or (fitnesses[idx] > best_fit):
                best = population[idx]
                best_fit = fitnesses[idx]
        return best[:]
    
    def one_point_crossover(self, p1, p2):
        """
        One-point crossover untuk menghasilkan offspring
        """
        if random.random() > self.crossover_rate:
            return p1[:], p2[:]
        
        point = random.randint(1, len(p1) - 1)
        c1 = p1[:point] + p2[point:]
        c2 = p2[:point] + p1[point:]
        return c1, c2
    
    def mutate(self, chromosome):
        """
        Mutasi dengan flip bit
        """
        for i in range(len(chromosome)):
            if random.random() < self.mutation_rate:
                chromosome[i] = 1 - chromosome[i]
    
    def run(self):
        """
        Jalankan algoritma genetika
        """
        # Inisialisasi populasi
        population = self.init_population()
        
        # Loop evolusi
        for gen in range(self.generations):
            # Evaluasi fitness
            fitnesses = []
            for chrom in population:
                f, c, b = self.compute_fitness(chrom)
                fitnesses.append(f)
                
                # Update solusi terbaik
                if f > self.best_fitness:
                    self.best_fitness = f
                    self.best_chromosome = chrom[:]
                    self.best_cost = c
                    self.best_benefit = b
            
            # Buat generasi baru
            new_pop = []
            while len(new_pop) < self.pop_size:
                # Seleksi parent
                p1 = self.tournament_selection(population, fitnesses)
                p2 = self.tournament_selection(population, fitnesses)
                
                # Crossover
                c1, c2 = self.one_point_crossover(p1, p2)
                
                # Mutasi
                self.mutate(c1)
                self.mutate(c2)
                
                # Tambahkan ke populasi baru
                new_pop.append(c1)
                if len(new_pop) < self.pop_size:
                    new_pop.append(c2)
            
            population = new_pop
        
        # Return hasil
        return self.decode_solution()
    
    def decode_solution(self):
        """
        Decode kromosom terbaik menjadi format yang mudah dibaca
        """
        n_seg = len(self.segments)
        seg_bits = self.best_chromosome[:n_seg]
        loc_bits = self.best_chromosome[n_seg:]
        
        # Kumpulkan segmen yang dipilih
        chosen_segments = []
        for idx, bit in enumerate(seg_bits):
            if bit == 1:
                s = self.segments[idx]
                chosen_segments.append({
                    "id": s["id"],
                    "start_m": s["start_m"],
                    "end_m": s["end_m"],
                    "length": s["end_m"] - s["start_m"],
                    "cost": s["cost"]
                })
        
        # Status perbaikan setiap kerusakan
        distress_status = []
        for idx, d in enumerate(self.distresses):
            loc = d["location_m"]
            covered_by_seg = False
            method = "Tidak diperbaiki"
            
            # Cek apakah tercakup dalam segmen resurfacing
            for s in chosen_segments:
                if s["start_m"] <= loc <= s["end_m"]:
                    covered_by_seg = True
                    method = "Resurfacing"
                    break
            
            repaired = False
            if covered_by_seg:
                repaired = True
            else:
                if loc_bits[idx] == 1:
                    repaired = True
                    method = "Local repair"
            
            distress_status.append({
                "id": d["id"],
                "location_m": d["location_m"],
                "deduction": d["deduction"],
                "cost_local": d["cost_local"],
                "repaired": repaired,
                "method": method
            })
        
        return {
            "best_fitness": round(self.best_fitness, 3),
            "total_cost": round(self.best_cost, 3),
            "total_benefit": round(self.best_benefit, 3),
            "budget": self.budget,
            "chosen_segments": chosen_segments,
            "distress_status": distress_status
        }
