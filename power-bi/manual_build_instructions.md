# Manual Build Instructions

1. Run `python scripts/run_sql.py`.
2. Open Power BI Desktop.
3. Load all CSV files from `data/powerbi/`.
4. Create relationships and DAX measures from `data_model.md` and `dax_measures.md`.
5. Build three pages:
   - Executive KPI: journey count, conversion rate, current budget, recommended budget, and budget gap by channel.
   - Attribution Diagnostics: channel credit by method, last-touch vs Markov-removal comparison, journey path table.
   - Budget Decision Support: scenario summary, estimated revenue lift, budget shifted, incremental ROAS.
6. Add footer text: `Source: CriteoPrivateAd shard via Hugging Face; budget/revenue values are documented assumptions.`
7. Save as `power-bi/marketing_attribution_roi.pbix`.

The screenshots are mockups generated from the included data.
