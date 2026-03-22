"""
Experiment script for paper validation.

Runs the StatementExtractor on all bank statement PDFs, compares results
against ground truth, calculates detailed metrics, and generates charts.

Usage:
    python scripts/run_experiment.py                    # full run (194 files)
    python scripts/run_experiment.py --limit 10         # quick test
    python scripts/run_experiment.py --analyze-only RESULTS.csv  # re-analyze existing results
"""

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

from src.core.file_utils import get_pdf_files
from src.infrastructure.evaluation.metrics import (
    validate_bank,
    validate_clabe,
    validate_owner,
)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
DATA_DIR = project_root / "data" / "processed" / "pdfs"
GROUND_TRUTH_CSV = DATA_DIR / "bank_accounts_filtered_corrected.csv"
GROUND_TRUTH_CSV_ORIGINAL = DATA_DIR / "bank_accounts_filtered.csv"
PDF_DIR = DATA_DIR / "bank_statements"
RESULTS_DIR = project_root / "data" / "results" / "experiments"


# ---------------------------------------------------------------------------
# Similarity helpers
# ---------------------------------------------------------------------------
def string_similarity(a: str, b: str) -> float:
    """Ratio of matching characters (SequenceMatcher-like)."""
    from difflib import SequenceMatcher

    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a.upper().strip(), b.upper().strip()).ratio()


def digit_difference(pred: str, actual: str) -> int | None:
    """Count differing digits between two CLABE strings."""
    p = pred.strip()
    a = actual.strip()
    if len(p) != 18 or len(a) != 18:
        return None
    return sum(1 for x, y in zip(p, a) if x != y)


# ---------------------------------------------------------------------------
# Extraction runner
# ---------------------------------------------------------------------------
def run_extraction(pdf_files: list[Path]) -> pd.DataFrame:
    """Run StatementExtractor on a list of PDFs and return results DataFrame."""
    from src.infrastructure.extractors.statement_extractor import StatementExtractor

    extractor = StatementExtractor()

    results = []
    total = len(pdf_files)

    for i, pdf_path in enumerate(pdf_files, 1):
        print(f"  [{i}/{total}] {pdf_path.name} ... ", end="", flush=True)
        start = time.time()

        try:
            result = extractor.extract_file(pdf_path)
            elapsed = time.time() - start

            if isinstance(result, dict):
                owner = result.get("owner", "Unknown")
                account = str(result.get("account_number", "000000000000000000")).strip().zfill(18)
                bank = result.get("bank_name", "Unknown")
                is_valid = result.get("is_valid_document", True)
            else:
                owner = result.owner
                account = str(result.account_number).strip().zfill(18)
                bank = result.bank_name
                is_valid = result.is_valid_document

            results.append(
                {
                    "file_name": pdf_path.name,
                    "owner_pred": owner,
                    "account_pred": account,
                    "bank_pred": bank,
                    "is_valid_document": is_valid,
                    "status": "success",
                    "time_seconds": round(elapsed, 2),
                    "error": None,
                }
            )
            print(f"OK ({elapsed:.1f}s) → {bank} | {owner[:30]}")

        except Exception as e:
            elapsed = time.time() - start
            results.append(
                {
                    "file_name": pdf_path.name,
                    "owner_pred": None,
                    "account_pred": None,
                    "bank_pred": None,
                    "is_valid_document": None,
                    "status": "error",
                    "time_seconds": round(elapsed, 2),
                    "error": str(e),
                }
            )
            print(f"ERROR ({elapsed:.1f}s) → {e}")

    return pd.DataFrame(results)


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------
def load_ground_truth() -> pd.DataFrame:
    """Load and clean ground truth CSV."""
    csv_path = GROUND_TRUTH_CSV if GROUND_TRUTH_CSV.exists() else GROUND_TRUTH_CSV_ORIGINAL
    gt = pd.read_csv(csv_path, dtype={"CLABE": str})
    print(f"  Ground truth: {csv_path.name} ({len(gt)} rows)")
    gt = gt.rename(
        columns={
            "downloaded_file": "file_name",
            "Owner": "owner_real",
            "CLABE": "account_real",
            "banco": "bank_real",
        }
    )
    gt = gt[["file_name", "owner_real", "account_real", "bank_real"]].copy()
    gt["account_real"] = gt["account_real"].astype(str).str.strip().str.zfill(18)
    gt["owner_real"] = gt["owner_real"].astype(str).str.strip()
    gt["bank_real"] = gt["bank_real"].astype(str).str.strip()
    return gt


