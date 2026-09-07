"""Step 4 异常值检测：对'每用户行为量'等派生连续量用 IQR 法则识别异常账号。
仅识别+打标+出报告，不强制删除（是否剔除由业务判断）。"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import pandas as pd
from configs import config as C


def build_user_stats(df):
    """构造每用户的派生连续量。"""
    # 还原真实行为次数：聚合数据里每行代表 count 次行为
    df = df.copy()
    stats = df.groupby(C.COL_USER).agg(
        total_actions=("count", "sum"),                 # 总行为次数
        active_days=(C.COL_TIME, lambda s: s.dt.date.nunique()),  # 活跃天数
        unique_items=(C.COL_ITEM, "nunique"),           # 交互商品数
    )
    return stats


def iqr_flags(series, k=3.0):
    """IQR 法则，k=3 为较宽松（圈极端异常）。返回上界与异常布尔。"""
    q1, q3 = series.quantile(0.25), series.quantile(0.75)
    iqr = q3 - q1
    upper = q3 + k * iqr
    return upper, series > upper


def main():
    df = pd.read_parquet(C.INTERIM_DIR / "cleaned.parquet")
    stats = build_user_stats(df)

    print("=== 每用户派生量描述统计 ===")
    print(stats.describe())

    # 对总行为次数用 IQR 圈异常（爬虫/刷单通常行为量畸高）
    upper, flag = iqr_flags(stats["total_actions"], k=3.0)
    stats["is_outlier"] = flag
    n_out = int(flag.sum())
    print(f"\n[outlier] total_actions 上界(IQR,k=3)：{upper:.0f}")
    print(f"[outlier] 疑似异常用户数：{n_out} / {len(stats)}"
          f"（{n_out/len(stats)*100:.2f}%）")
    print("\n[outlier] 行为量最高的 10 个用户：")
    print(stats.sort_values("total_actions", ascending=False).head(10))

    # 保存打标结果，供后续按需过滤
    C.INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    out = C.INTERIM_DIR / "user_outlier_flags.parquet"
    stats.reset_index().to_parquet(out, index=False)
    print(f"\n[save] 用户异常打标已保存：{out}")


if __name__ == "__main__":
    main()
