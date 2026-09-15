import csv
import json
from collections import defaultdict
import numpy as np
from sklearn.cluster import KMeans

IN_FILE = "hromada_combined_v6.csv"
OUT_JSON = "oblast_clusters.json"

# Same 22-oblast scope as Marie's original cluster_scores_and_regions.html
# (Donetsk & Luhansk excluded -- X4 logistics data was never assessed there).
EXCLUDE_OBLASTS = {"Донецька", "Луганська"}

UA_TO_EN = {
    "Черкаська": "Cherkasy", "Чернігівська": "Chernihiv", "Чернівецька": "Chernivtsi",
    "Дніпропетровська": "Dnipropetrovsk", "Івано-Франківська": "Ivano-Frankivsk",
    "Харківська": "Kharkiv", "Херсонська": "Kherson", "Хмельницька": "Khmelnytskyi",
    "Кіровоградська": "Kirovohrad", "Київська": "Kyiv", "Львівська": "Lviv",
    "Миколаївська": "Mykolaiv", "Одеська": "Odesa", "Полтавська": "Poltava",
    "Рівненська": "Rivne", "Сумська": "Sumy", "Тернопільська": "Ternopil",
    "Вінницька": "Vinnytsia", "Волинська": "Volyn", "Закарпатська": "Zakarpattia",
    "Запорізька": "Zaporizhzhia", "Житомирська": "Zhytomyr",
    "Донецька": "Donetsk", "Луганська": "Luhansk",
}

TOP5_CITY_HROMADAS = {
    ("Харківська", "Харківська"),
    ("Одеська", "Одеська"),
    ("Дніпровська", "Дніпропетровська"),
    ("Донецька", "Донецька"),
    ("Львівська", "Львівська"),
}


def main():
    with open(IN_FILE, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    by_oblast = defaultdict(list)
    for r in rows:
        by_oblast[r["oblast_name"]].append(r)

    oblast_agg = {}
    for oblast, group in by_oblast.items():
        if oblast in EXCLUDE_OBLASTS:
            continue
        pops = np.array([float(r["total_popultaion_2022"]) for r in group])
        w = pops / pops.sum()
        x1 = float((w * [float(r["attack_risk_score"]) for r in group]).sum())
        x2 = float((w * [float(r["outage_risk_proxy"]) for r in group]).sum())
        x3 = float((w * [float(r["frontline_proximity_score"]) for r in group]).sum())
        x4 = float(group[0]["logistics_risk_score"]) if group[0]["logistics_risk_assessed"] == "True" else None
        oblast_agg[oblast] = {"x1": x1, "x2": x2, "x3": x3, "x4": x4, "population": int(pops.sum())}

    oblasts = list(oblast_agg.keys())

    def rank_of(key):
        vals = sorted(oblasts, key=lambda o: oblast_agg[o][key])
        return {o: i + 1 for i, o in enumerate(vals)}  # rank 1 = lowest risk

    ranks = {k: rank_of(k) for k in ["x1", "x2", "x3", "x4"]}
    for o in oblasts:
        oblast_agg[o]["rank_x1"] = ranks["x1"][o]
        oblast_agg[o]["rank_x2"] = ranks["x2"][o]
        oblast_agg[o]["rank_x3"] = ranks["x3"][o]
        oblast_agg[o]["rank_x4"] = ranks["x4"][o]
        oblast_agg[o]["composite_rank"] = round(
            (ranks["x1"][o] + ranks["x2"][o] + ranks["x3"][o] + ranks["x4"][o]) / 4, 1
        )

    # K-means (k=3) on the 4 rank columns -- same scale (1..22) for all variables,
    # matches the rank-based composite score shown on the cards.
    X = np.array([[oblast_agg[o]["rank_x1"], oblast_agg[o]["rank_x2"],
                    oblast_agg[o]["rank_x3"], oblast_agg[o]["rank_x4"]] for o in oblasts])
    km = KMeans(n_clusters=3, random_state=42, n_init=10).fit(X)

    # order cluster ids by mean composite rank ascending -> safest first
    cluster_means = {}
    for cid in range(3):
        members = [o for o, lab in zip(oblasts, km.labels_) if lab == cid]
        cluster_means[cid] = np.mean([oblast_agg[o]["composite_rank"] for o in members])
    order = sorted(cluster_means, key=lambda c: cluster_means[c])
    names = ["Completely Safe", "Somewhat Safe", "Not Safe at all"]
    cid_to_name = {cid: names[i] for i, cid in enumerate(order)}

    clusters = {name: [] for name in names}
    for o, lab in zip(oblasts, km.labels_):
        clusters[cid_to_name[lab]].append(o)

    result = {"clusters": {}, "top5_cities": []}
    for name in names:
        members = sorted(clusters[name], key=lambda o: oblast_agg[o]["composite_rank"])
        result["clusters"][name] = {
            "n": len(members),
            "composite_avg": round(np.mean([oblast_agg[o]["composite_rank"] for o in members]), 1),
            "attack_pct_avg": round(100 * np.mean([oblast_agg[o]["x1"] for o in members]), 1),
            "attack_rank_avg": round(np.mean([oblast_agg[o]["rank_x1"] for o in members]), 1),
            "outage_avg": round(np.mean([oblast_agg[o]["x2"] for o in members]), 3),
            "outage_rank_avg": round(np.mean([oblast_agg[o]["rank_x2"] for o in members]), 1),
            "border_avg": round(np.mean([oblast_agg[o]["x3"] for o in members]), 3),
            "border_rank_avg": round(np.mean([oblast_agg[o]["rank_x3"] for o in members]), 1),
            "logistics_avg": round(np.mean([oblast_agg[o]["x4"] for o in members]), 3),
            "logistics_rank_avg": round(np.mean([oblast_agg[o]["rank_x4"] for o in members]), 1),
            "members_en": [UA_TO_EN.get(o, o) for o in members],
        }

    top5 = [r for r in rows if (r["hromada_name"], r["oblast_name"]) in TOP5_CITY_HROMADAS]
    top5 = sorted(top5, key=lambda r: -float(r["total_popultaion_2022"]))
    for r in top5:
        oblast = r["oblast_name"]
        result["top5_cities"].append({
            "hromada": r["hromada_name"],
            "oblast_en": UA_TO_EN.get(oblast, oblast),
            "population": int(float(r["total_popultaion_2022"])),
            "overall_score": round(float(r["overall_winter_safety_score"]), 3),
            "oblast_cluster": next((n for n in names if oblast in clusters[n]), "Donetsk/Luhansk (excluded)"),
            "x1": round(float(r["attack_risk_score"]), 3),
            "x2": round(float(r["outage_risk_proxy"]), 3),
            "x3": round(float(r["frontline_proximity_score"]), 3),
            "x4": r["logistics_risk_score"] if r["logistics_risk_assessed"] == "True" else None,
        })

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
