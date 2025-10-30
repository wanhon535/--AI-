# 项目目录结构（带层级标注和注释）

```
E:/pyhton/AI/AICp/
├── 1. 根目录层级
│   ├── .git/                          # Git版本控制目录
│   ├── .idea/                         # PyCharm IDE配置目录
│   ├── .venv/                         # Python虚拟环境目录
│   ├── LICENSE                        # 项目许可证文件
│   ├── README.md                      # 项目说明文档
│   ├── __init__.py                    # Python包初始化文件
│   ├── __pycache__/                   # Python编译缓存目录
│   ├── app.py                         # 应用主程序入口文件
│   ├── main.py                        # 主程序文件
│   ├── project_structure_with_comments.md  # 项目结构说明文档
│   ├── requirements.txt               # 项目依赖包列表
│   ├── run_backtest_simulation.py     # 回测模拟运行脚本
│   ├── simulation_controller.py        # 模拟控制器
│   ├── test_learning_loop.py          # 测试学习循环
│   └── outputs/                       # 输出目录
│       ├── backtest_summary_*.csv     # 回测结果文件
│
├── 2. 页面层 (pages/)
│   ├── Analysis.py                    # 分析页面 - 提供彩票数据分析功能
│   ├── Betting.py                     # 投注页面 - 用户投注操作界面
│   ├── History.py                     # 历史数据页面 - 展示历史开奖数据
│   ├── Home.py                        # 主页 - 应用程序主页
│   ├── Login.py                       # 登录页面 - 用户登录界面
│   ├── Recommendations.py              # 推荐页面 - 展示号码推荐结果
│   ├── Register.py                    # 注册页面 - 用户注册界面
│   ├── _Dashboard.py                  # 主仪表板页面 - 应用核心仪表板
│   └── __pycache__/                   # Python编译缓存目录
│
├── 3. 脚本层 (scripts/)
│   └── generate_backtest_data.py      # 生成回测数据脚本
│
├── 4. 源代码层 (src/)
│   ├── 4.1 算法模块 (algorithms/)
│   │   ├── advanced_algorithms/       # 高级算法目录
│   │   │   ├── adaptive_meta_ensemble.py      # 自适应元集成算法 - 动态调整算法权重
│   │   │   ├── backtesting_engine.py          # 回测引擎 - 用于算法性能回测
│   │   │   ├── bayesian_number_predictor.py   # 贝叶斯号码预测器 - 基于贝叶斯理论的号码预测
│   │   │   ├── feature_engineer.py            # 特征工程 - 数据特征提取和处理
│   │   │   ├── hit_rate_optimizer.py          # 命中率优化器 - 优化预测命中率
│   │   │   ├── lottery_rl_agent.py            # 彩票强化学习代理 - 使用强化学习进行号码选择
│   │   │   ├── markov_transition_model.py     # 马尔可夫转移模型 - 基于马尔可夫链的号码转移预测
│   │   │   ├── neural_lottery_predictor.py    # 神经网络彩票预测器 - 使用神经网络预测号码
│   │   │   └── number_graph_analyzer.py       # 号码图分析器 - 分析号码之间的关联关系
│   │   ├── base_algorithm.py                  # 算法基类 - 所有算法的基类定义
│   │   ├── dynamic_ensemble_optimizer.py      # 动态集成优化器 - 动态组合多个算法
│   │   ├── intelligent_pattern_recognizer.py  # 智能模式识别器 - 识别历史数据中的模式
│   │   ├── ml_algorithms.py                   # 机器学习算法 - 机器学习相关算法实现
│   │   ├── optimization_algorithms.py         # 优化算法 - 算法参数优化
│   │   ├── real_time_feedback_learner.py      # 实时反馈学习器 - 根据最新结果调整预测模型
│   │   ├── risk_management_algorithms.py      # 风险管理算法 - 控制投注风险
│   │   └── statistical_algorithms.py          # 统计分析算法 - 基于统计学的分析方法
│   │
│   ├── 4.2 分析模块 (analysis/)
│   │   ├── database_importer.py               # 数据库导入器 - 从外部源导入数据到数据库
│   │   ├── dlt_history_data.json              # 大乐透历史数据JSON文件 - 存储历史开奖数据
│   │   ├── import_from_json.py                # JSON导入工具 - 从JSON文件导入数据
│   │   ├── manager.py                         # 分析管理器 - 管理数据分析流程
│   │   ├── performance_analyzer.py            # 性能分析器 - 分析算法性能指标
│   │   └── 大乐透历史开奖数据.md              # 大乐透历史开奖数据文档 - 历史开奖数据说明
│   │
│   ├── 4.3 认证模块 (auth/)
│   │   └── auth_utils.py                      # 认证工具函数 - 提供用户认证相关功能
│   │
│   ├── 4.4 布局和功能模块 (bf/)
│   │   ├── aitongyi.py                        # AI通义相关文件 - 与通义大模型交互
│   │   ├── prompt_templates.py                # 提示模板文件 - AI提示词模板
│   │   └── 大乐透历史开奖数据.md              # 大乐透历史开奖数据文档 - 历史数据说明
│   │
│   ├── 4.5 配置模块 (config/)
│   │   ├── database_config.py                 # 数据库配置 - 数据库连接配置
│   │   ├── logging_config.py                  # 日志配置 - 系统日志配置
│   │   └── system_config.py                   # 系统配置 - 系统级配置参数
│   │
│   ├── 4.6 数据库模块 (database/)
│   │   ├── crud/                              # CRUD操作目录
│   │   │   ├── AlgorithmConfigDAO.py          # 算法配置DAO - 算法配置数据访问对象
│   │   │   ├── AlgorithmPerformanceDAO.py     # 算法性能DAO - 算法性能数据访问对象
│   │   │   ├── NumberStatisticsDAO.py         # 号码统计DAO - 号码统计数据访问对象
│   │   │   ├── add.py                         # 添加数据操作 - 数据插入功能
│   │   │   ├── algorithm_performance_dao.py   # 算法性能DAO - 算法性能数据访问
│   │   │   ├── algorithm_recommendation_dao.py # 算法推荐DAO - 算法推荐数据访问
│   │   │   ├── instead.py                     # 替换数据操作 - 数据更新功能
│   │   │   ├── lottery_history_dao.py         # 彩票历史DAO - 彩票历史数据访问对象
│   │   │   ├── model_training_log_dao.py      # 模型训练日志DAO - 模型训练日志数据访问
│   │   │   ├── personal_betting_dao.py        # 个人投注DAO - 个人投注数据访问对象
│   │   │   ├── prediction.py                   # 预测数据操作 - 预测结果数据处理
│   │   │   ├── recommendation_details_dao.py  # 推荐详情DAO - 推荐详情数据访问对象
│   │   │   └── user_purchase_dao.py           # 用户购买DAO - 用户购买数据访问对象
│   │   ├── AllDao.py                          # 所有DAO集合 - 汇总所有数据访问对象
│   │   ├── connection_manager.py              # 数据库连接管理器 - 管理数据库连接
│   │   └── database_manager.py                # 数据库管理器 - 数据库整体管理功能
│   │
│   ├── 4.7 引擎模块 (engine/)
│   │   ├── adaptive_weight_updater.py         # 自适应权重更新器 - 动态更新算法权重
│   │   ├── algorithm_runner.py                # 算法运行器 - 执行各种预测算法
│   │   ├── evaluation_system.py               # 评估系统 - 评估算法和推荐结果
│   │   ├── performance_logger.py              # 性能记录器 - 记录算法性能指标
│   │   └── recommendation_engine.py           # 推荐引擎 - 生成号码推荐结果
│   │
│   ├── 4.8 大语言模型模块 (llm/)
│   │   ├── clients/                           # 各种LLM客户端实现
│   │   │   ├── ai_caller.py                   # AI调用接口文件 - 统一调用各类AI模型
│   │   │   ├── ai_callerv_1.0.py              # AI调用接口v1.0版本 - 旧版本AI调用接口
│   │   │   ├── gemini.py                      # Gemini客户端 - Google Gemini模型客户端
│   │   │   └── openai_compatible.py           # OpenAI兼容客户端 - 兼容OpenAI接口的客户端
│   │   ├── bash.py                            # Bash命令执行相关 - 执行bash命令
│   │   └── config.py                          # LLM配置文件 - 大语言模型配置
│   │
│   ├── 4.9 模型模块 (model/)
│   │   ├── lottery_models.py                  # 彩票模型定义 - 彩票相关数据模型
│   │   ├── model_prediction.py                # 模型预测 - 模型预测结果相关
│   │   └── user_models.py                     # 用户模型定义 - 用户相关数据模型
│   │
│   ├── 4.10 UI组件模块 (ui/)
│   │   ├── 1.py                               # UI组件文件 - UI界面组件实现
│   │   └── style_utils.py                     # 样式工具函数 - UI样式相关工具函数
│   │
│   ├── 4.11 SQL脚本目录 (sql/)
│   │   └── lottery_analysis_system.sql        # 彩票分析系统数据库脚本 - 数据库表结构定义
│   │
│   ├── prompt_templates.py                    # 提示模板文件 - AI提示词模板
│   ├── prompt_templates_max.py                # 最大提示模板文件 - 复杂任务提示词模板
│   ├── prompt_templates_plas.py               # PLAS提示模板文件 - PLAS系统提示词模板
│   ├── test.md                                # 测试文档 - 测试相关说明
│   └── test.py                                # 测试文件 - 系统测试代码
```

