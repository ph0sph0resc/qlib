import qlib
import pandas as pd
from qlib.utils.time import Freq
from qlib.backtest import backtest, executor
from qlib.contrib.strategy import TopkDropoutStrategy
from qlib.contrib.report import analysis_position as ap

# 初始化 Qlib
qlib.init(provider_uri='~/.qlib/qlib_data/cn_data', region='cn')
pred_score = pd.read_pickle("score.pkl")["score"]
# 配置策略
STRATEGY_CONFIG = {
    "topk": 50,
    "n_drop": 5,
    "signal": pred_score,  # 预测分数
}

EXECUTOR_CONFIG = {
    "time_per_step": "day",
    "generate_portfolio_metrics": True,
}

backtest_config = {
    "start_time": "2017-01-01",
    "end_time": "2020-08-01",
    "account": 100000000,
    "benchmark": "SH000300",
    "exchange_kwargs": {
        "freq": "day",
        "limit_threshold": 0.095,
        "deal_price": "close",
        "open_cost": 0.0005,
        "close_cost": 0.0015,
        "min_cost": 5,
    },
}

# 执行回测
strategy_obj = TopkDropoutStrategy(**STRATEGY_CONFIG)
executor_obj = executor.SimulatorExecutor(**EXECUTOR_CONFIG)
portfolio_metric_dict, indicator_dict = backtest(
    executor=executor_obj,
    strategy=strategy_obj,
    **backtest_config
)

# 获取报告数据
analysis_freq = "{0}{1}".format(*Freq.parse("day"))
report_normal_df, positions_normal = portfolio_metric_dict.get(analysis_freq)

# 显示报告图表
ap.report_graph(report_normal_df)