import csv
import json
import random
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
PAPER = ROOT / "paper"
OUT_CSV = DOCS / "v2_event_reliability_stress_summary.csv"
OUT_JSON = DOCS / "v2_event_reliability_stress.json"
OUT_TEX = PAPER / "v2_event_reliability_table.tex"


METHODS = ("delayed_reward_td", "dense_shaping", "effect_trace")
METHOD_LABELS = {
    "delayed_reward_td": "Delayed reward TD",
    "dense_shaping": "Dense shaping proxy",
    "effect_trace": "Effect trace credit",
}


SCENARIOS = [
    {
        "scenario": "reliable_events",
        "trace_quality": 0.86,
        "proxy_conflict": 0.35,
        "event_coverage": 0.95,
        "false_event_rate": 0.02,
        "misbinding_rate": 0.02,
    },
    {
        "scenario": "missed_events",
        "trace_quality": 0.72,
        "proxy_conflict": 0.35,
        "event_coverage": 0.45,
        "false_event_rate": 0.06,
        "misbinding_rate": 0.08,
    },
    {
        "scenario": "misbound_events",
        "trace_quality": 0.74,
        "proxy_conflict": 0.35,
        "event_coverage": 0.75,
        "false_event_rate": 0.15,
        "misbinding_rate": 0.45,
    },
    {
        "scenario": "adversarial_events",
        "trace_quality": 0.62,
        "proxy_conflict": 0.35,
        "event_coverage": 0.35,
        "false_event_rate": 0.35,
        "misbinding_rate": 0.60,
    },
]


def clamp(value, lo, hi):
    return min(hi, max(lo, value))


def evaluate_row(rng, scenario, episode):
    delay = rng.randint(2, 12)
    trace_quality = clamp(rng.gauss(scenario["trace_quality"], 0.08), 0.02, 0.98)
    proxy_conflict = clamp(rng.gauss(scenario["proxy_conflict"], 0.10), 0.02, 0.98)
    coverage = clamp(rng.gauss(scenario["event_coverage"], 0.06), 0.01, 1.0)
    false_rate = clamp(rng.gauss(scenario["false_event_rate"], 0.04), 0.0, 0.95)
    misbinding = clamp(rng.gauss(scenario["misbinding_rate"], 0.05), 0.0, 0.95)
    rows = []
    for method in METHODS:
        noise = rng.gauss(0.0, 0.055)
        if method == "delayed_reward_td":
            localization_error = 1.45 + 0.30 * delay + 0.28 * proxy_conflict + noise
            precision = 0.42 - 0.015 * delay - 0.04 * proxy_conflict + rng.gauss(0.0, 0.025)
            success_lift = 0.11 - 0.012 * delay - 0.03 * proxy_conflict + rng.gauss(0.0, 0.018)
            reward_dependence = 1.0
        elif method == "dense_shaping":
            localization_error = 0.86 + 0.18 * delay + 1.15 * proxy_conflict - 0.16 * trace_quality + noise
            precision = 0.52 + 0.08 * trace_quality - 0.30 * proxy_conflict - 0.007 * delay + rng.gauss(0.0, 0.025)
            success_lift = 0.18 + 0.02 * trace_quality - 0.09 * proxy_conflict - 0.006 * delay + rng.gauss(0.0, 0.018)
            reward_dependence = 0.55
        else:
            localization_error = (
                0.25
                + 0.055 * delay
                + 0.18 * proxy_conflict
                + 0.70 * (1.0 - trace_quality)
                + 1.90 * (1.0 - coverage)
                + 1.70 * false_rate
                + 2.40 * misbinding
                + noise
            )
            precision = (
                0.90
                + 0.09 * trace_quality
                - 0.30 * (1.0 - coverage)
                - 0.55 * false_rate
                - 0.70 * misbinding
                - 0.003 * delay
                + rng.gauss(0.0, 0.022)
            )
            success_lift = (
                0.31
                + 0.04 * trace_quality
                - 0.10 * (1.0 - coverage)
                - 0.12 * false_rate
                - 0.18 * misbinding
                - 0.002 * delay
                + rng.gauss(0.0, 0.014)
            )
            reward_dependence = 0.0
        rows.append(
            {
                "scenario": scenario["scenario"],
                "episode": episode,
                "method": method,
                "delay_steps": delay,
                "trace_quality": round(trace_quality, 4),
                "event_coverage": round(coverage, 4),
                "false_event_rate": round(false_rate, 4),
                "misbinding_rate": round(misbinding, 4),
                "proxy_conflict": round(proxy_conflict, 4),
                "localization_error": round(max(0.01, localization_error), 4),
                "counterfactual_precision": round(clamp(precision, 0.01, 0.99), 4),
                "success_lift": round(clamp(success_lift, -0.10, 0.45), 4),
                "reward_dependence": reward_dependence,
            }
        )
    return rows


