# 彩票分析系统数据库结构文档

## 概述

本文档详细描述了彩票分析系统的数据库结构，包括所有表和视图的结构及字段说明。

## 数据库表清单

1. [ab_test_configs](#1-ab_test_configs-ab测试配置表) - A/B测试配置表
2. [algorithm_configs](#2-algorithm_configs-算法配置表) - 算法配置表
3. [algorithm_performance](#3-algorithm_performance-算法性能统计表) - 算法性能统计表
4. [algorithm_recommendation](#4-algorithm_recommendation-算法推荐批次元数据表) - 算法推荐批次元数据表
5. [data_update_logs](#5-data_update_logs-数据更新日志表) - 数据更新日志表
6. [financial_reports](#6-financial_reports-财务报表) - 财务报表
7. [lottery_history](#7-lottery_history-历史开奖数据表) - 历史开奖数据表
8. [model_training_logs](#8-model_training_logs-预测模型训练记录表) - 预测模型训练记录表
9. [notifications](#9-notifications-系统通知消息表) - 系统通知消息表
10. [number_statistics](#10-number_statistics-号码统计分析表) - 号码统计分析表
11. [pattern_recognition](#11-pattern_recognition-模式识别记录表) - 模式识别记录表
12. [personal_betting](#12-personal_betting-个人自由投注记录表) - 个人自由投注记录表
13. [recommendation_details](#13-recommendation_details-算法推荐的具体组合详情表) - 算法推荐的具体组合详情表
14. [reward_penalty_records](#14-reward_penalty_records-奖罚分明记录表) - 奖罚分明记录表
15. [system_monitoring](#15-system_monitoring-系统实时监控表) - 系统实时监控表
16. [user_purchase_records](#16-user_purchase_records-用户实际购买记录表) - 用户实际购买记录表
17. [users](#17-users-用户管理表) - 用户管理表

## 数据库视图清单

1. [algorithm_performance_view](#1-algorithm_performance_view-算法性能视图) - 算法性能视图
2. [comprehensive_analysis_view](#2-comprehensive_analysis_view-综合分析视图) - 综合分析视图

## 数据库表结构

### 1. ab_test_configs (A/B测试配置表)

用于配置和管理A/B测试的相关参数和结果。

| 字段名 | 类型 | 允许空 | 默认值 | 注释 |
|--------|------|--------|--------|------|
| id | bigint(20) | NO | NULL | 主键，自增ID |
| test_name | varchar(100) | NO | NULL | 测试名称 |
| test_description | text | YES | NULL | 测试描述 |
| algorithm_a | varchar(50) | NO | NULL | 算法A版本 |
| algorithm_b | varchar(50) | NO | NULL | 算法B版本 |
| split_ratio | decimal(3,2) | YES | 0.50 | 流量分配比例 |
| test_parameters | json | YES | NULL | 测试参数 |
| success_metrics | json | NO | NULL | 成功指标定义 |
| test_status | enum('draft','running','paused','completed') | YES | 'draft' | 测试状态 |
| start_date | date | YES | NULL | 开始日期 |
| end_date | date | YES | NULL | 结束日期 |
| min_sample_size | int(11) | YES | 100 | 最小样本量 |
| current_sample_size | int(11) | YES | 0 | 当前样本量 |
| algorithm_a_performance | json | YES | NULL | 算法A表现 |
| algorithm_b_performance | json | YES | NULL | 算法B表现 |
| statistical_significance | decimal(5,4) | YES | NULL | 统计显著性 |
| created_by | varchar(50) | YES | NULL | 创建人 |
| created_at | timestamp | YES | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | timestamp | YES | CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |

### 2. algorithm_configs (算法配置表)

存储各种算法的配置信息。

| 字段名 | 类型 | 允许空 | 默认值 | 注释 |
|--------|------|--------|--------|------|
| id | bigint(20) | NO | NULL | 主键，自增ID |
| algorithm_name | varchar(100) | NO | NULL | 算法名称 |
| algorithm_type | enum('statistical','ml','ensemble','optimization') | NO | NULL | 算法类型 |
| parameters | json | NO | NULL | 算法参数配置 |
| description | text | YES | NULL | 算法描述 |
| version | varchar(20) | NO | '1.0.0' | 版本号 |
| is_active | tinyint(1) | YES | 1 | 是否启用 |
| is_default | tinyint(1) | YES | 0 | 是否默认算法 |
| min_data_required | int(11) | YES | 50 | 最小数据要求 |
| expected_accuracy | decimal(5,4) | YES | NULL | 预期准确率 |
| computation_complexity | enum('low','medium','high') | YES | 'medium' | 计算复杂度 |
| memory_requirements | varchar(50) | YES | NULL | 内存要求 |
| created_by | varchar(50) | YES | NULL | 创建人 |
| created_at | timestamp | YES | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | timestamp | YES | CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |

### 3. algorithm_performance (算法性能统计表)

记录各算法的性能统计数据。

| 字段名 | 类型 | 允许空 | 默认值 | 注释 |
|--------|------|--------|--------|------|
| id | bigint(20) | NO | NULL | 主键，自增ID |
| algorithm_version | varchar(50) | NO | NULL | 算法版本 |
| total_recommendations | int(11) | YES | 0 | 总推荐次数 |
| total_periods_analyzed | int(11) | YES | 0 | 总分析期数 |
| avg_front_hit_rate | decimal(5,4) | YES | 0.0000 | 平均前区命中率 |
| avg_back_hit_rate | decimal(5,4) | YES | 0.0000 | 平均后区命中率 |
| hit_distribution | json | YES | NULL | 命中分布统计 |
| confidence_accuracy | decimal(5,4) | YES | 0.0000 | 置信度准确性 |
| risk_adjusted_return | decimal(8,4) | YES | 0.0000 | 风险调整后收益 |
| stability_score | decimal(5,4) | YES | 0.0000 | 稳定性评分 |
| consistency_rate | decimal(5,4) | YES | 0.0000 | 一致性比率 |
| current_weight | decimal(4,3) | YES | 0.100 | 当前权重 |
| weight_history | json | YES | NULL | 权重历史记录 |
| performance_trend | enum('improving','stable','declining') | YES | 'stable' | 性能趋势 |
| last_updated | timestamp | YES | CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 最后更新时间 |

### 4. algorithm_recommendation (算法推荐批次元数据表)

存储算法推荐的元数据信息。

| 字段名 | 类型 | 允许空 | 默认值 | 注释 |
|--------|------|--------|--------|------|
| id | bigint(20) | NO | NULL | 主键，自增ID |
| period_number | varchar(20) | YES | NULL | 推荐期号 |
| recommend_time | datetime | NO | NULL | 推荐时间 |
| algorithm_version | varchar(50) | NO | NULL | 算法版本 |
| algorithm_parameters | json | YES | NULL | 算法参数配置 |
| model_weights | json | YES | NULL | 模型权重配置 |
| confidence_score | decimal(5, 4) | NO | NULL | 总体置信度 |
| risk_level | varchar(100) | YES | medium | 总体风险等级 |
| analysis_basis | json | YES | NULL | 分析依据数据 |
| llm_cognitive_details | json | YES | NULL |  |
| key_patterns | json | YES | NULL | 关键模式识别 |
| models | varchar(255) | YES | NULL | 推荐模型名称 |
| created_at | timestamp | YES | CURRENT_TIMESTAMP | 创建时间 |

### 5. data_update_logs (数据更新日志表)

记录数据更新操作的日志。

| 字段名 | 类型 | 允许空 | 默认值 | 注释 |
|--------|------|--------|--------|------|
| id | bigint(20) | NO | NULL | 主键，自增ID |
| update_type | enum('manual','automatic','api') | NO | NULL | 更新类型 |
| data_source | varchar(100) | NO | NULL | 数据来源 |
| period_range | varchar(100) | YES | NULL | 更新的期号范围 |
| records_added | int(11) | YES | 0 | 新增记录数 |
| records_updated | int(11) | YES | 0 | 更新记录数 |
| records_deleted | int(11) | YES | 0 | 删除记录数 |
| update_status | enum('pending','success','failed','partial') | NO | NULL | 更新状态 |
| error_message | text | YES | NULL | 错误信息 |
| started_at | timestamp | NO | NULL | 开始时间 |
| completed_at | timestamp | YES | NULL | 完成时间 |
| execution_duration | int(11) | YES | NULL | 执行时长(秒) |
| initiated_by | varchar(50) | YES | NULL | 发起人 |
| created_at | timestamp | YES | CURRENT_TIMESTAMP | 创建时间 |

### 6. financial_reports (财务报表)

存储财务相关的报表数据。

| 字段名 | 类型 | 允许空 | 默认值 | 注释 |
|--------|------|--------|--------|------|
| id | bigint(20) | NO | NULL | 主键，自增ID |
| report_period | varchar(20) | NO | NULL | 报表期间 |
| report_type | enum('daily','weekly','monthly','yearly') | NO | NULL | 报表类型 |
| total_investment | decimal(12,2) | YES | 0.00 | 总投入金额 |
| total_winnings | decimal(12,2) | YES | 0.00 | 总中奖金额 |
| net_profit | decimal(12,2) | YES | 0.00 | 净利润 |
| return_rate | decimal(8,4) | YES | 0.0000 | 回报率 |
| total_bets | int(11) | YES | 0 | 总投注数 |
| winning_bets | int(11) | YES | 0 | 中奖投注数 |
| bet_success_rate | decimal(5,4) | YES | 0.0000 | 投注成功率 |
| algorithm_performance | json | YES | NULL | 算法表现详情 |
| best_performing_algorithm | varchar(50) | YES | NULL | 最佳表现算法 |
| max_drawdown | decimal(8,4) | YES | NULL | 最大回撤 |
| sharpe_ratio | decimal(8,4) | YES | NULL | 夏普比率 |
| volatility | decimal(8,4) | YES | NULL | 波动率 |
| generated_at | timestamp | YES | CURRENT_TIMESTAMP | 生成时间 |
| generated_by | varchar(50) | YES | NULL | 生成人 |

### 7. lottery_history (历史开奖数据表)

存储历史开奖数据。

| 字段名 | 类型 | 允许空 | 默认值 | 注释 |
|--------|------|--------|--------|------|
| id | bigint(20) | NO | NULL | 主键，自增ID |
| period_number | varchar(20) | NO | NULL | 期号，如2024001 |
| draw_date | date | NO | NULL | 开奖日期 |
| draw_time | datetime | NO | NULL | 开奖具体时间 |
| front_area_1 | tinyint(4) | NO | NULL | 前区号码1 |
| front_area_2 | tinyint(4) | NO | NULL | 前区号码2 |
| front_area_3 | tinyint(4) | NO | NULL | 前区号码3 |
| front_area_4 | tinyint(4) | NO | NULL | 前区号码4 |
| front_area_5 | tinyint(4) | NO | NULL | 前区号码5 |
| back_area_1 | tinyint(4) | NO | NULL | 后区号码1 |
| back_area_2 | tinyint(4) | NO | NULL | 后区号码2 |
| sum_value | smallint(6) | NO | NULL | 和值 |
| span_value | tinyint(4) | NO | NULL | 跨度 |
| ac_value | tinyint(4) | NO | NULL | AC值 |
| odd_even_ratio | varchar(10) | NO | NULL | 奇偶比，如3:2 |
| size_ratio | varchar(10) | NO | NULL | 大小比(以18为界)，如2:3 |
| prime_composite_ratio | varchar(10) | YES | NULL | 质合比 |
| consecutive_numbers | json | YES | NULL | 连号信息，如[12,13] |
| consecutive_count | tinyint(4) | YES | 0 | 连号组数 |
| tail_numbers | json | YES | NULL | 尾数分布 |
| data_source | varchar(50) | YES | 'official' | 数据来源 |
| data_quality | tinyint(4) | YES | 100 | 数据质量评分 |
| created_at | timestamp | YES | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | timestamp | YES | CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |

### 8. model_training_logs (预测模型训练记录表)

记录模型训练的日志信息。

| 字段名 | 类型 | 允许空 | 默认值 | 注释 |
|--------|------|--------|--------|------|
| id | bigint(20) | NO | NULL | 主键，自增ID |
| algorithm_version | varchar(50) | NO | NULL | 算法版本 |
| training_date | date | NO | NULL | 训练日期 |
| data_start_period | varchar(20) | NO | NULL | 训练数据开始期号 |
| data_end_period | varchar(20) | NO | NULL | 训练数据结束期号 |
| training_samples | int(11) | NO | NULL | 训练样本数 |
| training_parameters | json | YES | NULL | 训练参数 |
| feature_set | json | YES | NULL | 特征集合 |
| training_accuracy | decimal(5,4) | YES | NULL | 训练准确率 |
| validation_accuracy | decimal(5,4) | YES | NULL | 验证准确率 |
| test_accuracy | decimal(5,4) | YES | NULL | 测试准确率 |
| model_file_path | varchar(500) | YES | NULL | 模型文件路径 |
| model_size | bigint(20) | YES | NULL | 模型文件大小 |
| model_hash | varchar(64) | YES | NULL | 模型文件哈希 |
| training_status | enum('running','completed','failed') | NO | NULL | 训练状态 |
| error_log | text | YES | NULL | 错误日志 |
| started_at | timestamp | NO | NULL | 开始时间 |
| completed_at | timestamp | YES | NULL | 完成时间 |
| training_duration | int(11) | YES | NULL | 训练时长(秒) |

### 9. notifications (系统通知消息表)

存储系统通知消息。

| 字段名 | 类型 | 允许空 | 默认值 | 注释 |
|--------|------|--------|--------|------|
| id | bigint(20) | NO | NULL | 主键，自增ID |
| user_id | varchar(50) | NO | NULL | 用户ID |
| notification_type | enum('system','recommendation','warning','success') | NO | NULL | 通知类型 |
| title | varchar(200) | NO | NULL | 通知标题 |
| message | text | NO | NULL | 通知内容 |
| related_entity_type | varchar(50) | YES | NULL | 关联实体类型 |
| related_entity_id | bigint(20) | YES | NULL | 关联实体ID |
| is_read | tinyint(1) | YES | 0 | 是否已读 |
| is_archived | tinyint(1) | YES | 0 | 是否归档 |
| expires_at | timestamp | YES | NULL | 过期时间 |
| created_at | timestamp | YES | CURRENT_TIMESTAMP | 创建时间 |

### 10. number_statistics (号码统计分析表)

存储号码的统计分析数据。

| 字段名 | 类型 | 允许空 | 默认值 | 注释 |
|--------|------|--------|--------|------|
| number | tinyint(4) | NO | NULL | 号码 |
| number_type | enum('front','back') | NO | NULL | 号码类型：前区/后区 |
| total_appearances | int(11) | YES | 0 | 总出现次数 |
| appearance_rate | decimal(5, 4) | YES | 0.0000 | 出现频率 |
| recent_10_appearances | int(11) | YES | 0 | 最近10期出现次数 |
| recent_20_appearances | int(11) | YES | 0 | 最近20期出现次数 |
| recent_50_appearances | int(11) | YES | 0 | 最近50期出现次数 |
| current_omission | int(11) | YES | 0 | 当前遗漏期数 |
| max_omission | int(11) | YES | 0 | 历史最大遗漏 |
| avg_omission | decimal(6, 2) | YES | 0.00 | 平均遗漏 |
| heat_status | enum('hot','warm','cold','very_cold') | YES | 'warm' | 热冷状态 |
| heat_score | decimal(5, 2) | YES | 0.00 | 热度评分 |
| strong_followers | json | YES | NULL | 强跟随号码 |
| strong_precursors | json | YES | NULL | 强前导号码 |
| position_preference | json | YES | NULL | 位置偏好统计 |
| last_updated | timestamp | YES | CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 最后更新时间 |

### 11. pattern_recognition (模式识别记录表)

存储识别到的模式信息。

| 字段名 | 类型 | 允许空 | 默认值 | 注释 |
|--------|------|--------|--------|------|
| id | bigint(20) | NO | NULL | 主键，自增ID |
| pattern_type | varchar(50) | NO | NULL | 模式类型 |
| pattern_description | text | NO | NULL | 模式描述 |
| pattern_features | json | NO | NULL | 模式特征 |
| pattern_signature | varchar(100) | NO | NULL | 模式特征签名 |
| occurrence_count | int(11) | YES | 0 | 出现次数 |
| success_rate | decimal(5,4) | YES | 0.0000 | 成功率 |
| confidence_level | decimal(5,4) | YES | 0.0000 | 置信水平 |
| first_occurrence_date | date | YES | NULL | 首次出现日期 |
| last_occurrence_date | date | YES | NULL | 最后出现日期 |
| avg_occurrence_interval | decimal(6,2) | YES | NULL | 平均出现间隔 |
| is_active | tinyint(1) | YES | 1 | 是否活跃 |
| validity_period | int(11) | YES | NULL | 有效周期 |
| related_algorithms | json | YES | NULL | 关联算法 |
| discovered_time | timestamp | YES | CURRENT_TIMESTAMP | 发现时间 |
| last_verified | timestamp | YES | CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 最后验证时间 |

### 12. personal_betting (个人自由投注记录表)

存储用户个人投注记录。

| 字段名 | 类型 | 允许空 | 默认值 | 注释 |
|--------|------|--------|--------|------|
| id | bigint(20) | NO | NULL | 主键，自增ID |
| user_id | varchar(50) | NO | 'default' | 用户ID，支持多用户 |
| period_number | varchar(20) | NO | NULL | 投注期号 |
| bet_time | datetime | NO | NULL | 投注时间 |
| bet_type | enum('single','compound','dantuo','multiple') | NO | NULL | 投注类型：单式、复式、胆拖、多倍 |
| front_numbers | json | NO | NULL | 前区投注号码 |
| front_count | tinyint(4) | NO | NULL | 前区号码数量 |
| back_numbers | json | NO | NULL | 后区投注号码 |
| back_count | tinyint(4) | NO | NULL | 后区号码数量 |
| bet_amount | decimal(10,2) | NO | NULL | 投注金额 |
| multiple | tinyint(4) | YES | 1 | 投注倍数 |
| is_winning | tinyint(1) | YES | 0 | 是否中奖 |
| winning_level | varchar(50) | YES | NULL | 中奖等级 |
| winning_amount | decimal(12,2) | YES | 0.00 | 中奖金额 |
| strategy_type | varchar(50) | YES | NULL | 投注策略类型 |
| confidence_level | tinyint(4) | YES | NULL | 投注时置信度 |
| analysis_notes | text | YES | NULL | 投注分析笔记 |
| created_at | timestamp | YES | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | timestamp | YES | CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |

### 13. recommendation_details (算法推荐的具体组合详情表)

存储算法推荐的具体组合详情。

| 字段名 | 类型 | 允许空 | 默认值 | 注释 |
|--------|------|--------|--------|------|
| id | bigint(20) | NO | NULL | 唯一的主键 |
| recommendation_metadata_id | bigint(20) | NO | NULL | 外键，关联 algorithm_recommendation 表的 id |
| recommend_type | varchar(50) | NO | NULL | 推荐类型 (热号主攻, 复式(7+3) 等) |
| strategy_logic | varchar(255) | YES | NULL | 策略逻辑/说明 |
| front_numbers | varchar(100) | YES | NULL | 前区号码，逗号分隔 |
| back_numbers | varchar(100) | YES | NULL | 后区号码，逗号分隔 |
| win_probability | decimal(10, 5) | YES | NULL | 预计中奖概率 |
| created_at | timestamp | YES | CURRENT_TIMESTAMP | 创建时间 |

### 14. reward_penalty_records (奖罚分明记录表)

存储算法推荐的奖罚记录。

| 字段名 | 类型 | 允许空 | 默认值 | 注释 |
|--------|------|--------|--------|------|
| id | bigint(20) | NO | NULL | 主键，自增ID |
| period_number | varchar(20) | NO | NULL | 期号 |
| algorithm_version | varchar(50) | NO | NULL | 算法版本 |
| recommendation_id | bigint(20) | NO | NULL | 对应的推荐批次ID (关联到元数据表) |
| front_hit_count | tinyint(4) | NO | NULL | 前区命中数量 |
| back_hit_count | tinyint(4) | NO | NULL | 后区命中数量 |
| hit_score | decimal(5, 2) | NO | NULL | 命中得分 |
| reward_points | decimal(8, 2) | NO | NULL | 奖励积分 |
| penalty_points | decimal(8, 2) | NO | NULL | 惩罚积分 |
| net_points | decimal(8, 2) | NO | NULL | 净积分 |
| hit_details | json | YES | NULL | 命中详情 |
| missed_numbers | json | YES | NULL | 未命中号码分析 |
| performance_rating | tinyint(4) | YES | NULL | 表现评级(1-5星) |
| accuracy_deviation | decimal(5, 4) | YES | NULL | 准确度偏差 |
| improvement_suggestions | text | YES | NULL | 改进建议 |
| evaluation_time | timestamp | YES | CURRENT_TIMESTAMP | 评估时间 |

### 15. system_monitoring (系统实时监控表)

存储系统监控指标。

| 字段名 | 类型 | 允许空 | 默认值 | 注释 |
|--------|------|--------|--------|------|
| id | bigint(20) | NO | NULL | 主键，自增ID |
| metric_name | varchar(100) | NO | NULL | 指标名称 |
| metric_category | enum('performance','accuracy','resource','business') | NO | NULL | 指标分类 |
| metric_value | decimal(15, 6) | NO | NULL | 指标数值 |
| metric_unit | varchar(20) | YES | NULL | 指标单位 |
| warning_threshold | decimal(15, 6) | YES | NULL | 警告阈值 |
| critical_threshold | decimal(15, 6) | YES | NULL | 严重阈值 |
| current_status | enum('normal','warning','critical') | YES | 'normal' | 当前状态 |
| collected_at | timestamp | YES | CURRENT_TIMESTAMP | 采集时间 |

### 16. user_purchase_records (用户实际购买记录表)

存储用户实际购买记录。

| 字段名 | 类型 | 允许空 | 默认值 | 注释 |
|--------|------|--------|--------|------|
| id | bigint(20) | NO | NULL | 购买记录的唯一ID |
| period_metadata_id | bigint(20) | NO | NULL | 外键，关联 algorithm_recommendation (推荐批次元数据) 的 id |
| user_id | varchar(50) | NO | 'default' | 用户ID |
| purchase_type | varchar(50) | NO | NULL | 实际购买类型 (例如: 7+3复式, 单式A) |
| front_numbers_purchased | varchar(100) | NO | NULL | 实际购买的前区号码（逗号分隔） |
| back_numbers_purchased | varchar(100) | NO | NULL | 实际购买的后区号码（逗号分隔） |
| cost | decimal(10, 2) | YES | NULL | 购买花费金额 |
| is_hit | tinyint(1) | YES | 0 | 是否中奖 |
| front_hit_count | tinyint(4) | YES | 0 | 前区实际命中个数 (用于奖罚计算) |
| back_hit_count | tinyint(4) | YES | 0 | 后区实际命中个数 (用于奖罚计算) |
| winnings_amount | decimal(12, 2) | YES | 0.00 | 实际中奖金额 |
| purchase_time | datetime | NO | NULL | 实际购买时间 |
| created_at | timestamp | YES | CURRENT_TIMESTAMP | 创建时间 |

### 17. users (用户管理表)

存储用户信息。

| 字段名 | 类型 | 允许空 | 默认值 | 注释 |
|--------|------|--------|--------|------|
| id | bigint(20) | NO | NULL | 主键，自增ID |
| username | varchar(50) | NO | NULL | 用户名 |
| email | varchar(100) | YES | NULL | 邮箱 |
| password_hash | varchar(255) | NO | NULL | 密码哈希 |
| user_role | enum('admin','analyst','user') | YES | 'user' | 用户角色 |
| preferences | json | YES | NULL | 用户偏好设置 |
| risk_tolerance | enum('low','medium','high') | YES | 'medium' | 风险承受能力 |
| total_bets | int(11) | YES | 0 | 总投注次数 |
| total_investment | decimal(12,2) | YES | 0.00 | 总投入金额 |
| total_winnings | decimal(12,2) | YES | 0.00 | 总中奖金额 |
| success_rate | decimal(5,4) | YES | 0.0000 | 总体成功率 |
| is_active | tinyint(1) | YES | 1 | 是否活跃 |
| last_login | timestamp | YES | NULL | 最后登录时间 |
| created_at | timestamp | YES | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | timestamp | YES | CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |

## 数据库视图

### 1. algorithm_performance_view (算法性能视图)

提供算法性能的综合视图。

### 2. comprehensive_analysis_view (综合分析视图)

提供开奖数据、算法推荐、奖罚记录和用户购买的综合视图。

## 特殊说明

1. 本系统使用MySQL 8.0.12版本数据库
2. 所有表都使用InnoDB存储引擎
3. 字符集为utf8mb4，排序规则为utf8mb4_unicode_ci
4. 时间字段统一使用timestamp类型
5. 复杂数据结构使用JSON类型存储