# Git 提交与分支规范

## Commit Message 格式
`<type>(<scope>): <subject>`

### type 取值
- feat：新功能 / 新脚本
- fix：修 bug
- docs：文档、报告、笔记
- data：数据处理逻辑变更
- refactor：重构（不改行为）
- test：测试相关
- chore：环境、配置、杂项

### 示例
- `feat(load): 增加分块读取脚本`
- `data(clean): 四元组去重 + 时间有效性校验`
- `docs(report): 补充质量评估结果`

## 分支策略
- `main`：稳定可发布版本
- `dev`：集成开发分支
- `feature/*`：单功能开发，完成后合入 dev
