# Qlib 源码文件列表

## 根目录
- qlib/__init__.py
- qlib/constant.py
- qlib/config.py
- qlib/log.py
- qlib/typehint.py

## backtest 模块
- qlib/backtest/__init__.py
- qlib/backtest/account.py
- qlib/backtest/backtest.py
- qlib/backtest/decision.py
- qlib/backtest/exchange.py
- qlib/backtest/executor.py
- qlib/backtest/high_performance_ds.py
- qlib/backtest/position.py
- qlib/backtest/profit_attribution.py
- qlib/backtest/report.py
- qlib/backtest/signal.py
- qlib/backtest/utils.py

## cli 模块
- qlib/cli/__init__.py
- qlib/cli/data.py
- qlib/cli/run.py

## contrib/data 模块
- qlib/contrib/data/__init__.py
- qlib/contrib/data/data.py
- qlib/contrib/data/dataset.py
- qlib/contrib/data/handler.py
- qlib/contrib/data/highfreq_handler.py
- qlib/contrib/data/highfreq_processor.py
- qlib/contrib/data/highfreq_provider.py
- qlib/contrib/data/loader.py
- qlib/contrib/data/processor.py
- qlib/contrib/data/utils/__init__.py
- qlib/contrib/data/utils/sepdf.py

## contrib/eva 模块
- qlib/contrib/eva/__init__.py
- qlib/contrib/eva/alpha.py

## contrib/meta/data_selection 模块
- qlib/contrib/meta/__init__.py
- qlib/contrib/meta/data_selection/__init__.py
- qlib/contrib/meta/data_selection/dataset.py
- qlib/contrib/meta/data_selection/model.py
- qlib/contrib/meta/data_selection/net.py
- qlib/contrib/meta/data_selection/utils.py

## contrib/model 模块
- qlib/contrib/model/__init__.py
- qlib/contrib/model/catboost_model.py
- qlib/contrib/model/double_ensemble.py
- qlib/contrib/model/gbdt.py
- qlib/contrib/model/highfreq_gdbt_model.py
- qlib/contrib/model/linear.py
- qlib/contrib/model/pytorch_adarnn.py
- qlib/contrib/model/pytorch_add.py
- qlib/contrib/model/pytorch_alstm.py
- qlib/contrib/model/pytorch_alstm_ts.py
- qlib/contrib/model/pytorch_gats.py
- qlib/contrib/model/pytorch_gats_ts.py
- qlib/contrib/model/pytorch_general_nn.py
- qlib/contrib/model/pytorch_gru.py
- qlib/contrib/model/pytorch_gru_ts.py
- qlib/contrib/model/pytorch_hist.py
- qlib/contrib/model/pytorch_igmtf.py
- qlib/contrib/model/pytorch_krnn.py
- qlib/contrib/model/pytorch_localformer.py
- qlib/contrib/model/pytorch_localformer_ts.py
- qlib/contrib/model/pytorch_lstm.py
- qlib/contrib/model/pytorch_lstm_ts.py
- qlib/contrib/model/pytorch_nn.py
- qlib/contrib/model/pytorch_sandwich.py
- qlib/contrib/model/pytorch_sfm.py
- qlib/contrib/model/pytorch_tabnet.py
- qlib/contrib/model/pytorch_tcn.py
- qlib/contrib/model/pytorch_tcn_ts.py
- qlib/contrib/model/pytorch_tcts.py
- qlib/contrib/model/pytorch_tra.py
- qlib/contrib/model/pytorch_transformer.py
- qlib/contrib/model/pytorch_transformer_ts.py
- qlib/contrib/model/pytorch_utils.py
- qlqlib/contrib/model/tcn.py
- qlib/contrib/model/xgboost.py

## contrib/online 模块
- qlib/contrib/online/__init__.py
- qlib/contrib/online/manager.py
- qlib/contrib/online/online_model.py
- qlib/contrib/online/operator.py
- qlib/contrib/online/user.py
- qlib/contrib/online/utils.py

## contrib/ops 模块
- qlib/contrib/ops/__init__.py
- qlib/contrib/ops/high_freq.py

## contrib/report 模块
- qlib/contrib/report/__init__.py
- qlib/contrib/report/analysis_model/__init__.py
- qlib/contrib/report/analysis_model/analysis_model_performance.py
- qlib/contrib/report/analysis_position/__init__.py
- qlib/contrib/report/analysis_position/cumulative_return.py
- qlib/contrib/report/analysis_position/parse_position.py
- qlib/contrib/report/analysis_position/rank_label.py
- qlib/contrib/report/analysis_position/report.py
- qlib/contrib/report/analysis_position/risk_analysis.py
- qlibudi/contrib/report/analysis_position/score_ic.py
- qlib/contrib/report/data/__init__.py
- qlib/contrib/report/data/ana.py
- qlib/contrib/report/data/base.py
- qlib/contrib/report/graph.py
- qlib/contrib/report/utils.py

## contrib/rolling 模块
- qlib/contrib/rolling/__init__.py
- qlib/contrib/rolling/__main__.py
- qlib/contrib/rolling/base.py
- qlib/contrib/rolling/ddgda.py

## contrib/strategy 模块
- qlib/contrib/strategy/__init__.py
- qlud/contrib/strategy/cost_control.py
- qlib/contrib/strategy/optimizer/__init__.py
- qlib/contrib/strategy/optimizer/base.py
- qlib/contrib/strategy/optimizer/enhanced_indexing.py
- qlib/contrib/strategy/optimizer/optimizer.py
- qlib/contrib/strategy/order_generator.py
- qlib/contrib/strategy/rule_strategy.py
- qlib/contrib/strategy/signal_strategy.py

