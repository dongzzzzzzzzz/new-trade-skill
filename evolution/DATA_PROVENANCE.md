# 回放数据来源与边界

## 可作为原始事实的输入

来自 `/Users/lee.dong/Desktop/dc-stock` 的以下文件可以作为回放事实源，但不携带外部策略结论：

- `data/2026_raw/klines_2026.parquet`：日线开、高、低、收、成交量和成交额，覆盖 2026-01-05 至 2026-08-25。
- `data/2026_raw/special_pools_2026.parquet`：涨停、炸板、跌停池和股票名称，覆盖同一日线区间。
- `data/capital_profit_path_replay_v3/auction_process.parquet`：竞价逐笔过程，覆盖 2026-01-06 至 2026-02-02。
- `data/capital_profit_path_replay_v3/auction_summary.parquet`：竞价开盘价和数据质量字段，覆盖 2026-01-06 至 2026-02-02。

## 不得直接作为目标 skill 结论的输入

以下文件已经包含其他策略的方向选择、候选排序或交易结果，只能用于审计字段设计，不能直接当作小宝 skill 的主线、候选、竞价决策或收益基线：

- `capital_profit_path_replay_v3/trades.csv`
- `capital_profit_path_replay_v3/market_path_candidates.csv`
- `capital_profit_path_replay_v3/auction_market_confirmation.csv`
- `capital_profit_path_replay_v3/january_2026_replay.json`
- `2026_neutral_review/*_pred.json`
- `2026_neutral_review/*_returns.csv`

## 已完成的数据口径检查

用 14 条外部交易的日期和股票代码做了脱离策略的计算测试：

- T+1 开盘买入、T+2 竞价卖出；
- 重新读取原始日线和竞价开盘价；
- 平均收益 `1.0357%`，胜率 `42.86%`，简单收益和 `14.4999%`。

这只是证明收益计算器和原始价格链路可用，不是目标 skill 的回放成绩。

## 封存区

2026-09-01 至 2026-10-09 不参与当前规则选择和调参。当前可先使用 2026-01 至 2026-08 中具备完整事实和竞价数据的样本；若竞价源只覆盖到 2026-02-02，则先把 1 月作为开发/基线窗口，不能把它包装成全年验证。
