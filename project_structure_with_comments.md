# 项目目录结构（带注释）

```
E:/pyhton/AI/AICp/
├── .git/                          # Git版本控制目录
│   └── (12 items)
├── .idea/                         # PyCharm IDE配置目录
│   └── (12 items)
├── .venv/                         # Python虚拟环境目录
│   └── (6 items)
├── LICENSE                        # 项目许可证文件
├── README.md                      # 项目说明文档
├── __init__.py                    # Python包初始化文件
├── __pycache__/                   # Python编译缓存目录
│   └── (0 items)
├── app.py                         # 应用主程序入口文件
├── main.py                        # 主程序文件
├── pages/                         # Streamlit页面文件目录
│   ├── Analysis.py                # 分析页面 - 提供彩票数据分析功能
│   ├── Betting.py                 # 投注页面 - 用户投注操作界面
│   ├── History.py                 # 历史数据页面 - 展示历史开奖数据
│   ├── Home.py                    # 主页 - 应用程序主页
│   ├── Login.py                   # 登录页面 - 用户登录界面
│   ├── Recommendations.py         # 推荐页面 - 展示号码推荐结果
│   ├── Register.py                # 注册页面 - 用户注册界面
│   ├── _Dashboard.py              # 主仪表板页面 - 应用核心仪表板
│   └── __pycache__/
│       └── (1 items)
├── project_structure_with_comments.md  # 项目结构说明文档
├── requirements.txt               # 项目依赖包列表
├── run_backtest_simulation.py     # 回测模拟运行脚本
├── simulation_controller.py       # 模拟控制器
├── src/                           # 源代码根目录
│   ├── __init__.py                # 包初始化文件
│   ├── __pycache__/               # Python编译缓存目录
│   │   └── (2 items)
│   ├── algorithms/                # 算法模块目录
│   │   ├── __init__.py            # 算法包初始化文件
│   │   ├── __pycache__/           # 缓存目录
│   │   │   └── (4 items)
│   │   ├── advanced_algorithms/   # 高级算法目录
│   │   │   ├── __pycache__/       # 缓存目录
│   │   │   │   └── (6 items)
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
│   │   ├── ha.py                              # 临时文件
│   │   ├── intelligent_pattern_recognizer.py  # 智能模式识别器 - 识别历史数据中的模式
│   │   ├── ml_algorithms.py                   # 机器学习算法 - 机器学习相关算法实现
│   │   ├── optimization_algorithms.py         # 优化算法 - 算法参数优化
│   │   ├── real_time_feedback_learner.py      # 实时反馈学习器 - 根据最新结果调整预测模型
│   │   ├── risk_management_algorithms.py      # 风险管理算法 - 控制投注风险
│   │   └── statistical_algorithms.py          # 统计分析算法 - 基于统计学的分析方法
│   ├── analysis/                              # 分析模块目录
│   │   ├── __pycache__/                       # 缓存目录
│   │   │   └── (3 items)
│   │   ├── database_importer.py               # 数据库导入器 - 从外部源导入数据到数据库
│   │   ├── dlt_history_data.json              # 大乐透历史数据JSON文件 - 存储历史开奖数据
│   │   ├── import_from_json.py                # JSON导入工具 - 从JSON文件导入数据
│   │   ├── manager.py                         # 分析管理器 - 管理数据分析流程
│   │   ├── performance_analyzer.py            # 性能分析器 - 分析算法性能指标
│   │   └── 大乐透历史开奖数据.md              # 大乐透历史开奖数据文档 - 历史开奖数据说明
│   ├── auth/                                  # 认证模块目录
│   │   ├── __pycache__/                       # 缓存目录
│   │   │   └── (1 items)
│   │   └── auth_utils.py                      # 认证工具函数 - 提供用户认证相关功能
│   ├── bf/                                    # 布局和功能文件目录
│   │   ├── aitongyi.py                        # AI通义相关文件 - 与通义大模型交互
│   │   ├── prompt_templates.py                # 提示模板文件 - AI提示词模板
│   │   └── 大乐透历史开奖数据.md              # 大乐透历史开奖数据文档 - 历史数据说明
│   ├── config/                                # 配置文件目录
│   │   ├── __init__.py                        # 配置包初始化文件
│   │   ├── __pycache__/                       # 缓存目录
│   │   │   └── (3 items)
│   │   ├── database_config.py                 # 数据库配置 - 数据库连接配置
│   │   ├── logging_config.py                  # 日志配置 - 系统日志配置
│   │   └── system_config.py                   # 系统配置 - 系统级配置参数
│   ├── database/                              # 数据库模块目录
│   │   ├── __init__.py                        # 数据库包初始化文件
│   │   ├── __pycache__/                       # 缓存目录
│   │   │   └── (4 items)
│   │   ├── AllDao.py                          # 所有DAO集合 - 汇总所有数据访问对象
│   │   ├── connection_manager.py              # 数据库连接管理器 - 管理数据库连接
│   │   ├── crud/                              # CRUD操作目录
│   │   │   ├── AlgorithmConfigDAO.py          # 算法配置DAO - 算法配置数据访问对象
│   │   │   ├── AlgorithmPerformanceDAO.py     # 算法性能DAO - 算法性能数据访问对象
│   │   │   ├── NumberStatisticsDAO.py         # 号码统计DAO - 号码统计数据访问对象
│   │   │   ├── __init__.py                    # 初始化文件
│   │   │   ├── __pycache__/                   # 缓存目录
│   │   │   │   └── (11 items)
│   │   │   ├── add.py                         # 添加数据操作 - 数据插入功能
│   │   │   ├── algorithm_performance_dao.py   # 算法性能DAO - 算法性能数据访问
│   │   │   ├── algorithm_recommendation_dao.py # 算法推荐DAO - 算法推荐数据访问
│   │   │   ├── dlt_history_data.json          # 大乐透历史数据JSON文件 - 存储历史开奖数据
│   │   │   ├── instead.py                     # 替换数据操作 - 数据更新功能
│   │   │   ├── lottery_history_dao.py         # 彩票历史DAO - 彩票历史数据访问对象
│   │   │   ├── model_training_log_dao.py      # 模型训练日志DAO - 模型训练日志数据访问
│   │   │   ├── personal_betting_dao.py        # 个人投注DAO - 个人投注数据访问对象
│   │   │   ├── prediction.py                   # 预测数据操作 - 预测结果数据处理
│   │   │   ├── recommendation_details_dao.py  # 推荐详情DAO - 推荐详情数据访问对象
│   │   │   └── user_purchase_dao.py           # 用户购买DAO - 用户购买数据访问对象
│   │   └── database_manager.py                # 数据库管理器 - 数据库整体管理功能
│   ├── engine/                                # 引擎模块目录
│   │   ├── __init__.py                        # 引擎包初始化文件
│   │   ├── __pycache__/                       # 缓存目录
│   │   │   └── (5 items)
│   │   ├── adaptive_weight_updater.py         # 自适应权重更新器 - 动态更新算法权重
│   │   ├── algorithm_runner.py                # 算法运行器 - 执行各种预测算法
│   │   ├── evaluation_system.py               # 评估系统 - 评估算法和推荐结果
│   │   ├── performance_logger.py              # 性能记录器 - 记录算法性能指标
│   │   └── recommendation_engine.py           # 推荐引擎 - 生成号码推荐结果
│   ├── img.png                                # 图片资源文件
│   ├── llm/                                   # 大语言模型相关目录
│   │   ├── __init__.py                        # 包初始化文件
│   │   ├── __pycache__/                       # 缓存目录
│   │   │   └── (3 items)
│   │   ├── bash.py                            # Bash命令执行相关 - 执行bash命令
│   │   ├── config.py                          # LLM配置文件 - 大语言模型配置
│   │   └── clients/                           # 各种LLM客户端实现
│   │       ├── __init__.py                    # 客户端初始化文件
│   │       ├── __pycache__/                   # 缓存目录
│   │       │   └── (3 items)
│   │       ├── ai_caller.py                   # AI调用接口文件 - 统一调用各类AI模型
│   │       ├── ai_callerv_1.0.py              # AI调用接口v1.0版本 - 旧版本AI调用接口
│   │       ├── gemini.py                      # Gemini客户端 - Google Gemini模型客户端
│   │       └── openai_compatible.py           # OpenAI兼容客户端 - 兼容OpenAI接口的客户端
│   ├── model/                                 # 模型模块目录
│   │   ├── __init__.py                        # 模型包初始化文件
│   │   ├── __pycache__/                       # 缓存目录
│   │   │   └── (4 items)
│   │   ├── lottery_models.py                  # 彩票模型定义 - 彩票相关数据模型
│   │   ├── model_prediction.py                # 模型预测 - 模型预测结果相关
│   │   └── user_models.py                     # 用户模型定义 - 用户相关数据模型
│   ├── prompt_templates.py                    # 提示模板文件 - AI提示词模板
│   ├── prompt_templates_max.py                # 最大提示模板文件 - 复杂任务提示词模板
│   ├── prompt_templates_plas.py               # PLAS提示模板文件 - PLAS系统提示词模板
│   ├── sql/                                   # SQL脚本目录
│   │   └── lottery_analysis_system.sql        # 彩票分析系统数据库脚本 - 数据库表结构定义
│   ├── test.md                                # 测试文档 - 测试相关说明
│   ├── test.py                                # 测试文件 - 系统测试代码
│   └── ui/                                    # UI组件目录
│       ├── 1.py                               # UI组件文件 - UI界面组件实现
│       ├── __pycache__/                       # 缓存目录
│       │   └── (1 items)
│       └── style_utils.py                     # 样式工具函数 - UI样式相关工具函数
└── test_learning_loop.py                      # 测试学习循环 - 测试机器学习循环功能
```