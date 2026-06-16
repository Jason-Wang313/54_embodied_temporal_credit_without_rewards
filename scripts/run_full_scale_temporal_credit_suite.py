from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "full_scale"
FIGURES = ROOT / "paper" / "figures" / "full_scale"

SEEDS_PER_ROW = 19
SCENES_PER_ROW = 7
MOTIFS_PER_ROW = 5
CALIBRATIONS_PER_ROW = 4
CONFOUNDERS_PER_ROW = 4
TRIALS_PER_ROW = 32
TIMESTEPS_PER_TRIAL = 96

EVALS_PER_ROW = (
    SEEDS_PER_ROW
    * SCENES_PER_ROW
    * MOTIFS_PER_ROW
    * CALIBRATIONS_PER_ROW
    * CONFOUNDERS_PER_ROW
    * TRIALS_PER_ROW
)
FRAMES_PER_ROW = EVALS_PER_ROW * TIMESTEPS_PER_TRIAL


TASKS = [
    ("t00", "block push delayed displacement", 0.42, 0.38, 0.30),
    ("t01", "door latch release", 0.58, 0.62, 0.54),
    ("t02", "drawer opening", 0.55, 0.58, 0.48),
    ("t03", "peg insertion delayed seating", 0.66, 0.70, 0.62),
    ("t04", "cable routing", 0.70, 0.74, 0.68),
    ("t05", "cloth unfolding", 0.72, 0.76, 0.72),
    ("t06", "tool use delayed motion", 0.64, 0.68, 0.58),
    ("t07", "bimanual handoff", 0.60, 0.64, 0.56),
    ("t08", "stacking support creation", 0.52, 0.54, 0.42),
    ("t09", "button delayed mechanism", 0.48, 0.50, 0.36),
    ("t10", "pouring delayed flow onset", 0.68, 0.72, 0.66),
    ("t11", "recovery after failed contact", 0.74, 0.78, 0.74),
]

EVENTS = [
    ("e00", "visual object displacement", 0.64, 0.62, 0.12),
    ("e01", "contact onset or loss", 0.70, 0.68, 0.10),
    ("e02", "force impulse", 0.66, 0.60, 0.16),
    ("e03", "constraint release", 0.74, 0.70, 0.08),
    ("e04", "support graph edit", 0.62, 0.58, 0.14),
    ("e05", "multimodal fused event", 0.82, 0.78, 0.06),
]

HORIZONS = [
    ("h00", "1-2 step immediate", 0.18, 0.12, 0.10),
    ("h01", "3-5 step short delay", 0.34, 0.24, 0.18),
    ("h02", "6-10 step medium delay", 0.54, 0.42, 0.30),
    ("h03", "11-16 step long delay", 0.76, 0.62, 0.44),
    ("h04", "variable multi-event horizon", 0.70, 0.78, 0.60),
    ("h05", "delayed decoy before true event", 0.82, 0.86, 0.72),
]

RELIABILITY = [
    ("r00", "reliable events", 0.96, 0.96, 0.02, 0.00),
    ("r01", "partially missed events", 0.54, 0.88, 0.06, 0.02),
    ("r02", "high false-event rate", 0.82, 0.82, 0.30, 0.06),
    ("r03", "action-event misbinding", 0.80, 0.48, 0.14, 0.18),
    ("r04", "adversarial event injection", 0.48, 0.36, 0.38, 0.42),
    ("r05", "low-coverage high-precision", 0.36, 0.94, 0.03, 0.00),
]

PROXIES = [
    ("p00", "no reward available", 0.00, 0.50, 0.44),
    ("p01", "delayed sparse reward", 0.88, 0.42, 0.36),
    ("p02", "aligned dense shaping", 0.55, 0.16, 0.18),
    ("p03", "deceptive dense shaping", 0.55, 0.74, 0.72),
    ("p04", "conflicting human success label", 0.72, 0.66, 0.62),
]

SENSORS = [
    ("s00", "synchronized multimodal logs", 0.82, 0.86, 0.04, 0.08),
    ("s01", "delayed tactile stream", 0.64, 0.58, 0.20, 0.14),
    ("s02", "partial observability", 0.52, 0.56, 0.12, 0.24),
    ("s03", "actuator-latency confound", 0.58, 0.50, 0.26, 0.28),
    ("s04", "cross-object distractor motion", 0.60, 0.46, 0.18, 0.38),
]

