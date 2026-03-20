#!/usr/bin/env python3
"""Generate charts from dq-manual summary JSON artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D

PROFILE_ORDER = ["P05", "P10", "P20", "P50"]


def _load_rows(summary_path: Path) -> pd.DataFrame:
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    rows = payload.get("aggregated_rows", [])
    if not rows:
        raise ValueError("No aggregated_rows found in summary JSON.")
    df = pd.DataFrame(rows)
    required = {
        "scenario",
        "model",
        "profile",
        "run_count",
        "delta_precision_mean",
        "delta_recall_mean",
        "delta_f1_mean",
        "total_tokens_mean",
    }
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    return df


def _setup_theme() -> None:
    plt.style.use("ggplot")
    plt.rcParams["figure.dpi"] = 160
    plt.rcParams["savefig.dpi"] = 200
    plt.rcParams["axes.grid"] = True


def _profile_sort_index(series: pd.Series) -> pd.Series:
    return series.map({name: i for i, name in enumerate(PROFILE_ORDER)}).fillna(99)


def _plot_heatmap(df: pd.DataFrame, scenario: str, output_dir: Path) -> None:
    subset = df[df["scenario"] == scenario].copy()
    if subset.empty:
        return

    pivot = subset.pivot_table(
        index="model",
        columns="profile",
        values="delta_f1_mean",
        aggfunc="mean",
    )
    ordered_cols = [p for p in PROFILE_ORDER if p in pivot.columns] + [
        p for p in pivot.columns if p not in PROFILE_ORDER
    ]
    pivot = pivot[ordered_cols]

    fig, ax = plt.subplots(figsize=(10, max(3.2, 0.65 * len(pivot.index) + 1.4)))
    heat = ax.imshow(pivot.values, cmap="YlGnBu", vmin=0.0, vmax=1.0, aspect="auto")
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            value = pivot.iat[i, j]
            if pd.isna(value):
                continue
            ax.text(j, i, f"{value:.3f}", ha="center", va="center", fontsize=9, color="black")
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, rotation=0)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)
    cbar = fig.colorbar(heat, ax=ax)
    cbar.set_label("Delta F1 (mean)")
    ax.set_title(f"Manual Benchmark Delta F1 Heatmap ({scenario.title()})")
    ax.set_xlabel("Profile")
    ax.set_ylabel("Model")
    fig.tight_layout()
    fig.savefig(output_dir / f"manual-summary-f1-heatmap-{scenario}.png")
    plt.close(fig)


def _plot_recall_vs_tokens(df: pd.DataFrame, scenario: str, output_dir: Path) -> None:
    subset = df[df["scenario"] == scenario].copy()
    if subset.empty:
        return

    subset["profile_order"] = _profile_sort_index(subset["profile"])
    subset = subset.sort_values(["model", "profile_order", "profile"])

    fig, ax = plt.subplots(figsize=(11, 6))
    markers = {"P05": "o", "P10": "s", "P20": "^", "P50": "D"}
    models = sorted(subset["model"].astype(str).unique())
    colors = plt.get_cmap("tab10", max(1, len(models)))
    model_to_color = {model: colors(i) for i, model in enumerate(models)}

    for _, row in subset.iterrows():
        model = str(row["model"])
        profile = str(row["profile"])
        ax.scatter(
            float(row["total_tokens_mean"]),
            float(row["delta_recall_mean"]),
            color=model_to_color[model],
            marker=markers.get(profile, "o"),
            s=140,
            edgecolors="black",
            linewidths=0.4,
            alpha=0.9,
        )

    for _, row in subset.iterrows():
        ax.annotate(
            row["profile"],
            (row["total_tokens_mean"], row["delta_recall_mean"]),
            xytext=(6, 5),
            textcoords="offset points",
            fontsize=8,
            alpha=0.8,
        )

    ax.set_title(f"Recall vs Tokens ({scenario.title()})")
    ax.set_xlabel("Total Tokens (mean)")
    ax.set_ylabel("Delta Recall (mean)")
    ax.set_ylim(-0.02, 1.02)
    model_legend = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor=model_to_color[m], label=m, markersize=8)
        for m in models
    ]
    profile_legend = [
        Line2D([0], [0], marker=markers[p], color="black", label=p, linestyle="None", markersize=8)
        for p in PROFILE_ORDER
        if p in set(subset["profile"])
    ]
    legend1 = ax.legend(handles=model_legend, title="Model", loc="upper left", fontsize=8)
    ax.add_artist(legend1)
    ax.legend(handles=profile_legend, title="Profile", loc="lower right", fontsize=8)
    fig.tight_layout()
    fig.savefig(output_dir / f"manual-summary-recall-vs-tokens-{scenario}.png")
    plt.close(fig)


def _plot_profile_lines(df: pd.DataFrame, scenario: str, output_dir: Path) -> None:
    subset = df[df["scenario"] == scenario].copy()
    if subset.empty:
        return
    subset["profile_order"] = _profile_sort_index(subset["profile"])
    subset = subset.sort_values(["model", "profile_order", "profile"])

    fig, ax = plt.subplots(figsize=(11, 6))
    models = sorted(subset["model"].astype(str).unique())
    colors = plt.get_cmap("tab10", max(1, len(models)))
    for i, model in enumerate(models):
        model_rows = subset[subset["model"] == model].sort_values("profile_order")
        ax.plot(
            model_rows["profile_order"],
            model_rows["delta_f1_mean"],
            marker="o",
            linewidth=2.0,
            color=colors(i),
            label=model,
        )
    ax.set_title(f"Delta F1 by Profile ({scenario.title()})")
    ax.set_xlabel("Profile")
    ax.set_ylabel("Delta F1 (mean)")
    ax.set_ylim(-0.02, 1.02)
    present_profiles = [p for p in PROFILE_ORDER if p in set(subset["profile"])]
    ticks = [PROFILE_ORDER.index(p) for p in present_profiles]
    ax.set_xticks(ticks)
    ax.set_xticklabels(present_profiles)
    ax.legend(loc="best", fontsize=8, title="Model")
    fig.tight_layout()
    fig.savefig(output_dir / f"manual-summary-f1-lines-{scenario}.png")
    plt.close(fig)


def _write_flat_table(df: pd.DataFrame, output_dir: Path) -> None:
    out_csv = output_dir / "manual-summary-aggregated.csv"
    out_md = output_dir / "manual-summary-aggregated.md"
    ordered = df.copy()
    ordered["profile_order"] = _profile_sort_index(ordered["profile"])
    ordered = ordered.sort_values(["scenario", "model", "profile_order", "profile"]).drop(
        columns=["profile_order"]
    )
    ordered.to_csv(out_csv, index=False)
    out_md.write_text(ordered.to_markdown(index=False), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot manual benchmark summary JSON.")
    parser.add_argument("summary_json", help="Path to runs/manual-benchmark-summary-*.json")
    parser.add_argument(
        "--output-dir",
        default="",
        help="Optional output directory. Default: runs/plots-<summary-stem>/",
    )
    args = parser.parse_args()

    summary_path = Path(args.summary_json).expanduser().resolve()
    if not summary_path.exists():
        raise FileNotFoundError(f"Summary file not found: {summary_path}")

    if args.output_dir:
        output_dir = Path(args.output_dir).expanduser().resolve()
    else:
        output_dir = summary_path.parent / f"plots-{summary_path.stem}"
    output_dir.mkdir(parents=True, exist_ok=True)

    _setup_theme()
    df = _load_rows(summary_path)
    _write_flat_table(df, output_dir)
    for scenario in sorted(df["scenario"].dropna().unique()):
        _plot_heatmap(df, str(scenario), output_dir)
        _plot_recall_vs_tokens(df, str(scenario), output_dir)
        _plot_profile_lines(df, str(scenario), output_dir)

    print(f"Saved plots to: {output_dir}")


if __name__ == "__main__":
    main()
