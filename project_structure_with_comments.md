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
│   ├── Analysis.py                # 分析页面
│   ├── Betting.py                 # 投注页面
│   ├── Dashboard.py               # 主仪表板页面
│   ├── History.py                 # 历史数据页面
│   ├── Home.py                    # 主页
│   ├── Login.py                   # 登录页面
│   ├── Recommendations.py         # 推荐页面
│   ├── Register.py                # 注册页面
│   └── __pycache__/
│       └── (1 items)
├── requirements.txt               # 项目依赖包列表
└── src/                           # 源代码根目录
    ├── __init__.py                # 包初始化文件
    ├── __pycache__/               # Python编译缓存目录
    │   └── (2 items)
    ├── algorithms/                # 算法模块目录
    │   ├── __init__.py            # 算法包初始化文件
    │   ├── __pycache__/           # 缓存目录
    │   │   └── (3 items)
    │   ├── advanced_algorithms/   # 高级算法目录
    │   │   ├── __pycache__/       # 缓存目录
    │   │   │   └── (6 items)
    │   │   ├── adaptive_meta_ensemble.py      # 自适应元集成算法
    │   │   ├── backtesting_engine.py          # 回测引擎
    │   │   ├── bayesian_number_predictor.py   # 贝叶斯号码预测器
    │   │   ├── feature_engineer.py            # 特征工程
    │   │   ├── hit_rate_optimizer.py          # 命中率优化器
    │   │   ├── lottery_rl_agent.py            # 彩票强化学习代理
    │   │   ├── markov_transition_model.py     # 马尔可夫转移模型
    │   │   ├── neural_lottery_predictor.py    # 神经网络彩票预测器
    │   │   └── number_graph_analyzer.py       # 号码图分析器
    │   ├── base_algorithm.py      # 算法基类
    │   ├── dynamic_ensemble_optimizer.py # 动态集成优化器
    │   ├── ha.py                  # 临时文件
    │   ├── intelligent_pattern_recognizer.py # 智能模式识别器
    │   ├── ml_algorithms.py       # 机器学习算法
    │   ├── optimization_algorithms.py # 优化算法
    │   ├── real_time_feedback_learner.py # 实时反馈学习器
    │   ├── risk_management_algorithms.py # 风险管理算法
    │   └── statistical_algorithms.py # 统计分析算法
    ├── analysis/                  # 分析模块目录
    │   ├── __pycache__/           # 缓存目录
    │   │   └── (1 items)
    │   ├── manager.py             # 分析管理器
    │   └── performance_analyzer.py # 性能分析器
    ├── auth/                      # 认证模块目录
    │   ├── __pycache__/           # 缓存目录
    │   │   └── (1 items)
    │   └── auth_utils.py          # 认证工具函数
    ├── bf/                        # 布局和功能文件目录
    │   ├── aitongyi.py            # AI通义相关文件
    │   ├── prompt_templates.py    # 提示模板文件
    │   └── 大乐透历史开奖数据.md  # 大乐透历史开奖数据文档
    ├── config/                    # 配置文件目录
    │   ├── __init__.py            # 配置包初始化文件
    │   ├── __pycache__/           # 缓存目录
    │   │   └── (3 items)
    │   ├── database_config.py     # 数据库配置
    │   ├── logging_config.py      # 日志配置
    │   └── system_config.py       # 系统配置
    ├── database/                  # 数据库模块目录
    │   ├── __init__.py            # 数据库包初始化文件
    │   ├── __pycache__/           # 缓存目录
    │   │   └── (4 items)
    │   ├── AllDao.py              # 所有DAO集合
    │   ├── connection_manager.py  # 数据库连接管理器
    │   ├── crud/                  # CRUD操作目录
    │   │   ├── AlgorithmConfigDAO.py          # 算法配置DAO
    │   │   ├── AlgorithmPerformanceDAO.py     # 算法性能DAO
    │   │   ├── NumberStatisticsDAO.py         # 号码统计DAO
    │   │   ├── __pycache__/       # 缓存目录
    │   │   │   └── (8 items)
    │   │   ├── add.py             # 添加数据操作
    │   │   ├── algorithm_performance_dao.py   # 算法性能DAO
    │   │   ├── algorithm_recommendation_dao.py # 算法推荐DAO
    │   │   ├── instead.py         # 替换数据操作
    │   │   ├── lottery_history_dao.py         # 彩票历史DAO
    │   │   ├── personal_betting_dao.py        # 个人投注DAO
    │   │   ├── prediction.py       # 预测数据操作
    │   │   ├── recommendation_details_dao.py  # 推荐详情DAO
    │   │   └── user_purchase_dao.py           # 用户购买DAO
    │   └── database_manager.py    # 数据库管理器
    ├── engine/                    # 引擎模块目录
    │   ├── __init__.py            # 引擎包初始化文件
    │   ├── __pycache__/           # 缓存目录
    │   │   └── (3 items)
    │   ├── adaptive_weight_updater.py # 自适应权重更新器
    │   ├── algorithm_runner.py    # 算法运行器
    │   ├── evaluation_system.py   # 评估系统
    │   ├── performance_logger.py  # 性能记录器
    │   └── recommendation_engine.py # 推荐引擎
    ├── img.png                    # 图片资源文件
    ├── llm/                       # 大语言模型相关目录
    │   ├── __init__.py            # 包初始化文件
    │   ├── __pycache__/           # 缓存目录
    │   │   └── (3 items)
    │   ├── bash.py                # Bash命令执行相关
    │   ├── config.py              # LLM配置文件
    │   └── clients/               # 各种LLM客户端实现
    │       ├── __init__.py        # 客户端初始化文件
    │       ├── __pycache__/       # 缓存目录
    │       │   └── (3 items)
    │       ├── ai_caller.py       # AI调用接口文件
    │       ├── ai_callerv_1.0.py  # AI调用接口v1.0版本
    │       ├── gemini.py          # Gemini客户端
    │       └── openai_compatible.py # OpenAI兼容客户端
    ├── model/                     # 模型模块目录
    │   ├── __init__.py            # 模型包初始化文件
    │   ├── __pycache__/           # 缓存目录
    │   │   └── (3 items)
    │   ├── lottery_models.py      # 彩票模型定义
    │   └── user_models.py         # 用户模型定义
    ├── prompt_templates.py        # 提示模板文件
    ├── prompt_templates_max.py    # 最大提示模板文件
    ├── prompt_templates_plas.py   # PLAS提示模板文件
    ├── sql/                       # SQL脚本目录
    │   └── lottery_analysis_system.sql # 彩票分析系统数据库脚本
    ├── test.md                    # 测试文档
    ├── test.py                    # 测试文件
    └── ui/                        # UI组件目录
        ├── 1.py                   # UI组件文件
        ├── __pycache__/           # 缓存目录
        │   └── (1 items)
        └── style_utils.py         # 样式工具函数
```