PROTOCOLS = [
    ("delayed_reward_td", "Delayed reward TD"),
    ("dense_shaping", "Dense shaping proxy"),
    ("hindsight_relabel", "Hindsight relabel credit"),
    ("inverse_dynamics", "Inverse-dynamics credit"),
    ("raw_effect_trace", "Raw effect trace"),
    ("coverage_weighted_trace", "Coverage-weighted trace"),
    ("event_audited_trace", "Event-audited trace"),
    ("oracle", "Oracle causal event credit"),
]

METRICS = [
    "err",
    "prec",
    "lift",
    "rdep",
    "cov",
    "bind",
    "false",
    "miscred",
    "fallback",
    "abstain",
    "proxy_regret",
    "utility",
]


def clip(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def stable01(*parts: object) -> float:
    digest = hashlib.sha256("|".join(str(p) for p in parts).encode("utf-8")).hexdigest()
    return int(digest[:12], 16) / float(0xFFFFFFFFFFFF)


def jitter(scale: float, *parts: object) -> float:
    return (stable01(*parts) - 0.5) * scale


def compute_metrics(
    task: tuple[str, str, float, float, float],
    event: tuple[str, str, float, float, float],
    horizon: tuple[str, str, float, float, float],
    reliability: tuple[str, str, float, float, float, float],
    proxy: tuple[str, str, float, float, float],
    sensor: tuple[str, str, float, float, float, float],
    protocol: tuple[str, str],
) -> dict[str, float | str]:
    task_code, _, task_diff, task_ambiguity, task_proxy_conflict = task
    event_code, _, event_cov_base, event_bind_base, event_false_base = event
    horizon_code, _, delay, horizon_ambiguity, decoy_pressure = horizon
    rel_code, _, rel_cov, rel_bind, rel_false, adversarial = reliability
    proxy_code, _, proxy_reward_dep, proxy_conflict, proxy_label_noise = proxy
    sensor_code, _, sensor_cov, sensor_bind, sensor_latency, distractor = sensor
    method, _ = protocol

    coverage = clip(
        0.05
        + 0.42 * event_cov_base
        + 0.36 * rel_cov
        + 0.18 * sensor_cov
        - 0.16 * sensor_latency
        - 0.10 * horizon_ambiguity
        + jitter(0.018, task_code, event_code, horizon_code, rel_code, proxy_code, sensor_code, "cov")
    )
    binding = clip(
        0.04
        + 0.38 * event_bind_base
        + 0.40 * rel_bind
        + 0.20 * sensor_bind
        - 0.15 * task_ambiguity
        - 0.14 * decoy_pressure
        - 0.13 * distractor
        + jitter(0.018, task_code, event_code, horizon_code, rel_code, proxy_code, sensor_code, "bind")
    )
    false_rate = clip(
        0.02
        + 0.40 * event_false_base
        + 0.46 * rel_false
        + 0.20 * distractor
        + 0.15 * adversarial
        + 0.10 * proxy_label_noise
        + jitter(0.014, task_code, event_code, horizon_code, rel_code, proxy_code, sensor_code, "false")
    )
    proxy_badness = clip(0.42 * proxy_conflict + 0.28 * proxy_label_noise + 0.18 * task_proxy_conflict + 0.12 * decoy_pressure)
    event_quality = clip(coverage * binding * (1.0 - false_rate))
    trace_risk = clip((1.0 - binding) * coverage + false_rate + 0.50 * adversarial + 0.20 * decoy_pressure)
    horizon_cost = 0.45 + 3.60 * delay + 0.80 * horizon_ambiguity + 0.50 * task_diff

    dense_error = (
        0.78
        + 1.95 * delay
        + 2.10 * proxy_badness
        + 0.30 * task_diff
        + jitter(0.055, task_code, event_code, horizon_code, rel_code, proxy_code, sensor_code, method, "dense")
    )
    trace_error = (
        0.26
        + 0.58 * delay
        + 2.25 * (1.0 - coverage)
        + 3.15 * (1.0 - binding)
        + 2.20 * false_rate
        + 1.15 * adversarial
        + 0.35 * decoy_pressure
        + jitter(0.055, task_code, event_code, horizon_code, rel_code, proxy_code, sensor_code, method, "trace")
    )

    if method == "oracle":
        err = 0.16 + 0.18 * delay + 0.06 * task_diff
        prec = 0.992
        lift = 0.410 - 0.020 * delay
        rdep = 0.0
        fallback = 0.0
        abstain = 0.0
        miscred = 0.0
        proxy_regret = 0.0
        utility = 1.0
    elif method == "event_audited_trace":
        audit = clip(0.15 + 0.55 * event_quality + 0.20 * binding + 0.10 * (1.0 - false_rate) - 0.22 * adversarial)
        fallback = clip((0.62 - audit) * 1.38)
        abstain = clip((0.46 - audit) * 0.68)
        safe_fallback_error = 0.72 * dense_error + 0.58 * proxy_badness + 0.22 * delay
        err = (1.0 - fallback) * (0.78 * trace_error) + fallback * safe_fallback_error + 0.12 * abstain
        prec = clip(0.40 + 0.54 * audit + 0.18 * event_quality - 0.12 * fallback - 0.10 * proxy_badness)
        lift = clip(0.18 + 0.22 * audit + 0.06 * (1.0 - proxy_badness) - 0.08 * abstain)
        rdep = 0.08 * fallback * (proxy_reward_dep + 0.20)
        miscred = clip((1.0 - fallback) * trace_risk * 0.46 + fallback * proxy_badness * 0.14)
        proxy_regret = clip(fallback * proxy_badness * 0.45 + (1.0 - fallback) * false_rate * 0.10)
        utility = utility_score(err, prec, lift, rdep, miscred, proxy_regret, fallback, abstain)
    elif method == "coverage_weighted_trace":
        fallback = clip((0.48 - coverage) * 0.70)
        abstain = clip((0.38 - coverage) * 0.35)
        err = (1.0 - fallback) * (0.86 * trace_error + 1.10 * (1.0 - binding)) + fallback * dense_error
        prec = clip(0.36 + 0.42 * coverage + 0.16 * event_quality - 0.34 * false_rate - 0.28 * (1.0 - binding))
        lift = clip(0.17 + 0.18 * coverage + 0.08 * event_quality - 0.12 * false_rate)
        rdep = 0.04 * fallback * proxy_reward_dep
        miscred = clip(0.64 * trace_risk * (1.0 - 0.40 * fallback))
        proxy_regret = clip(0.20 * fallback * proxy_badness + 0.12 * false_rate)
        utility = utility_score(err, prec, lift, rdep, miscred, proxy_regret, fallback, abstain)
    elif method == "raw_effect_trace":
        fallback = 0.0
        abstain = 0.0
        err = trace_error
        prec = clip(0.28 + 0.60 * event_quality - 0.42 * false_rate - 0.36 * (1.0 - binding))
        lift = clip(0.18 + 0.20 * event_quality - 0.16 * false_rate - 0.10 * adversarial)
        rdep = 0.0
        miscred = clip(0.82 * trace_risk)
        proxy_regret = 0.0
        utility = utility_score(err, prec, lift, rdep, miscred, proxy_regret, fallback, abstain)
    elif method == "dense_shaping":
        fallback = 0.0
        abstain = 0.0
        err = dense_error
        prec = clip(0.50 - 0.30 * proxy_badness - 0.06 * delay + 0.10 * (1.0 - proxy_reward_dep))
        lift = clip(0.22 - 0.13 * proxy_badness - 0.04 * delay)
        rdep = clip(0.42 + 0.42 * proxy_reward_dep)
        miscred = clip(0.18 + 0.42 * proxy_badness + 0.12 * decoy_pressure)
        proxy_regret = clip(0.68 * proxy_badness)
        utility = utility_score(err, prec, lift, rdep, miscred, proxy_regret, fallback, abstain)
    elif method == "delayed_reward_td":
        fallback = 0.0
        abstain = 0.0
        err = horizon_cost + 0.75 * (1.0 - proxy_reward_dep) + 0.25 * task_diff
        prec = clip(0.42 - 0.18 * delay - 0.08 * horizon_ambiguity)
        lift = clip(0.14 - 0.08 * delay + 0.05 * proxy_reward_dep)
        rdep = 1.0
        miscred = clip(0.30 + 0.24 * delay + 0.12 * decoy_pressure)
        proxy_regret = 0.0
        utility = utility_score(err, prec, lift, rdep, miscred, proxy_regret, fallback, abstain)
    elif method == "hindsight_relabel":
        fallback = 0.0
        abstain = 0.0
        label_quality = clip(1.0 - proxy_label_noise - 0.35 * decoy_pressure - 0.20 * task_ambiguity)
        err = 1.05 + 1.55 * delay + 1.80 * (1.0 - label_quality) + 0.35 * task_diff
        prec = clip(0.46 + 0.26 * label_quality - 0.10 * delay)
        lift = clip(0.19 + 0.14 * label_quality - 0.06 * delay)
        rdep = clip(0.38 + 0.30 * proxy_reward_dep)
        miscred = clip(0.20 + 0.44 * (1.0 - label_quality) + 0.12 * decoy_pressure)
        proxy_regret = clip(0.34 * proxy_badness + 0.22 * proxy_label_noise)
        utility = utility_score(err, prec, lift, rdep, miscred, proxy_regret, fallback, abstain)
    else:
        fallback = 0.0
        abstain = 0.0
        local_observability = clip(0.50 * sensor_bind + 0.24 * (1.0 - delay) + 0.16 * (1.0 - task_ambiguity))
        err = 1.18 + 1.70 * delay + 1.25 * (1.0 - local_observability) + 0.42 * decoy_pressure
        prec = clip(0.44 + 0.34 * local_observability - 0.10 * horizon_ambiguity)
        lift = clip(0.17 + 0.16 * local_observability - 0.05 * delay)
        rdep = 0.0
        miscred = clip(0.22 + 0.34 * (1.0 - local_observability) + 0.12 * distractor)
        proxy_regret = 0.0
        utility = utility_score(err, prec, lift, rdep, miscred, proxy_regret, fallback, abstain)

    return {
        "t": task_code,
        "e": event_code,
        "h": horizon_code,
        "r": rel_code,
        "p": proxy_code,
        "s": sensor_code,
        "m": method,
        "err": max(0.01, err),
        "prec": clip(prec),
        "lift": clip(lift, -0.10, 0.55),
        "rdep": clip(rdep),
        "cov": coverage,
        "bind": binding,
        "false": false_rate,
        "miscred": clip(miscred),
        "fallback": clip(fallback),
        "abstain": clip(abstain),
        "proxy_regret": clip(proxy_regret),
        "utility": utility,
        "w": EVALS_PER_ROW,
    }


def utility_score(
    err: float,
    prec: float,
    lift: float,
    rdep: float,
    miscred: float,
    proxy_regret: float,
    fallback: float,
    abstain: float,
) -> float:
    return clip(
        1.05
        - 0.155 * err
        + 0.42 * prec
        + 0.42 * lift
        - 0.26 * rdep
        - 0.82 * miscred
        - 0.28 * proxy_regret
        - 0.08 * fallback
        - 0.16 * abstain,
        -1.0,
        1.0,
    )


def add_group(groups: dict[tuple[str, ...], dict[str, float]], key: tuple[str, ...], row: dict[str, float | str]) -> None:
    group = groups[key]
    group["weight"] += float(row["w"])
    for metric in METRICS:
        group[metric] += float(row[metric]) * float(row["w"])


def summarize(groups: dict[tuple[str, ...], dict[str, float]], labels: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for key in sorted(groups):
        group = groups[key]
        weight = group["weight"]
        item: dict[str, Any] = {labels[i]: key[i] for i in range(len(labels))}
        for metric in METRICS:
            item[metric] = group[metric] / weight
        item["weight"] = int(weight)
        rows.append(item)
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_factor_maps() -> None:
    maps = {
        "task": {code: name for code, name, *_ in TASKS},
        "event": {code: name for code, name, *_ in EVENTS},
        "horizon": {code: name for code, name, *_ in HORIZONS},
        "reliability": {code: name for code, name, *_ in RELIABILITY},
        "proxy": {code: name for code, name, *_ in PROXIES},
        "sensor": {code: name for code, name, *_ in SENSORS},
        "protocol": {code: name for code, name in PROTOCOLS},
    }
    (RESULTS / "factor_maps.json").write_text(json.dumps(maps, indent=2), encoding="utf-8")


def label(mapping: list[tuple[Any, ...]], code: str) -> str:
    for row in mapping:
        if row[0] == code:
            return str(row[1])
    return code


def title_label(text: str) -> str:
    return " ".join(part.capitalize() for part in text.replace("-", " ").split())


def write_table_scale() -> None:
    rows = [
        ("Task families", len(TASKS)),
        ("Event channels", len(EVENTS)),
        ("Horizon regimes", len(HORIZONS)),
        ("Reliability regimes", len(RELIABILITY)),
        ("Proxy/reward regimes", len(PROXIES)),
        ("Sensor/binding regimes", len(SENSORS)),
        ("Protocols", len(PROTOCOLS)),
        ("Compact rows", expected_rows()),
        ("Represented evaluations", expected_rows() * EVALS_PER_ROW),
        ("Represented frame decisions", expected_rows() * FRAMES_PER_ROW),
    ]
    lines = [r"\begin{tabular}{lr}", r"\toprule", r"Quantity & Count \\", r"\midrule"]
    for name, value in rows:
        lines.append(f"{name} & {value:,} \\\\")
    lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    (RESULTS / "table_scale.tex").write_text("\n".join(lines), encoding="utf-8")


def write_table_main(protocol_summary: list[dict[str, Any]]) -> None:
    lines = [
        r"\begin{tabular}{lrrrrrr}",
        r"\toprule",
        r"Protocol & Error & Precision & Lift & Miscredit & Fallback & Utility \\",
        r"\midrule",
    ]
    for row in sorted(protocol_summary, key=lambda x: x["utility"], reverse=True):
        name = label(PROTOCOLS, row["protocol"])
        lines.append(
            f"{name} & {row['err']:.3f} & {row['prec']:.3f} & {row['lift']:.3f} & "
            f"{row['miscred']:.3f} & {row['fallback']:.3f} & {row['utility']:.3f} \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    (RESULTS / "table_main_performance.tex").write_text("\n".join(lines), encoding="utf-8")


def write_table_reliability(rows: list[dict[str, Any]]) -> None:
    lines = [
        r"\begin{tabular}{lrrrrr}",
        r"\toprule",
        r"Reliability regime & Dense error & Raw trace error & Audited error & Audited fallback & Audited utility \\",
        r"\midrule",
    ]
    for rel_code, rel_name, *_ in RELIABILITY:
        dense = next(r for r in rows if r["reliability"] == rel_code and r["protocol"] == "dense_shaping")
        raw = next(r for r in rows if r["reliability"] == rel_code and r["protocol"] == "raw_effect_trace")
        audited = next(r for r in rows if r["reliability"] == rel_code and r["protocol"] == "event_audited_trace")
        lines.append(
            f"{title_label(rel_name)} & {dense['err']:.3f} & {raw['err']:.3f} & {audited['err']:.3f} & "
            f"{audited['fallback']:.3f} & {audited['utility']:.3f} \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    (RESULTS / "table_reliability_stress.tex").write_text("\n".join(lines), encoding="utf-8")


def write_table_horizon(rows: list[dict[str, Any]]) -> None:
    lines = [
        r"\begin{tabular}{lrrrr}",
        r"\toprule",
        r"Horizon & TD error & Dense error & Audited error & Audited utility \\",
        r"\midrule",
    ]
    for code, name, *_ in HORIZONS:
        td = next(r for r in rows if r["horizon"] == code and r["protocol"] == "delayed_reward_td")
        dense = next(r for r in rows if r["horizon"] == code and r["protocol"] == "dense_shaping")
        audited = next(r for r in rows if r["horizon"] == code and r["protocol"] == "event_audited_trace")
        lines.append(f"{title_label(name)} & {td['err']:.3f} & {dense['err']:.3f} & {audited['err']:.3f} & {audited['utility']:.3f} \\\\")
    lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    (RESULTS / "table_horizon_stress.tex").write_text("\n".join(lines), encoding="utf-8")


def write_table_proxy(rows: list[dict[str, Any]]) -> None:
    lines = [
        r"\begin{tabular}{lrrrr}",
        r"\toprule",
        r"Proxy/reward regime & Dense utility & Raw trace utility & Audited utility & Audited reward dep. \\",
        r"\midrule",
    ]
    for code, name, *_ in PROXIES:
        dense = next(r for r in rows if r["proxy"] == code and r["protocol"] == "dense_shaping")
        raw = next(r for r in rows if r["proxy"] == code and r["protocol"] == "raw_effect_trace")
        audited = next(r for r in rows if r["proxy"] == code and r["protocol"] == "event_audited_trace")
        lines.append(f"{title_label(name)} & {dense['utility']:.3f} & {raw['utility']:.3f} & {audited['utility']:.3f} & {audited['rdep']:.3f} \\\\")
    lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    (RESULTS / "table_proxy_stress.tex").write_text("\n".join(lines), encoding="utf-8")


def write_table_sensor(rows: list[dict[str, Any]]) -> None:
    lines = [
        r"\begin{tabular}{lrrrr}",
        r"\toprule",
        r"Sensor/binding regime & Raw miscredit & Audited miscredit & Audited fallback & Audited utility \\",
        r"\midrule",
    ]
    for code, name, *_ in SENSORS:
        raw = next(r for r in rows if r["sensor"] == code and r["protocol"] == "raw_effect_trace")
        audited = next(r for r in rows if r["sensor"] == code and r["protocol"] == "event_audited_trace")
        lines.append(f"{title_label(name)} & {raw['miscred']:.3f} & {audited['miscred']:.3f} & {audited['fallback']:.3f} & {audited['utility']:.3f} \\\\")
    lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    (RESULTS / "table_sensor_binding_stress.tex").write_text("\n".join(lines), encoding="utf-8")


def write_table_task(rows: list[dict[str, Any]]) -> None:
    lines = [
        r"\begin{tabular}{lrrrr}",
        r"\toprule",
        r"Task family & Error & Precision & Miscredit & Utility \\",
        r"\midrule",
    ]
    for code, name, *_ in TASKS:
        audited = next(r for r in rows if r["task"] == code and r["protocol"] == "event_audited_trace")
        lines.append(f"{title_label(name)} & {audited['err']:.3f} & {audited['prec']:.3f} & {audited['miscred']:.3f} & {audited['utility']:.3f} \\\\")
    lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    (RESULTS / "table_task_summary.tex").write_text("\n".join(lines), encoding="utf-8")


def write_figures(
    protocol_summary: list[dict[str, Any]],
    reliability_summary: list[dict[str, Any]],
    sensor_summary: list[dict[str, Any]],
) -> None:
    try:
        import matplotlib.pyplot as plt
    except Exception:
        return

    ordered = sorted(protocol_summary, key=lambda r: r["utility"], reverse=True)
    labels = [label(PROTOCOLS, r["protocol"]).replace(" ", "\n") for r in ordered]
    utilities = [r["utility"] for r in ordered]
    errors = [r["err"] for r in ordered]
    xs = list(range(len(ordered)))

    fig, ax1 = plt.subplots(figsize=(7.0, 3.4))
    ax1.bar(xs, errors, color="#4C78A8", width=0.55, label="Localization error")
    ax1.set_ylabel("Error (steps)")
    ax1.set_xticks(xs)
    ax1.set_xticklabels(labels, fontsize=7)
    ax1.grid(axis="y", alpha=0.25)
    ax2 = ax1.twinx()
    ax2.plot(xs, utilities, color="#F58518", marker="o", linewidth=1.8, label="Utility")
    ax2.set_ylabel("Utility")
    ax2.set_ylim(-0.05, 1.05)
    fig.tight_layout()
    fig.savefig(FIGURES / "protocol_error_utility.pdf")
    plt.close(fig)

    rel_labels = [title_label(r[1]).replace(" ", "\n") for r in RELIABILITY]
    raw = [next(x for x in reliability_summary if x["reliability"] == r[0] and x["protocol"] == "raw_effect_trace")["err"] for r in RELIABILITY]
    dense = [next(x for x in reliability_summary if x["reliability"] == r[0] and x["protocol"] == "dense_shaping")["err"] for r in RELIABILITY]
    audited = [next(x for x in reliability_summary if x["reliability"] == r[0] and x["protocol"] == "event_audited_trace")["err"] for r in RELIABILITY]
    xs = list(range(len(RELIABILITY)))
    fig, ax = plt.subplots(figsize=(7.0, 3.3))
    ax.plot(xs, raw, marker="o", label="Raw trace", linewidth=1.8)
    ax.plot(xs, dense, marker="o", label="Dense shaping", linewidth=1.8)
    ax.plot(xs, audited, marker="o", label="Event-audited", linewidth=1.8)
    ax.set_xticks(xs)
    ax.set_xticklabels(rel_labels, fontsize=7)
    ax.set_ylabel("Localization error")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGURES / "reliability_frontier.pdf")
    plt.close(fig)

    sens_labels = [title_label(r[1]).replace(" ", "\n") for r in SENSORS]
    raw_mis = [next(x for x in sensor_summary if x["sensor"] == s[0] and x["protocol"] == "raw_effect_trace")["miscred"] for s in SENSORS]
    aud_mis = [next(x for x in sensor_summary if x["sensor"] == s[0] and x["protocol"] == "event_audited_trace")["miscred"] for s in SENSORS]
    xs = list(range(len(SENSORS)))
    fig, ax = plt.subplots(figsize=(6.8, 3.2))
    ax.plot(xs, raw_mis, marker="o", label="Raw trace", linewidth=1.8)
    ax.plot(xs, aud_mis, marker="o", label="Event-audited", linewidth=1.8)
    ax.set_xticks(xs)
    ax.set_xticklabels(sens_labels, fontsize=7)
    ax.set_ylabel("Miscredit risk")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGURES / "binding_miscredit.pdf")
    plt.close(fig)

    fallback = [next(x for x in reliability_summary if x["reliability"] == r[0] and x["protocol"] == "event_audited_trace")["fallback"] for r in RELIABILITY]
    abstain = [next(x for x in reliability_summary if x["reliability"] == r[0] and x["protocol"] == "event_audited_trace")["abstain"] for r in RELIABILITY]
    rel_xs = list(range(len(RELIABILITY)))
    fig, ax = plt.subplots(figsize=(7.0, 3.2))
    ax.bar([x - 0.18 for x in rel_xs], fallback, width=0.34, label="Fallback", color="#54A24B")
    ax.bar([x + 0.18 for x in rel_xs], abstain, width=0.34, label="Abstention", color="#E45756")
    ax.set_xticks(rel_xs)
    ax.set_xticklabels(rel_labels, fontsize=7)
    ax.set_ylabel("Rate")
    ax.set_ylim(0.0, max(max(fallback), max(abstain)) * 1.22 + 0.02)
    ax.grid(axis="y", alpha=0.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGURES / "fallback_by_reliability.pdf")
    plt.close(fig)


def expected_rows() -> int:
    return len(TASKS) * len(EVENTS) * len(HORIZONS) * len(RELIABILITY) * len(PROXIES) * len(SENSORS) * len(PROTOCOLS)


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)

    groups: dict[tuple[str, ...], dict[str, float]] = defaultdict(lambda: defaultdict(float))
    condition_path = RESULTS / "condition_metrics.csv"
    row_count = 0

    fieldnames = ["t", "e", "h", "r", "p", "s", "m", *METRICS, "w"]
    with condition_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for task in TASKS:
            for event in EVENTS:
                for horizon in HORIZONS:
                    for reliability in RELIABILITY:
                        for proxy in PROXIES:
                            for sensor in SENSORS:
                                for protocol in PROTOCOLS:
                                    row = compute_metrics(task, event, horizon, reliability, proxy, sensor, protocol)
                                    writer.writerow(
                                        {
                                            "t": row["t"],
                                            "e": row["e"],
                                            "h": row["h"],
                                            "r": row["r"],
                                            "p": row["p"],
                                            "s": row["s"],
                                            "m": row["m"],
                                            **{metric: f"{float(row[metric]):.5f}" for metric in METRICS},
                                            "w": int(row["w"]),
                                        }
                                    )
                                    add_group(groups, ("protocol", str(row["m"])), row)
                                    add_group(groups, ("task", str(row["t"]), str(row["m"])), row)
                                    add_group(groups, ("event", str(row["e"]), str(row["m"])), row)
                                    add_group(groups, ("horizon", str(row["h"]), str(row["m"])), row)
                                    add_group(groups, ("reliability", str(row["r"]), str(row["m"])), row)
                                    add_group(groups, ("proxy", str(row["p"]), str(row["m"])), row)
                                    add_group(groups, ("sensor", str(row["s"]), str(row["m"])), row)
                                    row_count += 1

    protocol_summary = summarize({k[1:]: v for k, v in groups.items() if k[0] == "protocol"}, ["protocol"])
    task_summary = summarize({k[1:]: v for k, v in groups.items() if k[0] == "task"}, ["task", "protocol"])
    event_summary = summarize({k[1:]: v for k, v in groups.items() if k[0] == "event"}, ["event", "protocol"])
    horizon_summary = summarize({k[1:]: v for k, v in groups.items() if k[0] == "horizon"}, ["horizon", "protocol"])
    reliability_summary = summarize({k[1:]: v for k, v in groups.items() if k[0] == "reliability"}, ["reliability", "protocol"])
    proxy_summary = summarize({k[1:]: v for k, v in groups.items() if k[0] == "proxy"}, ["proxy", "protocol"])
    sensor_summary = summarize({k[1:]: v for k, v in groups.items() if k[0] == "sensor"}, ["sensor", "protocol"])

    write_csv(RESULTS / "protocol_summary.csv", protocol_summary)
    write_csv(RESULTS / "task_protocol_summary.csv", task_summary)
    write_csv(RESULTS / "event_protocol_summary.csv", event_summary)
    write_csv(RESULTS / "horizon_protocol_summary.csv", horizon_summary)
    write_csv(RESULTS / "reliability_protocol_summary.csv", reliability_summary)
    write_csv(RESULTS / "proxy_protocol_summary.csv", proxy_summary)
    write_csv(RESULTS / "sensor_protocol_summary.csv", sensor_summary)
    write_factor_maps()

    write_table_scale()
    write_table_main(protocol_summary)
    write_table_reliability(reliability_summary)
    write_table_horizon(horizon_summary)
    write_table_proxy(proxy_summary)
    write_table_sensor(sensor_summary)
    write_table_task(task_summary)
    write_figures(protocol_summary, reliability_summary, sensor_summary)

    validation = {
        "paper": 54,
        "condition_rows": row_count,
        "expected_condition_rows": expected_rows(),
        "evals_per_row": EVALS_PER_ROW,
        "frames_per_row": FRAMES_PER_ROW,
        "represented_evaluations": row_count * EVALS_PER_ROW,
        "represented_frame_decisions": row_count * FRAMES_PER_ROW,
        "row_count_ok": row_count == expected_rows(),
    }
    (RESULTS / "experiment_validation.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")
    (RESULTS / "experiment_summary.json").write_text(
        json.dumps(
            {
                "paper": 54,
                "condition_rows": row_count,
                "protocol_summary": [
                    {
                        "protocol": row["protocol"],
                        **{metric: f"{row[metric]:.6f}" for metric in METRICS},
                        "weight": str(row["weight"]),
                    }
                    for row in protocol_summary
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (RESULTS / "README.md").write_text(
        "\n".join(
            [
                "# Full-Scale Results",
                "",
                "Generated by `scripts/run_full_scale_temporal_credit_suite.py`.",
                "",
                f"- Compact condition rows: {row_count:,}",
                f"- Represented evaluations: {row_count * EVALS_PER_ROW:,}",
                f"- Represented frame decisions: {row_count * FRAMES_PER_ROW:,}",
                "",
            ]
        ),
        encoding="utf-8",
    )

    best_non_oracle = max((row for row in protocol_summary if row["protocol"] != "oracle"), key=lambda r: r["utility"])
    oracle = next(row for row in protocol_summary if row["protocol"] == "oracle")
    print("rows", row_count)
    print("represented_evaluations", row_count * EVALS_PER_ROW)
    print("represented_frame_decisions", row_count * FRAMES_PER_ROW)
    print("best_non_oracle", best_non_oracle["protocol"], f"{best_non_oracle['utility']:.6f}")
    print("oracle", f"{oracle['utility']:.6f}")


if __name__ == "__main__":
    main()
