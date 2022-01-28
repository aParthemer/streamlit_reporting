from __future__ import annotations
from collections import namedtuple
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Union, Dict

import pandas as pd
import yaml

import CONSTANTS as C

class ConfigParser:

    def __init__(self, config_path: Union[Path, str]):

        self.config_path = Path(config_path)

    @property
    def config(self) -> dict:
        _config_path = self.config_path
        with open(_config_path, "r") as f:
            config = yaml.safe_load(f)
            return config

    @property
    def table_name(self) -> str:
        return self.config["table_name"]

    @property
    def column_mapper(self) -> dict:
        return self.config["column_mapper"]

    @property
    def column_prefix(self) -> str:
        return self.config["column_prefix"]

    @property
    def type_conversions(self) -> dict:
        return self.config["type_conversions"]

    @property
    def datetime_column(self) -> str:
        return self.config.get("datetime_column", None)

    def apply_column_mapper(self,
                            df: pd.DataFrame) -> pd.DataFrame:

        _mapper = self.column_mapper

        if (
                all([c in df.columns for c in _mapper.values()]) and
                all([c in _mapper.values() for c in df.columns])
        ):
            return df
        elif all([c in _mapper.keys() for c in df.columns]):
            return df.rename(columns=_mapper)

        else:
            unexpected = [c for c in df.columns if c not in _mapper.keys()]
            not_found = [c for c in _mapper.keys() if c not in df.columns]
            _table_name = self.table_name
            e = f"Error parsing config for table: `{_table_name}`"
            if not_found:
                e += f"\n    Expected columns not found in DataFrame: {not_found}."
            if unexpected:
                e += f"\n    Unexpected columns found in DataFrame: {unexpected}."
            raise Exception(e)

    def apply_type_conversions(self,
                               df: pd.DataFrame) -> pd.DataFrame:

        _conversions = self.type_conversions

        for c in _conversions:
            _name = c["name"]
            _type = c["type"]

            if _type == "datetime":
                _formatter = c["formatter"]
                df[_name] = pd.to_datetime(df[_name], format=_formatter)

            else:
                df[_name] = df[_name].astype(dtype=_type)

        return df

    def __repr__(self):
        return str(self.config)

    def __eq__(self,
               other:ConfigParser) -> bool:
        if self.table_name == other.table_name:
            return True
        else:
            return False

@dataclass(frozen=True)
class CONFIG_SCHEMAS:
    sk_transactions: ConfigParser = ConfigParser(C.DIR_TABLE_CONFIGS / "sk_transactions.yml")
    sk_transaction_items: ConfigParser = ConfigParser(C.DIR_TABLE_CONFIGS / "sk_transaction_items.yml")

def detect_config(df: pd.DataFrame,
                  config_schemas: List[ConfigParser]) -> ConfigParser:

    df_cols = df.columns

    selected_config = None
    for config in config_schemas:
        col_mapper = config.column_mapper
        if all(
            [c in col_mapper.keys() for c in df_cols] or
            [c in col_mapper.values() for c in df_cols]
        ):
            selected_config = config

    if selected_config is None:
        e = f"Failed to detect schema from DataFrame with columns: {df_cols}."
        raise ValueError(e)

    else:
        return selected_config



