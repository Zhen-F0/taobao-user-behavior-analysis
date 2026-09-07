# 淘宝用户行为数据分析

基于淘宝用户行为数据集的全流程分析与建模项目，覆盖数据工程、特征工程、多模型建模与业务洞察。

## 目录结构
- `data/`   raw(原始) / interim(中间) / processed(Parquet 成品)
- `src/`    load / clean / quality / transform
- `docs/`   报告与文献调研笔记
- `results/` 图表与质量报告
- `notebooks/` 探索性分析
- `tests/`  单元测试
- `configs/` 路径与参数配置

## 环境
```bash
conda env create -f environment.yml
conda activate taobao
```
