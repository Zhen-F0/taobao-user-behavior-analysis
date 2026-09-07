"""诊断四元组重复的真实性质：看它们是同类行为的高频，还是异常。"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import pandas as pd
from configs import config as C

dtypes = {C.COL_USER:"int64", C.COL_ITEM:"int64", C.COL_CATEGORY:"int64", C.COL_BEHAVIOR:"int8"}
df = pd.read_csv(C.RAW_FILE, dtype=dtypes, parse_dates=[C.COL_TIME])

# 每个四元组出现的次数分布
grp = df.groupby([C.COL_USER, C.COL_ITEM, C.COL_BEHAVIOR, C.COL_TIME]).size()
print("=== 四元组出现次数的分布 ===")
print(grp.value_counts().sort_index().head(20))
print("\n出现次数的描述统计：")
print(grp.describe())

# 重复主要集中在哪种行为？（浏览 pv 大概率最多）
dup_rows = df[df.duplicated([C.COL_USER, C.COL_ITEM, C.COL_BEHAVIOR, C.COL_TIME], keep=False)]
print("\n=== 参与重复的记录里，各 behavior 占比 ===")
print(dup_rows[C.COL_BEHAVIOR].value_counts())

# 看一个具体例子：挑一个重复最多的四元组
top = grp.sort_values(ascending=False).head(3)
print("\n=== 重复次数最多的 3 个四元组 ===")
print(top)
