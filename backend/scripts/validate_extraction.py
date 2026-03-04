import argparse
import sys
from pathlib import Path

import pandas as pd

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.infrastructure.evaluation.metrics import (
    validate_bank,
    validate_clabe,
    validate_owner,
)


def main():
    parser = argparse.ArgumentParser(description="Validate extraction results against ground truth")
    parser.add_argument(
        "--results",
        type=str,
        default="data/results/bank_extraction_comparison.csv",
        help="Path to extraction results CSV",
    )
    parser.add_argument(
        "--ground-truth",
        type=str,
        default="data/processed/pdfs/bank_accounts_filtered.csv",
        help="Path to ground truth CSV",
    )

    args = parser.parse_args()

    results_path = project_root / args.results
    ground_truth_path = project_root / args.ground_truth

    results_df = pd.read_csv(results_path)
    ground_truth_df = pd.read_csv(ground_truth_path)

    results_df["downloaded_file"] = results_df["file_name"]

    merged = pd.merge(
        results_df,
        ground_truth_df[["downloaded_file", "Owner", "CLABE", "banco"]],
        on="downloaded_file",
        how="inner",
        suffixes=("_pred", "_actual"),
    )

    print("=" * 100)
    print("EXTRACTION VALIDATION REPORT")
    print("=" * 100)

    parsers = merged["parser"].unique()

    for parser_name in parsers:
        parser_df = merged[merged["parser"] == parser_name]

        print(f"\n\n{'=' * 100}")
        print(f"PARSER: {parser_name.upper()}")
        print(f"{'=' * 100}")

        metrics = {
            "owner": {"correct": 0, "incorrect": 0, "not_extracted": 0, "total": 0},
            "clabe": {"correct": 0, "incorrect": 0, "not_extracted": 0, "total": 0},
            "bank": {"correct": 0, "incorrect": 0, "not_extracted": 0, "total": 0},
        }

        details = []

        for _, row in parser_df.iterrows():
            file_name = row["downloaded_file"]

            owner_correct, owner_type = validate_owner(str(row.get("owner", "")), str(row["Owner"]))
            clabe_correct, clabe_type = validate_clabe(
                str(row.get("account_number", "")), str(row["CLABE"])
            )
            bank_correct, bank_type = validate_bank(
                str(row.get("bank_name", "")), str(row["banco"])
            )

            metrics["owner"]["total"] += 1
            metrics["clabe"]["total"] += 1
            metrics["bank"]["total"] += 1

            if owner_correct:
                metrics["owner"]["correct"] += 1
            elif owner_type == "not_extracted":
                metrics["owner"]["not_extracted"] += 1
            else:
                metrics["owner"]["incorrect"] += 1

            if clabe_correct:
                metrics["clabe"]["correct"] += 1
            elif clabe_type in ["default_value", "not_extracted"]:
                metrics["clabe"]["not_extracted"] += 1
            else:
                metrics["clabe"]["incorrect"] += 1

            if bank_correct:
                metrics["bank"]["correct"] += 1
            elif bank_type == "not_extracted":
                metrics["bank"]["not_extracted"] += 1
            else:
                metrics["bank"]["incorrect"] += 1

            details.append(
                {
                    "file": file_name,
                    "owner": "✓"
                    if owner_correct
                    else ("✗" if owner_type != "not_extracted" else "-"),
                    "clabe": "✓"
                    if clabe_correct
                    else ("✗" if clabe_type not in ["default_value", "not_extracted"] else "-"),
                    "bank": "✓" if bank_correct else ("✗" if bank_type != "not_extracted" else "-"),
                    "owner_pred": str(row.get("owner", ""))[:30],
                    "owner_actual": str(row["Owner"])[:30],
                    "clabe_pred": str(row.get("account_number", "")),
                    "clabe_actual": str(row["CLABE"]),
                    "bank_pred": str(row.get("bank_name", "")),
                    "bank_actual": str(row["banco"]),
                }
            )

        print("\nOVERALL ACCURACY:")
        total = metrics["owner"]["total"]

        for field in ["owner", "clabe", "bank"]:
            correct = metrics[field]["correct"]
            incorrect = metrics[field]["incorrect"]
            not_extracted = metrics[field]["not_extracted"]

            accuracy = (correct / total * 100) if total > 0 else 0
            print(f"\n  {field.upper()}:")
            print(f"    Correct:       {correct}/{total} ({accuracy:.1f}%)")
            print(f"    Incorrect:     {incorrect}/{total} ({incorrect / total * 100:.1f}%)")
            print(
                f"    Not Extracted: {not_extracted}/{total} ({not_extracted / total * 100:.1f}%)"
            )

        print("\n\nDETAILED RESULTS:")
        print(f"{'-' * 100}")
        print(f"{'File':<30} {'Owner':<7} {'CLABE':<7} {'Bank':<7}")
        print(f"{'-' * 100}")

        for detail in details:
            print(
                f"{detail['file']:<30} {detail['owner']:<7} "
                f"{detail['clabe']:<7} {detail['bank']:<7}"
            )

        print("\n\nFIELD COMPARISONS (showing first 50 chars):")
        print(f"{'-' * 100}")

        for detail in details:
            print(f"\n{detail['file']}:")
            if detail["owner"] != "✓":
                print(f"  Owner:   Pred: {detail['owner_pred'][:50]}")
                print(f"           Act:  {detail['owner_actual'][:50]}")
            if detail["clabe"] != "✓":
                print(f"  CLABE:   Pred: {detail['clabe_pred']}")
                print(f"           Act:  {detail['clabe_actual']}")
            if detail["bank"] != "✓":
                print(f"  Bank:    Pred: {detail['bank_pred']}")
                print(f"           Act:  {detail['bank_actual']}")

    print(f"\n\n{'=' * 100}")
    print("SUMMARY")
    print(f"{'=' * 100}\n")

    summary = []
    for parser_name in parsers:
        parser_df = merged[merged["parser"] == parser_name]

        total = len(parser_df)
        owner_correct = sum(
            1
            for _, row in parser_df.iterrows()
            if validate_owner(str(row.get("owner", "")), str(row["Owner"]))[0]
        )
        clabe_correct = sum(
            1
            for _, row in parser_df.iterrows()
            if validate_clabe(str(row.get("account_number", "")), str(row["CLABE"]))[0]
        )
        bank_correct = sum(
            1
            for _, row in parser_df.iterrows()
            if validate_bank(str(row.get("bank_name", "")), str(row["banco"]))[0]
        )

        avg_accuracy = ((owner_correct + clabe_correct + bank_correct) / (total * 3)) * 100

        summary.append(
            {
                "Parser": parser_name.replace("_parser", "").upper(),
                "Owner": f"{owner_correct}/{total} ({owner_correct / total * 100:.1f}%)",
                "CLABE": f"{clabe_correct}/{total} ({clabe_correct / total * 100:.1f}%)",
                "Bank": f"{bank_correct}/{total} ({bank_correct / total * 100:.1f}%)",
                "Average": f"{avg_accuracy:.1f}%",
                "Score": avg_accuracy,
            }
        )

    summary_df = pd.DataFrame(summary).sort_values("Score", ascending=False)

    print(f"{'Parser':<15} {'Owner':<20} {'CLABE':<20} {'Bank':<20} {'Average':<10}")
    print(f"{'-' * 100}")
    for _, row in summary_df.iterrows():
        print(
            f"{row['Parser']:<15} {row['Owner']:<20} {row['CLABE']:<20} "
            f"{row['Bank']:<20} {row['Average']:<10}"
        )

    print(f"\n{'=' * 100}")
    print(
        f"WINNER: {summary_df.iloc[0]['Parser']} with "
        f"{summary_df.iloc[0]['Average']} average accuracy"
    )
    print(f"{'=' * 100}\n")


if __name__ == "__main__":
    main()
