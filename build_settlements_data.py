import csv
import json

HROMADA_CSV = "hromada_combined_v6.csv"
SETTLEMENT_CSV = "kse/data/derived/ua-admin-map.csv"
OUT_FILE = "settlements_by_hromada.json"

TYPE_CODE = {
    "місто": "м",
    "селище міського типу": "смт",
    "селище": "сщ",
    "село": "с",
}
TYPE_ORDER = {"м": 0, "смт": 1, "сщ": 2, "с": 3}


def main():
    # hromada_code -> row index, in the exact same order build_embedded_data.py
    # iterates hromada_combined_v6.csv (file order, 0-based), so this index lines
    # up with the positional "rows" array embedded in welcome.html.
    code_to_idx = {}
    with open(HROMADA_CSV, encoding="utf-8") as f:
        for i, r in enumerate(csv.DictReader(f)):
            code_to_idx[r["hromada_code"]] = i

    by_idx = {}
    with open(SETTLEMENT_CSV, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            idx = code_to_idx.get(r["hromada_code"])
            if idx is None:
                continue  # settlement belongs to a hromada outside our 1,469 (e.g. Crimea)
            t = TYPE_CODE.get(r["settlement_type"], "с")
            by_idx.setdefault(idx, []).append([r["settlement_name"], t])

    missing = set(code_to_idx.values()) - set(by_idx.keys())
    if missing:
        print(f"WARNING: {len(missing)} hromadas have no settlement rows")

    for idx, lst in by_idx.items():
        lst.sort(key=lambda x: (TYPE_ORDER.get(x[1], 9), x[0]))

    # JSON object keyed by row-index string (sparse map, keeps payload small)
    out = {str(k): v for k, v in sorted(by_idx.items())}
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))

    import os
    n_settlements = sum(len(v) for v in out.values())
    print(f"Wrote {OUT_FILE}: {len(out)} hromadas, {n_settlements} settlements, "
          f"{os.path.getsize(OUT_FILE)/1024:.1f} KB")


if __name__ == "__main__":
    main()
