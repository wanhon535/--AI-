/*
 Navicat Premium Data Transfer

 Source Server         : mysql8
 Source Server Type    : MySQL
 Source Server Version : 80012 (8.0.12)
 Source Host           : localhost:3309
 Source Schema         : lottery_analysis_system

 Target Server Type    : MySQL
 Target Server Version : 80012 (8.0.12)
 File Encoding         : 65001

 Date: 22/10/2025 11:47:17
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for ab_test_configs
-- ----------------------------
DROP TABLE IF EXISTS `ab_test_configs`;
CREATE TABLE `ab_test_configs`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `test_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '测试名称',
  `test_description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '测试描述',
  `algorithm_a` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '算法A版本',
  `algorithm_b` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '算法B版本',
  `split_ratio` decimal(3, 2) NULL DEFAULT 0.50 COMMENT '流量分配比例',
  `test_parameters` json NULL COMMENT '测试参数',
  `success_metrics` json NOT NULL COMMENT '成功指标定义',
  `test_status` enum('draft','running','paused','completed') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT 'draft' COMMENT '测试状态',
  `start_date` date NULL DEFAULT NULL COMMENT '开始日期',
  `end_date` date NULL DEFAULT NULL COMMENT '结束日期',
  `min_sample_size` int(11) NULL DEFAULT 100 COMMENT '最小样本量',
  `current_sample_size` int(11) NULL DEFAULT 0 COMMENT '当前样本量',
  `algorithm_a_performance` json NULL COMMENT '算法A表现',
  `algorithm_b_performance` json NULL COMMENT '算法B表现',
  `statistical_significance` decimal(5, 4) NULL DEFAULT NULL COMMENT '统计显著性',
  `created_by` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '创建人',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = 'A/B测试配置表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of ab_test_configs
-- ----------------------------

    -- 文件：src/sql/upgrade_add_performance_tables.sql
-- 用途：记录各算法每期表现 & 持久化当前算法权重

-- 1) 算法表现记录表
CREATE TABLE IF NOT EXISTS algorithm_performance (
  id INT AUTO_INCREMENT PRIMARY KEY,
  period_number VARCHAR(32) NOT NULL,
  algorithm VARCHAR(128) NOT NULL,
  hits FLOAT NOT NULL COMMENT '平均命中数（front+back的期望或实绩）',
  hit_rate FLOAT NOT NULL COMMENT '命中率（0-1）',
  score FLOAT NOT NULL COMMENT '算法表现得分，用于权重化',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_period_algo (period_number, algorithm)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2) 保存/持久化当前算法权重（用于下次prompt注入）
CREATE TABLE IF NOT EXISTS algorithm_weights (
  id INT AUTO_INCREMENT PRIMARY KEY,
  algorithm VARCHAR(128) NOT NULL UNIQUE,
  weight FLOAT NOT NULL COMMENT '0-1 归一化权重',
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ----------------------------
-- Table structure for algorithm_configs
-- ----------------------------
DROP TABLE IF EXISTS `algorithm_configs`;
CREATE TABLE `algorithm_configs`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `algorithm_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '算法名称',
  `algorithm_type` enum('statistical','ml','ensemble','optimization') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '算法类型',
  `parameters` json NOT NULL COMMENT '算法参数配置',
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '算法描述',
  `version` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '1.0.0' COMMENT '版本号',
  `is_active` tinyint(1) NULL DEFAULT 1 COMMENT '是否启用',
  `is_default` tinyint(1) NULL DEFAULT 0 COMMENT '是否默认算法',
  `min_data_required` int(11) NULL DEFAULT 50 COMMENT '最小数据要求',
  `expected_accuracy` decimal(5, 4) NULL DEFAULT NULL COMMENT '预期准确率',
  `computation_complexity` enum('low','medium','high') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT 'medium' COMMENT '计算复杂度',
  `memory_requirements` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '内存要求',
  `created_by` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '创建人',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '算法配置表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of algorithm_configs
-- ----------------------------

-- ----------------------------
-- Table structure for algorithm_performance
-- ----------------------------
DROP TABLE IF EXISTS `algorithm_performance`;
CREATE TABLE `algorithm_performance`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `algorithm_version` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '算法版本',
  `total_recommendations` int(11) NULL DEFAULT 0 COMMENT '总推荐次数',
  `total_periods_analyzed` int(11) NULL DEFAULT 0 COMMENT '总分析期数',
  `avg_front_hit_rate` decimal(5, 4) NULL DEFAULT 0.0000 COMMENT '平均前区命中率',
  `avg_back_hit_rate` decimal(5, 4) NULL DEFAULT 0.0000 COMMENT '平均后区命中率',
  `hit_distribution` json NULL COMMENT '命中分布统计',
  `confidence_accuracy` decimal(5, 4) NULL DEFAULT 0.0000 COMMENT '置信度准确性',
  `risk_adjusted_return` decimal(8, 4) NULL DEFAULT 0.0000 COMMENT '风险调整后收益',
  `stability_score` decimal(5, 4) NULL DEFAULT 0.0000 COMMENT '稳定性评分',
  `consistency_rate` decimal(5, 4) NULL DEFAULT 0.0000 COMMENT '一致性比率',
  `current_weight` decimal(4, 3) NULL DEFAULT 0.100 COMMENT '当前权重',
  `weight_history` json NULL COMMENT '权重历史记录',
  `performance_trend` enum('improving','stable','declining') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT 'stable' COMMENT '性能趋势',
  `last_updated` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `algorithm_version`(`algorithm_version` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '算法性能统计表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of algorithm_performance
-- ----------------------------
INSERT INTO `algorithm_performance` VALUES (1, 'v1.0-statistical', 0, 0, 0.0000, 0.0000, NULL, 0.0000, 0.0000, 0.0000, 0.0000, 0.300, NULL, 'stable', '2025-10-20 10:37:19');
INSERT INTO `algorithm_performance` VALUES (2, 'v2.0-ml-basic', 0, 0, 0.0000, 0.0000, NULL, 0.0000, 0.0000, 0.0000, 0.0000, 0.400, NULL, 'stable', '2025-10-20 10:37:19');
INSERT INTO `algorithm_performance` VALUES (3, 'v3.0-ensemble', 0, 0, 0.0000, 0.0000, NULL, 0.0000, 0.0000, 0.0000, 0.0000, 0.300, NULL, 'stable', '2025-10-20 10:37:19');

-- ----------------------------
-- Table structure for algorithm_recommendation
-- ----------------------------
DROP TABLE IF EXISTS `algorithm_recommendation`;
CREATE TABLE `algorithm_recommendation`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `period_number` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '推荐期号',
  `recommend_time` datetime NOT NULL COMMENT '推荐时间',
  `algorithm_version` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '算法版本',
  `algorithm_parameters` json NULL COMMENT '算法参数配置',
  `model_weights` json NULL COMMENT '模型权重配置',
  `confidence_score` decimal(5, 4) NOT NULL COMMENT '总体置信度',
  `risk_level` enum('low','medium','high') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '总体风险等级',
  `analysis_basis` json NULL COMMENT '分析依据数据',
  `key_patterns` json NULL COMMENT '关键模式识别',
  `models` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '推荐模型名称 (根据原始表增加)',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_period_algorithm`(`period_number` ASC, `algorithm_version` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '算法推荐批次元数据表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of algorithm_recommendation
-- ----------------------------

-- ----------------------------
-- Table structure for data_update_logs
-- ----------------------------
DROP TABLE IF EXISTS `data_update_logs`;
CREATE TABLE `data_update_logs`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `update_type` enum('manual','automatic','api') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '更新类型',
  `data_source` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '数据来源',
  `period_range` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '更新的期号范围',
  `records_added` int(11) NULL DEFAULT 0 COMMENT '新增记录数',
  `records_updated` int(11) NULL DEFAULT 0 COMMENT '更新记录数',
  `records_deleted` int(11) NULL DEFAULT 0 COMMENT '删除记录数',
  `update_status` enum('pending','success','failed','partial') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '更新状态',
  `error_message` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '错误信息',
  `started_at` timestamp NOT NULL COMMENT '开始时间',
  `completed_at` timestamp NULL DEFAULT NULL COMMENT '完成时间',
  `execution_duration` int(11) NULL DEFAULT NULL COMMENT '执行时长(秒)',
  `initiated_by` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '发起人',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '数据更新日志表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of data_update_logs
-- ----------------------------

-- ----------------------------
-- Table structure for financial_reports
-- ----------------------------
DROP TABLE IF EXISTS `financial_reports`;
CREATE TABLE `financial_reports`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `report_period` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '报表期间',
  `report_type` enum('daily','weekly','monthly','yearly') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '报表类型',
  `total_investment` decimal(12, 2) NULL DEFAULT 0.00 COMMENT '总投入金额',
  `total_winnings` decimal(12, 2) NULL DEFAULT 0.00 COMMENT '总中奖金额',
  `net_profit` decimal(12, 2) NULL DEFAULT 0.00 COMMENT '净利润',
  `return_rate` decimal(8, 4) NULL DEFAULT 0.0000 COMMENT '回报率',
  `total_bets` int(11) NULL DEFAULT 0 COMMENT '总投注数',
  `winning_bets` int(11) NULL DEFAULT 0 COMMENT '中奖投注数',
  `bet_success_rate` decimal(5, 4) NULL DEFAULT 0.0000 COMMENT '投注成功率',
  `algorithm_performance` json NULL COMMENT '算法表现详情',
  `best_performing_algorithm` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '最佳表现算法',
  `max_drawdown` decimal(8, 4) NULL DEFAULT NULL COMMENT '最大回撤',
  `sharpe_ratio` decimal(8, 4) NULL DEFAULT NULL COMMENT '夏普比率',
  `volatility` decimal(8, 4) NULL DEFAULT NULL COMMENT '波动率',
  `generated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '生成时间',
  `generated_by` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '生成人',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_period_type`(`report_period` ASC, `report_type` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '财务报表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of financial_reports
-- ----------------------------

-- ----------------------------
-- Table structure for lottery_history
-- ----------------------------
DROP TABLE IF EXISTS `lottery_history`;
CREATE TABLE `lottery_history`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `period_number` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '期号，如2024001',
  `draw_date` date NOT NULL COMMENT '开奖日期',
  `draw_time` datetime NOT NULL COMMENT '开奖具体时间',
  `front_area_1` tinyint(4) NOT NULL,
  `front_area_2` tinyint(4) NOT NULL,
  `front_area_3` tinyint(4) NOT NULL,
  `front_area_4` tinyint(4) NOT NULL,
  `front_area_5` tinyint(4) NOT NULL,
  `back_area_1` tinyint(4) NOT NULL,
  `back_area_2` tinyint(4) NOT NULL,
  `sum_value` smallint(6) NOT NULL COMMENT '和值',
  `span_value` tinyint(4) NOT NULL COMMENT '跨度',
  `ac_value` tinyint(4) NOT NULL COMMENT 'AC值',
  `odd_even_ratio` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '奇偶比，如3:2',
  `size_ratio` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '大小比(以18为界)，如2:3',
  `prime_composite_ratio` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '质合比',
  `consecutive_numbers` json NULL COMMENT '连号信息，如[12,13]',
  `consecutive_count` tinyint(4) NULL DEFAULT 0 COMMENT '连号组数',
  `tail_numbers` json NULL COMMENT '尾数分布',
  `data_source` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT 'official' COMMENT '数据来源',
  `data_quality` tinyint(4) NULL DEFAULT 100 COMMENT '数据质量评分',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `period_number`(`period_number` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 6 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '历史开奖数据表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of lottery_history
-- ----------------------------
INSERT INTO `lottery_history` VALUES (1, '2025067', '2025-06-07', '2025-10-22 10:57:52', 6, 10, 12, 21, 22, 1, 6, 78, 16, 0, '1:4', '2:3', NULL, '[[21, 22]]', 1, NULL, 'official', 100, '2025-10-22 10:57:51', '2025-10-22 10:57:51');

-- ----------------------------
-- Table structure for model_training_logs
-- ----------------------------
DROP TABLE IF EXISTS `model_training_logs`;
CREATE TABLE `model_training_logs`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `algorithm_version` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '算法版本',
  `training_date` date NOT NULL COMMENT '训练日期',
  `data_start_period` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '训练数据开始期号',
  `data_end_period` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '训练数据结束期号',
  `training_samples` int(11) NOT NULL COMMENT '训练样本数',
  `training_parameters` json NULL COMMENT '训练参数',
  `feature_set` json NULL COMMENT '特征集合',
  `training_accuracy` decimal(5, 4) NULL DEFAULT NULL COMMENT '训练准确率',
  `validation_accuracy` decimal(5, 4) NULL DEFAULT NULL COMMENT '验证准确率',
  `test_accuracy` decimal(5, 4) NULL DEFAULT NULL COMMENT '测试准确率',
  `model_file_path` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '模型文件路径',
  `model_size` bigint(20) NULL DEFAULT NULL COMMENT '模型文件大小',
  `model_hash` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '模型文件哈希',
  `training_status` enum('running','completed','failed') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '训练状态',
  `error_log` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '错误日志',
  `started_at` timestamp NOT NULL COMMENT '开始时间',
  `completed_at` timestamp NULL DEFAULT NULL COMMENT '完成时间',
  `training_duration` int(11) NULL DEFAULT NULL COMMENT '训练时长(秒)',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '预测模型训练记录表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of model_training_logs
-- ----------------------------

-- ----------------------------
-- Table structure for notifications
-- ----------------------------
DROP TABLE IF EXISTS `notifications`;
CREATE TABLE `notifications`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '用户ID',
  `notification_type` enum('system','recommendation','warning','success') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '通知类型',
  `title` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '通知标题',
  `message` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '通知内容',
  `related_entity_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '关联实体类型',
  `related_entity_id` bigint(20) NULL DEFAULT NULL COMMENT '关联实体ID',
  `is_read` tinyint(1) NULL DEFAULT 0 COMMENT '是否已读',
  `is_archived` tinyint(1) NULL DEFAULT 0 COMMENT '是否归档',
  `expires_at` timestamp NULL DEFAULT NULL COMMENT '过期时间',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '系统通知消息表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of notifications
-- ----------------------------

-- ----------------------------
-- Table structure for number_statistics
-- ----------------------------
DROP TABLE IF EXISTS `number_statistics`;
CREATE TABLE `number_statistics`  (
  `number` tinyint(4) NOT NULL COMMENT '号码',
  `number_type` enum('front','back') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '号码类型：前区/后区',
  `total_appearances` int(11) NULL DEFAULT 0 COMMENT '总出现次数',
  `appearance_rate` decimal(5, 4) NULL DEFAULT 0.0000 COMMENT '出现频率',
  `recent_10_appearances` int(11) NULL DEFAULT 0 COMMENT '最近10期出现次数',
  `recent_20_appearances` int(11) NULL DEFAULT 0 COMMENT '最近20期出现次数',
  `recent_50_appearances` int(11) NULL DEFAULT 0 COMMENT '最近50期出现次数',
  `current_omission` int(11) NULL DEFAULT 0 COMMENT '当前遗漏期数',
  `max_omission` int(11) NULL DEFAULT 0 COMMENT '历史最大遗漏',
  `avg_omission` decimal(6, 2) NULL DEFAULT 0.00 COMMENT '平均遗漏',
  `heat_status` enum('hot','warm','cold','very_cold') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT 'warm' COMMENT '热冷状态',
  `heat_score` decimal(5, 2) NULL DEFAULT 0.00 COMMENT '热度评分',
  `strong_followers` json NULL COMMENT '强跟随号码',
  `strong_precursors` json NULL COMMENT '强前导号码',
  `position_preference` json NULL COMMENT '位置偏好统计',
  `last_updated` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`number`, `number_type`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '号码统计分析表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of number_statistics
-- ----------------------------
INSERT INTO `number_statistics` VALUES (1, 'front', 0, 0.0000, 0, 0, 0, 0, 0, 0.00, 'warm', 0.00, NULL, NULL, NULL, '2025-10-20 10:37:19');
INSERT INTO `number_statistics` VALUES (1, 'back', 0, 0.0000, 0, 0, 0, 0, 0, 0.00, 'warm', 0.00, NULL, NULL, NULL, '2025-10-20 10:37:19');
INSERT INTO `number_statistics` VALUES (12, 'back', 0, 0.0000, 0, 0, 0, 0, 0, 0.00, 'warm', 0.00, NULL, NULL, NULL, '2025-10-20 10:37:19');
INSERT INTO `number_statistics` VALUES (35, 'front', 0, 0.0000, 0, 0, 0, 0, 0, 0.00, 'warm', 0.00, NULL, NULL, NULL, '2025-10-20 10:37:19');

-- ----------------------------
-- Table structure for pattern_recognition
-- ----------------------------
DROP TABLE IF EXISTS `pattern_recognition`;
CREATE TABLE `pattern_recognition`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `pattern_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '模式类型',
  `pattern_description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '模式描述',
  `pattern_features` json NOT NULL COMMENT '模式特征',
  `pattern_signature` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '模式特征签名',
  `occurrence_count` int(11) NULL DEFAULT 0 COMMENT '出现次数',
  `success_rate` decimal(5, 4) NULL DEFAULT 0.0000 COMMENT '成功率',
  `confidence_level` decimal(5, 4) NULL DEFAULT 0.0000 COMMENT '置信水平',
  `first_occurrence_date` date NULL DEFAULT NULL COMMENT '首次出现日期',
  `last_occurrence_date` date NULL DEFAULT NULL COMMENT '最后出现日期',
  `avg_occurrence_interval` decimal(6, 2) NULL DEFAULT NULL COMMENT '平均出现间隔',
  `is_active` tinyint(1) NULL DEFAULT 1 COMMENT '是否活跃',
  `validity_period` int(11) NULL DEFAULT NULL COMMENT '有效周期',
  `related_algorithms` json NULL COMMENT '关联算法',
  `discovered_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `last_verified` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `pattern_signature`(`pattern_signature` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '模式识别记录表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of pattern_recognition
-- ----------------------------

-- ----------------------------
-- Table structure for personal_betting
-- ----------------------------
DROP TABLE IF EXISTS `personal_betting`;
CREATE TABLE `personal_betting`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'default' COMMENT '用户ID，支持多用户',
  `period_number` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '投注期号',
  `bet_time` datetime NOT NULL COMMENT '投注时间',
  `bet_type` enum('single','compound','dantuo','multiple') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '投注类型：单式、复式、胆拖、多倍',
  `front_numbers` json NOT NULL COMMENT '前区投注号码',
  `front_count` tinyint(4) NOT NULL COMMENT '前区号码数量',
  `back_numbers` json NOT NULL COMMENT '后区投注号码',
  `back_count` tinyint(4) NOT NULL COMMENT '后区号码数量',
  `bet_amount` decimal(10, 2) NOT NULL COMMENT '投注金额',
  `multiple` tinyint(4) NULL DEFAULT 1 COMMENT '投注倍数',
  `is_winning` tinyint(1) NULL DEFAULT 0 COMMENT '是否中奖',
  `winning_level` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '中奖等级',
  `winning_amount` decimal(12, 2) NULL DEFAULT 0.00 COMMENT '中奖金额',
  `strategy_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '投注策略类型',
  `confidence_level` tinyint(4) NULL DEFAULT NULL COMMENT '投注时置信度',
  `analysis_notes` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '投注分析笔记',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '个人自由投注记录表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of personal_betting
-- ----------------------------

-- ----------------------------
-- Table structure for recommendation_details
-- ----------------------------
DROP TABLE IF EXISTS `recommendation_details`;
CREATE TABLE `recommendation_details`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '唯一的主键',
  `recommendation_metadata_id` bigint(20) NOT NULL COMMENT '外键，关联 algorithm_recommendation 表的 id',
  `recommend_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '推荐类型 (热号主攻, 复式(7+3) 等)',
  `strategy_logic` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '策略逻辑/说明',
  `front_numbers` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '前区号码，逗号分隔',
  `back_numbers` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '后区号码，逗号分隔',
  `win_probability` decimal(10, 5) NULL DEFAULT NULL COMMENT '预计中奖概率',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_metadata_id`(`recommendation_metadata_id` ASC) USING BTREE,
  INDEX `idx_recommend_type`(`recommend_type` ASC) USING BTREE,
  CONSTRAINT `fk_recommendation_metadata_id` FOREIGN KEY (`recommendation_metadata_id`) REFERENCES `algorithm_recommendation` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '算法推荐的具体组合详情表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of recommendation_details
-- ----------------------------

-- ----------------------------
-- Table structure for reward_penalty_records
-- ----------------------------
DROP TABLE IF EXISTS `reward_penalty_records`;
CREATE TABLE `reward_penalty_records`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `period_number` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '期号',
  `algorithm_version` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '算法版本',
  `recommendation_id` bigint(20) NOT NULL COMMENT '对应的推荐批次ID (关联到元数据表)',
  `front_hit_count` tinyint(4) NOT NULL COMMENT '前区命中数量',
  `back_hit_count` tinyint(4) NOT NULL COMMENT '后区命中数量',
  `hit_score` decimal(5, 2) NOT NULL COMMENT '命中得分',
  `reward_points` decimal(8, 2) NOT NULL COMMENT '奖励积分',
  `penalty_points` decimal(8, 2) NOT NULL COMMENT '惩罚积分',
  `net_points` decimal(8, 2) NOT NULL COMMENT '净积分',
  `hit_details` json NULL COMMENT '命中详情',
  `missed_numbers` json NULL COMMENT '未命中号码分析',
  `performance_rating` tinyint(4) NULL DEFAULT NULL COMMENT '表现评级(1-5星)',
  `accuracy_deviation` decimal(5, 4) NULL DEFAULT NULL COMMENT '准确度偏差',
  `improvement_suggestions` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '改进建议',
  `evaluation_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_period_algorithm`(`period_number` ASC, `algorithm_version` ASC) USING BTREE,
  INDEX `recommendation_id`(`recommendation_id` ASC) USING BTREE,
  CONSTRAINT `fk_reward_to_recommendation_metadata` FOREIGN KEY (`recommendation_id`) REFERENCES `algorithm_recommendation` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '奖罚分明记录表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of reward_penalty_records
-- ----------------------------

-- ----------------------------
-- Table structure for system_monitoring
-- ----------------------------
DROP TABLE IF EXISTS `system_monitoring`;
CREATE TABLE `system_monitoring`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `metric_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '指标名称',
  `metric_category` enum('performance','accuracy','resource','business') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '指标分类',
  `metric_value` decimal(15, 6) NOT NULL COMMENT '指标数值',
  `metric_unit` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '指标单位',
  `warning_threshold` decimal(15, 6) NULL DEFAULT NULL COMMENT '警告阈值',
  `critical_threshold` decimal(15, 6) NULL DEFAULT NULL COMMENT '严重阈值',
  `current_status` enum('normal','warning','critical') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT 'normal' COMMENT '当前状态',
  `collected_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '采集时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '系统实时监控表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of system_monitoring
-- ----------------------------

-- ----------------------------
-- Table structure for user_purchase_records
-- ----------------------------
DROP TABLE IF EXISTS `user_purchase_records`;
CREATE TABLE `user_purchase_records`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '购买记录的唯一ID',
  `period_metadata_id` bigint(20) NOT NULL COMMENT '外键，关联 algorithm_recommendation (推荐批次元数据) 的 id',
  `user_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'default' COMMENT '用户ID',
  `purchase_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '实际购买类型 (例如: 7+3复式, 单式A)',
  `front_numbers_purchased` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '实际购买的前区号码（逗号分隔）',
  `back_numbers_purchased` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '实际购买的后区号码（逗号分隔）',
  `cost` decimal(10, 2) NULL DEFAULT NULL COMMENT '购买花费金额',
  `is_hit` tinyint(1) NULL DEFAULT 0 COMMENT '是否中奖',
  `front_hit_count` tinyint(4) NULL DEFAULT 0 COMMENT '前区实际命中个数 (用于奖罚计算)',
  `back_hit_count` tinyint(4) NULL DEFAULT 0 COMMENT '后区实际命中个数 (用于奖罚计算)',
  `winnings_amount` decimal(12, 2) NULL DEFAULT 0.00 COMMENT '实际中奖金额',
  `purchase_time` datetime NOT NULL COMMENT '实际购买时间',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_period_metadata_id`(`period_metadata_id` ASC) USING BTREE,
  INDEX `idx_user_period`(`user_id` ASC, `period_metadata_id` ASC) USING BTREE,
  CONSTRAINT `fk_purchase_to_metadata` FOREIGN KEY (`period_metadata_id`) REFERENCES `algorithm_recommendation` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '用户实际购买记录表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of user_purchase_records
-- ----------------------------

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '用户名',
  `email` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '邮箱',
  `password_hash` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '密码哈希',
  `user_role` enum('admin','analyst','user') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT 'user' COMMENT '用户角色',
  `preferences` json NULL COMMENT '用户偏好设置',
  `risk_tolerance` enum('low','medium','high') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT 'medium' COMMENT '风险承受能力',
  `total_bets` int(11) NULL DEFAULT 0 COMMENT '总投注次数',
  `total_investment` decimal(12, 2) NULL DEFAULT 0.00 COMMENT '总投入金额',
  `total_winnings` decimal(12, 2) NULL DEFAULT 0.00 COMMENT '总中奖金额',
  `success_rate` decimal(5, 4) NULL DEFAULT 0.0000 COMMENT '总体成功率',
  `is_active` tinyint(1) NULL DEFAULT 1 COMMENT '是否活跃',
  `last_login` timestamp NULL DEFAULT NULL COMMENT '最后登录时间',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `username`(`username` ASC) USING BTREE,
  UNIQUE INDEX `email`(`email` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '用户管理表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of users
-- ----------------------------

-- ----------------------------
-- View structure for algorithm_performance_view
-- ----------------------------
DROP VIEW IF EXISTS `algorithm_performance_view`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `algorithm_performance_view` AS select `ap`.`algorithm_version` AS `algorithm_version`,`ap`.`total_recommendations` AS `total_recommendations`,`ap`.`avg_front_hit_rate` AS `avg_front_hit_rate`,`ap`.`avg_back_hit_rate` AS `avg_back_hit_rate`,`ap`.`confidence_accuracy` AS `confidence_accuracy`,`ap`.`stability_score` AS `stability_score`,`ap`.`performance_trend` AS `performance_trend`,count(`rpr`.`id`) AS `recent_evaluations`,avg(`rpr`.`performance_rating`) AS `recent_rating` from (`algorithm_performance` `ap` left join `reward_penalty_records` `rpr` on(((`ap`.`algorithm_version` = `rpr`.`algorithm_version`) and (`rpr`.`evaluation_time` >= (now() - interval 30 day))))) group by `ap`.`algorithm_version`;

-- ----------------------------
-- View structure for comprehensive_analysis_view
-- ----------------------------
DROP VIEW IF EXISTS `comprehensive_analysis_view`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `comprehensive_analysis_view` AS select `lh`.`period_number` AS `period_number`,`lh`.`draw_date` AS `draw_date`,`lh`.`front_area_1` AS `front_area_1`,`lh`.`sum_value` AS `sum_value`,`lh`.`odd_even_ratio` AS `odd_even_ratio`,`lh`.`size_ratio` AS `size_ratio`,`ar`.`algorithm_version` AS `algorithm_version`,`ar`.`confidence_score` AS `confidence_score`,`ar`.`risk_level` AS `risk_level`,`rpr`.`front_hit_count` AS `front_hit_count`,`rpr`.`back_hit_count` AS `back_hit_count`,`rpr`.`hit_score` AS `hit_score`,`rpr`.`performance_rating` AS `performance_rating`,`upr`.`purchase_type` AS `purchased_type`,`upr`.`front_hit_count` AS `purchased_front_hit`,`upr`.`back_hit_count` AS `purchased_back_hit`,`upr`.`winnings_amount` AS `purchased_winnings` from (((`lottery_history` `lh` left join `algorithm_recommendation` `ar` on((`lh`.`period_number` = `ar`.`period_number`))) left join `reward_penalty_records` `rpr` on((`ar`.`id` = `rpr`.`recommendation_id`))) left join `user_purchase_records` `upr` on((`ar`.`id` = `upr`.`period_metadata_id`)));

SET FOREIGN_KEY_CHECKS = 1;
