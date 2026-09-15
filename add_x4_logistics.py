import csv

HROMADA_FILE = "hromada_combined_v4.csv"
LOGISTICS_FILE = "/mnt/user-data/uploads/Winter Safe/logistics_risk_dataset.csv"
OUT_FILE = "hromada_combined_v5.csv"

# English (Marie's logistics table) -> Ukrainian oblast name matching hromada_combined
OBLAST_MAP = {
    "Cherkasy": "Черкаська", "Chernihiv": "Чернігівська", "Chernivtsi": "Чернівецька",
    "Dnipropetrovsk": "Дніпропетровська", "Ivano-Frankivsk": "Івано-Франківська",
    "Kharkiv": "Харківська", "Kherson": "Херсонська", "Khmelnytskyi": "Хмельницька",
    "Kirovohrad": "Кіровоградська", "Kyiv": "Київська", "Lviv": "Львівська",
    "Mykolaiv": "Миколаївська", "Odesa": "Одеська", "Poltava": "Полтавська",
    "Rivne": "Рівненська", "Sumy": "Сумська", "Ternopil": "Тернопільська",
    "Vinnytsia": "Вінницька", "Volyn": "Волинська", "Zakarpattia": "Закарпатська",
    "Zaporizhzhia": "Запорізька", "Zhytomyr": "Житомирська",
    # Donetsk, Luhansk not in Marie's source review -- left unassessed, not zero
}


def main():
    with open(LOGISTICS_FILE, encoding="utf-8-sig") as f:
        logi_rows = list(csv.DictReader(f))

    by_oblast = {}
    for r in logi_rows:
        oblast_ua = OBLAST_MAP.get(r["oblast"].strip())
        if not oblast_ua:
            print(f"WARNING: no mapping for oblast '{r['oblast']}'")
            continue
        by_oblast[oblast_ua] = r

    with open(HROMADA_FILE, encoding="utf-8") as f:
        hromadas = list(csv.DictReader(f))

    n_assessed, n_unassessed = 0, 0
    for h in hromadas:
        rec = by_oblast.get(h["oblast_name"])
        if rec:
            h["logistics_risk_score"] = rec["logistics_risk_score"]
            h["logistics_risk_assessed"] = "True"
            h["logistics_risk_rationale"] = rec["rationale"]
            h["logistics_risk_source"] = rec["source"]
            n_assessed += 1
        else:
            h["logistics_risk_score"] = ""
            h["logistics_risk_assessed"] = "False"
            h["logistics_risk_rationale"] = "Not reviewed in source reporting (Donetsk/Luhansk excluded from Marie's 2-source review)"
            h["logistics_risk_source"] = ""
            n_unassessed += 1

    fieldnames = list(hromadas[0].keys())
    with open(OUT_FILE, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(hromadas)

    print(f"Wrote {OUT_FILE} with {len(hromadas)} rows")
    print(f"Hromadas with an assessed oblast (score, incl. 0.0): {n_assessed}")
    print(f"Hromadas with NO assessment (Donetsk/Luhansk oblasts): {n_unassessed}")
    print("\nDistinct oblast-level logistics_risk_score values used:")
    seen = set()
    for h in sorted(hromadas, key=lambda h: -float(h["logistics_risk_score"] or -1)):
        key = (h["oblast_name"], h["logistics_risk_score"])
        if key not in seen and h["logistics_risk_assessed"] == "True":
            seen.add(key)
            print(f"  {h['oblast_name']:18s} score={h['logistics_risk_score']:>4s}  {h['logistics_risk_rationale']}")


if __name__ == "__main__":
    main()
