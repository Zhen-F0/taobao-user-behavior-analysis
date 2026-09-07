"""Step 1 数据探查：只读样本 + 关键统计，判断这份 processed 数据的清洗需求。"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import pandas as pd
from configs import config as C


def explore():
    # 先只读前 10 万行做快速探查，避免一上来就全量
    print("=== 抽样读取前 100000 行 ===")
    sample = pd.read_csv(C.RAW_FILE, nrows=100_000)
    print("列名：", list(sample.columns))
    print("\n前 5 行：")
    print(sample.head())
    print("\n各列 dtype：")
    print(sample.dtypes)

    # behavior 取值分布：确认是否只有 1/2/3/4
    print("\n=== behavior_type 取值分布（样本）===")
    print(sample[C.COL_BEHAVIOR].value_counts(dropna=False))

    # 全量读取关键列，做整体统计（只读 4 列省内存）
    print("\n=== 全量读取（仅关键列）做整体校验 ===")
    dtypes = {
        C.COL_USER: "int64",
        C.COL_ITEM: "int64",
        C.COL_CATEGORY: "int64",
        C.COL_BEHAVIOR: "int8",
    }
    df = pd.read_csv(C.RAW_FILE, dtype=dtypes, parse_dates=[C.COL_TIME])
    print("总行数：", len(df))

    print("\n各列空值数：")
    print(df.isna().sum())

    print("\n时间范围（定标签期基准）：")
    print("  最早：", df[C.COL_TIME].min())
    print("  最晚：", df[C.COL_TIME].max())

    print("\nbehavior 全量取值：", sorted(df[C.COL_BEHAVIOR].unique()))

    print("\n唯一用户数：", df[C.COL_USER].nunique())
    print("唯一商品数：", df[C.COL_ITEM].nunique())
    print("唯一类目数：", df[C.COL_CATEGORY].nunique())

    # 四元组重复量级（先量化，不删）
    dup = df.duplicated(subset=[C.COL_USER, C.COL_ITEM, C.COL_BEHAVIOR, C.COL_TIME]).sum()
    print(f"\n四元组完全重复行数：{dup}（占比 {dup/len(df)*100:.4f}%）")


if __name__ == "__main__":
    explore()
