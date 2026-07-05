from attribution_roi.pipeline import generate_data, run_analysis


if __name__ == "__main__":
    generate_data()
    run_analysis()
    print("Generated EDA summaries, attribution outputs, and figures.")
