from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
SYNTHETIC_DATA_DIR = DATA_DIR / "synthetic"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"

SYNTHETIC_TOUCHPOINTS_PATH = SYNTHETIC_DATA_DIR / "customer_journeys.csv"

CHANNELS = [
    "Display",
    "Paid Social",
    "Referral",
    "Organic Search",
    "Paid Search",
    "Affiliate",
    "Email",
    "Direct",
]

CHANNEL_STAGE = {
    "Display": "Awareness",
    "Paid Social": "Awareness",
    "Referral": "Consideration",
    "Organic Search": "Consideration",
    "Paid Search": "Consideration",
    "Affiliate": "Consideration",
    "Email": "Decision",
    "Direct": "Decision",
}

# Synthetic current-quarter spend assumption for a mid-size e-commerce business.
# It intentionally reflects a last-touch-heavy operating model that favors
# branded demand capture over upper-funnel demand creation.
CURRENT_QUARTER_BUDGET = {
    "Display": 14000.0,
    "Paid Social": 18000.0,
    "Referral": 6000.0,
    "Organic Search": 24000.0,
    "Paid Search": 55000.0,
    "Affiliate": 20000.0,
    "Email": 22000.0,
    "Direct": 15000.0,
}

RANDOM_SEED = 42