## 层级说明

### 1. 根目录层级
项目的根目录，包含主要的项目文件、配置文件和入口文件。

### 2. 页面层 (pages/)
存放所有Streamlit页面文件，每个页面对应一个功能模块。

### 3. 脚本层 (scripts/)
存放各种辅助脚本，如数据生成、批处理等脚本。

### 4. 源代码层 (src/)
项目的核心源代码，按功能模块划分为多个子模块。

#### 4.1 算法模块 (algorithms/)
包含所有预测和分析算法，分为基础算法和高级算法。

#### 4.2 分析模块 (analysis/)
负责数据分析和性能评估相关功能。

#### 4.3 认证模块 (auth/)
处理用户认证和权限管理。

#### 4.4 布局和功能模块 (bf/)
包含AI相关功能和提示模板。

#### 4.5 配置模块 (config/)
系统和数据库配置文件。

#### 4.6 数据库模块 (database/)
数据库访问层，包含DAO和连接管理。

#### 4.7 引擎模块 (engine/)
核心业务引擎，如推荐引擎、评估系统等。

#### 4.8 大语言模型模块 (llm/)
与各种大语言模型交互的客户端。

#### 4.9 模型模块 (model/)
数据模型定义。

#### 4.10 UI组件模块 (ui/)
用户界面相关组件和样式工具。

#### 4.11 SQL脚本目录 (sql/)
数据库脚本文件。