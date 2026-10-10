# 回放数据来源与边界

## 可作为原始事实的输入

来自 `/Users/lee.dong/Desktop/dc-stock` 的以下文件可以作为回放事实源，但不携带外部策略结论：

- `data/2026_raw/klines_2026.parquet`：日线开、高、低、收、成交量和成交额，覆盖 2026-01-05 至 2026-08-25。
- `data/2026_raw/special_pools_2026.parquet`：涨停、炸板、跌停池和股票名称，覆盖同一日线区间。
- `data/trade_setup_strategy/hithink_enriched/special_pools_enriched.csv`：涨停原因、连板文字、封单和涨停时间等描述性事实；不使用其中任何市场角色、路径、候选资格或排序字段。
- `data/capital_profit_path_replay_v3/auction_process.parquet`：竞价逐笔过程，覆盖 2026-01-06 至 2026-02-02。
- `data/capital_profit_path_replay_v3/auction_summary.parquet`：竞价开盘价和数据质量字段，覆盖 2026-01-06 至 2026-02-02。
- `evolution/index_facts_2026-01.json`：通过东方财富 `push2his` 历史 K 线接口抓取的上证指数、深证成指和创业板指日线事实；保存接口 URL、字段和抓取时间。
- `evolution/index_facts_2026-02.json`：通过腾讯 `web.ifzq.gtimg.cn/appstock/app/fqkline/get` 公共历史 K 线接口抓取的上证指数、深证成指和创业板指日线事实；保存接口 URL、字段和抓取时间。
- `evolution/auction_cache_2026-02/auction_summary.parquet` 与 `auction_process.parquet`：使用 `eltdx==3.1.1` 专用历史行情主站池，按 `09:15:00` 至 `09:25:00` 过程和 `09:25` 正式撮合口径抓取二月候选的竞价事实；首轮 T+1 范围覆盖 861 个股票/日期对，2026-02-02 至 2026-02-27 信号日对应的 2026-02-03 至 2026-03-02 竞价日，全部为 `full_series`。另有 57 个 2026-02-05 诊断对，用于审计 2026-02-03 的候选生成失败，不得当作已冻结决策输入。

二月指数文件的 `index_amount_*` 字段使用腾讯接口返回的指数成交量代理值，不是成交额。二月市场宽度和个股成交额仍来自本地股票日线事实；任何依赖指数成交额绝对值的规则在该窗口不得被宣称已验证。

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

2026-09-01 至 2026-10-09 不参与当前规则选择和调参。当前可先使用 2026-01 至 2026-08 中具备完整事实和竞价数据的样本；二月的 `market_facts_2026-02.csv` 和 `replay_inputs_2026-02.csv` 已生成，覆盖 2026-02-02 至 2026-02-27 共 14 个交易日、1334 条股票级输入。二月候选的 T+1 竞价事实已补齐，但只有实际由优化后 skill 产生并执行的候选，才继续抓取对应 T+2 竞价卖出价；不能把候选池全量的未来价格当作收益验证。

`evolution/replay_inputs_2026-01.csv` 是由上述事实源合成的 T 日输入。它不包含 `market_role`、`path_id`、`candidate_eligible`、外部主线结论、候选排序或收益字段；这些必须由目标 `SKILL.md` 在回放时生成。
