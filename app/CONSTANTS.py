from pathlib import Path

DIR_ROOT = Path(__file__).parent.parent

DIR_APP = DIR_ROOT.joinpath("app")
DIR_DATA = DIR_ROOT.joinpath("data")

DIR_TABLE_CONFIGS = DIR_APP.joinpath("table_configs")

if __name__ == '__main__':
    print(DIR_ROOT,
          sep="\n")
