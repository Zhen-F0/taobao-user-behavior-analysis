"""亿级数据加载方案（工程能力展示）：用 Dask 分区惰性加载 + 并行聚合。

设计意图（写进报告）：
本项目实际数据为 1225 万行（469MB），单机 pandas 全量可处理，主流程即用全量读。
但为应对数据规模扩展到亿级、超出单机内存的场景，此脚本提供等价的 Dask 实现：
- read_csv 惰性分区，不一次性载入内存，从根本上规避单节点 OOM；
- groupby 聚合由 Dask 调度并行执行，compute() 时才触发计算；
- 与 pandas 版产出一致的聚合结果，验证方案可平滑扩展。
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import dask.dataframe as dd
from configs import config as C


def load_and_aggregate_dask():
    dtypes = {
        C.COL_USER: "int64",
        C.COL_ITEM: "int64",
        C.COL_CATEGORY: "int64",
        C.COL_BEHAVIOR: "int8",
    }
    # 惰性分区读取：blocksize 控制每个分区大小，内存可控
    ddf = dd.read_csv(
        C.RAW_FILE,
        dtype=dtypes,
        parse_dates=[C.COL_TIME],
        blocksize="64MB",   # 每分区约 64MB，按机器内存调整
    )
    print(f"[dask] 分区数：{ddf.npartitions}")

    # 四元组聚合去重（与 pandas 版等价），惰性定义
    agg = (
        ddf.groupby([C.COL_USER, C.COL_ITEM, C.COL_CATEGORY,
                     C.COL_BEHAVIOR, C.COL_TIME])
           .size()
           .reset_index()
    )
    # dask 不同版本对 size() 结果列命名不一，按位置重命名最后一列为 count
    agg = agg.rename(columns={agg.columns[-1]: "count"})

    # 触发实际计算
    print("[dask] 开始并行计算（compute）...")
    result = agg.compute()
    print(f"[dask] 聚合后行数：{len(result):,}")
    return result


if __name__ == "__main__":
    df = load_and_aggregate_dask()
    print(df.head())
