import requests
import os
import json

BASE_URL = "http://127.0.0.1:8000"
DATA_DIR = "c:/Users/Admin/OneDrive/Documents/Office_work/CostOptimization/data"

variants = [
    "variant_missing_quality.csv",
    "variant_long_lead_times.csv",
    "variant_small_price_diff.csv"
]

def run_analysis(filename):
    print(f"\n--- Analyzing {filename} ---")
    file_path = os.path.join(DATA_DIR, filename)
    with open(file_path, 'rb') as f:
        files = {'files': (filename, f, 'text/csv')}
        response = requests.post(f"{BASE_URL}/analyze", files=files)
        
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error {response.status_code}: {response.text}")

if __name__ == "__main__":
    for variant in variants:
        run_analysis(variant)
