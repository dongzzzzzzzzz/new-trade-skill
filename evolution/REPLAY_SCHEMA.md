# 历史回放记录格式

## 目的

逐日重放真实选股流程，验证上游框架是否让候选质量和可实现收益改善。回放必须先保存 T 日盘后输出，再追加 T+1 竞价信息和执行结果；不能用结果倒写前面的判断。

## 一条记录的字段

```text
case_id
signal_date
data_cutoff
environment_state
environment_evidence
sentiment_state
sentiment_evidence
market_mode
market_mode_evidence
theme_classification
node_role_records
candidate_audit
original_queue
auction_date
auction_records
executed_candidate
executed
t1_open_buy_price
t2_auction_sell_price
return_pct
invalidated_reason
excluded_candidates
leakage_check
```

## 时间边界

- `data_cutoff` 固定为 `T` 日收盘后、任何 T+1 竞价信息出现前。
- `environment_*`、`sentiment_*`、`market_mode`、`theme_classification`、`node_role_records`、`candidate_audit` 和 `original_queue` 只能使用 T 日收盘前事实。
- `auction_records` 只能记录 T+1 09:25 前的封单、撤单、开盘预期、开盘位置和板块跟随。
- `t1_open_buy_price` 只能是 T+1 开盘成交价；不可成交时留空并写明原因。
- `t2_auction_sell_price` 只能是 T+2 竞价卖出价；不能用 T+1 收盘价、盘中高点或 T+2 之后价格替代。
- `return_pct` 只在实际执行且两个价格齐全时计算：`(t2_auction_sell_price / t1_open_buy_price - 1) * 100`。

## 候选审计格式

`candidate_audit` 中每只股票必须保存：

```text
candidate
original_rank
environment_pass
environment_evidence
theme_pass
theme_evidence
node_pass
node_evidence
risk_pass
risk_evidence
role
include_status
include_or_exclude_reason
```

这样可以区分“主线识别错了”“节点识别错了”“候选门误杀了”以及“竞价确认后不可交易”，不能只看最终收益猜原因。

## 封存数据

2026-09-01 至 2026-10-09 的数据标记为 `sealed=true`。在环境、情绪、模式、主线、节点和候选池全部完成初轮优化前，不得用于参数调整、规则选择或 Challenger 胜负判断；可以在最终冻结规则后作为留出的验证集。