## contrib/tuner 模块
- qlib/contrib/tuner/__init__.py
- qlib/contrib/tuner/config.py
- qlib/contrib/tuner/launcher.py
- qlib/contrib/tuner/pipeline.py
- qlib/contrib/tuner/space.py
- qlib/contrib/tuner/tuner.py

## contrib/workflow 模块
- qlib/contrib/workflow/__init__.py
- qlib/contrib/workflow/record_temp.py

## data 模块
- qlib/data/__init__.py
- qlib/data/_libs/__init__.py
- qlib/data/_libs/rolling.pyx
- qlib/data/_libs/expanding.pyx
- qlib/data/base.py
- qlib/data/cache.py
- qlib/data/client.py
- qlib/data/data.py
- qlib/data/filter.py
- qlud/data/inst_processor.py
- qlib/data/ops.py
- qlib/data/pit.py

## data/dataset 模块
- qlib/data/dataset/__init__.py
- qlib/data/dataset/handler.py
- qlib/data/dataset/loader.py
- qlib/data/dataset/processor.py
- qlib/data/dataset/storage.py
- qlib/data/dataset/utils.py
- qlib/data/dataset/weight.py

## data/storage 模块
- qlib/data/storage/__init__.py
- qlib/data/storage/file_storage.py
- qlib/data/storage/storage.py

## model 模块
- qlib/model/__init__.py
- qlib/model/base.py
- qlib/model/trainer.py
- qlib/model/utils.py

## model/ens 模块
- qlib/model/ens/__init__.py
- qlib/model/ens/ensemble.py
- qlib/model/ens/group.py

## model/interpret 模块
- qlib/model/interpret/__init__.py
- qlib/model/interpret/base.py

## model/meta 模块
- qlib/model/meta/__init__.py
- qlib/model/meta/dataset.py
- qlib/model/meta/model.py
- qlib/model/meta/task.py

## model/riskmodel 模块
- qlib/model/riskmodel/__init__.py
- qlib/model/riskmodel/base.py
- qlib/model/riskmodel/oet.py
- qlib/model/riskmodel/shrink.py
- qlib/model/riskmodel/structured.py

## rl 模块
- qlib/rl/__init__.py
- qlib/rl/aux_info.py
- qlib/rl/interpreter.py
- qlib/rl/reward.py
- qlib/rl/seed.py
- qlib/rl/simulator.py

## rl/contrib 模块
- qlib/rl/contrib/__init__.py
- qlib/rl/contrib/backtest.py
- qlib/rl/contrib/naive_config_parser.py
- qlib/rl/contrib/train_onpolicy.py
- qlib/rl/contrib/utils.py

## rl/data 模块
- qlib/rl/data/__init__.py
- qlib/rl/data/base.py
- qlib/rl/data/integration.py
- qlib/rl/data/native.py
- qlib/rl/data/pickle_styled.py

## rl/order_execution 模块
- qlib/rl/order_execution/__init__.py
- qlib/rl/order_execution/interpreter.py
- qlib/rl/order_execution/network.py
- qlib/rl/order_execution/policy.py
- qlib/rl/order_execution/reward.py
- qlib/rl/order_execution/simulator_qlib.py
- qlib/rl/order_execution/simulator_simple.py
- qlib/rl/order_execution/state.py
- qlib/rl/order_execution/strategy.py
- qlib/rl/order_execution/utils.py

## rl/strategy 模块
- qlib/rl/strategy/__init__.py
- qlib/rl/strategy/single_order.py

## rl/trainer 模块
- qlib/rl/trainer/__init__.py
- qlib/rl/trainer/api.py
- qlib/rl/trainer/callbacks.py
- qlib/rl/trainer/trainer.py
- qlib/rl/trainer/vessel.py

## rl/utils 模块
- qlib/rl/utils/__init__.py
- qlib/rl/utils/data_queue.py
- qlib/rl/utils/env_wrapper.py
- qlib/rl/utils/finite_env.py
- qlib/rl/utils/log.py

## strategy 模块
- qlib/strategy/__init__.py
- qlib/strategy/base.py

## tests 模块
- qlib/tests/__init__.py
- qlib/tests/config.py
- qlib/tests/data.py

## utils 模块
- qlib/utils/__init__.py
- qlib/utils/data.py
- qlib/utils/exceptions.py
- qlib/utils/file.py
- qlib/utils/index_data.py
- qlib/utils/mod.py
- qlib/utils/objm.py
- qlib/utils/paral.py
- qlib/utils/pickle_utils.py
- qlib/utils/resam.py
- qlib/utils/serial.py
- qlib/utils/time.py

## workflow 模块
- qlib/workflow/__init__.py
- qlib/workflow/exp.py
- qlib/workflow/expm.py
- qlib/workflow/record_temp.py
- qlib/workflow/recorder.py
- qlib/workflow/utils.py

## workflow/online 模块
- qlib/workflow/online/__init__.py
- qlib/workflow/online/manager.py
- qlib/workflow/online/strategy.py
- qlib/workflow/online/update.py
- qlib/workflow/online/utils.py

## workflow/task 模块
- qlib/workflow/task/__init__.py
- qlib/workflow/task/collect.py
- qlib/workflow/task/gen.py
- qlib/workflow/task/manage.py
- qlib/workflow/task/utils.py
