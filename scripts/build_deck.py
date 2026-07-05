from attribution_roi.pipeline import build_reports, run_analysis


if __name__ == "__main__":
    build_reports(run_analysis())
    print("Built reports/strategy_deck.md.")