def analyze_results(results_df: pd.DataFrame, gt_df: pd.DataFrame) -> pd.DataFrame:
    """Merge predictions with ground truth and compute per-row metrics."""
    merged = results_df.merge(gt_df, on="file_name", how="inner")

    # Per-field validation
    owner_vals = []
    clabe_vals = []
    bank_vals = []

    def _is_empty(val) -> bool:
        """Check if a ground truth value is effectively empty."""
        s = str(val).strip()
        return s in ("", "nan", "NaN", "None", "none")

    for _, row in merged.iterrows():
        if row["status"] != "success":
            owner_vals.append((False, "error"))
            clabe_vals.append((False, "error"))
            bank_vals.append((False, "error"))
            continue

        # Skip validation when ground truth is missing
        if _is_empty(row.get("owner_real")):
            owner_vals.append((False, "no_ground_truth"))
        else:
            owner_vals.append(validate_owner(str(row["owner_pred"] or ""), str(row["owner_real"])))

        if _is_empty(row.get("account_real")):
            clabe_vals.append((False, "no_ground_truth"))
        else:
            clabe_vals.append(
                validate_clabe(str(row["account_pred"] or ""), str(row["account_real"]))
            )

        if _is_empty(row.get("bank_real")):
            bank_vals.append((False, "no_ground_truth"))
        else:
            bank_vals.append(validate_bank(str(row["bank_pred"] or ""), str(row["bank_real"])))

    merged["owner_correct"] = [v[0] for v in owner_vals]
    merged["owner_match_type"] = [v[1] for v in owner_vals]
    merged["clabe_correct"] = [v[0] for v in clabe_vals]
    merged["clabe_match_type"] = [v[1] for v in clabe_vals]
    merged["bank_correct"] = [v[0] for v in bank_vals]
    merged["bank_match_type"] = [v[1] for v in bank_vals]

    # Similarity scores
    merged["owner_similarity"] = merged.apply(
        lambda r: (
            string_similarity(str(r["owner_pred"] or ""), str(r["owner_real"] or ""))
            if r["status"] == "success"
            else 0.0
        ),
        axis=1,
    )
    merged["clabe_similarity"] = merged.apply(
        lambda r: (
            string_similarity(str(r["account_pred"] or ""), str(r["account_real"] or ""))
            if r["status"] == "success"
            else 0.0
        ),
        axis=1,
    )
    merged["bank_similarity"] = merged.apply(
        lambda r: (
            string_similarity(str(r["bank_pred"] or ""), str(r["bank_real"] or ""))
            if r["status"] == "success"
            else 0.0
        ),
        axis=1,
    )
    merged["clabe_digit_diff"] = merged.apply(
        lambda r: (
            digit_difference(str(r["account_pred"] or ""), str(r["account_real"] or ""))
            if r["status"] == "success"
            else None
        ),
        axis=1,
    )

    return merged


