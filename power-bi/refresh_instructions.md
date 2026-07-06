# Refresh Instructions

```bash
python scripts/run_all.py
python scripts/run_sql.py
```

The SQL runner writes the exact CSV files in `data/powerbi/`. If OneDrive locks an existing generated CSV, the runner keeps the existing file and prints the expected row count.

Open the manually built `.pbix`, verify the CSV source paths, and use Home -> Refresh.
