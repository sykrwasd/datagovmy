import requests
import zipfile
import csv
import polyline

#installing the zip files

url = "https://api.data.gov.my/gtfs-static/prasarana?category=rapid-bus-kl"
r = requests.get(url)

with open("rapid-rail-kl.zip", "wb") as f:
    f.write(r.content)

with zipfile.ZipFile("rapid-rail-kl.zip", "r") as zip_ref:
    zip_ref.extractall("rapid-rail-kl")

# getting specific route shape
TARGET_SHAPE_ID = "T788002"

points = []

with open("rapid-rail-kl/shapes.txt", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row["shape_id"] == TARGET_SHAPE_ID:
            points.append({
                "lat": float(row["shape_pt_lat"]),
                "lon": float(row["shape_pt_lon"]),
                "seq": int(row["shape_pt_sequence"]),
            })

# GTFS requires ordering by sequence
points.sort(key=lambda p: p["seq"])


BASE_URL = "https://router.project-osrm.org/route/v1/driving"

links = []

for i in range(len(points) - 1):
    p1 = points[i]
    p2 = points[i + 1]

    link = (
        f"{BASE_URL}/"
        f"{p1['lon']},{p1['lat']};"
        f"{p2['lon']},{p2['lat']}"
        "?overview=full&geometries=geojson"
    )

    links.append({
        "from_seq": p1["seq"],
        "to_seq": p2["seq"],
        "url": link,
    })

coord = []

for l in links:
    url  = l["url"]
    
    r = requests.get(url)
    data = r.json()
    
    for lon, lat in data["routes"][0]["geometry"]["coordinates"]:
        print(lon, lat)
        
        coord.append([lon,lat])


latlon = [(lat, lon) for lon, lat in coord]

NewPolyline = polyline.encode(latlon)

oriCoord = []
for i in points:
    oriCoord.append([i["lon"], i["lat"]])
    

latlon = [(lat, lon) for lon, lat in oriCoord]

originalPolyline = polyline.encode(latlon)

print('-'*40)
print("ORIGINAL SHAPES POLYLINE ENCODED STRING")
print(originalPolyline)


print('-'*40)
print("NEW SHAPES POLYLINE ENCODED STRING")
print(NewPolyline)