def compute_summary_metrics(merged: pd.DataFrame) -> dict:
    """Compute aggregate metrics for the paper."""
    total = len(merged)
    successful = len(merged[merged["status"] == "success"])
    errors = total - successful

    metrics = {
        "total_files": total,
        "successful_extractions": successful,
        "errors": errors,
        "error_rate": round(errors / total * 100, 2) if total > 0 else 0,
    }

    success_df = merged[merged["status"] == "success"]

    for field in ["owner", "clabe", "bank"]:
        correct_col = f"{field}_correct"
        match_col = f"{field}_match_type"
        sim_col = f"{field}_similarity"

        # Exclude rows with no ground truth from all calculations
        has_gt = success_df[success_df[match_col] != "no_ground_truth"]

        correct = has_gt[correct_col].sum()

        # Accuracy total: correct / files with ground truth
        total_with_gt = len(has_gt)
        acc_total = correct / total_with_gt if total_with_gt > 0 else 0

        # Accuracy condicional: correct / (extraction attempted AND has ground truth)
        if field == "clabe":
            attempted = has_gt[
                (has_gt["account_pred"] != "000000000000000000") & (has_gt["account_pred"].notna())
            ]
        elif field == "owner":
            attempted = has_gt[(has_gt["owner_pred"] != "Unknown") & (has_gt["owner_pred"].notna())]
        else:  # bank
            attempted = has_gt[(has_gt["bank_pred"] != "Unknown") & (has_gt["bank_pred"].notna())]

        acc_conditional = attempted[correct_col].sum() / len(attempted) if len(attempted) > 0 else 0

        # Not extracted count (among files with ground truth)
        not_extracted = total_with_gt - len(attempted)

        # Similarity stats (only on attempted)
        sim_values = attempted[sim_col]
        sim_mean = sim_values.mean() if len(sim_values) > 0 else 0
        sim_median = sim_values.median() if len(sim_values) > 0 else 0
        sim_std = sim_values.std() if len(sim_values) > 0 else 0

        # Match type breakdown (exclude no_ground_truth)
        match_counts = has_gt[match_col].value_counts().to_dict()

        metrics[field] = {
            "total_with_ground_truth": total_with_gt,
            "accuracy_total": round(acc_total, 4),
            "accuracy_conditional": round(acc_conditional, 4),
            "correct": int(correct),
            "attempted": len(attempted),
            "not_extracted": not_extracted,
            "no_ground_truth": len(success_df) - len(has_gt),
            "similarity_mean": round(sim_mean, 4),
            "similarity_median": round(sim_median, 4),
            "similarity_std": round(sim_std, 4),
            "match_types": {k: int(v) for k, v in match_counts.items()},
        }

    # CLABE-specific: digit difference stats
    digit_diffs = merged[(merged["clabe_digit_diff"].notna()) & (merged["clabe_digit_diff"] > 0)][
        "clabe_digit_diff"
    ]
    if len(digit_diffs) > 0:
        metrics["clabe"]["avg_digit_diff_on_errors"] = round(digit_diffs.mean(), 2)

    # Timing stats
    times = merged[merged["status"] == "success"]["time_seconds"]
    metrics["timing"] = {
        "mean_seconds": round(times.mean(), 2),
        "median_seconds": round(times.median(), 2),
        "std_seconds": round(times.std(), 2),
        "min_seconds": round(times.min(), 2),
        "max_seconds": round(times.max(), 2),
        "total_minutes": round(times.sum() / 60, 2),
    }

    # Per-bank accuracy
    bank_metrics = {}
    for bank_name, group in success_df.groupby("bank_real"):
        bank_name = str(bank_name)
        if bank_name in ("", "nan"):
            continue
        bank_metrics[bank_name] = {
            "count": len(group),
            "owner_accuracy": round(group["owner_correct"].mean(), 4),
            "clabe_accuracy": round(group["clabe_correct"].mean(), 4),
            "bank_accuracy": round(group["bank_correct"].mean(), 4),
        }
    metrics["per_bank"] = bank_metrics

    return metrics


