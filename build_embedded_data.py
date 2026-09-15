import csv
import json

IN_FILE = "hromada_combined_v6.csv"
OUT_FILE = "hromada_embedded.json"

# compact positional schema to keep the embedded payload small
# [name, oblast, raion, lat, lon, population, urban_pct, occupied(0/1),
#  frontline_km, x1, x2, x3, x4(or null), overall, facilities]

FIELDS_ORDER = ["n","o","r","lat","lon","pop","urb","occ","fl","x1","x2","x3","x4","ov","fac"]

def main():
    with open(IN_FILE, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    out = []
    for r in rows:
        x4 = float(r["logistics_risk_score"]) if r["logistics_risk_assessed"] == "True" else None
        fac = r["documented_powerplant_facilities"].strip()
        rec = [
            r["hromada_name"],
            r["oblast_name"],
            r["raion_name"],
            round(float(r["lat_center"]), 4),
            round(float(r["lon_center"]), 4),
            int(float(r["total_popultaion_2022"])),
            round(float(r["urban_pct"]), 3) if r["urban_pct"] not in ("", "NA") else 0,
            1 if r["currently_occupied"].strip().lower() == "true" else 0,
            round(float(r["distance_to_frontline_km"]), 1),
            round(float(r["attack_risk_score"]), 4),
            round(float(r["outage_risk_proxy"]), 4),
            round(float(r["frontline_proximity_score"]), 4),
            round(x4, 3) if x4 is not None else None,
            round(float(r["overall_winter_safety_score"]), 4),
            fac if fac else None,
        ]
        out.append(rec)

    payload = {"fields": FIELDS_ORDER, "rows": out}
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))

    import os
    print(f"Wrote {OUT_FILE}, {len(out)} rows, {os.path.getsize(OUT_FILE)/1024:.1f} KB")


if __name__ == "__main__":
    main()
