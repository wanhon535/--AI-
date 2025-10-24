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
│   ├── Dashboard.py               # 主仪表板页面
│   ├── Login.py                   # 登录页面
│   ├── Register.py                # 注册页面
│   └── __pycache__/
│       └── (1 items)
├── requirements.txt               # 项目依赖包列表
└── src/                           # 源代码根目录
    ├── __pycache__/               # Python编译缓存目录
    │   └── (1 items)
    ├── ai_caller.py               # AI调用接口文件
    ├── algorithms/                # 算法模块目录
    │   ├── __init__.py            # 算法包初始化文件
    │   ├── base_algorithm.py      # 算法基类
    │   ├── ha.py                  # 临时文件
    │   ├── ml_algorithms.py       # 机器学习算法
    │   ├── optimization_algorithms.py # 优化算法
    │   ├── risk_management_algorithms.py # 风险管理算法
    │   └── statistical_algorithms.py # 统计分析算法
    ├── analysis/                  # 分析模块目录
    │   ├── __pycache__/           # 缓存目录
    │   │   └── (1 items)
    │   └── performance_analyzer.py # 性能分析器
    ├── auth/                      # 认证模块目录
    │   ├── __pycache__/           # 缓存目录
    │   │   └── (1 items)
    │   └── auth_utils.py          # 认证工具函数
    ├── bf/                        # 布局和功能文件目录
    │   ├── aitongyi.py            # AI通义相关文件
    │   └── 大乐透历史开奖数据.md  # 大乐透历史开奖数据文档
    ├── config/                    # 配置文件目录
    │   ├── __init__.py            # 配置包初始化文件
    │   ├── database_config.py     # 数据库配置
    │   ├── logging_config.py      # 日志配置
    │   └── system_config.py       # 系统配置
    ├── database/                  # 数据库模块目录
    │   ├── __init__.py            # 数据库包初始化文件
    │   ├── __pycache__/           # 缓存目录
    │   │   └── (2 items)
    │   ├── curd/                  # CRUD操作目录
    │   │   ├── add.py             # 添加数据操作
    │   │   ├── instead.py         # 替换数据操作
    │   │   └── prediction.py      # 预测数据操作
    │   └── database_manager.py    # 数据库管理器
    ├── engine/                    # 引擎模块目录
    │   ├── __init__.py            # 引擎包初始化文件
    │   ├── evaluation_system.py   # 评估系统
    │   └── recommendation_engine.py # 推荐引擎
    ├── img.png                    # 图片资源文件
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