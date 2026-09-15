import csv

IN_FILE = "hromada_combined_v5.csv"
OUT_FILE = "hromada_combined_v6.csv"

# Same decay scale used for X1's shelling component, for methodological
# consistency: risk falls off sharply within ~30km of the front line and is
# negligible past ~150-200km. Occupied hromadas are treated as maximum
# border/front-line risk outright (distance-to-boundary is ambiguous once
# you're already inside occupied territory).
FRONTLINE_DECAY_KM = 30.0


def frontline_proximity_score(h):
    if h["currently_occupied"].strip().lower() == "true":
        return 1.0
    dist = float(h["distance_to_frontline_km"])
    import math
    return math.exp(-dist / FRONTLINE_DECAY_KM)


def main():
    with open(IN_FILE, encoding="utf-8") as f:
        hromadas = list(csv.DictReader(f))

    for h in hromadas:
        x1 = float(h["attack_risk_score"])
        x2 = float(h["outage_risk_proxy"])
        x3 = frontline_proximity_score(h)
        x4_assessed = h["logistics_risk_assessed"].strip() == "True"
        x4 = float(h["logistics_risk_score"]) if x4_assessed else None

        components = [x1, x2, x3] + ([x4] if x4_assessed else [])
        overall = sum(components) / len(components)

        h["frontline_proximity_score"] = round(x3, 4)
        h["overall_winter_safety_score"] = round(overall, 4)
        h["overall_score_components_used"] = f"{len(components)}/4" + ("" if x4_assessed else " (X4 unassessed)")

    fieldnames = list(hromadas[0].keys())
    with open(OUT_FILE, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(hromadas)

    print(f"Wrote {OUT_FILE} with {len(hromadas)} rows")
    print(f"Hromadas scored on all 4 variables: {sum(1 for h in hromadas if '4/4' in h['overall_score_components_used'])}")
    print(f"Hromadas scored on 3 (X4 unassessed): {sum(1 for h in hromadas if '3/4' in h['overall_score_components_used'])}")

    print("\nTop 15 HIGHEST winter-safety risk hromadas:")
    worst = sorted(hromadas, key=lambda h: -h["overall_winter_safety_score"])[:15]
    for h in worst:
        print(f"  {h['hromada_name']:20s} {h['oblast_name']:15s} overall={h['overall_winter_safety_score']:.3f}  "
              f"X1={h['attack_risk_score']}  X2={h['outage_risk_proxy']}  X3={h['frontline_proximity_score']}  "
              f"X4={h['logistics_risk_score'] or 'NA':>4}  [{h['overall_score_components_used']}]")

    print("\nTop 15 LOWEST winter-safety risk hromadas (candidate 'green cluster' pool):")
    best = sorted(hromadas, key=lambda h: h["overall_winter_safety_score"])[:15]
    for h in best:
        print(f"  {h['hromada_name']:20s} {h['oblast_name']:15s} overall={h['overall_winter_safety_score']:.3f}  "
              f"X1={h['attack_risk_score']}  X2={h['outage_risk_proxy']}  X3={h['frontline_proximity_score']}  "
              f"X4={h['logistics_risk_score'] or 'NA':>4}  [{h['overall_score_components_used']}]")


if __name__ == "__main__":
    main()
