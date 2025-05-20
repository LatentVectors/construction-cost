from pathlib import Path

from dotenv import load_dotenv
from loguru import logger

# Load environment variables from .env file if it exists
load_dotenv()

# Paths
PROJ_ROOT = Path(__file__).resolve().parents[1]
logger.info(f"PROJ_ROOT path is: {PROJ_ROOT}")

DATA_DIR = PROJ_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
INTERIM_DATA_DIR = DATA_DIR / "interim"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXTERNAL_DATA_DIR = DATA_DIR / "external"

COST_HISTORY_USD = PROCESSED_DATA_DIR / "construction_cost_history_usd.csv"
COST_HISTORY_PERCENT = PROCESSED_DATA_DIR / "construction_cost_history.csv"
COST_DETAIL_SUBTOTALS = PROCESSED_DATA_DIR / "construction_cost_subtotals.csv"
COST_DETAIL_TOTALS = PROCESSED_DATA_DIR / "construction_cost_totals.csv"
COST_BREAKDOWN = PROCESSED_DATA_DIR / "cost_breakdown.csv"
MEDIAN_INCOME = PROCESSED_DATA_DIR / "median_income.csv"
SQUARE_FOOTAGE = PROCESSED_DATA_DIR / "square_footage.csv"

MODELS_DIR = PROJ_ROOT / "models"

REPORTS_DIR = PROJ_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

# If tqdm is installed, configure loguru with tqdm.write
# https://github.com/Delgan/loguru/issues/135
try:
    from tqdm import tqdm

    logger.remove(0)
    logger.add(lambda msg: tqdm.write(msg, end=""), colorize=True)
except ModuleNotFoundError:
    pass
