from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"

TOUCHPOINTS_PATH = PROCESSED_DATA_DIR / "criteo_touchpoints_sample.csv"
RAW_CRITEO_PARQUET_PATH = RAW_DATA_DIR / "criteo_day1_part-00238.parquet"

CHANNELS = [
    "Publisher 01",
    "Publisher 02",
    "Publisher 03",
    "Publisher 04",
    "Publisher 05",
    "Publisher 06",
    "Publisher 07",
    "Publisher 08",
    "Long-tail placements",
]

CHANNEL_STAGE = {
    "Publisher 01": "Display placement",
    "Publisher 02": "Display placement",
    "Publisher 03": "Display placement",
    "Publisher 04": "Display placement",
    "Publisher 05": "Display placement",
    "Publisher 06": "Display placement",
    "Publisher 07": "Display placement",
    "Publisher 08": "Display placement",
    "Long-tail placements": "Display placement",
}

# Assumed pilot budget for a mid-size e-commerce business. The sourced Criteo
# data includes anonymized impressions, clicks, campaigns, publishers, and sales
# labels, but not marketer spend/revenue by publisher. Budget ROI therefore uses
# this explicit business assumption rather than pretending the source contains it.
CURRENT_QUARTER_BUDGET = {
    "Publisher 01": 42000.0,
    "Publisher 02": 28000.0,
    "Publisher 03": 19000.0,
    "Publisher 04": 12000.0,
    "Publisher 05": 11000.0,
    "Publisher 06": 9000.0,
    "Publisher 07": 8000.0,
    "Publisher 08": 7000.0,
    "Long-tail placements": 38000.0,
}

RANDOM_SEED = 42
ASSUMED_CONTRIBUTION_PER_SALE = 120.0

CRITEO_SOURCE_URL = (
    "https://huggingface.co/datasets/criteo/CriteoPrivateAd/resolve/main/"
    "data/day_int=1/part-00238-7fb458b7-00d9-490c-b19b-addd568a5fe9-c000.gz.parquet"
)
CRITEO_DATASET_CARD_URL = "https://huggingface.co/datasets/criteo/CriteoPrivateAd"
