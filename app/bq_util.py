import os
from pathlib import Path

from dotenv import load_dotenv
from icecream import ic

from bigquery_utils.config_util import BqConfig

load_dotenv(".env")

TR_ITEMS_CONFIG = os.environ.get("TR_ITEMS_CONFIG")
TR_ITEMS_CONFIG = Path(TR_ITEMS_CONFIG)
ic(TR_ITEMS_CONFIG)
bq_config = BqConfig(config_path=TR_ITEMS_CONFIG)
ic(bq_config)

