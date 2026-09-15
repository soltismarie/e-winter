import csv
from collections import defaultdict

ACLED_FILE = "/mnt/user-data/uploads/Winter Safe/ACLED Data_2026-09-09_event_date_from_2025-01-01_event_date_to_2026-09-04 (1).csv"
HROMADA_FILE = "hromada_combined_v1.csv"
OUT_FILE = "hromada_combined_v2.csv"

RECENT_WEEKS = 8  # ~2 months, most recent
ATTACK_SUBTYPES = {"Air/drone strike", "Shelling/artillery/missile attack"}

# English (ACLED) -> Ukrainian adjectival oblast name (matches KSE geography.csv oblast_name)
OBLAST_MAP = {
    "Cherkasy": "Черкаська",
    "Chernihiv": "Чернігівська",
    "Chernivtsi": "Чернівецька",
    "Dnipropetrovsk": "Дніпропетровська",
    "Donetsk": "Донецька",
    "Ivano-Frankivsk": "Івано-Франківська",
    "Kharkiv": "Харківська",
    "Kherson": "Херсонська",
    "Khmelnytskyi": "Хмельницька",
    "Kirovohrad": "Кіровоградська",
    "Kyiv": "Київська",
    "Luhansk": "Луганська",
    "Lviv": "Львівська",
    "Mykolaiv": "Миколаївська",
    "Odesa": "Одеська",
    "Poltava": "Полтавська",
    "Rivne": "Рівненська",
    "Sumy": "Сумська",
    "Ternopil": "Тернопільська",
    "Vinnytsia": "Вінницька",
    "Volyn": "Волинська",
    "Zakarpattia": "Закарпатська",
    "Zaporizhia": "Запорізька",
    "Zhytomyr": "Житомирська",
    # Not mapped to any hromada oblast (occupied/city-level, no matching row): Crimea, Kyiv City, Wider Black Sea Region
}


def main():
    with open(ACLED_FILE, encoding="utf-8-sig") as f:
        acled_rows = list(csv.DictReader(f))

    all_weeks = sorted({r["week"] for r in acled_rows})
    recent_weeks = set(all_weeks[-RECENT_WEEKS:])
    print(f"ACLED weeks available: {all_weeks[0]} to {all_weeks[-1]} ({len(all_weeks)} weeks)")
    print(f"Using most recent {RECENT_WEEKS} weeks: {sorted(recent_weeks)}")

    events_recent = defaultdict(int)
    events_all_time = defaultdict(int)
    for r in acled_rows:
        if r["sub_event_type"] not in ATTACK_SUBTYPES:
            continue
        oblast_ua = OBLAST_MAP.get(r["admin1"])
        if not oblast_ua:
            continue
        n = int(r["events"])
        events_all_time[oblast_ua] += n
        if r["week"] in recent_weeks:
            events_recent[oblast_ua] += n

    with open(HROMADA_FILE, encoding="utf-8") as f:
        hromadas = list(csv.DictReader(f))

    for h in hromadas:
        oblast = h["oblast_name"]
        h["oblast_attack_events_last8wk"] = events_recent.get(oblast, 0)
        h["oblast_attack_events_since_2025"] = events_all_time.get(oblast, 0)
        h["attacks_as_of_week"] = all_weeks[-1]

    fieldnames = list(hromadas[0].keys())
    with open(OUT_FILE, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(hromadas)

    print(f"\nWrote {OUT_FILE} with {len(hromadas)} rows")
    print("\nOblast attack-event totals, last 8 weeks (air/drone strikes + shelling/artillery/missile attacks):")
    for oblast, n in sorted(events_recent.items(), key=lambda x: -x[1]):
        print(f"  {oblast:20s} {n:5d}")


if __name__ == "__main__":
    main()
