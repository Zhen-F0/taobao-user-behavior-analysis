"""任务四：构建用户/商品/时间三张基础聚合中间表，为第二周特征工程预计算。
输入 cleaned.parquet，输出三张 Parquet 到 data/processed/。
所有次数均基于 count 还原真实频次。"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import pandas as pd
from configs import config as C


def load_cleaned():
    df = pd.read_parquet(C.INTERIM_DIR / "cleaned.parquet")
    # 加一列行为语义名，便于透视
    df["bh_name"] = df[C.COL_BEHAVIOR].map(C.BEHAVIOR_MAP)
    return df


def build_user_dim(df):
    """用户维度：各行为次数、活跃天数、首末行为时间、交互商品数。"""
    # 各行为次数（透视：pv/fav/cart/buy 各一列）
    pivot = (df.pivot_table(index=C.COL_USER, columns="bh_name",
                            values="count", aggfunc="sum", fill_value=0)
               .add_prefix("cnt_"))
    base = df.groupby(C.COL_USER).agg(
        total_actions=("count", "sum"),
        active_days=(C.COL_TIME, lambda s: s.dt.date.nunique()),
        unique_items=(C.COL_ITEM, "nunique"),
        first_time=(C.COL_TIME, "min"),
        last_time=(C.COL_TIME, "max"),
    )
    user_dim = base.join(pivot).reset_index()
    return user_dim


def build_item_dim(df):
    """商品维度：被各行为次数、交互用户数、所属类目、各环节转化率。"""
    pivot = (df.pivot_table(index=C.COL_ITEM, columns="bh_name",
                            values="count", aggfunc="sum", fill_value=0)
               .add_prefix("cnt_"))
    base = df.groupby(C.COL_ITEM).agg(
        item_category=(C.COL_CATEGORY, "first"),
        unique_users=(C.COL_USER, "nunique"),
    )
    item_dim = base.join(pivot).reset_index()
    # 转化率（避免除零）
    for col in ["cnt_pv", "cnt_fav", "cnt_cart", "cnt_buy"]:
        if col not in item_dim.columns:
            item_dim[col] = 0
    item_dim["cvr_pv2buy"] = item_dim["cnt_buy"] / item_dim["cnt_pv"].replace(0, pd.NA)
    return item_dim


def build_time_dim(df):
    """时间维度：按天聚合各行为次数 + 活跃用户数（供趋势分析）。"""
    d = df.copy()
    d["date"] = d[C.COL_TIME].dt.date
    pivot = (d.pivot_table(index="date", columns="bh_name",
                           values="count", aggfunc="sum", fill_value=0)
               .add_prefix("cnt_"))
    users = d.groupby("date")[C.COL_USER].nunique().rename("active_users")
    time_dim = pivot.join(users).reset_index()
    return time_dim


def main():
    df = load_cleaned()
    C.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    user_dim = build_user_dim(df)
    user_dim.to_parquet(C.PROCESSED_DIR / "user_dim.parquet", index=False)
    print(f"[user_dim]  {user_dim.shape} → {list(user_dim.columns)}")

    item_dim = build_item_dim(df)
    item_dim.to_parquet(C.PROCESSED_DIR / "item_dim.parquet", index=False)
    print(f"[item_dim]  {item_dim.shape} → {list(item_dim.columns)}")

    time_dim = build_time_dim(df)
    time_dim.to_parquet(C.PROCESSED_DIR / "time_dim.parquet", index=False)
    print(f"[time_dim]  {time_dim.shape} → {list(time_dim.columns)}")

    print("\n[time_dim] 预览：")
    print(time_dim.head())


if __name__ == "__main__":
    main()
