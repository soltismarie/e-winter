import json
import csv
import math
from shapely.geometry import shape, Point
from shapely.ops import nearest_points

DEEPSTATE_FILE = "deepstate/data/deepstatemap_data_20260909.geojson"
GEOGRAPHY_CSV = "kse/data/derived/geography.csv"
OUT_CSV = "hromada_frontline_distance.csv"


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0088  # mean Earth radius, km
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def main():
    with open(DEEPSTATE_FILE, encoding="utf-8") as f:
        gj = json.load(f)
    occupied = shape(gj["features"][0]["geometry"])
    occupied_boundary = occupied.boundary
    print(f"Loaded occupied-territory geometry as of 2026-09-09, valid={occupied.is_valid}")

    rows_out = []
    with open(GEOGRAPHY_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            try:
                lat = float(row["lat_center"])
                lon = float(row["lon_center"])
            except (ValueError, KeyError):
                continue
            pt = Point(lon, lat)  # shapely uses (x=lon, y=lat)
            is_occupied = occupied.contains(pt)
            _, nearest_on_boundary = nearest_points(pt, occupied_boundary)
            dist_km = haversine_km(lat, lon, nearest_on_boundary.y, nearest_on_boundary.x)
            rows_out.append({
                "hromada_code": row["hromada_code"],
                "hromada": row["hromada"],
                "oblast_name": row["oblast_name"],
                "raion_name": row["raion_name"],
                "lat_center": lat,
                "lon_center": lon,
                "distance_to_frontline_km": round(dist_km, 1),
                "currently_occupied": is_occupied,
                "as_of_date": "2026-09-09",
            })
            if (i + 1) % 200 == 0:
                print(f"  processed {i + 1} hromadas...")

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows_out[0].keys()))
        writer.writeheader()
        writer.writerows(rows_out)

    print(f"Done. Wrote {len(rows_out)} hromadas to {OUT_CSV}")
    dists = [r["distance_to_frontline_km"] for r in rows_out if not r["currently_occupied"]]
    occ_count = sum(1 for r in rows_out if r["currently_occupied"])
    print(f"Currently-occupied hromada centers: {occ_count}")
    print(f"Distance range (non-occupied): {min(dists):.1f} km to {max(dists):.1f} km")


if __name__ == "__main__":
    main()
