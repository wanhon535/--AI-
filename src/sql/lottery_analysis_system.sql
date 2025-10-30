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

 Date: 30/10/2025 17:48:58
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
  `issue` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `algorithm` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `hits` float NULL DEFAULT 0,
  `hit_rate` float NULL DEFAULT 0,
  `score` float NULL DEFAULT 0,
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uq_issue_algo`(`issue`, `algorithm`) USING BTREE
) ENGINE = MyISAM AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of algorithm_performance
-- ----------------------------

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
  `risk_level` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT 'medium',
  `analysis_basis` json NULL COMMENT '分析依据数据',
  `key_patterns` json NULL COMMENT '关键模式识别',
  `models` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '推荐模型名称 (根据原始表增加)',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_period_algorithm`(`period_number` ASC, `algorithm_version` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 34 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '算法推荐批次元数据表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of algorithm_recommendation
-- ----------------------------
INSERT INTO `algorithm_recommendation` VALUES (1, '2025068', '2025-10-22 14:52:11', 'qwen3-max', NULL, NULL, 0.8500, 'medium', NULL, NULL, 'qwen3-max', '2025-10-22 14:52:10');
INSERT INTO `algorithm_recommendation` VALUES (2, '2025068', '2025-10-22 15:38:14', 'qwen3-max', NULL, NULL, 0.8500, 'medium', NULL, NULL, 'qwen3-max', '2025-10-22 15:38:14');
INSERT INTO `algorithm_recommendation` VALUES (3, '2025068', '2025-10-22 15:56:53', 'qwen3-max', NULL, NULL, 0.8500, 'medium', NULL, NULL, 'qwen3-max', '2025-10-22 15:56:53');
INSERT INTO `algorithm_recommendation` VALUES (4, '2025068', '2025-10-22 16:21:43', 'qwen3-max', NULL, NULL, 0.8500, 'medium', NULL, NULL, 'qwen3-max', '2025-10-22 16:21:43');
INSERT INTO `algorithm_recommendation` VALUES (5, '2025068', '2025-10-22 17:51:38', 'qwen3-max', NULL, NULL, 0.8500, 'medium', NULL, NULL, 'qwen3-max', '2025-10-22 17:51:37');
INSERT INTO `algorithm_recommendation` VALUES (6, '2025068', '2025-10-23 11:24:37', 'qwen3-max', NULL, NULL, 0.8500, 'medium', NULL, NULL, 'qwen3-max', '2025-10-23 11:24:37');
INSERT INTO `algorithm_recommendation` VALUES (7, '2025069', '2025-10-24 17:36:22', 'qwen3-max', NULL, NULL, 0.8500, 'medium', NULL, NULL, 'qwen3-max', '2025-10-24 17:36:22');
INSERT INTO `algorithm_recommendation` VALUES (8, '2025069', '2025-10-24 17:52:07', 'qwen3-max', NULL, NULL, 0.8500, 'medium', NULL, NULL, 'qwen3-max', '2025-10-24 17:52:06');
INSERT INTO `algorithm_recommendation` VALUES (9, '2025069', '2025-10-24 17:52:07', 'qwen3-max', NULL, NULL, 0.8500, 'medium', NULL, NULL, 'qwen3-max', '2025-10-24 17:52:06');
INSERT INTO `algorithm_recommendation` VALUES (10, '2025068', '2025-10-27 11:08:57', 'v1.0-statistical', NULL, NULL, 0.7500, 'medium', NULL, NULL, 'v1.0-statistical', '2025-10-27 11:08:56');
INSERT INTO `algorithm_recommendation` VALUES (11, '2025069', '2025-10-28 09:49:05', 'qwen3-max', NULL, NULL, 0.8500, '整体风险中等偏低。核心复式提供稳定基础命中，卫星单式覆盖边缘可能性，策略具备良好容错性。', NULL, NULL, 'qwen3-max', '2025-10-28 09:49:05');
INSERT INTO `algorithm_recommendation` VALUES (12, '2025069', '2025-10-28 15:45:56', 'qwen3-max (V14.5-Prometheus-Ω)', NULL, NULL, 0.8800, '整体风险中等。核心注较为稳健，卫星注具备博取高回报的潜力，策略已做风险对冲。', NULL, NULL, 'qwen3-max (V14.5-Prometheus-Ω)', '2025-10-28 15:45:56');
INSERT INTO `algorithm_recommendation` VALUES (13, '2025069', '2025-10-28 18:05:50', 'qwen3-max (V14.5-Prometheus-Ω)', NULL, NULL, 0.8900, '整体风险中等偏低。主力胆拖覆盖高置信热区，邻号扩展增强边缘弹性，冷热混合提供尾部对冲。策略在数据稀疏条件下稳健性较强。', NULL, NULL, 'qwen3-max (V14.5-Prometheus-Ω)', '2025-10-28 18:05:50');
INSERT INTO `algorithm_recommendation` VALUES (14, '2025069', '2025-10-28 18:11:10', 'qwen3-max (V14.5-Prometheus-Ω)', NULL, NULL, 0.8500, '整体风险中性。核心复式提供稳定覆盖，卫星注增强边缘情景应对能力，符合用户风险偏好。', NULL, NULL, 'qwen3-max (V14.5-Prometheus-Ω)', '2025-10-28 18:11:09');
INSERT INTO `algorithm_recommendation` VALUES (15, '2025069', '2025-10-29 12:53:20', 'qwen3-max (V14.5-Prometheus-Ω)', NULL, NULL, 0.6900, '整体风险中性偏低。因无历史数据，策略以探索与覆盖为主，避免重仓单一假设。总成本仅10元，风险敞口极小。', NULL, NULL, 'qwen3-max (V14.5-Prometheus-Ω)', '2025-10-29 12:53:20');
INSERT INTO `algorithm_recommendation` VALUES (16, '2025070', '2025-10-29 16:51:47', 'qwen3-max (V14.5-Prometheus-Ω)', NULL, NULL, 0.8200, '整体风险中性。核心注提供稳定基础命中，卫星注通过扰动与冷号试探提升上限，策略在无历史数据条件下实现稳健与探索的平衡。', NULL, NULL, 'qwen3-max (V14.5-Prometheus-Ω)', '2025-10-29 16:51:46');
INSERT INTO `algorithm_recommendation` VALUES (17, '2025070', '2025-10-29 17:01:35', 'qwen3-max (V14.5-Prometheus-Ω)', NULL, NULL, 0.7200, '风险中等偏低。因无历史数据，策略以稳健探索为主，牺牲部分收益潜力换取覆盖广度，符合中性风险偏好。', NULL, NULL, 'qwen3-max (V14.5-Prometheus-Ω)', '2025-10-29 17:01:35');
INSERT INTO `algorithm_recommendation` VALUES (18, '2025123', '2025-10-29 17:26:22', 'qwen3-max (V14.5-Prometheus-Ω)', NULL, NULL, 0.8500, '整体风险中性。核心注提供稳定期望，卫星注覆盖冷号、结构平衡与次热区域，有效分散模型不确定性带来的风险。', '{\"dynamic_ensemble_optimizer\": {\"version\": \"2.0\", \"analysis\": {\"algorithms_used\": [\"frequency_analysis\", \"hot_cold_number\", \"omission_value\", \"bayesian_number_predictor\", \"markov_transition_model\", \"number_graph_analyzer\"], \"current_weights\": {\"omission_value\": 0.2608695652173913, \"hot_cold_number\": 0.04347826086956521, \"frequency_analysis\": 0.17391304347826084, \"number_graph_analyzer\": 0.3478260869565217, \"markov_transition_model\": 0.08695652173913042, \"bayesian_number_predictor\": 0.08695652173913042}, \"ensemble_method\": \"dynamic_weighted\"}, \"algorithm\": \"dynamic_ensemble_optimizer\", \"recommendations\": [{\"confidence\": 0.617391304347826, \"back_numbers\": [4, 10], \"front_numbers\": [3, 5, 6, 7, 8], \"dynamic_weights_applied\": true}]}}', NULL, 'qwen3-max (V14.5-Prometheus-Ω)', '2025-10-29 17:26:22');
INSERT INTO `algorithm_recommendation` VALUES (19, '2025123', '2025-10-29 17:30:43', 'qwen3-max (V14.5-Prometheus-Ω)', NULL, NULL, 0.7700, '在无历史数据约束下，策略采取保守探索姿态。核心复式提供基础命中保障，单式探索增强尾部覆盖。整体风险可控，符合中性偏好。', '{\"dynamic_ensemble_optimizer\": {\"version\": \"2.0\", \"analysis\": {\"algorithms_used\": [\"frequency_analysis\", \"hot_cold_number\", \"omission_value\", \"bayesian_number_predictor\", \"markov_transition_model\", \"number_graph_analyzer\"], \"current_weights\": {\"omission_value\": 0.2608695652173913, \"hot_cold_number\": 0.04347826086956521, \"frequency_analysis\": 0.17391304347826084, \"number_graph_analyzer\": 0.3478260869565217, \"markov_transition_model\": 0.08695652173913042, \"bayesian_number_predictor\": 0.08695652173913042}, \"ensemble_method\": \"dynamic_weighted\"}, \"algorithm\": \"dynamic_ensemble_optimizer\", \"recommendations\": [{\"confidence\": 0.617391304347826, \"back_numbers\": [4, 10], \"front_numbers\": [3, 5, 6, 7, 8], \"dynamic_weights_applied\": true}]}}', NULL, 'qwen3-max (V14.5-Prometheus-Ω)', '2025-10-29 17:30:43');
INSERT INTO `algorithm_recommendation` VALUES (20, '2025123', '2025-10-29 18:07:12', 'qwen3-max (V14.5-Prometheus-Ω)', NULL, NULL, 0.8500, '整体风险中性。核心注稳健，胆拖注兼顾效率与覆盖，双冷单式提供尾部风险对冲。总成本68元，留有32元缓冲，符合中性风险偏好。', '{\"dynamic_ensemble_optimizer\": {\"version\": \"2.0\", \"analysis\": {\"algorithms_used\": [\"frequency_analysis\", \"hot_cold_number\", \"omission_value\", \"bayesian_number_predictor\", \"markov_transition_model\", \"number_graph_analyzer\"], \"current_weights\": {\"omission_value\": 0.2608695652173913, \"hot_cold_number\": 0.04347826086956521, \"frequency_analysis\": 0.17391304347826084, \"number_graph_analyzer\": 0.3478260869565217, \"markov_transition_model\": 0.08695652173913042, \"bayesian_number_predictor\": 0.08695652173913042}, \"ensemble_method\": \"dynamic_weighted\"}, \"algorithm\": \"dynamic_ensemble_optimizer\", \"recommendations\": [{\"confidence\": 0.617391304347826, \"back_numbers\": [4, 10], \"front_numbers\": [3, 5, 6, 7, 8], \"dynamic_weights_applied\": true}]}}', NULL, 'qwen3-max (V14.5-Prometheus-Ω)', '2025-10-29 18:07:12');
INSERT INTO `algorithm_recommendation` VALUES (21, '2025123', '2025-10-29 18:08:43', 'qwen3-max (V14.5-Prometheus-Ω)', NULL, NULL, 0.8200, '整体风险中等偏低。在无历史数据前提下，策略以稳健覆盖为主，卫星注提供有限探索，避免激进押注。组合多样性良好，符合中性风险偏好。', '{\"dynamic_ensemble_optimizer\": {\"version\": \"2.0\", \"analysis\": {\"algorithms_used\": [\"frequency_analysis\", \"hot_cold_number\", \"omission_value\", \"bayesian_number_predictor\", \"markov_transition_model\", \"number_graph_analyzer\"], \"current_weights\": {\"omission_value\": 0.2608695652173913, \"hot_cold_number\": 0.04347826086956521, \"frequency_analysis\": 0.17391304347826084, \"number_graph_analyzer\": 0.3478260869565217, \"markov_transition_model\": 0.08695652173913042, \"bayesian_number_predictor\": 0.08695652173913042}, \"ensemble_method\": \"dynamic_weighted\"}, \"algorithm\": \"dynamic_ensemble_optimizer\", \"recommendations\": [{\"confidence\": 0.617391304347826, \"back_numbers\": [4, 10], \"front_numbers\": [3, 5, 6, 7, 8], \"dynamic_weights_applied\": true}]}}', NULL, 'qwen3-max (V14.5-Prometheus-Ω)', '2025-10-29 18:08:43');
INSERT INTO `algorithm_recommendation` VALUES (22, '2025123', '2025-10-29 18:11:14', 'qwen3-max (V14.5-Prometheus-Ω)', NULL, NULL, 0.7600, '在无历史数据前提下，策略偏向稳健覆盖。总成本仅32元，风险极低，具备高容错性，适合数据真空期的探索性投注。', '{\"dynamic_ensemble_optimizer\": {\"version\": \"2.0\", \"analysis\": {\"algorithms_used\": [\"frequency_analysis\", \"hot_cold_number\", \"omission_value\", \"bayesian_number_predictor\", \"markov_transition_model\", \"number_graph_analyzer\"], \"current_weights\": {\"omission_value\": 0.2608695652173913, \"hot_cold_number\": 0.04347826086956521, \"frequency_analysis\": 0.17391304347826084, \"number_graph_analyzer\": 0.3478260869565217, \"markov_transition_model\": 0.08695652173913042, \"bayesian_number_predictor\": 0.08695652173913042}, \"ensemble_method\": \"dynamic_weighted\"}, \"algorithm\": \"dynamic_ensemble_optimizer\", \"recommendations\": [{\"confidence\": 0.617391304347826, \"back_numbers\": [4, 10], \"front_numbers\": [3, 5, 6, 7, 8], \"dynamic_weights_applied\": true}]}}', NULL, 'qwen3-max (V14.5-Prometheus-Ω)', '2025-10-29 18:11:14');
INSERT INTO `algorithm_recommendation` VALUES (23, '2025123', '2025-10-29 18:14:12', 'qwen3-max (V14.5-Prometheus-Ω)', NULL, NULL, 0.8600, '整体风险中等偏低。策略不依赖趋势延续，适用于无历史数据的冷启动场景，通过复式组合实现稳健覆盖，避免极端偏差。', '{\"dynamic_ensemble_optimizer\": {\"version\": \"2.0\", \"analysis\": {\"algorithms_used\": [\"frequency_analysis\", \"hot_cold_number\", \"omission_value\", \"bayesian_number_predictor\", \"markov_transition_model\", \"number_graph_analyzer\"], \"current_weights\": {\"omission_value\": 0.2608695652173913, \"hot_cold_number\": 0.04347826086956521, \"frequency_analysis\": 0.17391304347826084, \"number_graph_analyzer\": 0.3478260869565217, \"markov_transition_model\": 0.08695652173913042, \"bayesian_number_predictor\": 0.08695652173913042}, \"ensemble_method\": \"dynamic_weighted\"}, \"algorithm\": \"dynamic_ensemble_optimizer\", \"recommendations\": [{\"confidence\": 0.617391304347826, \"back_numbers\": [4, 10], \"front_numbers\": [3, 5, 6, 7, 8], \"dynamic_weights_applied\": true}]}}', NULL, 'qwen3-max (V14.5-Prometheus-Ω)', '2025-10-29 18:14:11');
INSERT INTO `algorithm_recommendation` VALUES (24, '2025123', '2025-10-30 09:28:09', 'qwen3-max (V14.5-Prometheus-Ω)', NULL, NULL, 0.8200, '整体风险中等偏低。策略在数据真空期采取保守广谱覆盖，核心注稳健，卫星注成本低、探索性强，组合总成本100元，严格符合预算与风险偏好约束。', '{\"dynamic_ensemble_optimizer\": {\"version\": \"2.0\", \"analysis\": {\"algorithms_used\": [\"frequency_analysis\", \"hot_cold_number\", \"omission_value\", \"bayesian_number_predictor\", \"markov_transition_model\", \"number_graph_analyzer\"], \"current_weights\": {\"omission_value\": 0.2608695652173913, \"hot_cold_number\": 0.04347826086956521, \"frequency_analysis\": 0.17391304347826084, \"number_graph_analyzer\": 0.3478260869565217, \"markov_transition_model\": 0.08695652173913042, \"bayesian_number_predictor\": 0.08695652173913042}, \"ensemble_method\": \"dynamic_weighted\"}, \"algorithm\": \"dynamic_ensemble_optimizer\", \"recommendations\": [{\"confidence\": 0.617391304347826, \"back_numbers\": [4, 10], \"front_numbers\": [3, 5, 6, 7, 8], \"dynamic_weights_applied\": true}]}}', NULL, 'qwen3-max (V14.5-Prometheus-Ω)', '2025-10-30 09:28:09');
INSERT INTO `algorithm_recommendation` VALUES (25, '2025123', '2025-10-30 09:30:11', 'qwen3-max (V14.5-Prometheus-Ω)', NULL, NULL, 0.7500, '风险中性。虽无历史数据支撑，但通过多样化投注结构实现内部对冲，避免单一模式依赖。复式与胆拖构成稳健核心，单式提供尾部机会。', '{\"dynamic_ensemble_optimizer\": {\"version\": \"2.0\", \"analysis\": {\"algorithms_used\": [\"frequency_analysis\", \"hot_cold_number\", \"omission_value\", \"bayesian_number_predictor\", \"markov_transition_model\", \"number_graph_analyzer\"], \"current_weights\": {\"omission_value\": 0.2608695652173913, \"hot_cold_number\": 0.04347826086956521, \"frequency_analysis\": 0.17391304347826084, \"number_graph_analyzer\": 0.3478260869565217, \"markov_transition_model\": 0.08695652173913042, \"bayesian_number_predictor\": 0.08695652173913042}, \"ensemble_method\": \"dynamic_weighted\"}, \"algorithm\": \"dynamic_ensemble_optimizer\", \"recommendations\": [{\"confidence\": 0.617391304347826, \"back_numbers\": [4, 10], \"front_numbers\": [3, 5, 6, 7, 8], \"dynamic_weights_applied\": true}]}}', NULL, 'qwen3-max (V14.5-Prometheus-Ω)', '2025-10-30 09:30:10');
INSERT INTO `algorithm_recommendation` VALUES (26, '2025123', '2025-10-30 09:35:58', 'qwen3-max (V14.5-Prometheus-Ω)', NULL, NULL, 0.8500, '整体风险中性。核心复式提供稳定期望，卫星单式分散极端风险，总成本58元留有充足缓冲，符合中性风险偏好。', '{\"dynamic_ensemble_optimizer\": {\"version\": \"2.0\", \"analysis\": {\"algorithms_used\": [\"frequency_analysis\", \"hot_cold_number\", \"omission_value\", \"bayesian_number_predictor\", \"markov_transition_model\", \"number_graph_analyzer\"], \"current_weights\": {\"omission_value\": 0.2608695652173913, \"hot_cold_number\": 0.04347826086956521, \"frequency_analysis\": 0.17391304347826084, \"number_graph_analyzer\": 0.3478260869565217, \"markov_transition_model\": 0.08695652173913042, \"bayesian_number_predictor\": 0.08695652173913042}, \"ensemble_method\": \"dynamic_weighted\"}, \"algorithm\": \"dynamic_ensemble_optimizer\", \"recommendations\": [{\"confidence\": 0.617391304347826, \"back_numbers\": [4, 10], \"front_numbers\": [3, 5, 6, 7, 8], \"dynamic_weights_applied\": true}]}}', NULL, 'qwen3-max (V14.5-Prometheus-Ω)', '2025-10-30 09:35:58');
INSERT INTO `algorithm_recommendation` VALUES (27, '2025123', '2025-10-30 09:40:29', 'qwen3-max (V14.5-Prometheus-Ω)', NULL, NULL, 0.8400, '整体风险中等偏低。策略以覆盖代替预测，在无历史数据条件下实现风险分散，三组复式互为补充，避免孤注一掷。', '{\"dynamic_ensemble_optimizer\": {\"version\": \"2.0\", \"analysis\": {\"algorithms_used\": [\"frequency_analysis\", \"hot_cold_number\", \"omission_value\", \"bayesian_number_predictor\", \"markov_transition_model\", \"number_graph_analyzer\"], \"current_weights\": {\"omission_value\": 0.2608695652173913, \"hot_cold_number\": 0.04347826086956521, \"frequency_analysis\": 0.17391304347826084, \"number_graph_analyzer\": 0.3478260869565217, \"markov_transition_model\": 0.08695652173913042, \"bayesian_number_predictor\": 0.08695652173913042}, \"ensemble_method\": \"dynamic_weighted\"}, \"algorithm\": \"dynamic_ensemble_optimizer\", \"recommendations\": [{\"confidence\": 0.617391304347826, \"back_numbers\": [4, 10], \"front_numbers\": [3, 5, 6, 7, 8], \"dynamic_weights_applied\": true}]}}', NULL, 'qwen3-max (V14.5-Prometheus-Ω)', '2025-10-30 09:40:28');
INSERT INTO `algorithm_recommendation` VALUES (28, '2025123', '2025-10-30 09:41:37', 'qwen3-max (V14.5-Prometheus-Ω)', NULL, NULL, 0.8500, '整体风险中性偏低。核心注稳健，卫星注成本可控，策略具备良好容错性与反转捕捉能力。', '{\"dynamic_ensemble_optimizer\": {\"version\": \"2.0\", \"analysis\": {\"algorithms_used\": [\"frequency_analysis\", \"hot_cold_number\", \"omission_value\", \"bayesian_number_predictor\", \"markov_transition_model\", \"number_graph_analyzer\"], \"current_weights\": {\"omission_value\": 0.2608695652173913, \"hot_cold_number\": 0.04347826086956521, \"frequency_analysis\": 0.17391304347826084, \"number_graph_analyzer\": 0.3478260869565217, \"markov_transition_model\": 0.08695652173913042, \"bayesian_number_predictor\": 0.08695652173913042}, \"ensemble_method\": \"dynamic_weighted\"}, \"algorithm\": \"dynamic_ensemble_optimizer\", \"recommendations\": [{\"confidence\": 0.617391304347826, \"back_numbers\": [4, 10], \"front_numbers\": [3, 5, 6, 7, 8], \"dynamic_weights_applied\": true}]}}', NULL, 'qwen3-max (V14.5-Prometheus-Ω)', '2025-10-30 09:41:36');
INSERT INTO `algorithm_recommendation` VALUES (29, '2025123', '2025-10-30 09:59:01', 'qwen3-max (V14.5-Prometheus-Ω)', NULL, NULL, 0.8900, '整体风险中性。核心复式提供稳定基础命中，两组卫星单式以极低成本覆盖冷码与结构突变风险，实现高效对冲。', '{\"dynamic_ensemble_optimizer\": {\"version\": \"2.0\", \"analysis\": {\"algorithms_used\": [\"frequency_analysis\", \"hot_cold_number\", \"omission_value\", \"bayesian_number_predictor\", \"markov_transition_model\", \"number_graph_analyzer\"], \"current_weights\": {\"omission_value\": 0.2608695652173913, \"hot_cold_number\": 0.04347826086956521, \"frequency_analysis\": 0.17391304347826084, \"number_graph_analyzer\": 0.3478260869565217, \"markov_transition_model\": 0.08695652173913042, \"bayesian_number_predictor\": 0.08695652173913042}, \"ensemble_method\": \"dynamic_weighted\"}, \"algorithm\": \"dynamic_ensemble_optimizer\", \"recommendations\": [{\"confidence\": 0.617391304347826, \"back_numbers\": [4, 10], \"front_numbers\": [3, 5, 6, 7, 8], \"dynamic_weights_applied\": true}]}}', NULL, 'qwen3-max (V14.5-Prometheus-Ω)', '2025-10-30 09:59:00');
INSERT INTO `algorithm_recommendation` VALUES (30, '2025123', '2025-10-30 10:54:57', 'qwen3-max (V14.5-Prometheus-Ω)', NULL, NULL, 0.8800, '整体风险中等。核心注较为稳健，卫星注具备博取高回报的潜力，策略已做风险对冲。', '{\"dynamic_ensemble_optimizer\": {\"version\": \"2.0\", \"analysis\": {\"algorithms_used\": [\"frequency_analysis\", \"hot_cold_number\", \"omission_value\", \"bayesian_number_predictor\", \"markov_transition_model\", \"number_graph_analyzer\"], \"current_weights\": {\"omission_value\": 0.2608695652173913, \"hot_cold_number\": 0.04347826086956521, \"frequency_analysis\": 0.17391304347826084, \"number_graph_analyzer\": 0.3478260869565217, \"markov_transition_model\": 0.08695652173913042, \"bayesian_number_predictor\": 0.08695652173913042}, \"ensemble_method\": \"dynamic_weighted\"}, \"algorithm\": \"dynamic_ensemble_optimizer\", \"recommendations\": [{\"confidence\": 0.617391304347826, \"back_numbers\": [4, 10], \"front_numbers\": [3, 5, 6, 7, 8], \"dynamic_weights_applied\": true}]}}', NULL, 'qwen3-max (V14.5-Prometheus-Ω)', '2025-10-30 10:54:57');
INSERT INTO `algorithm_recommendation` VALUES (31, '2025124', '2025-10-30 11:03:22', 'qwen3-max (V14.5-Prometheus-Ω)', NULL, NULL, 0.8800, '整体风险中等。核心注较为稳健，卫星注具备博取高回报的潜力，策略已做风险对冲。', '{\"dynamic_ensemble_optimizer\": {\"version\": \"2.0\", \"analysis\": {\"algorithms_used\": [\"frequency_analysis\", \"hot_cold_number\", \"omission_value\", \"bayesian_number_predictor\", \"markov_transition_model\", \"number_graph_analyzer\"], \"current_weights\": {\"omission_value\": 0.25490196078431376, \"hot_cold_number\": 0.019607843137254905, \"frequency_analysis\": 0.13725490196078433, \"number_graph_analyzer\": 0.35294117647058826, \"markov_transition_model\": 0.07843137254901962, \"bayesian_number_predictor\": 0.15686274509803924}, \"ensemble_method\": \"dynamic_weighted\"}, \"algorithm\": \"dynamic_ensemble_optimizer\", \"recommendations\": [{\"confidence\": 0.623529411764706, \"back_numbers\": [2, 11], \"front_numbers\": [5, 6, 7, 9, 20], \"dynamic_weights_applied\": true}]}}', NULL, 'qwen3-max (V14.5-Prometheus-Ω)', '2025-10-30 11:03:21');
INSERT INTO `algorithm_recommendation` VALUES (32, '2025124', '2025-10-30 11:46:06', 'qwen3-max (V14.5-Prometheus-Ω)', NULL, NULL, 0.8700, '整体风险中性。核心复式提供稳定基础命中，两组卫星单式分别对冲冷热极端情形，策略具备良好适应性。', '{\"dynamic_ensemble_optimizer\": {\"version\": \"2.0\", \"analysis\": {\"algorithms_used\": [\"frequency_analysis\", \"hot_cold_number\", \"omission_value\", \"bayesian_number_predictor\", \"markov_transition_model\", \"number_graph_analyzer\"], \"current_weights\": {\"omission_value\": 0.2608695652173913, \"hot_cold_number\": 0.043478260869565216, \"frequency_analysis\": 0.17391304347826086, \"number_graph_analyzer\": 0.3913043478260869, \"markov_transition_model\": 0.08695652173913043, \"bayesian_number_predictor\": 0.043478260869565216}, \"ensemble_method\": \"dynamic_weighted\"}, \"algorithm\": \"dynamic_ensemble_optimizer\", \"recommendations\": [{\"confidence\": 0.6043478260869565, \"back_numbers\": [2, 11], \"front_numbers\": [3, 8, 26, 32, 33], \"dynamic_weights_applied\": true}]}}', NULL, 'qwen3-max (V14.5-Prometheus-Ω)', '2025-10-30 11:46:06');
INSERT INTO `algorithm_recommendation` VALUES (33, '2025124', '2025-10-30 11:55:23', 'qwen3-max (V14.5-Pr)', NULL, NULL, 0.8900, '策略已实现冷热对冲与多路径覆盖，整体风险中性。主力注稳健，卫星注具备弹性，符合用户风险偏好。', '{\"dynamic_ensemble_optimizer\": {\"version\": \"2.0\", \"analysis\": {\"algorithms_used\": [\"frequency_analysis\", \"hot_cold_number\", \"omission_value\", \"bayesian_number_predictor\", \"markov_transition_model\", \"number_graph_analyzer\"], \"current_weights\": {\"omission_value\": 0.18421052631578944, \"hot_cold_number\": 0.0, \"frequency_analysis\": 0.13157894736842105, \"number_graph_analyzer\": 0.47368421052631576, \"markov_transition_model\": 0.10526315789473684, \"bayesian_number_predictor\": 0.10526315789473684}, \"ensemble_method\": \"dynamic_weighted\"}, \"algorithm\": \"dynamic_ensemble_optimizer\", \"recommendations\": [{\"confidence\": 0.5921052631578948, \"back_numbers\": [1, 9], \"front_numbers\": [2, 5, 7, 8, 9], \"dynamic_weights_applied\": true}]}}', NULL, 'qwen3-max (V14.5-Pr)', '2025-10-30 11:55:23');

-- ----------------------------
-- Table structure for algorithm_weights
-- ----------------------------
DROP TABLE IF EXISTS `algorithm_weights`;
CREATE TABLE `algorithm_weights`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `algorithm` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `weight` float NOT NULL COMMENT '0-1 归一化权重',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `algorithm`(`algorithm` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of algorithm_weights
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
) ENGINE = InnoDB AUTO_INCREMENT = 172 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '历史开奖数据表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of lottery_history
-- ----------------------------
INSERT INTO `lottery_history` VALUES (1, '2025067', '2025-06-07', '2025-10-22 10:57:52', 6, 10, 12, 21, 22, 1, 6, 78, 16, 0, '1:4', '2:3', NULL, '[[21, 22]]', 1, NULL, 'official', 100, '2025-10-22 10:57:51', '2025-10-22 10:57:51');
INSERT INTO `lottery_history` VALUES (7, '2025068', '2025-06-09', '2025-10-23 11:25:36', 3, 7, 14, 18, 29, 2, 8, 81, 26, 18, '3:2', '1:4', '3:2', NULL, 0, '{\"2\": 1, \"3\": 1, \"4\": 1, \"7\": 1, \"8\": 2, \"9\": 1}', 'official', 100, '2025-10-23 11:25:35', '2025-10-23 11:25:35');
INSERT INTO `lottery_history` VALUES (14, '2025069', '2025-06-10', '2025-10-29 16:50:16', 4, 6, 7, 33, 34, 9, 10, 103, 30, 22, '2:3', '2:3', '1:4', '[[6, 7], [33, 34]]', 2, '{\"0\": 1, \"3\": 1, \"4\": 2, \"6\": 1, \"7\": 1, \"9\": 1}', 'official', 100, '2025-10-29 16:50:16', '2025-10-29 16:50:16');
INSERT INTO `lottery_history` VALUES (21, '2025073', '2025-06-30', '2025-10-29 17:20:06', 1, 4, 17, 33, 34, 3, 9, 101, 33, 25, '3:2', '2:3', '1:4', '[[33, 34]]', 1, '{\"1\": 1, \"3\": 2, \"4\": 2, \"7\": 1, \"9\": 1}', 'official', 100, '2025-10-29 17:20:06', '2025-10-29 17:20:06');
INSERT INTO `lottery_history` VALUES (22, '2025074', '2025-07-02', '2025-10-29 17:20:07', 2, 11, 15, 18, 21, 5, 10, 82, 19, 11, '3:2', '1:4', '2:3', NULL, 0, '{\"0\": 1, \"1\": 2, \"2\": 1, \"5\": 2, \"8\": 1}', 'official', 100, '2025-10-29 17:20:06', '2025-10-29 17:20:06');
INSERT INTO `lottery_history` VALUES (23, '2025075', '2025-07-05', '2025-10-29 17:20:07', 8, 12, 16, 19, 35, 6, 9, 105, 27, 19, '2:3', '2:3', '1:4', NULL, 0, '{\"2\": 1, \"5\": 1, \"6\": 2, \"8\": 1, \"9\": 2}', 'official', 100, '2025-10-29 17:20:06', '2025-10-29 17:20:06');
INSERT INTO `lottery_history` VALUES (24, '2025076', '2025-07-07', '2025-10-29 17:20:07', 11, 18, 22, 25, 29, 4, 12, 121, 18, 10, '3:2', '3:2', '2:3', NULL, 0, '{\"1\": 1, \"2\": 2, \"4\": 1, \"5\": 1, \"8\": 1, \"9\": 1}', 'official', 100, '2025-10-29 17:20:06', '2025-10-29 17:20:06');
INSERT INTO `lottery_history` VALUES (25, '2025077', '2025-07-09', '2025-10-29 17:20:07', 12, 14, 16, 19, 28, 1, 4, 94, 16, 8, '1:4', '2:3', '1:4', NULL, 0, '{\"1\": 1, \"2\": 1, \"4\": 2, \"6\": 1, \"8\": 1, \"9\": 1}', 'official', 100, '2025-10-29 17:20:06', '2025-10-29 17:20:06');
INSERT INTO `lottery_history` VALUES (26, '2025078', '2025-07-12', '2025-10-29 17:20:07', 7, 10, 15, 21, 24, 5, 6, 88, 17, 9, '3:2', '2:3', '1:4', NULL, 0, '{\"0\": 1, \"1\": 1, \"4\": 1, \"5\": 2, \"6\": 1, \"7\": 1}', 'official', 100, '2025-10-29 17:20:06', '2025-10-29 17:20:06');
INSERT INTO `lottery_history` VALUES (27, '2025079', '2025-07-14', '2025-10-29 17:20:07', 2, 14, 32, 34, 35, 5, 11, 133, 33, 25, '1:4', '3:2', '1:4', '[[34, 35]]', 1, '{\"1\": 1, \"2\": 2, \"4\": 2, \"5\": 2}', 'official', 100, '2025-10-29 17:20:06', '2025-10-29 17:20:06');
INSERT INTO `lottery_history` VALUES (28, '2025080', '2025-07-16', '2025-10-29 17:20:07', 9, 10, 18, 22, 24, 3, 12, 98, 15, 7, '1:4', '2:3', '0:5', '[[9, 10]]', 1, '{\"0\": 1, \"2\": 2, \"3\": 1, \"4\": 1, \"8\": 1, \"9\": 1}', 'official', 100, '2025-10-29 17:20:06', '2025-10-29 17:20:06');
INSERT INTO `lottery_history` VALUES (29, '2025081', '2025-07-19', '2025-10-29 17:20:07', 1, 4, 6, 15, 18, 2, 3, 49, 17, 9, '2:3', '0:5', '0:5', NULL, 0, '{\"1\": 1, \"2\": 1, \"3\": 1, \"4\": 1, \"5\": 1, \"6\": 1, \"8\": 1}', 'official', 100, '2025-10-29 17:20:06', '2025-10-29 17:20:06');
INSERT INTO `lottery_history` VALUES (30, '2025082', '2025-07-21', '2025-10-29 17:20:07', 2, 3, 4, 12, 26, 1, 8, 56, 24, 16, '1:4', '1:4', '2:3', '[[2, 3, 4], [3, 4]]', 2, '{\"1\": 1, \"2\": 2, \"3\": 1, \"4\": 1, \"6\": 1, \"8\": 1}', 'official', 100, '2025-10-29 17:20:06', '2025-10-29 17:20:06');
INSERT INTO `lottery_history` VALUES (31, '2025083', '2025-07-23', '2025-10-29 17:20:07', 12, 17, 18, 20, 34, 2, 5, 108, 22, 14, '1:4', '2:3', '1:4', '[[17, 18]]', 1, '{\"0\": 1, \"2\": 2, \"4\": 1, \"5\": 1, \"7\": 1, \"8\": 1}', 'official', 100, '2025-10-29 17:20:06', '2025-10-29 17:20:06');
INSERT INTO `lottery_history` VALUES (32, '2025084', '2025-07-26', '2025-10-29 17:20:07', 9, 11, 13, 18, 29, 4, 11, 95, 20, 12, '4:1', '1:4', '3:2', NULL, 0, '{\"1\": 2, \"3\": 1, \"4\": 1, \"8\": 1, \"9\": 2}', 'official', 100, '2025-10-29 17:20:06', '2025-10-29 17:20:06');
INSERT INTO `lottery_history` VALUES (33, '2025085', '2025-07-28', '2025-10-29 17:20:07', 2, 5, 9, 14, 33, 4, 9, 76, 31, 23, '3:2', '1:4', '2:3', NULL, 0, '{\"2\": 1, \"3\": 1, \"4\": 2, \"5\": 1, \"9\": 2}', 'official', 100, '2025-10-29 17:20:06', '2025-10-29 17:20:06');
INSERT INTO `lottery_history` VALUES (34, '2025086', '2025-07-30', '2025-10-29 17:20:07', 2, 6, 23, 24, 33, 1, 10, 99, 31, 23, '2:3', '3:2', '2:3', '[[23, 24]]', 1, '{\"0\": 1, \"1\": 1, \"2\": 1, \"3\": 2, \"4\": 1, \"6\": 1}', 'official', 100, '2025-10-29 17:20:06', '2025-10-29 17:20:06');
INSERT INTO `lottery_history` VALUES (35, '2025087', '2025-08-02', '2025-10-29 17:20:07', 5, 13, 14, 16, 20, 3, 8, 79, 15, 7, '2:3', '1:4', '2:3', '[[13, 14]]', 1, '{\"0\": 1, \"3\": 2, \"4\": 1, \"5\": 1, \"6\": 1, \"8\": 1}', 'official', 100, '2025-10-29 17:20:06', '2025-10-29 17:20:06');
INSERT INTO `lottery_history` VALUES (36, '2025088', '2025-08-04', '2025-10-29 17:20:07', 8, 9, 10, 11, 35, 5, 11, 89, 27, 19, '3:2', '1:4', '1:4', '[[8, 9, 10, 11], [9, 10, 11], [10, 11]]', 3, '{\"0\": 1, \"1\": 2, \"5\": 2, \"8\": 1, \"9\": 1}', 'official', 100, '2025-10-29 17:20:06', '2025-10-29 17:20:06');
INSERT INTO `lottery_history` VALUES (37, '2025089', '2025-08-06', '2025-10-29 17:20:07', 2, 11, 12, 32, 34, 3, 10, 104, 32, 24, '1:4', '2:3', '2:3', '[[11, 12]]', 1, '{\"0\": 1, \"1\": 1, \"2\": 3, \"3\": 1, \"4\": 1}', 'official', 100, '2025-10-29 17:20:06', '2025-10-29 17:20:06');
INSERT INTO `lottery_history` VALUES (38, '2025090', '2025-08-09', '2025-10-29 17:20:07', 6, 14, 19, 22, 27, 1, 4, 93, 21, 13, '2:3', '3:2', '1:4', NULL, 0, '{\"1\": 1, \"2\": 1, \"4\": 2, \"6\": 1, \"7\": 1, \"9\": 1}', 'official', 100, '2025-10-29 17:20:06', '2025-10-29 17:20:06');
INSERT INTO `lottery_history` VALUES (39, '2025091', '2025-08-11', '2025-10-29 17:20:07', 1, 19, 22, 25, 27, 3, 10, 107, 26, 18, '4:1', '4:1', '1:4', NULL, 0, '{\"0\": 1, \"1\": 1, \"2\": 1, \"3\": 1, \"5\": 1, \"7\": 1, \"9\": 1}', 'official', 100, '2025-10-29 17:20:06', '2025-10-29 17:20:06');
INSERT INTO `lottery_history` VALUES (40, '2025092', '2025-08-13', '2025-10-29 17:20:07', 4, 10, 17, 25, 32, 5, 7, 100, 28, 20, '2:3', '2:3', '1:4', NULL, 0, '{\"0\": 1, \"2\": 1, \"4\": 1, \"5\": 2, \"7\": 2}', 'official', 100, '2025-10-29 17:20:06', '2025-10-29 17:20:06');
INSERT INTO `lottery_history` VALUES (41, '2025093', '2025-08-16', '2025-10-29 17:20:07', 1, 7, 9, 16, 30, 2, 5, 70, 29, 21, '3:2', '1:4', '1:4', NULL, 0, '{\"0\": 1, \"1\": 1, \"2\": 1, \"5\": 1, \"6\": 1, \"7\": 1, \"9\": 1}', 'official', 100, '2025-10-29 17:20:06', '2025-10-29 17:20:06');
INSERT INTO `lottery_history` VALUES (42, '2025094', '2025-08-18', '2025-10-29 17:20:07', 4, 9, 17, 30, 33, 5, 9, 107, 29, 21, '3:2', '2:3', '1:4', NULL, 0, '{\"0\": 1, \"3\": 1, \"4\": 1, \"5\": 1, \"7\": 1, \"9\": 2}', 'official', 100, '2025-10-29 17:20:06', '2025-10-29 17:20:06');
INSERT INTO `lottery_history` VALUES (43, '2025095', '2025-08-20', '2025-10-29 17:20:07', 7, 13, 14, 19, 27, 6, 10, 96, 20, 12, '4:1', '2:3', '3:2', '[[13, 14]]', 1, '{\"0\": 1, \"3\": 1, \"4\": 1, \"6\": 1, \"7\": 2, \"9\": 1}', 'official', 100, '2025-10-29 17:20:06', '2025-10-29 17:20:06');
INSERT INTO `lottery_history` VALUES (44, '2025096', '2025-08-23', '2025-10-29 17:20:07', 2, 11, 17, 22, 24, 7, 9, 92, 22, 14, '2:3', '2:3', '3:2', NULL, 0, '{\"1\": 1, \"2\": 2, \"4\": 1, \"7\": 2, \"9\": 1}', 'official', 100, '2025-10-29 17:20:07', '2025-10-29 17:20:07');
INSERT INTO `lottery_history` VALUES (45, '2025097', '2025-08-25', '2025-10-29 17:20:07', 5, 24, 25, 32, 34, 1, 9, 130, 29, 21, '2:3', '4:1', '1:4', '[[24, 25]]', 1, '{\"1\": 1, \"2\": 1, \"4\": 2, \"5\": 2, \"9\": 1}', 'official', 100, '2025-10-29 17:20:07', '2025-10-29 17:20:07');
INSERT INTO `lottery_history` VALUES (46, '2025098', '2025-08-27', '2025-10-29 17:20:07', 1, 7, 9, 10, 23, 10, 12, 72, 22, 14, '4:1', '1:4', '2:3', '[[9, 10]]', 1, '{\"0\": 2, \"1\": 1, \"2\": 1, \"3\": 1, \"7\": 1, \"9\": 1}', 'official', 100, '2025-10-29 17:20:07', '2025-10-29 17:20:07');
INSERT INTO `lottery_history` VALUES (47, '2025099', '2025-08-30', '2025-10-29 17:20:07', 6, 12, 20, 26, 31, 2, 4, 101, 25, 17, '1:4', '3:2', '1:4', NULL, 0, '{\"0\": 1, \"1\": 1, \"2\": 2, \"4\": 1, \"6\": 2}', 'official', 100, '2025-10-29 17:20:07', '2025-10-29 17:20:07');
INSERT INTO `lottery_history` VALUES (48, '2025100', '2025-09-01', '2025-10-29 17:20:07', 26, 28, 32, 34, 35, 2, 7, 164, 9, 1, '1:4', '5:0', '0:5', '[[34, 35]]', 1, '{\"2\": 2, \"4\": 1, \"5\": 1, \"6\": 1, \"7\": 1, \"8\": 1}', 'official', 100, '2025-10-29 17:20:07', '2025-10-29 17:20:07');
INSERT INTO `lottery_history` VALUES (49, '2025101', '2025-09-03', '2025-10-29 17:20:07', 5, 7, 19, 26, 32, 8, 9, 106, 27, 19, '3:2', '3:2', '3:2', NULL, 0, '{\"2\": 1, \"5\": 1, \"6\": 1, \"7\": 1, \"8\": 1, \"9\": 2}', 'official', 100, '2025-10-29 17:20:07', '2025-10-29 17:20:07');
INSERT INTO `lottery_history` VALUES (50, '2025102', '2025-09-06', '2025-10-29 17:20:07', 9, 10, 13, 26, 28, 2, 4, 92, 19, 11, '2:3', '2:3', '1:4', '[[9, 10]]', 1, '{\"0\": 1, \"2\": 1, \"3\": 1, \"4\": 1, \"6\": 1, \"8\": 1, \"9\": 1}', 'official', 100, '2025-10-29 17:20:07', '2025-10-29 17:20:07');
INSERT INTO `lottery_history` VALUES (51, '2025103', '2025-09-08', '2025-10-29 17:20:07', 5, 8, 19, 32, 34, 4, 5, 107, 29, 21, '2:3', '3:2', '2:3', NULL, 0, '{\"2\": 1, \"4\": 2, \"5\": 2, \"8\": 1, \"9\": 1}', 'official', 100, '2025-10-29 17:20:07', '2025-10-29 17:20:07');
INSERT INTO `lottery_history` VALUES (52, '2025104', '2025-09-10', '2025-10-29 17:20:07', 2, 6, 9, 22, 34, 2, 8, 83, 32, 24, '1:4', '2:3', '1:4', NULL, 0, '{\"2\": 3, \"4\": 1, \"6\": 1, \"8\": 1, \"9\": 1}', 'official', 100, '2025-10-29 17:20:07', '2025-10-29 17:20:07');
INSERT INTO `lottery_history` VALUES (53, '2025105', '2025-09-13', '2025-10-29 17:20:07', 15, 16, 25, 28, 34, 10, 12, 140, 19, 11, '2:3', '3:2', '0:5', '[[15, 16]]', 1, '{\"0\": 1, \"2\": 1, \"4\": 1, \"5\": 2, \"6\": 1, \"8\": 1}', 'official', 100, '2025-10-29 17:20:07', '2025-10-29 17:20:07');
INSERT INTO `lottery_history` VALUES (54, '2025106', '2025-09-15', '2025-10-29 17:20:07', 5, 6, 11, 26, 29, 5, 10, 92, 24, 16, '3:2', '2:3', '3:2', '[[5, 6]]', 1, '{\"0\": 1, \"1\": 1, \"5\": 2, \"6\": 2, \"9\": 1}', 'official', 100, '2025-10-29 17:20:07', '2025-10-29 17:20:07');
INSERT INTO `lottery_history` VALUES (55, '2025107', '2025-09-17', '2025-10-29 17:20:07', 5, 7, 8, 15, 33, 6, 10, 84, 28, 20, '4:1', '1:4', '2:3', '[[7, 8]]', 1, '{\"0\": 1, \"3\": 1, \"5\": 2, \"6\": 1, \"7\": 1, \"8\": 1}', 'official', 100, '2025-10-29 17:20:07', '2025-10-29 17:20:07');
INSERT INTO `lottery_history` VALUES (56, '2025108', '2025-09-20', '2025-10-29 17:20:07', 14, 18, 21, 24, 29, 3, 6, 115, 15, 7, '2:3', '3:2', '1:4', NULL, 0, '{\"1\": 1, \"3\": 1, \"4\": 2, \"6\": 1, \"8\": 1, \"9\": 1}', 'official', 100, '2025-10-29 17:20:07', '2025-10-29 17:20:07');
INSERT INTO `lottery_history` VALUES (57, '2025109', '2025-09-22', '2025-10-29 17:20:07', 4, 8, 10, 13, 26, 9, 10, 80, 22, 14, '1:4', '1:4', '1:4', NULL, 0, '{\"0\": 2, \"3\": 1, \"4\": 1, \"6\": 1, \"8\": 1, \"9\": 1}', 'official', 100, '2025-10-29 17:20:07', '2025-10-29 17:20:07');
INSERT INTO `lottery_history` VALUES (58, '2025110', '2025-09-24', '2025-10-29 17:20:07', 1, 15, 22, 30, 31, 2, 8, 109, 30, 22, '3:2', '3:2', '1:4', '[[30, 31]]', 1, '{\"0\": 1, \"1\": 2, \"2\": 2, \"5\": 1, \"8\": 1}', 'official', 100, '2025-10-29 17:20:07', '2025-10-29 17:20:07');
INSERT INTO `lottery_history` VALUES (59, '2025111', '2025-09-27', '2025-10-29 17:20:07', 2, 9, 14, 21, 26, 2, 12, 86, 24, 16, '2:3', '2:3', '1:4', NULL, 0, '{\"1\": 1, \"2\": 3, \"4\": 1, \"6\": 1, \"9\": 1}', 'official', 100, '2025-10-29 17:20:07', '2025-10-29 17:20:07');
INSERT INTO `lottery_history` VALUES (60, '2025112', '2025-09-29', '2025-10-29 17:20:07', 3, 4, 21, 23, 24, 9, 12, 96, 21, 13, '3:2', '3:2', '2:3', '[[3, 4], [23, 24]]', 2, '{\"1\": 1, \"2\": 1, \"3\": 2, \"4\": 2, \"9\": 1}', 'official', 100, '2025-10-29 17:20:07', '2025-10-29 17:20:07');
INSERT INTO `lottery_history` VALUES (61, '2025113', '2025-10-06', '2025-10-29 17:20:07', 1, 14, 18, 28, 35, 2, 3, 101, 34, 26, '2:3', '2:3', '0:5', NULL, 0, '{\"1\": 1, \"2\": 1, \"3\": 1, \"4\": 1, \"5\": 1, \"8\": 2}', 'official', 100, '2025-10-29 17:20:07', '2025-10-29 17:20:07');
INSERT INTO `lottery_history` VALUES (62, '2025114', '2025-10-08', '2025-10-29 17:20:07', 3, 8, 9, 12, 16, 1, 5, 54, 13, 5, '2:3', '0:5', '1:4', '[[8, 9]]', 1, '{\"1\": 1, \"2\": 1, \"3\": 1, \"5\": 1, \"6\": 1, \"8\": 1, \"9\": 1}', 'official', 100, '2025-10-29 17:20:07', '2025-10-29 17:20:07');
INSERT INTO `lottery_history` VALUES (63, '2025115', '2025-10-11', '2025-10-29 17:20:07', 3, 12, 14, 21, 35, 1, 5, 91, 32, 24, '3:2', '2:3', '1:4', NULL, 0, '{\"1\": 2, \"2\": 1, \"3\": 1, \"4\": 1, \"5\": 2}', 'official', 100, '2025-10-29 17:20:07', '2025-10-29 17:20:07');
INSERT INTO `lottery_history` VALUES (64, '2025116', '2025-10-13', '2025-10-29 17:20:07', 2, 6, 16, 22, 29, 8, 12, 95, 27, 19, '1:4', '2:3', '2:3', NULL, 0, '{\"2\": 3, \"6\": 2, \"8\": 1, \"9\": 1}', 'official', 100, '2025-10-29 17:20:07', '2025-10-29 17:20:07');
INSERT INTO `lottery_history` VALUES (65, '2025117', '2025-10-15', '2025-10-29 17:20:08', 5, 10, 18, 21, 29, 5, 7, 95, 24, 16, '3:2', '2:3', '2:3', NULL, 0, '{\"0\": 1, \"1\": 1, \"5\": 2, \"7\": 1, \"8\": 1, \"9\": 1}', 'official', 100, '2025-10-29 17:20:07', '2025-10-29 17:20:07');
INSERT INTO `lottery_history` VALUES (66, '2025118', '2025-10-18', '2025-10-29 17:20:08', 2, 8, 9, 12, 21, 4, 5, 61, 19, 11, '2:3', '1:4', '1:4', '[[8, 9]]', 1, '{\"1\": 1, \"2\": 2, \"4\": 1, \"5\": 1, \"8\": 1, \"9\": 1}', 'official', 100, '2025-10-29 17:20:07', '2025-10-29 17:20:07');
INSERT INTO `lottery_history` VALUES (67, '2025119', '2025-10-20', '2025-10-29 17:20:08', 8, 15, 27, 29, 31, 1, 7, 118, 23, 15, '4:1', '3:2', '2:3', NULL, 0, '{\"1\": 2, \"5\": 1, \"7\": 2, \"8\": 1, \"9\": 1}', 'official', 100, '2025-10-29 17:20:07', '2025-10-29 17:20:07');
INSERT INTO `lottery_history` VALUES (68, '2025120', '2025-10-22', '2025-10-29 17:20:08', 11, 13, 22, 26, 35, 2, 8, 117, 24, 16, '3:2', '3:2', '2:3', NULL, 0, '{\"1\": 1, \"2\": 2, \"3\": 1, \"5\": 1, \"6\": 1, \"8\": 1}', 'official', 100, '2025-10-29 17:20:07', '2025-10-29 17:20:07');
INSERT INTO `lottery_history` VALUES (69, '2025121', '2025-10-25', '2025-10-29 17:20:08', 2, 3, 8, 13, 21, 7, 12, 66, 19, 11, '3:2', '1:4', '3:2', '[[2, 3]]', 1, '{\"1\": 1, \"2\": 2, \"3\": 2, \"7\": 1, \"8\": 1}', 'official', 100, '2025-10-29 17:20:07', '2025-10-29 17:20:07');
INSERT INTO `lottery_history` VALUES (70, '2025122', '2025-10-27', '2025-10-29 17:20:08', 2, 3, 6, 16, 17, 4, 5, 53, 15, 7, '2:3', '0:5', '3:2', '[[2, 3], [16, 17]]', 2, '{\"2\": 1, \"3\": 1, \"4\": 1, \"5\": 1, \"6\": 2, \"7\": 1}', 'official', 100, '2025-10-29 17:20:07', '2025-10-29 17:20:07');
INSERT INTO `lottery_history` VALUES (171, '2025123', '2025-10-29', '2025-10-30 11:02:20', 8, 13, 24, 25, 31, 4, 10, 115, 23, 15, '3:2', '3:2', '2:3', '[[24, 25]]', 1, '{\"0\": 1, \"1\": 1, \"3\": 1, \"4\": 2, \"5\": 1, \"8\": 1}', 'official', 100, '2025-10-30 11:02:20', '2025-10-30 11:02:20');

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
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '预测模型训练记录表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of model_training_logs
-- ----------------------------
INSERT INTO `model_training_logs` VALUES (1, 'Prometheus-Pipeline-V5', '2025-10-28', '2025067', '2025068', 2, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'running', NULL, '2025-10-28 17:06:38', NULL, NULL);

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
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '号码统计分析表' ROW_FORMAT = DYNAMIC;

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
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '个人自由投注记录表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of personal_betting
-- ----------------------------
INSERT INTO `personal_betting` VALUES (1, 'wanhong', '2025068', '2025-10-27 11:03:20', 'single', '[4, 6, 7, 9, 11]', 5, '[3, 6]', 2, 2.00, 1, 0, NULL, 0.00, 'manual', 50, '', '2025-10-27 11:03:19', '2025-10-27 11:03:19');
INSERT INTO `personal_betting` VALUES (2, 'wanhong', '2025068', '2025-10-27 11:03:34', 'compound', '[4, 6, 7, 9, 10, 11, 32]', 7, '[3, 6, 8]', 3, 126.00, 1, 0, NULL, 0.00, 'manual', 50, '', '2025-10-27 11:03:33', '2025-10-27 11:03:33');

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
) ENGINE = InnoDB AUTO_INCREMENT = 102 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '算法推荐的具体组合详情表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of recommendation_details
-- ----------------------------
INSERT INTO `recommendation_details` VALUES (4, 6, '热号主攻', '遵循最强模式 + 热号集中', '06,10,12,21,22', '01,06', 0.00003, '2025-10-23 11:24:37');
INSERT INTO `recommendation_details` VALUES (5, 6, '冷号回补', '模式+冷号突破', '03,07,18,28,33', '02,09', 0.00003, '2025-10-23 11:24:37');
INSERT INTO `recommendation_details` VALUES (6, 6, '复式 (7+3)', '综合高潜力池全覆盖', '06,10,12,21,22,07,18,28', '01,06,09', 0.00041, '2025-10-23 11:24:37');
INSERT INTO `recommendation_details` VALUES (7, 6, '均衡混合', '热冷搭配 + 和值控制在80±10', '06,10,18,21,28', '03,07', 0.00003, '2025-10-23 11:24:37');
INSERT INTO `recommendation_details` VALUES (12, 9, '热号主攻', '遵循最强模式 + 热号集中', '07,14,18,22,29', '02,08', 0.83000, '2025-10-24 17:52:06');
INSERT INTO `recommendation_details` VALUES (13, 9, '冷号回补', '模式+冷号突破（侧重前期遗漏回补）', '03,06,10,12,21', '01,06', 0.81000, '2025-10-24 17:52:06');
INSERT INTO `recommendation_details` VALUES (14, 9, '复式 (8+3)', '综合高潜力池全覆盖，覆盖全部10个高潜力号中的8个，兼顾奇偶与大小均衡', '03,07,10,14,18,21,22,29', '01,02,08', 1.96000, '2025-10-24 17:52:06');
INSERT INTO `recommendation_details` VALUES (15, 9, '均衡混合', '融合热冷，奇偶3:2，大小3:2，和值≈85', '06,07,14,21,29', '02,06', 0.85000, '2025-10-24 17:52:06');
INSERT INTO `recommendation_details` VALUES (16, 11, '核心复式(6+2)', '主力覆盖热核与关键冷号，确保前区至少3中，后区高概率命中。', '7,14,18,23,31,29', '2,8', 0.89000, '2025-10-28 09:49:05');
INSERT INTO `recommendation_details` VALUES (17, 11, '卫星单式A', '试探性覆盖次热号10、21，后区引入6作为潜在替代。', '7,10,18,21,31', '2,6', 0.72000, '2025-10-28 09:49:05');
INSERT INTO `recommendation_details` VALUES (18, 11, '卫星单式B', '捕捉前区冷号3的潜在回归，后区测试11的上升趋势。', '3,14,23,29,31', '8,11', 0.68000, '2025-10-28 09:49:05');
INSERT INTO `recommendation_details` VALUES (19, 11, '卫星单式C', '强化热核组合，后区引入1作为低概率对冲。', '7,18,22,23,31', '1,8', 0.75000, '2025-10-28 09:49:05');
INSERT INTO `recommendation_details` VALUES (20, 12, '核心复式(7+2)', '主力攻击，覆盖高概率热区，旨在确保基础命中。', '3,8,14,18,23,29,31', '3,10', 0.91000, '2025-10-28 15:45:56');
INSERT INTO `recommendation_details` VALUES (21, 12, '卫星单式A (冷码突击)', '高风险对冲，捕捉高遗漏冷码的反转机会。', '7,10,15,21,33', '1,6', 0.65000, '2025-10-28 15:45:56');
INSERT INTO `recommendation_details` VALUES (22, 12, '卫星单式B (后区强热)', '聚焦后区双热号组合，提升二等奖捕获概率。', '6,12,18,22,29', '8,10', 0.72000, '2025-10-28 15:45:56');
INSERT INTO `recommendation_details` VALUES (23, 12, '卫星单式C (奇偶均衡)', '平衡奇偶结构，应对近期奇偶波动加剧的走势。', '3,10,14,21,31', '3,8', 0.69000, '2025-10-28 15:45:56');
INSERT INTO `recommendation_details` VALUES (24, 14, '核心复式(7+2)', '主力覆盖近期高热区域，确保基础命中率，利用复式结构捕获号码微调波动。', '3,7,10,14,18,22,29', '2,8', 0.89000, '2025-10-28 18:11:09');
INSERT INTO `recommendation_details` VALUES (25, 14, '卫星单式A (邻号扩展)', '基于上期21,22及12的邻号逻辑，捕捉可能的横向扩散路径。', '6,11,13,19,21', '1,6', 0.72000, '2025-10-28 18:11:09');
INSERT INTO `recommendation_details` VALUES (26, 14, '卫星单式B (冷码对冲)', '引入前区高遗漏号31、34及后区冷号11，防范极端反转风险。', '5,16,25,31,34', '7,11', 0.61000, '2025-10-28 18:11:09');
INSERT INTO `recommendation_details` VALUES (27, 15, '单式A', '主探索注，覆盖前区Top5与后区Top2热号。', '7,12,19,24,31', '6,11', 0.72000, '2025-10-29 12:53:20');
INSERT INTO `recommendation_details` VALUES (28, 15, '单式B', '交叉验证注，检验12/19/24的稳定性。', '5,12,18,19,24', '2,9', 0.70000, '2025-10-29 12:53:20');
INSERT INTO `recommendation_details` VALUES (29, 15, '单式C', '冷热混合注，引入5/31作为潜在冷码。', '7,18,19,31,5', '1,6', 0.68000, '2025-10-29 12:53:20');
INSERT INTO `recommendation_details` VALUES (30, 15, '单式D', '高熵覆盖注，最大化号码多样性。', '12,24,31,7,18', '11,2', 0.67000, '2025-10-29 12:53:20');
INSERT INTO `recommendation_details` VALUES (31, 15, '单式E', '边缘探索注，测试低概率组合的潜在爆发。', '5,7,19,24,18', '9,1', 0.66000, '2025-10-29 12:53:20');
INSERT INTO `recommendation_details` VALUES (32, 16, '核心复式(5+3)', '主力覆盖，确保在高熵分布下捕获至少2个前区命中与1个后区命中。', '5,12,19,27,33', '2,7,11', 0.89000, '2025-10-29 16:51:46');
INSERT INTO `recommendation_details` VALUES (33, 16, '卫星单式A', '引入中冷号24、31，试探潜在遗漏回补。', '5,12,19,24,31', '2,9', 0.72000, '2025-10-29 16:51:46');
INSERT INTO `recommendation_details` VALUES (34, 16, '卫星单式B', '替换边缘热号，测试边界扩展可能性。', '8,12,19,27,35', '4,11', 0.70000, '2025-10-29 16:51:46');
INSERT INTO `recommendation_details` VALUES (35, 16, '卫星单式C', '扰动中间区号码，增强中部覆盖密度。', '5,14,19,27,30', '7,4', 0.68000, '2025-10-29 16:51:46');
INSERT INTO `recommendation_details` VALUES (36, 16, '卫星单式D', '引入后区冷号1，对冲极端分布风险。', '3,12,20,27,33', '11,1', 0.65000, '2025-10-29 16:51:46');
INSERT INTO `recommendation_details` VALUES (37, 17, '核心复式(7+2)', '主力覆盖，囊括热力图前5及中位补充号，确保基础命中概率。', '5,12,18,24,31,8,20', '2,7', 0.82000, '2025-10-29 17:01:35');
INSERT INTO `recommendation_details` VALUES (38, 17, '探索单式A (低区强化)', '试探低区潜在冷转热机会，成本低，风险可控。', '3,5,9,12,16', '2,4', 0.61000, '2025-10-29 17:01:35');
INSERT INTO `recommendation_details` VALUES (39, 17, '探索单式B (高区对冲)', '对冲高区遗漏反弹可能，与主干形成互补。', '20,24,27,31,33', '7,11', 0.63000, '2025-10-29 17:01:35');
INSERT INTO `recommendation_details` VALUES (40, 18, '核心复式(7+3)', '主力覆盖，捕获前区多热点与后区高概率组合，确保基础命中期望。', '5,12,19,27,33,8,21', '6,11,2', 0.89000, '2025-10-29 17:26:22');
INSERT INTO `recommendation_details` VALUES (41, 18, '卫星单式A', '试探后区次热组合，成本低，提升二等及以上奖级捕获概率。', '5,12,19,27,33', '9,4', 0.72000, '2025-10-29 17:26:22');
INSERT INTO `recommendation_details` VALUES (42, 18, '卫星单式B', '引入中低频前区冷号（14,30,3）与高热后区组合，对冲热号失效风险。', '8,21,14,30,3', '6,11', 0.68000, '2025-10-29 17:26:22');
INSERT INTO `recommendation_details` VALUES (43, 18, '卫星单式C', '聚焦前区中部热区，搭配后区稳健组合，平衡奇偶与大小结构。', '12,19,27,33,1', '2,4', 0.70000, '2025-10-29 17:26:22');
INSERT INTO `recommendation_details` VALUES (44, 18, '卫星单式D', '纳入高遗漏冷号15、31，利用熵正则化提示的潜在反转信号，增强组合弹性。', '5,8,21,15,31', '11,9', 0.67000, '2025-10-29 17:26:22');
INSERT INTO `recommendation_details` VALUES (45, 19, '核心复式(7+3)', '主力覆盖，基于热力图Top区域构建，旨在捕获最可能的开奖组合。', '7,12,19,24,31,5,18', '6,11,2', 0.82000, '2025-10-29 17:30:43');
INSERT INTO `recommendation_details` VALUES (46, 19, '探索单式A', '次优路径探索，捕捉热力图次级高概率组合。', '12,19,24,31,5', '9,4', 0.68000, '2025-10-29 17:30:43');
INSERT INTO `recommendation_details` VALUES (47, 19, '探索单式B', '交叉验证组合，强化核心号码间的协同出现可能性。', '7,18,24,31,19', '11,6', 0.71000, '2025-10-29 17:30:43');
INSERT INTO `recommendation_details` VALUES (48, 20, '核心复式(7+2)', '主力覆盖高概率热区，确保前区至少3中，后区高概率命中。', '7,12,19,24,31,5,18', '6,11', 0.89000, '2025-10-29 18:07:12');
INSERT INTO `recommendation_details` VALUES (49, 20, '胆拖组合(3胆+5拖+2后)', '以热号为胆，嵌入高遗漏冷码15、22作为拖码，兼顾效率与反转机会。', 'b胆,t拖', '2,9', 0.82000, '2025-10-29 18:07:12');
INSERT INTO `recommendation_details` VALUES (50, 20, '冷码突击单式A', '聚焦前区高遗漏冷码3、15、22，博取极端反转收益。', '3,11,15,22,28', '4', 0.61000, '2025-10-29 18:07:12');
INSERT INTO `recommendation_details` VALUES (51, 20, '冷码突击单式B', '覆盖边缘冷区与后区冷号12，扩大形态覆盖广度。', '6,14,20,29,35', '12', 0.59000, '2025-10-29 18:07:12');
INSERT INTO `recommendation_details` VALUES (52, 20, '均衡形态单式', '构建奇偶比3:2、区间比2:2:1的标准均衡形态，作为策略稳健基线。', '7,13,19,25,31', '6', 0.76000, '2025-10-29 18:07:12');
INSERT INTO `recommendation_details` VALUES (53, 21, '核心复式(7+2)', '主力覆盖前区热力集中带与后区高概率组合，确保基础命中期望。', '7,12,19,24,31,5,28', '5,9', 0.85000, '2025-10-29 18:08:43');
INSERT INTO `recommendation_details` VALUES (54, 21, '卫星单式A (冷区试探)', '试探前区两端冷号（1,35）及后区极冷号（1,12），防范分布突变风险。', '1,3,15,22,35', '1,12', 0.60000, '2025-10-29 18:08:43');
INSERT INTO `recommendation_details` VALUES (55, 21, '卫星单式B (热区强化)', '强化热力图次高概率区域，与核心复式形成互补，提升中奖连带效应。', '8,13,18,23,30', '7,11', 0.70000, '2025-10-29 18:08:43');
INSERT INTO `recommendation_details` VALUES (56, 22, '核心复式(6+2)', '主力覆盖前区前5热号及一个中位补充号，后区锁定最高概率两码，确保基础命中。', '7,12,19,24,31,5', '5,9', 0.82000, '2025-10-29 18:11:14');
INSERT INTO `recommendation_details` VALUES (57, 22, '卫星单式A', '微调后区，引入第三高概率号11，测试后区组合弹性。', '7,12,19,24,31,14', '5,11', 0.71000, '2025-10-29 18:11:14');
INSERT INTO `recommendation_details` VALUES (58, 22, '卫星单式B', '测试后区次高概率组合，前区保持热号主体。', '7,12,19,24,31,28', '9,2', 0.70000, '2025-10-29 18:11:14');
INSERT INTO `recommendation_details` VALUES (59, 22, '卫星单式C（冷热混合）', '引入前区极冷号1（理论遗漏值高），与热号混合，试探极端分布。', '7,12,19,24,31,1', '7,5', 0.68000, '2025-10-29 18:11:14');
INSERT INTO `recommendation_details` VALUES (60, 22, '卫星单式D（均衡型）', '前区加入中部均衡号20，后区覆盖第二、第四高概率号，提升分布广度。', '7,12,19,24,31,20', '11,2', 0.69000, '2025-10-29 18:11:14');
INSERT INTO `recommendation_details` VALUES (61, 23, '复式A (6+2)', '低成本广谱覆盖，作为策略基底。', '5,12,19,27,33,8', '7,11', 0.82000, '2025-10-29 18:14:11');
INSERT INTO `recommendation_details` VALUES (62, 23, '复式B (7+2)', '主力覆盖，增强前区密度，提升中奖概率。', '5,12,19,27,33,14,22', '7,2', 0.89000, '2025-10-29 18:14:11');
INSERT INTO `recommendation_details` VALUES (63, 23, '复式C (7+2)', '横向扩展，覆盖热力图次高概率区域，降低遗漏风险。', '12,19,27,33,3,16,30', '11,9', 0.87000, '2025-10-29 18:14:11');
INSERT INTO `recommendation_details` VALUES (64, 24, '核心复式(7+2)', '主力覆盖，捕获前区5热号中的多数及后区高概率组合，确保基础命中期望。', '7,12,19,24,31,5,18', '5,8', 0.85000, '2025-10-30 09:28:09');
INSERT INTO `recommendation_details` VALUES (65, 24, '卫星单式A', '补充后区次热组合，提升二等奖以上中奖概率。', '7,12,19,24,31', '11,2', 0.78000, '2025-10-30 09:28:09');
INSERT INTO `recommendation_details` VALUES (66, 24, '卫星单式B', '交叉验证后区热号5的稳定性，强化核心后区覆盖。', '7,12,19,24,31', '9,5', 0.76000, '2025-10-30 09:28:09');
INSERT INTO `recommendation_details` VALUES (67, 24, '卫星单式C', '测试前区热号子集与后区组合的协同效应。', '12,19,24,31,18', '8,11', 0.74000, '2025-10-30 09:28:09');
INSERT INTO `recommendation_details` VALUES (68, 24, '卫星单式D', '引入边缘热号5、18以扩展前区覆盖半径，防范模型初始偏差。', '7,19,24,5,18', '2,9', 0.72000, '2025-10-30 09:28:09');
INSERT INTO `recommendation_details` VALUES (69, 25, '核心复式(7+3)', '主力覆盖前区五大热号及两端冷号，后区锁定前三热号，构建高概率基础网。', '7,12,19,24,31,3,35', '5,8,11', 0.78000, '2025-10-30 09:30:10');
INSERT INTO `recommendation_details` VALUES (70, 25, '胆拖A (前胆2后拖6)', '以双热号为胆，扩大后区覆盖，应对后区高度均匀分布。', '7,19', '2,5,8,9,11,12', 0.72000, '2025-10-30 09:30:10');
INSERT INTO `recommendation_details` VALUES (71, 25, '胆拖B (前胆2后拖6)', '补充中高区热号组合，增强对潜在偏态的适应性。', '12,31', '1,3,5,8,10,11', 0.70000, '2025-10-30 09:30:10');
INSERT INTO `recommendation_details` VALUES (72, 25, '卫星单式1', '等距跳跃组合，覆盖未被热力图强调但数学上可能的结构。', '1,8,15,22,29', '4,7', 0.45000, '2025-10-30 09:30:10');
INSERT INTO `recommendation_details` VALUES (73, 25, '卫星单式2', '镜像对称结构，作为极端随机情形下的冗余覆盖。', '5,14,21,28,33', '6,12', 0.44000, '2025-10-30 09:30:10');
INSERT INTO `recommendation_details` VALUES (74, 26, '核心复式(5+5)', '主力覆盖，利用复式结构捕获前区2-3个热号与后区1-2个热号，奠定基础命中。', '5,12,18,24,33', '7,11,2,9,4', 0.89000, '2025-10-30 09:35:58');
INSERT INTO `recommendation_details` VALUES (75, 26, '卫星单式A', '热号微调，引入中位冷号19、27试探分布偏移。', '5,12,19,27,33', '7,11', 0.76000, '2025-10-30 09:35:58');
INSERT INTO `recommendation_details` VALUES (76, 26, '卫星单式B', '边缘热区探索，覆盖热力图次级峰值区域。', '8,18,24,30,35', '2,9', 0.74000, '2025-10-30 09:35:58');
INSERT INTO `recommendation_details` VALUES (77, 26, '卫星单式C', '极值试探，包含前区最小号1与后区稳定热号。', '1,12,18,25,33', '4,11', 0.75000, '2025-10-30 09:35:58');
INSERT INTO `recommendation_details` VALUES (78, 26, '卫星单式D', '遗漏回补测试，引入近期遗漏值较高的14、28。', '5,14,24,28,33', '7,2', 0.73000, '2025-10-30 09:35:58');
INSERT INTO `recommendation_details` VALUES (79, 27, '广域复式A (5+2)', '主力覆盖前区高概率区间与后区最强双码，构建基础命中保障。', '5,12,19,27,33', '6,11', 0.82000, '2025-10-30 09:40:28');
INSERT INTO `recommendation_details` VALUES (80, 27, '广域复式B (5+2)', '交叉覆盖前区次热区与后区次优组合，增强区域冗余。', '8,21,19,12,5', '2,9', 0.79000, '2025-10-30 09:40:28');
INSERT INTO `recommendation_details` VALUES (81, 27, '广域复式C (5+2)', '补全前区边缘热号与后区潜在冷转热码，完成全域覆盖闭环。', '27,33,21,8,19', '4,6', 0.80000, '2025-10-30 09:40:28');
INSERT INTO `recommendation_details` VALUES (82, 28, '核心复式(7+3)', '主力覆盖，基于热力图前7与后3构建，确保高概率区域全覆盖。', '5,7,12,15,19,24,31', '2,6,11', 0.89000, '2025-10-30 09:41:36');
INSERT INTO `recommendation_details` VALUES (83, 28, '卫星单式A (冷码试探)', '试探极端冷号（后区12遗漏值高），成本低，博取反转收益。', '1,8,14,22,27', '12', 0.60000, '2025-10-30 09:41:36');
INSERT INTO `recommendation_details` VALUES (84, 28, '卫星单式B (形态补位)', '补位中间遗漏区间，覆盖热力图次级区域，增强组合鲁棒性。', '3,10,18,25,33', '4', 0.63000, '2025-10-30 09:41:36');
INSERT INTO `recommendation_details` VALUES (85, 29, '核心复式(7+3)', '主力覆盖双热核区域，确保前区至少命中3码、后区至少命中1码的高概率事件。', '12,16,19,28,31,15,8', '4,10,1', 0.93000, '2025-10-30 09:59:00');
INSERT INTO `recommendation_details` VALUES (86, 29, '卫星单式A (冷码对冲)', '捕捉遗漏值模型提示的冷码反转信号（如后区3），对冲主策略可能遗漏的边缘趋势。', '11,18,22,25,29', '3,9', 0.68000, '2025-10-30 09:59:00');
INSERT INTO `recommendation_details` VALUES (87, 29, '卫星单式B (图网络突变点)', '基于图网络分析器识别的潜在突变连边（如{14,21}与{7,35}），布局非主流但结构稳定的组合。', '2,7,14,21,35', '6,12', 0.64000, '2025-10-30 09:59:00');
INSERT INTO `recommendation_details` VALUES (88, 30, '核心复式(7+3)', '主力攻击，覆盖高概率热区，旨在确保基础命中。', '5,8,15,23,27,31,34', '3,7,10', 0.91000, '2025-10-30 10:54:57');
INSERT INTO `recommendation_details` VALUES (89, 30, '卫星单式A (冷码突击)', '高风险对冲，捕捉高遗漏冷码的反转机会。', '2,15,19,26,31', '2,11', 0.65000, '2025-10-30 10:54:57');
INSERT INTO `recommendation_details` VALUES (90, 30, '卫星单式B (热号延续)', '捕捉热号延续趋势，与核心注形成协同效应。', '8,14,23,28,33', '3,10', 0.72000, '2025-10-30 10:54:57');
INSERT INTO `recommendation_details` VALUES (91, 30, '均衡单式C', '融合热冷元素，作为稳健型补充。', '5,12,15,23,31', '7,11', 0.69000, '2025-10-30 10:54:57');
INSERT INTO `recommendation_details` VALUES (92, 30, '防御型复式(6+2)', '低成本复式，用于增强核心区域覆盖，提升容错率。', '8,15,23,27,31,34', '3,10', 0.83000, '2025-10-30 10:54:57');
INSERT INTO `recommendation_details` VALUES (93, 31, '核心复式(7+3)', '主力攻击，覆盖高概率热区，旨在确保基础命中。', '8,15,19,23,27,31,5', '3,7,10', 0.91000, '2025-10-30 11:03:21');
INSERT INTO `recommendation_details` VALUES (94, 31, '卫星单式A (冷码突击)', '高风险对冲，捕捉高遗漏冷码的反转机会。', '1,15,22,31,34', '2,11', 0.65000, '2025-10-30 11:03:21');
INSERT INTO `recommendation_details` VALUES (95, 31, '卫星单式B (热号延续)', '顺势强化，押注近期高频组合的延续性。', '8,12,16,19,23', '3,10', 0.73000, '2025-10-30 11:03:21');
INSERT INTO `recommendation_details` VALUES (96, 32, '核心复式(7+2)', '主力覆盖双核区域，确保前区至少2码命中，后区高概率捕获1码。', '5,8,15,19,23,27,31', '3,10', 0.89000, '2025-10-30 11:46:06');
INSERT INTO `recommendation_details` VALUES (97, 32, '卫星单式A (冷码突袭)', '押注高遗漏冷号15/31反弹，搭配中期回补后区7/11，博取高赔率。', '15,31,6,20,34', '7,11', 0.72000, '2025-10-30 11:46:06');
INSERT INTO `recommendation_details` VALUES (98, 32, '卫星单式B (热号强化)', '强化热号组合，利用马尔可夫链捕捉近期高频转移路径（如12→18→29）。', '8,23,12,18,29', '10,1', 0.76000, '2025-10-30 11:46:06');
INSERT INTO `recommendation_details` VALUES (99, 33, '主力复式(7+2)', '覆盖前区双峰核心与后区最强热号，作为命中基础保障。', '8,23,15,31,19,5,27', '10,3', 0.92000, '2025-10-30 11:55:23');
INSERT INTO `recommendation_details` VALUES (100, 33, '卫星复式A(6+2)', '侧重热号组合，搭配次热后区，提升中等奖级概率。', '8,23,15,19,5,27', '7,11', 0.85000, '2025-10-30 11:55:23');
INSERT INTO `recommendation_details` VALUES (101, 33, '卫星复式B(6+2)', '强化冷号组合，利用10的后区热度对冲前区冷码风险。', '23,15,31,27,5,19', '1,10', 0.87000, '2025-10-30 11:55:23');

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
) ENGINE = InnoDB AUTO_INCREMENT = 21 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '用户实际购买记录表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of user_purchase_records
-- ----------------------------
INSERT INTO `user_purchase_records` VALUES (1, 2, 'default', '复式', '06,10,12,18,21,22,25', '01,06,08', 42.00, 0, 0, 0, 0.00, '2025-10-22 15:38:14', '2025-10-22 15:38:14');
INSERT INTO `user_purchase_records` VALUES (2, 2, 'default', '单式', '06,10,12,21,22', '01,06', 2.00, 0, 0, 0, 0.00, '2025-10-22 15:38:14', '2025-10-22 15:38:14');
INSERT INTO `user_purchase_records` VALUES (3, 2, 'default', '单式', '03,07,14,18,29', '02,08', 2.00, 0, 0, 0, 0.00, '2025-10-22 15:38:14', '2025-10-22 15:38:14');
INSERT INTO `user_purchase_records` VALUES (4, 3, 'default', '复式', '06,10,12,18,21,22,25', '01,06,08', 42.00, 0, 0, 0, 0.00, '2025-10-22 15:56:53', '2025-10-22 15:56:53');
INSERT INTO `user_purchase_records` VALUES (5, 3, 'default', '单式', '06,10,12,21,22', '01,06', 2.00, 0, 0, 0, 0.00, '2025-10-22 15:56:53', '2025-10-22 15:56:53');
INSERT INTO `user_purchase_records` VALUES (6, 3, 'default', '单式', '03,07,14,18,29', '02,08', 2.00, 0, 0, 0, 0.00, '2025-10-22 15:56:53', '2025-10-22 15:56:53');
INSERT INTO `user_purchase_records` VALUES (7, 4, 'default', '复式', '06,10,12,18,21,22,25', '01,06,08', 42.00, 0, 0, 0, 0.00, '2025-10-22 16:21:43', '2025-10-22 16:21:43');
INSERT INTO `user_purchase_records` VALUES (8, 4, 'default', '单式', '06,10,12,21,22', '01,06', 2.00, 0, 0, 0, 0.00, '2025-10-22 16:21:43', '2025-10-22 16:21:43');
INSERT INTO `user_purchase_records` VALUES (9, 4, 'default', '单式', '03,07,14,18,29', '02,08', 2.00, 0, 0, 0, 0.00, '2025-10-22 16:21:43', '2025-10-22 16:21:43');
INSERT INTO `user_purchase_records` VALUES (10, 5, 'default', '复式', '06,10,12,18,21,22,25', '01,06,08', 42.00, 0, 0, 0, 0.00, '2025-10-22 17:51:38', '2025-10-22 17:51:38');
INSERT INTO `user_purchase_records` VALUES (11, 5, 'default', '单式', '06,10,12,21,22', '01,06', 2.00, 0, 0, 0, 0.00, '2025-10-22 17:51:38', '2025-10-22 17:51:38');
INSERT INTO `user_purchase_records` VALUES (12, 5, 'default', '单式', '03,07,14,18,29', '02,08', 2.00, 0, 0, 0, 0.00, '2025-10-22 17:51:38', '2025-10-22 17:51:38');
INSERT INTO `user_purchase_records` VALUES (13, 6, 'default', '复式', '06,10,12,18,21,22,25', '01,06,08', 42.00, 0, 0, 0, 0.00, '2025-10-23 11:24:37', '2025-10-23 11:24:37');
INSERT INTO `user_purchase_records` VALUES (14, 6, 'default', '单式', '06,10,12,21,22', '01,06', 2.00, 0, 0, 0, 0.00, '2025-10-23 11:24:37', '2025-10-23 11:24:37');
INSERT INTO `user_purchase_records` VALUES (15, 6, 'default', '单式', '03,07,14,18,29', '02,08', 2.00, 0, 0, 0, 0.00, '2025-10-23 11:24:37', '2025-10-23 11:24:37');
INSERT INTO `user_purchase_records` VALUES (19, 9, 'default', '复式', '06,10,12,18,21,22,25', '01,06,08', 42.00, 0, 0, 0, 0.00, '2025-10-24 17:52:07', '2025-10-24 17:52:06');
INSERT INTO `user_purchase_records` VALUES (20, 9, 'default', '单式', '06,10,12,21,22', '01,06', 2.00, 0, 0, 0, 0.00, '2025-10-24 17:52:07', '2025-10-24 17:52:06');

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
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '用户管理表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of users
-- ----------------------------
INSERT INTO `users` VALUES (1, 'admin', 'wanyihong32@gmail.com', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'admin', NULL, 'medium', 0, 0.00, 0.00, 0.0000, 1, '2025-10-27 13:57:00', '2025-10-25 00:26:57', '2025-10-27 13:57:00');
INSERT INTO `users` VALUES (2, 'wanhong', '1806755934@qq.com', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'user', NULL, 'medium', 0, 0.00, 0.00, 0.0000, 1, '2025-10-29 17:30:42', '2025-10-27 10:16:49', '2025-10-29 17:30:42');

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
