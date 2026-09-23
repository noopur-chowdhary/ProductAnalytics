from __future__ import annotations

import argparse
import pandas as pd

from productpulse.orchestration import (
    run_cookie_cats,
    run_criteo,
    run_online_retail,
    run_retailrocket,
)
from productpulse.services.results import ResultStore


def main():
    parser = argparse.ArgumentParser(
        prog="productpulse",
        description="ProductPulse analytics and ML pipelines",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    run_parser = subparsers.add_parser(
        "run",
        help="Run a ProductPulse pipeline",
    )

    run_parser.add_argument(
        "pipeline",
        choices=[
            "cookie-cats",
            "criteo",
            "online-retail",
            "retailrocket",
        ],
    )

    run_parser.add_argument(
        "--criteo-per-arm",
        type=int,
        default=100_000,
    )

    args = parser.parse_args()
    store = ResultStore()

    # ---------------------------------------------------------
    # Cookie Cats
    # ---------------------------------------------------------

    if args.pipeline == "cookie-cats":
        result = run_cookie_cats()

        retention = pd.DataFrame([
            result["retention_1"],
            result["retention_7"],
        ])

        store.save_csv(
            "cookie_cats/retention.csv",
            retention,
        )

        store.save_json(
            "cookie_cats/rounds.json",
            result["rounds"],
        )

        store.save_json(
            "cookie_cats/summary.json",
            {
                "rows": result["rows"],
                "retention_1_action":
                    result["retention_1_action"],
                "retention_7_action":
                    result["retention_7_action"],
            },
        )

        print("\nCookie Cats")
        print("=" * 60)
        print(retention.to_string(index=False))

        print(
            "\nRetention 1 action:",
            result["retention_1_action"],
        )

        print(
            "Retention 7 action:",
            result["retention_7_action"],
        )

        print(
            "\nSaved results to results/cookie_cats/"
        )

    # ---------------------------------------------------------
    # Criteo
    # ---------------------------------------------------------

    elif args.pipeline == "criteo":
        result = run_criteo(
            rows_per_arm=args.criteo_per_arm,
        )

        store.save_csv(
            "criteo/targeting_table.csv",
            result["targeting_table"],
        )

        store.save_json(
            "criteo/summary.json",
            {
                "rows": result["rows"],
                "train_rows": result["train_rows"],
                "test_rows": result["test_rows"],
                "mean_treatment_score":
                    result["mean_treatment_score"],
                "mean_control_score":
                    result["mean_control_score"],
                "mean_predicted_uplift":
                    result["mean_predicted_uplift"],
                "qini_coefficient":
                    result["qini_coefficient"],
            },
        )

        print("\nCriteo Uplift")
        print("=" * 60)

        print(
            "Mean predicted uplift:",
            result["mean_predicted_uplift"],
        )

        print(
            "Qini coefficient:",
            result["qini_coefficient"],
        )

        print("\nTargeting table:")
        print(
            result["targeting_table"]
            .to_string(index=False)
        )

        print(
            "\nSaved results to results/criteo/"
        )

    # ---------------------------------------------------------
    # Online Retail
    # ---------------------------------------------------------

    elif args.pipeline == "online-retail":
        result = run_online_retail()

        split_summary = (
            pd.DataFrame
            .from_dict(
                result["split_summary"],
                orient="index",
            )
            .reset_index()
            .rename(
                columns={"index": "split"}
            )
        )

        store.save_csv(
            "online_retail/split_summary.csv",
            split_summary,
        )

        store.save_json(
            "online_retail/summary.json",
            {
                "clean_rows": result["clean_rows"],
                "customers": result["customers"],
                "total_revenue":
                    result["total_revenue"],
                "date_start":
                    result["date_start"],
                "date_end":
                    result["date_end"],
            },
        )

        print("\nOnline Retail")
        print("=" * 60)

        print(
            "Clean rows:",
            result["clean_rows"],
        )

        print(
            "Customers:",
            result["customers"],
        )

        print(
            "Revenue:",
            result["total_revenue"],
        )

        print("\nSplits:")
        print(
            split_summary.to_string(
                index=False
            )
        )

        print(
            "\nSaved results to results/online_retail/"
        )

    # ---------------------------------------------------------
    # Retailrocket
    # ---------------------------------------------------------

    elif args.pipeline == "retailrocket":
        result = run_retailrocket()

        store.save_csv(
            "retailrocket/validation_metrics.csv",
            result["validation_metrics"],
        )

        store.save_csv(
            "retailrocket/test_metrics.csv",
            result["test_metrics"],
        )

        store.save_json(
            "retailrocket/summary.json",
            {
                "selected_model":
                    result["selected_model"],
                "split_rows":
                    result["split_rows"],
            },
        )

        print("\nRetailrocket")
        print("=" * 60)

        print(
            "Selected model:",
            result["selected_model"],
        )

        print("\nValidation:")
        print(
            result["validation_metrics"]
            .to_string(index=False)
        )

        print("\nTest:")
        print(
            result["test_metrics"]
            .to_string(index=False)
        )

        print(
            "\nSaved results to results/retailrocket/"
        )


if __name__ == "__main__":
    main()
