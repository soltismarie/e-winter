import csv
from collections import defaultdict

HROMADA_FILE = "hromada_combined_v2.csv"
DAMAGE_FILE = "documented_powerplant_damage.csv"
OUT_FILE = "hromada_combined_v3.csv"

# Marie's confirmed weights (2026-09-09): 20% strike history + 75% documented
# power-plant damage + 5% front-line/occupation flag. Sums to 100%, used as-is.
W_STRIKES = 0.20
W_DAMAGE = 0.75
W_FRONTLINE = 0.05

# Discount applied to a hromada that does NOT host a documented facility itself
# but sits in the same oblast as one that does -- represents cascading/regional
# outage risk from grid damage upstream, rather than treating 1,454 of 1,469
# hromadas as flat zero on the highest-weighted (75%) component. This is a
# suggested addition on top of what Marie specified -- see note to her.
OBLAST_CASCADE_DISCOUNT = 0.4

STATUS_SEVERITY = {
    "destroyed": 3,
    "occupied/destroyed": 3,
    "damaged": 2,
    "damaged/front-line": 2,
    "occupied/at-risk": 2,
    "at-risk": 1,
}

FRONTLINE_ADJACENT_KM = 10.0


def main():
    with open(DAMAGE_FILE, encoding="utf-8") as f:
        damage_rows = list(csv.DictReader(f))

    severity_by_hromada = {}
    facilities_by_hromada = defaultdict(list)
    severity_by_oblast = defaultdict(int)
    facilities_by_oblast = defaultdict(list)
    unmatched = []

    for r in damage_rows:
        code = r["hromada_code"].strip()
        oblast = r["oblast_name"].strip()
        sev = STATUS_SEVERITY.get(r["status"], 0)

        if oblast:
            facilities_by_oblast[oblast].append(r["facility_name"])
            if sev > severity_by_oblast[oblast]:
                severity_by_oblast[oblast] = sev

        if not code:
            unmatched.append(r["facility_name"])
            continue

        facilities_by_hromada[code].append(r["facility_name"])
        if sev > severity_by_hromada.get(code, 0):
            severity_by_hromada[code] = sev

    with open(HROMADA_FILE, encoding="utf-8") as f:
        hromadas = list(csv.DictReader(f))

    strike_vals = [int(h["oblast_attack_events_since_2025"]) for h in hromadas]
    smin, smax = min(strike_vals), max(strike_vals)

    for h in hromadas:
        code = h["hromada_code"]
        oblast = h["oblast_name"]

        host_sev = severity_by_hromada.get(code, 0)
        oblast_sev = severity_by_oblast.get(oblast, 0)

        if host_sev > 0:
            dmg_sev = host_sev
            dmg_basis = "hosts_facility"
        elif oblast_sev > 0:
            dmg_sev = OBLAST_CASCADE_DISCOUNT * oblast_sev
            dmg_basis = "oblast_cascade"
        else:
            dmg_sev = 0
            dmg_basis = "none"
        dmg_norm = dmg_sev / 3.0

        strikes = int(h["oblast_attack_events_since_2025"])
        strike_norm = (strikes - smin) / (smax - smin) if smax > smin else 0.0

        occupied = h["currently_occupied"].strip().lower() == "true"
        try:
            dist = float(h["distance_to_frontline_km"])
        except ValueError:
            dist = 9999.0
        frontline_flag = 1.0 if (occupied or dist <= FRONTLINE_ADJACENT_KM) else 0.0

        outage_risk_proxy = (
            W_STRIKES * strike_norm + W_DAMAGE * dmg_norm + W_FRONTLINE * frontline_flag
        )

        h["documented_powerplant_damage_score"] = round(dmg_sev, 3)
        h["documented_powerplant_damage_basis"] = dmg_basis
        h["documented_powerplant_facilities"] = "; ".join(facilities_by_hromada.get(code, []))
        h["oblast_documented_facilities"] = "; ".join(facilities_by_oblast.get(oblast, []))
        h["frontline_occupation_flag"] = int(frontline_flag)
        h["outage_strike_component_norm"] = round(strike_norm, 4)
        h["outage_risk_proxy"] = round(outage_risk_proxy, 4)

    fieldnames = list(hromadas[0].keys())
    with open(OUT_FILE, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(hromadas)

    print(f"Wrote {OUT_FILE} with {len(hromadas)} rows")
    print(f"Hromadas hosting a documented facility: {len(severity_by_hromada)}")
    print(f"Hromadas getting oblast-cascade damage score: "
          f"{sum(1 for h in hromadas if h['documented_powerplant_damage_basis']=='oblast_cascade')}")
    print(f"Hromadas with zero damage signal: "
          f"{sum(1 for h in hromadas if h['documented_powerplant_damage_basis']=='none')}")
    print(f"Documented facilities with NO hromada match: {unmatched}")

    print("\nTop 20 hromadas by outage_risk_proxy:")
    top = sorted(hromadas, key=lambda h: -h["outage_risk_proxy"])[:20]
    for h in top:
        print(f"  {h['hromada_name']:22s} {h['oblast_name']:15s} score={h['outage_risk_proxy']:.3f}  "
              f"dmg={h['documented_powerplant_damage_score']}({h['documented_powerplant_damage_basis']})  "
              f"frontline={h['frontline_occupation_flag']}  strikes_norm={h['outage_strike_component_norm']}")


if __name__ == "__main__":
    main()
