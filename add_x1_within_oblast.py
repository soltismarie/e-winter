import csv
import math
from collections import defaultdict

ACLED_FILE = "/mnt/user-data/uploads/Winter Safe/ACLED Data_2026-09-09_event_date_from_2025-01-01_event_date_to_2026-09-04 (1).csv"
HROMADA_FILE = "hromada_combined_v3.csv"
OUT_FILE = "hromada_combined_v4.csv"

RECENT_WEEKS = 8

# ACLED reports two sub-event types we use for X1. They behave differently in
# space, so they get different within-oblast disaggregation weights:
#  - Shelling/artillery/missile attack: short-range, so it should concentrate
#    almost entirely on hromadas close to the front line (exponential decay).
#  - Air/drone strike: long-range, tends to target cities/population/
#    infrastructure regardless of front-line distance (population-weighted).
SHELLING_TYPE = "Shelling/artillery/missile attack"
AIRDRONE_TYPE = "Air/drone strike"

SHELLING_DECAY_KM = 30.0  # weight halves roughly every ~21km beyond the line
OCCUPIED_EFFECTIVE_DIST_KM = 0.0  # treat occupied hromadas as on the line for shelling exposure

OBLAST_MAP = {
    "Cherkasy": "Черкаська", "Chernihiv": "Чернігівська", "Chernivtsi": "Чернівецька",
    "Dnipropetrovsk": "Дніпропетровська", "Donetsk": "Донецька", "Ivano-Frankivsk": "Івано-Франківська",
    "Kharkiv": "Харківська", "Kherson": "Херсонська", "Khmelnytskyi": "Хмельницька",
    "Kirovohrad": "Кіровоградська", "Kyiv": "Київська", "Luhansk": "Луганська",
    "Lviv": "Львівська", "Mykolaiv": "Миколаївська", "Odesa": "Одеська",
    "Poltava": "Полтавська", "Rivne": "Рівненська", "Sumy": "Сумська",
    "Ternopil": "Тернопільська", "Vinnytsia": "Вінницька", "Volyn": "Волинська",
    "Zakarpattia": "Закарпатська", "Zaporizhia": "Запорізька", "Zhytomyr": "Житомирська",
}


def main():
    with open(ACLED_FILE, encoding="utf-8-sig") as f:
        acled_rows = list(csv.DictReader(f))
    all_weeks = sorted({r["week"] for r in acled_rows})
    recent_weeks = set(all_weeks[-RECENT_WEEKS:])

    # oblast totals per sub-event type, both windows
    shelling_recent, shelling_alltime = defaultdict(int), defaultdict(int)
    airdrone_recent, airdrone_alltime = defaultdict(int), defaultdict(int)
    for r in acled_rows:
        oblast_ua = OBLAST_MAP.get(r["admin1"])
        if not oblast_ua:
            continue
        n = int(r["events"])
        if r["sub_event_type"] == SHELLING_TYPE:
            shelling_alltime[oblast_ua] += n
            if r["week"] in recent_weeks:
                shelling_recent[oblast_ua] += n
        elif r["sub_event_type"] == AIRDRONE_TYPE:
            airdrone_alltime[oblast_ua] += n
            if r["week"] in recent_weeks:
                airdrone_recent[oblast_ua] += n

    with open(HROMADA_FILE, encoding="utf-8") as f:
        hromadas = list(csv.DictReader(f))

    by_oblast = defaultdict(list)
    for h in hromadas:
        by_oblast[h["oblast_name"]].append(h)

    def shelling_weight(h):
        occupied = h["currently_occupied"].strip().lower() == "true"
        dist = OCCUPIED_EFFECTIVE_DIST_KM if occupied else float(h["distance_to_frontline_km"])
        return math.exp(-dist / SHELLING_DECAY_KM)

    def airdrone_weight(h):
        pop = float(h["total_popultaion_2022"])
        urban = float(h["urban_pct"]) if h["urban_pct"] not in ("", "NA") else 0.0
        return pop * (0.5 + 0.5 * urban)

    for oblast, group in by_oblast.items():
        sh_weights = {id(h): shelling_weight(h) for h in group}
        ad_weights = {id(h): airdrone_weight(h) for h in group}
        sh_total = sum(sh_weights.values()) or 1.0
        ad_total = sum(ad_weights.values()) or 1.0

        sh_recent_o = shelling_recent.get(oblast, 0)
        sh_all_o = shelling_alltime.get(oblast, 0)
        ad_recent_o = airdrone_recent.get(oblast, 0)
        ad_all_o = airdrone_alltime.get(oblast, 0)

        for h in group:
            sh_share = sh_weights[id(h)] / sh_total
            ad_share = ad_weights[id(h)] / ad_total

            h["hromada_shelling_events_last8wk"] = round(sh_recent_o * sh_share, 2)
            h["hromada_shelling_events_since_2025"] = round(sh_all_o * sh_share, 2)
            h["hromada_airdrone_events_last8wk"] = round(ad_recent_o * ad_share, 2)
            h["hromada_airdrone_events_since_2025"] = round(ad_all_o * ad_share, 2)
            h["hromada_attack_events_last8wk"] = round(
                sh_recent_o * sh_share + ad_recent_o * ad_share, 2
            )
            h["hromada_attack_events_since_2025"] = round(
                sh_all_o * sh_share + ad_all_o * ad_share, 2
            )

    # normalized 0-1 attack risk score, min-max over the new hromada-level total
    vals = [h["hromada_attack_events_since_2025"] for h in hromadas]
    vmin, vmax = min(vals), max(vals)
    for h in hromadas:
        v = h["hromada_attack_events_since_2025"]
        h["attack_risk_score"] = round((v - vmin) / (vmax - vmin), 4) if vmax > vmin else 0.0

    fieldnames = list(hromadas[0].keys())
    with open(OUT_FILE, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(hromadas)

    print(f"Wrote {OUT_FILE} with {len(hromadas)} rows")

    # sanity check: does per-oblast sum reproduce the old oblast-level total?
    check = defaultdict(float)
    for h in hromadas:
        check[h["oblast_name"]] += h["hromada_attack_events_since_2025"]
    print("\nConservation check (should match old oblast_attack_events_since_2025):")
    sample = sorted(check.items(), key=lambda x: -x[1])[:5]
    for oblast, total in sample:
        old = next(h["oblast_attack_events_since_2025"] for h in hromadas if h["oblast_name"] == oblast)
        print(f"  {oblast:18s} disaggregated_sum={total:10.1f}  old_oblast_value={old}")

    print("\nWithin-oblast spread example -- Запорізька (highest-attack oblast), top 8 hromadas:")
    zap = sorted([h for h in hromadas if h["oblast_name"] == "Запорізька"],
                 key=lambda h: -h["hromada_attack_events_since_2025"])[:8]
    for h in zap:
        print(f"  {h['hromada_name']:20s} events={h['hromada_attack_events_since_2025']:9.1f}  "
              f"dist_frontline={h['distance_to_frontline_km']:>7s}km  pop={h['total_popultaion_2022']}")


if __name__ == "__main__":
    main()
