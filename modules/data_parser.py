"""
Module untuk parsing data CSV
"""

import csv
import io


class DataParser:
    """
    Class untuk parsing data CSV input
    """
    
    @staticmethod
    def parse_distress(csv_text):
        """
        Parse CSV kerusakan jalan menjadi list dictionary
        
        Args:
            csv_text: String CSV dengan format id,location_m,deduction,cost_local
            
        Returns:
            List of dict dengan informasi kerusakan
        """
        distresses = []
        reader = csv.DictReader(io.StringIO(csv_text.strip()))
        required = {"id", "location_m", "deduction", "cost_local"}
        
        # Validasi header
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("Header distress CSV harus: id,location_m,deduction,cost_local")
        
        # Parse setiap baris
        for row in reader:
            if not row.get("id"):
                continue
            
            distresses.append({
                "id": row["id"].strip(),
                "location_m": float(row["location_m"]),
                "deduction": float(row["deduction"]),
                "cost_local": float(row["cost_local"])
            })
        
        if not distresses:
            raise ValueError("Data distress kosong. Pastikan ada data selain header.")
        
        return distresses
    
    @staticmethod
    def parse_segments(csv_text):
        """
        Parse CSV segmen resurfacing menjadi list dictionary
        
        Args:
            csv_text: String CSV dengan format id,start_m,end_m,cost_resurfacing
            
        Returns:
            List of dict dengan informasi segmen
        """
        segments = []
        reader = csv.DictReader(io.StringIO(csv_text.strip()))
        required = {"id", "start_m", "end_m", "cost_resurfacing"}
        
        # Validasi header
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("Header segment CSV harus: id,start_m,end_m,cost_resurfacing")
        
        # Parse setiap baris
        for row in reader:
            if not row.get("id"):
                continue
            
            # Pastikan start < end
            start = float(row["start_m"])
            end = float(row["end_m"])
            if end < start:
                start, end = end, start
            
            segments.append({
                "id": row["id"].strip(),
                "start_m": start,
                "end_m": end,
                "cost": float(row["cost_resurfacing"])
            })
        
        if not segments:
            raise ValueError("Data segmen kosong. Pastikan ada data selain header.")
        
        return segments
