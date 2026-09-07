"""Step 2 清洗主流程：加载 → 时间校验 → 四元组聚合(保留频次 count) → 存中间文件。

设计说明（写进报告）：
- 该数据 time 仅精确到小时，四元组"重复"实为同一小时内的高频行为（主要是浏览），
  占比约 49%。直接删除会摧毁行为频次信息，故采用"聚合计数"：合并重复四元组，
  新增 count 记录该小时内行为次数，信息零丢失。
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import pandas as pd
from configs import config as C


def load_raw() -> pd.DataFrame:
    """加载原始数据，读入即指定 dtype 压内存，time 解析为 datetime。"""
    dtypes = {
        C.COL_USER: "int64",
        C.COL_ITEM: "int64",
        C.COL_CATEGORY: "int64",
        C.COL_BEHAVIOR: "int8",
    }
    df = pd.read_csv(C.RAW_FILE, dtype=dtypes, parse_dates=[C.COL_TIME])
    print(f"[load] 原始行数：{len(df):,}")
    return df


def validate_time(df: pd.DataFrame) -> pd.DataFrame:
    """时间有效性校验：剔除空值/超出数据集区间的记录。区间以数据实际范围为准。"""
    t_min, t_max = df[C.COL_TIME].min(), df[C.COL_TIME].max()
    print(f"[time] 数据时间区间：{t_min} ~ {t_max}")

    before = len(df)
    mask = df[C.COL_TIME].notna() & (df[C.COL_TIME] >= t_min) & (df[C.COL_TIME] <= t_max)
    df = df[mask]
    print(f"[time] 时间校验剔除：{before - len(df):,} 行")
    return df


def validate_behavior(df: pd.DataFrame) -> pd.DataFrame:
    """一致性校验：behavior 只保留合法取值 1/2/3/4。"""
    before = len(df)
    df = df[df[C.COL_BEHAVIOR].isin(C.VALID_BEHAVIORS)]
    print(f"[behavior] 非法行为剔除：{before - len(df):,} 行")
    return df


def aggregate_dedup(df: pd.DataFrame) -> pd.DataFrame:
    """四元组聚合去重：合并重复，用 count 保留同一小时内的行为频次。"""
    before = len(df)
    df = (
        df.groupby(
            [C.COL_USER, C.COL_ITEM, C.COL_CATEGORY, C.COL_BEHAVIOR, C.COL_TIME],
            as_index=False,
        )
        .size()
        .rename(columns={"size": "count"})
    )
    print(f"[dedup] 聚合前：{before:,} 行 → 聚合后：{len(df):,} 行")
    print(f"[dedup] count 分布：min={df['count'].min()}, "
          f"max={df['count'].max()}, mean={df['count'].mean():.2f}")
    return df


def main():
    df = load_raw()
    df = validate_time(df)
    df = validate_behavior(df)
    df = aggregate_dedup(df)

    C.INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    out = C.INTERIM_DIR / "cleaned.parquet"
    df.to_parquet(out, index=False)
    print(f"[save] 已保存清洗结果：{out}")
    print(f"[save] 最终列：{list(df.columns)}")


if __name__ == "__main__":
    main()
