import csv
import json

HROMADA_CSV = "hromada_combined_v6.csv"
SCHOOLS_CSV = "kse/data/derived/matched_schools.csv"
OUT_FILE = "schools_by_hromada.json"


def main():
    code_to_idx = {}
    with open(HROMADA_CSV, encoding="utf-8") as f:
        for i, r in enumerate(csv.DictReader(f)):
            code_to_idx[r["hromada_code"]] = i

    # EDEBO school registry (via KSE-Loc-Data-Hub). Working (status == "працює")
    # rows, trusted by hromada_code directly. NOTE: we deliberately do NOT filter
    # on match_status_koatuu=="matched" -- checked and that flag fails almost
    # entirely for big-city hromadas (e.g. Kharkiv city: 232 of 233 schools flagged
    # "unmatched" despite carrying a correct, valid hromada_code that lines up
    # exactly with our own hromada_combined_v6.csv codes) while still being
    # correct for small rural hromadas -- so trusting it would have silently
    # undercounted every major city to near zero. hromada_code itself checks out.
    # This registry covers general secondary schools (школа/ліцей/гімназія/etc.)
    # -- it does NOT include preschools/kindergartens (дошкільна освіта), which
    # is a real gap we surface honestly in the UI.
    counts = {}
    with open(SCHOOLS_CSV, encoding="cp1251") as f:
        for r in csv.DictReader(f):
            if r["status"] != "працює":
                continue
            idx = code_to_idx.get(r["hromada_code"])
            if idx is None:
                continue
            counts[idx] = counts.get(idx, 0) + 1

    out = {str(k): v for k, v in sorted(counts.items())}
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))

    import os
    print(f"Wrote {OUT_FILE}: {len(out)} hromadas with school counts, "
          f"{sum(out.values())} schools total, {os.path.getsize(OUT_FILE)/1024:.1f} KB")


if __name__ == "__main__":
    main()
