"""Step 3 数据质量校验：对原始与清洗后数据做完整性/一致性/唯一性检测，
输出可追溯的 Markdown 质量报告到 results/。"""
import sys
from pathlib import Path
from datetime import datetime
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import pandas as pd
from configs import config as C


def load_both():
    dtypes = {C.COL_USER:"int64", C.COL_ITEM:"int64",
              C.COL_CATEGORY:"int64", C.COL_BEHAVIOR:"int8"}
    raw = pd.read_csv(C.RAW_FILE, dtype=dtypes, parse_dates=[C.COL_TIME])
    cleaned = pd.read_parquet(C.INTERIM_DIR / "cleaned.parquet")
    return raw, cleaned


def run_checks(raw, cleaned):
    lines = []
    def log(s):
        print(s)
        lines.append(s)

    log(f"# 数据质量报告\n")
    log(f"生成时间：{datetime.now():%Y-%m-%d %H:%M:%S}\n")

    # ---- 1. 完整性 ----
    log("## 1. 完整性检查\n")
    log(f"- 原始行数：{len(raw):,}")
    log(f"- 清洗后行数：{len(cleaned):,}（聚合去重后）")
    log(f"- 原始空值总数：{int(raw.isna().sum().sum())}")
    log(f"- 清洗后空值总数：{int(cleaned.isna().sum().sum())}\n")

    # ---- 2. 一致性 ----
    log("## 2. 一致性检查\n")
    illegal = (~raw[C.COL_BEHAVIOR].isin(C.VALID_BEHAVIORS)).sum()
    log(f"- 非法 behavior 取值行数：{illegal}")
    log(f"- behavior 取值集合：{sorted(raw[C.COL_BEHAVIOR].unique())}")
    # item→category 映射是否唯一（一个商品是否只属于一个类目）
    map_check = raw.groupby(C.COL_ITEM)[C.COL_CATEGORY].nunique()
    multi_cat = (map_check > 1).sum()
    log(f"- 映射到多个类目的商品数：{multi_cat}（应为 0）\n")

    # ---- 3. 唯一性 ----
    log("## 3. 唯一性检查\n")
    key = [C.COL_USER, C.COL_ITEM, C.COL_CATEGORY, C.COL_BEHAVIOR, C.COL_TIME]
    dup_after = cleaned.duplicated(key).sum()
    log(f"- 清洗后四元组重复数：{dup_after}（聚合后应为 0）")
    log(f"- count 字段范围：{cleaned['count'].min()} ~ {cleaned['count'].max()}\n")

    # ---- 4. 分布概览 ----
    log("## 4. 关键分布\n")
    log(f"- 唯一用户数：{cleaned[C.COL_USER].nunique():,}")
    log(f"- 唯一商品数：{cleaned[C.COL_ITEM].nunique():,}")
    log(f"- 唯一类目数：{cleaned[C.COL_CATEGORY].nunique():,}")
    log(f"- 时间区间：{cleaned[C.COL_TIME].min()} ~ {cleaned[C.COL_TIME].max()}")
    bh = cleaned.groupby(C.COL_BEHAVIOR)["count"].sum()
    log("- 各行为总次数（还原频次后）：")
    for b, cnt in bh.items():
        log(f"    - {C.BEHAVIOR_MAP[b]}({b})：{int(cnt):,}")

    return "\n".join(lines)


def main():
    raw, cleaned = load_both()
    report = run_checks(raw, cleaned)
    C.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out = C.RESULTS_DIR / "quality_report.md"
    out.write_text(report, encoding="utf-8")
    print(f"\n[save] 质量报告已保存：{out}")


if __name__ == "__main__":
    main()