def aggregate(rows):
    groups = defaultdict(lambda: {"n": 0, "localization_error": 0.0, "counterfactual_precision": 0.0, "success_lift": 0.0, "reward_dependence": 0.0})
    for row in rows:
        key = (row["scenario"], row["method"])
        groups[key]["n"] += 1
        for metric in ("localization_error", "counterfactual_precision", "success_lift", "reward_dependence"):
            groups[key][metric] += float(row[metric])

    summary = []
    for scenario in [s["scenario"] for s in SCENARIOS]:
        scenario_rows = []
        for method in METHODS:
            group = groups[(scenario, method)]
            n = group["n"]
            item = {
                "scenario": scenario,
                "method": method,
                "method_label": METHOD_LABELS[method],
                "n": n,
                "localization_error": group["localization_error"] / n,
                "counterfactual_precision": group["counterfactual_precision"] / n,
                "success_lift": group["success_lift"] / n,
                "reward_dependence": group["reward_dependence"] / n,
            }
            summary.append(item)
            scenario_rows.append(item)
        best = min(scenario_rows, key=lambda r: r["localization_error"])
        for item in scenario_rows:
            item["best_by_error"] = best["method"]
            item["effect_trace_wins"] = best["method"] == "effect_trace"
    return summary


def main():
    DOCS.mkdir(exist_ok=True)
    PAPER.mkdir(exist_ok=True)
    rng = random.Random(540542)
    rows = []
    for scenario in SCENARIOS:
        for episode in range(480):
            rows.extend(evaluate_row(rng, scenario, episode))
    summary = aggregate(rows)

    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary[0].keys()))
        writer.writeheader()
        writer.writerows(summary)

    OUT_JSON.write_text(
        json.dumps(
            {
                "decision": "workshop-only",
                "reason": "Effect-trace credit is useful only when event traces have adequate coverage and binding accuracy.",
                "scenario_parameters": SCENARIOS,
                "summary": summary,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    selected = [row for row in summary if row["method"] in {"dense_shaping", "effect_trace"}]
    table_lines = []
    for scenario in [s["scenario"] for s in SCENARIOS]:
        dense = next(row for row in selected if row["scenario"] == scenario and row["method"] == "dense_shaping")
        effect = next(row for row in selected if row["scenario"] == scenario and row["method"] == "effect_trace")
        table_lines.append(
            f"{scenario.replace('_', ' ')} & {dense['localization_error']:.3f} & {effect['localization_error']:.3f} & "
            f"{effect['counterfactual_precision']:.3f} & {effect['best_by_error'].replace('_', ' ')} \\\\"
        )

    OUT_TEX.write_text(
        "\n".join(
            [
                r"\begin{tabular}{lrrrr}",
                r"\toprule",
                r"Event regime & Dense error & Trace error & Trace precision & Best \\",
                r"\midrule",
                *table_lines,
                r"\bottomrule",
                r"\end{tabular}",
                "",
            ]
        ),
        encoding="utf-8",
    )

    for scenario in [s["scenario"] for s in SCENARIOS]:
        items = [row for row in summary if row["scenario"] == scenario]
        effect = next(row for row in items if row["method"] == "effect_trace")
        dense = next(row for row in items if row["method"] == "dense_shaping")
        td = next(row for row in items if row["method"] == "delayed_reward_td")
        print(
            scenario,
            f"effect={effect['localization_error']:.3f}",
            f"dense={dense['localization_error']:.3f}",
            f"td={td['localization_error']:.3f}",
            f"best={effect['best_by_error']}",
        )


if __name__ == "__main__":
    main()
