import requests
import zipfile
import csv
import polyline
from collections import defaultdict
import pandas as pd
import os

url = "https://api.data.gov.my/gtfs-static/prasarana?category=rapid-bus-kl"
zip_path = "rapid-bus-kl.zip"
extract_dir = "rapid-bus-kl"

r = requests.get(url)
r.raise_for_status()

with open(zip_path, "wb") as f:
    f.write(r.content)

if not os.path.exists(extract_dir):
    os.makedirs(extract_dir)

with zipfile.ZipFile(zip_path, "r") as zip_ref:
    zip_ref.extractall(extract_dir)

shapes = defaultdict(list)

with open(f"{extract_dir}/shapes.txt", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        shapes[row["shape_id"]].append({
            "lat": float(row["shape_pt_lat"]),
            "lon": float(row["shape_pt_lon"]),
            "seq": int(row["shape_pt_sequence"]),
        })

# sort each shape by sequence
for shape_id in shapes:
    shapes[shape_id].sort(key=lambda p: p["seq"])

print("Total shapes:", len(shapes))
print("Points in T788002:", len(shapes.get("T788002", [])))


rows = []


for shape_id, points in shapes.items():
    for p in points:
        rows.append({
            "shape_id": shape_id,
            "lat": p["lat"],
            "lon": p["lon"],
            "seq": p["seq"],
        })

df = pd.DataFrame(rows)
df = df.sort_values(["shape_id", "seq"]).reset_index(drop=True)

print(df.head())
print("Total rows:", len(df))
df.to_csv("shapes.csv", index=False)