# ---------------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------------
def generate_charts(merged: pd.DataFrame, metrics: dict, output_dir: Path):
    """Generate publication-quality charts."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import seaborn as sns

    sns.set_theme(style="whitegrid", font_scale=1.1)
    charts_dir = output_dir / "charts"
    charts_dir.mkdir(parents=True, exist_ok=True)

    # 1. Accuracy comparison bar chart (total vs conditional)
    fig, ax = plt.subplots(figsize=(8, 5))
    fields = ["owner", "clabe", "bank"]
    field_labels = ["Titular", "CLABE", "Banco"]
    acc_total = [metrics[f]["accuracy_total"] for f in fields]
    acc_cond = [metrics[f]["accuracy_conditional"] for f in fields]

    x = np.arange(len(fields))
    width = 0.35
    bars1 = ax.bar(x - width / 2, acc_total, width, label="Accuracy Total", color="#4C72B0")
    bars2 = ax.bar(x + width / 2, acc_cond, width, label="Accuracy Condicional", color="#55A868")

    ax.set_ylabel("Accuracy")
    ax.set_title("Accuracy Total vs Condicional por Campo")
    ax.set_xticks(x)
    ax.set_xticklabels(field_labels)
    ax.set_ylim(0, 1.15)
    ax.legend()

    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.annotate(
                f"{height:.2f}",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=10,
            )

    plt.tight_layout()
    fig.savefig(charts_dir / "accuracy_comparison.png", dpi=150)
    plt.close(fig)
    print("  → accuracy_comparison.png")

    # 2. Similarity distribution histograms
    success_df = merged[merged["status"] == "success"]
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    for idx, (field, label) in enumerate(zip(fields, field_labels)):
        sim_col = f"{field}_similarity"
        data = success_df[success_df[sim_col] > 0][sim_col]
        if len(data) > 0:
            axes[idx].hist(data, bins=20, color="#4C72B0", edgecolor="white", alpha=0.8)
            axes[idx].axvline(
                data.mean(), color="red", linestyle="--", label=f"Media: {data.mean():.2f}"
            )
            axes[idx].axvline(
                data.median(), color="orange", linestyle="--", label=f"Mediana: {data.median():.2f}"
            )
            axes[idx].legend(fontsize=9)
        axes[idx].set_title(f"Similaridad - {label}")
        axes[idx].set_xlabel("Similaridad")
        axes[idx].set_ylabel("Frecuencia")

    plt.tight_layout()
    fig.savefig(charts_dir / "similarity_distributions.png", dpi=150)
    plt.close(fig)
    print("  → similarity_distributions.png")

    # 3. Per-bank accuracy heatmap
    per_bank = metrics.get("per_bank", {})
    if per_bank:
        banks = sorted(per_bank.keys())
        bank_data = []
        for b in banks:
            bank_data.append(
                {
                    "Banco": b,
                    "Titular": per_bank[b]["owner_accuracy"],
                    "CLABE": per_bank[b]["clabe_accuracy"],
                    "Banco (campo)": per_bank[b]["bank_accuracy"],
                    "n": per_bank[b]["count"],
                }
            )
        bank_df = pd.DataFrame(bank_data).set_index("Banco")

        # Only banks with >= 3 documents for meaningful heatmap
        bank_df_filtered = bank_df[bank_df["n"] >= 3].drop(columns=["n"])

        if len(bank_df_filtered) > 0:
            fig, ax = plt.subplots(figsize=(8, max(4, len(bank_df_filtered) * 0.5)))
            sns.heatmap(
                bank_df_filtered,
                annot=True,
                fmt=".2f",
                cmap="RdYlGn",
                vmin=0,
                vmax=1,
                ax=ax,
                linewidths=0.5,
            )
            ax.set_title("Accuracy por Banco y Campo (bancos con ≥3 documentos)")
            plt.tight_layout()
            fig.savefig(charts_dir / "per_bank_heatmap.png", dpi=150)
            plt.close(fig)
            print("  → per_bank_heatmap.png")

    # 4. Processing time distribution
    times = merged[merged["status"] == "success"]["time_seconds"]
    if len(times) > 0:
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.hist(times, bins=25, color="#4C72B0", edgecolor="white", alpha=0.8)
        ax.axvline(times.mean(), color="red", linestyle="--", label=f"Media: {times.mean():.1f}s")
        ax.axvline(
            times.median(), color="orange", linestyle="--", label=f"Mediana: {times.median():.1f}s"
        )
        ax.set_title("Distribución de Tiempo de Procesamiento")
        ax.set_xlabel("Tiempo (segundos)")
        ax.set_ylabel("Frecuencia")
        ax.legend()
        plt.tight_layout()
        fig.savefig(charts_dir / "processing_time.png", dpi=150)
        plt.close(fig)
        print("  → processing_time.png")

    # 5. Match type breakdown (stacked bar)
    fig, ax = plt.subplots(figsize=(8, 5))
    match_data = {}
    for field, label in zip(fields, field_labels):
        types = metrics[field]["match_types"]
        match_data[label] = types

    all_types = set()
    for types in match_data.values():
        all_types.update(types.keys())

    type_colors = {
        "exact_match": "#2ca02c",
        "partial_match": "#98df8a",
        "alias_match": "#aec7e8",
        "no_match": "#ff7f0e",
        "not_extracted": "#d62728",
        "default_value": "#d62728",
        "invalid_length": "#ff9896",
        "error": "#7f7f7f",
    }

    bottom = np.zeros(len(field_labels))
    for mtype in sorted(all_types):
        values = [match_data[label].get(mtype, 0) for label in field_labels]
        color = type_colors.get(mtype, "#888888")
        ax.bar(field_labels, values, bottom=bottom, label=mtype, color=color)
        bottom += np.array(values)

    ax.set_title("Desglose de Tipos de Match por Campo")
    ax.set_ylabel("Cantidad de Documentos")
    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    fig.savefig(charts_dir / "match_type_breakdown.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("  → match_type_breakdown.png")

    # 6. CLABE digit difference histogram (for non-exact matches)
    digit_diffs = merged[(merged["clabe_digit_diff"].notna()) & (merged["clabe_digit_diff"] > 0)][
        "clabe_digit_diff"
    ]
    if len(digit_diffs) > 0:
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.hist(digit_diffs, bins=range(0, 19), color="#ff7f0e", edgecolor="white", alpha=0.8)
        ax.set_title("Diferencia de Dígitos en CLABE (errores)")
        ax.set_xlabel("Dígitos diferentes")
        ax.set_ylabel("Frecuencia")
        ax.set_xticks(range(0, 19))
        plt.tight_layout()
        fig.savefig(charts_dir / "clabe_digit_diff.png", dpi=150)
        plt.close(fig)
        print("  → clabe_digit_diff.png")

    print(f"\nAll charts saved to: {charts_dir}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="Run paper validation experiment")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of files")
    parser.add_argument(
        "--analyze-only",
        type=str,
        default=None,
        help="Path to existing results CSV (skip extraction)",
    )
    parser.add_argument("--no-charts", action="store_true", help="Skip chart generation")
    args = parser.parse_args()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = RESULTS_DIR / f"run_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("EXPERIMENT: Paper Validation - Bank Statement Extraction")
    print(f"Output: {output_dir}")
    print("=" * 60)

    # Step 1: Run extraction or load existing results
    if args.analyze_only:
        print(f"\n→ Loading existing results from: {args.analyze_only}")
        results_df = pd.read_csv(args.analyze_only, dtype={"account_pred": str})
        # Ensure CLABEs are zero-padded to 18 digits
        if "account_pred" in results_df.columns:
            results_df["account_pred"] = (
                results_df["account_pred"].astype(str).str.strip().str.zfill(18)
            )
    else:
        pdf_files = get_pdf_files(PDF_DIR)
        if args.limit:
            pdf_files = pdf_files[: args.limit]

        print(f"\n→ Running extraction on {len(pdf_files)} files...")
        results_df = run_extraction(pdf_files)

        results_csv = output_dir / "extraction_results.csv"
        import csv

        results_df.to_csv(results_csv, index=False, quoting=csv.QUOTE_NONNUMERIC)
        print(f"\n→ Results saved to: {results_csv}")

    # Step 2: Load ground truth and analyze
    print("\n→ Loading ground truth and analyzing...")
    gt_df = load_ground_truth()
    merged = analyze_results(results_df, gt_df)

    merged_csv = output_dir / "merged_analysis.csv"
    merged.to_csv(merged_csv, index=False)
    print(f"→ Merged analysis saved to: {merged_csv}")

    # Step 3: Compute summary metrics
    print("\n→ Computing metrics...")
    metrics = compute_summary_metrics(merged)

    metrics_json = output_dir / "metrics.json"
    with open(metrics_json, "w") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
    print(f"→ Metrics saved to: {metrics_json}")

    # Step 4: Print summary
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    print(f"Total files: {metrics['total_files']}")
    print(f"Successful:  {metrics['successful_extractions']}")
    print(f"Errors:      {metrics['errors']}")
    print()

    header = (
        f"{'Campo':<12} {'Acc Total':>10} {'Acc Cond':>10}"
        f" {'Correct':>8} {'Attempted':>10} {'Sim Mean':>10}"
    )
    print(header)
    print("-" * len(header))
    for field, label in [("owner", "Titular"), ("clabe", "CLABE"), ("bank", "Banco")]:
        m = metrics[field]
        print(
            f"{label:<12} {m['accuracy_total']:>10.4f} {m['accuracy_conditional']:>10.4f} "
            f"{m['correct']:>8} {m['attempted']:>10} {m['similarity_mean']:>10.4f}"
        )

    if "timing" in metrics:
        print(
            f"\nTiempo promedio: {metrics['timing']['mean_seconds']:.1f}s "
            f"(mediana: {metrics['timing']['median_seconds']:.1f}s)"
        )
        print(f"Tiempo total:    {metrics['timing']['total_minutes']:.1f} minutos")

    # Step 5: Generate charts
    if not args.no_charts:
        print("\n→ Generating charts...")
        generate_charts(merged, metrics, output_dir)

    print(f"\n✓ Experiment complete! All outputs in: {output_dir}")


if __name__ == "__main__":
    main()
