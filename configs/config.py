"""项目全局配置：路径与常量集中管理，换数据只改这里。"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

RAW_DIR       = ROOT / "data" / "raw"
INTERIM_DIR   = ROOT / "data" / "interim"
PROCESSED_DIR = ROOT / "data" / "processed"
RESULTS_DIR   = ROOT / "results"

RAW_FILE = RAW_DIR / "user_behavior_processed.csv"

COL_TIME     = "time"
COL_USER     = "user_id"
COL_ITEM     = "item_id"
COL_CATEGORY = "item_category"
COL_BEHAVIOR = "behavior_type"

BEHAVIOR_MAP = {1: "pv", 2: "fav", 3: "cart", 4: "buy"}
VALID_BEHAVIORS = {1, 2, 3, 4}
