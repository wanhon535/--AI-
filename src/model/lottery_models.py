# models/lottery_models.py
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

@dataclass
class LotteryHistory:
    """历史开奖数据实体类"""
    id: int
    period_number: str  # 期号
    draw_date: datetime.date  # 开奖日期
    draw_time: datetime  # 开奖具体时间
    front_area: List[int]  # 前区号码
    back_area: List[int]  # 后区号码
    sum_value: int  # 和值
    span_value: int  # 跨度
    ac_value: int  # AC值
    odd_even_ratio: str  # 奇偶比
    size_ratio: str  # 大小比
    prime_composite_ratio: Optional[str]  # 质合比
    consecutive_numbers: Optional[List[int]]  # 连号信息
    consecutive_count: int  # 连号组数
    tail_numbers: Optional[List[int]]  # 尾数分布
    data_source: str = "official"  # 数据来源
    data_quality: int = 100  # 数据质量评分

    def __post_init__(self):
        # 确保前区和后区号码排序
        if self.front_area:
            self.front_area.sort()
        if self.back_area:
            self.back_area.sort()

@dataclass
class NumberStatistics:
    """号码统计分析实体类"""
    number: int  # 号码
    number_type: str  # 号码类型：front/back
    total_appearances: int = 0  # 总出现次数
    appearance_rate: float = 0.0  # 出现频率
    recent_10_appearances: int = 0  # 最近10期出现次数
    recent_20_appearances: int = 0  # 最近20期出现次数
    recent_50_appearances: int = 0  # 最近50期出现次数
    current_omission: int = 0  # 当前遗漏期数
    max_omission: int = 0  # 历史最大遗漏
    avg_omission: float = 0.0  # 平均遗漏
    heat_status: str = "warm"  # 热冷状态
    heat_score: float = 0.0  # 热度评分
    strong_followers: Optional[List[int]] = None  # 强跟随号码
    strong_precursors: Optional[List[int]] = None  # 强前导号码
    position_preference: Optional[Dict[str, Any]] = None  # 位置偏好统计

@dataclass
class AlgorithmConfig:
    """算法配置实体类"""
    id: int
    algorithm_name: str  # 算法名称
    algorithm_type: str  # 算法类型
    parameters: Dict[str, Any]  # 算法参数配置
    description: Optional[str]  # 算法描述
    version: str = "1.0.0"  # 版本号
    is_active: bool = True  # 是否启用
    is_default: bool = False  # 是否默认算法
    min_data_required: int = 50  # 最小数据要求
    expected_accuracy: Optional[float] = None  # 预期准确率
    computation_complexity: str = "medium"  # 计算复杂度
    memory_requirements: Optional[str] = None  # 内存要求

@dataclass
class AlgorithmPerformance:
    """算法性能统计实体类"""
    id: int
    algorithm_version: str  # 算法版本
    total_recommendations: int = 0  # 总推荐次数
    total_periods_analyzed: int = 0  # 总分析期数
    avg_front_hit_rate: float = 0.0  # 平均前区命中率
    avg_back_hit_rate: float = 0.0  # 平均后区命中率
    hit_distribution: Optional[Dict[str, Any]] = None  # 命中分布统计
    confidence_accuracy: float = 0.0  # 置信度准确性
    risk_adjusted_return: float = 0.0  # 风险调整后收益
    stability_score: float = 0.0  # 稳定性评分
    consistency_rate: float = 0.0  # 一致性比率
    current_weight: float = 0.1  # 当前权重
    weight_history: Optional[List[Dict[str, Any]]] = None  # 权重历史记录
    performance_trend: str = "stable"  # 性能趋势

@dataclass
class AlgorithmRecommendation:
    """算法推荐记录实体类"""
    id: int
    period_number: str  # 推荐期号
    recommend_time: datetime  # 推荐时间
    algorithm_version: str  # 算法版本
    recommendation_combinations: List[Dict[str, Any]]  # 推荐组合数组
    algorithm_parameters: Optional[Dict[str, Any]]  # 算法参数配置
    model_weights: Optional[Dict[str, float]]  # 模型权重配置
    confidence_score: float  # 总体置信度
    risk_level: str  # 风险等级
    analysis_basis: Optional[Dict[str, Any]]  # 分析依据数据
    key_patterns: Optional[List[str]]  # 关键模式识别
    recommend_type: str  # 推荐类型：primary/secondary/hedge

@dataclass
class PersonalBetting:
    """个人投注记录实体类"""
    id: int
    user_id: str  # 用户ID
    period_number: str  # 投注期号
    bet_time: datetime  # 投注时间
    bet_type: str  # 投注类型
    front_numbers: List[int]  # 前区投注号码
    front_count: int  # 前区号码数量
    back_numbers: List[int]  # 后区投注号码
    back_count: int  # 后区号码数量
    bet_amount: float  # 投注金额
    multiple: int = 1  # 投注倍数
    is_winning: bool = False  # 是否中奖
    winning_level: Optional[str] = None  # 中奖等级
    winning_amount: float = 0.0  # 中奖金额
    strategy_type: Optional[str] = None  # 投注策略类型
    confidence_level: Optional[int] = None  # 投注时置信度
    analysis_notes: Optional[str] = None  # 投注分析笔记

@dataclass
class RewardPenaltyRecord:
    """奖罚分明记录实体类"""
    id: int
    period_number: str  # 期号
    algorithm_version: str  # 算法版本
    recommendation_id: int  # 对应的推荐记录ID
    front_hit_count: int  # 前区命中数量
    back_hit_count: int  # 后区命中数量
    hit_score: float  # 命中得分
    reward_points: float  # 奖励积分
    penalty_points: float  # 惩罚积分
    net_points: float  # 净积分
    hit_details: Optional[Dict[str, Any]]  # 命中详情
    missed_numbers: Optional[List[int]]  # 未命中号码分析
    performance_rating: Optional[int] = None  # 表现评级(1-5星)
    accuracy_deviation: Optional[float] = None  # 准确度偏差
    improvement_suggestions: Optional[str] = None  # 改进建议

@dataclass
class ABTestConfig:
    """A/B测试配置实体类"""
    id: int
    test_name: str  # 测试名称
    test_description: Optional[str]  # 测试描述
    algorithm_a: str  # 算法A版本
    algorithm_b: str  # 算法B版本
    split_ratio: float = 0.5  # 流量分配比例
    test_parameters: Optional[Dict[str, Any]] = None  # 测试参数
    success_metrics: Dict[str, Any]  # 成功指标定义
    test_status: str = "draft"  # 测试状态
    start_date: Optional[datetime.date] = None  # 开始日期
    end_date: Optional[datetime.date] = None  # 结束日期
    min_sample_size: int = 100  # 最小样本量
    current_sample_size: int = 0  # 当前样本量
    algorithm_a_performance: Optional[Dict[str, Any]] = None  # 算法A表现
    algorithm_b_performance: Optional[Dict[str, Any]] = None  # 算法B表现
    statistical_significance: Optional[float] = None  # 统计显著性
# models/lottery_models.py
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

@dataclass
class LotteryHistory:
    """历史开奖数据实体类"""
    id: int
    period_number: str  # 期号
    draw_date: datetime.date  # 开奖日期
    draw_time: datetime  # 开奖具体时间
    front_area: List[int]  # 前区号码
    back_area: List[int]  # 后区号码
    sum_value: int  # 和值
    span_value: int  # 跨度
    ac_value: int  # AC值
    odd_even_ratio: str  # 奇偶比
    size_ratio: str  # 大小比
    prime_composite_ratio: Optional[str]  # 质合比
    consecutive_numbers: Optional[List[int]]  # 连号信息
    consecutive_count: int  # 连号组数
    tail_numbers: Optional[List[int]]  # 尾数分布
    data_source: str = "official"  # 数据来源
    data_quality: int = 100  # 数据质量评分

    def __post_init__(self):
        # 确保前区和后区号码排序
        if self.front_area:
            self.front_area.sort()
        if self.back_area:
            self.back_area.sort()

@dataclass
class NumberStatistics:
    """号码统计分析实体类"""
    number: int  # 号码
    number_type: str  # 号码类型：front/back
    total_appearances: int = 0  # 总出现次数
    appearance_rate: float = 0.0  # 出现频率
    recent_10_appearances: int = 0  # 最近10期出现次数
    recent_20_appearances: int = 0  # 最近20期出现次数
    recent_50_appearances: int = 0  # 最近50期出现次数
    current_omission: int = 0  # 当前遗漏期数
    max_omission: int = 0  # 历史最大遗漏
    avg_omission: float = 0.0  # 平均遗漏
    heat_status: str = "warm"  # 热冷状态
    heat_score: float = 0.0  # 热度评分
    strong_followers: Optional[List[int]] = None  # 强跟随号码
    strong_precursors: Optional[List[int]] = None  # 强前导号码
    position_preference: Optional[Dict[str, Any]] = None  # 位置偏好统计

@dataclass
class AlgorithmConfig:
    """算法配置实体类"""
    id: int
    algorithm_name: str  # 算法名称
    algorithm_type: str  # 算法类型
    parameters: Dict[str, Any]  # 算法参数配置
    description: Optional[str]  # 算法描述
    version: str = "1.0.0"  # 版本号
    is_active: bool = True  # 是否启用
    is_default: bool = False  # 是否默认算法
    min_data_required: int = 50  # 最小数据要求
    expected_accuracy: Optional[float] = None  # 预期准确率
    computation_complexity: str = "medium"  # 计算复杂度
    memory_requirements: Optional[str] = None  # 内存要求

@dataclass
class AlgorithmPerformance:
    """算法性能统计实体类"""
    id: int
    algorithm_version: str  # 算法版本
    total_recommendations: int = 0  # 总推荐次数
    total_periods_analyzed: int = 0  # 总分析期数
    avg_front_hit_rate: float = 0.0  # 平均前区命中率
    avg_back_hit_rate: float = 0.0  # 平均后区命中率
    hit_distribution: Optional[Dict[str, Any]] = None  # 命中分布统计
    confidence_accuracy: float = 0.0  # 置信度准确性
    risk_adjusted_return: float = 0.0  # 风险调整后收益
    stability_score: float = 0.0  # 稳定性评分
    consistency_rate: float = 0.0  # 一致性比率
    current_weight: float = 0.1  # 当前权重
    weight_history: Optional[List[Dict[str, Any]]] = None  # 权重历史记录
    performance_trend: str = "stable"  # 性能趋势

@dataclass
class AlgorithmRecommendation:
    """算法推荐记录实体类"""
    id: int
    period_number: str  # 推荐期号
    recommend_time: datetime  # 推荐时间
    algorithm_version: str  # 算法版本
    recommendation_combinations: List[Dict[str, Any]]  # 推荐组合数组
    algorithm_parameters: Optional[Dict[str, Any]]  # 算法参数配置
    model_weights: Optional[Dict[str, float]]  # 模型权重配置
    confidence_score: float  # 总体置信度
    risk_level: str  # 风险等级
    analysis_basis: Optional[Dict[str, Any]]  # 分析依据数据
    key_patterns: Optional[List[str]]  # 关键模式识别
    recommend_type: str  # 推荐类型：primary/secondary/hedge

@dataclass
class PersonalBetting:
    """个人投注记录实体类"""
    id: int
    user_id: str  # 用户ID
    period_number: str  # 投注期号
    bet_time: datetime  # 投注时间
    bet_type: str  # 投注类型
    front_numbers: List[int]  # 前区投注号码
    front_count: int  # 前区号码数量
    back_numbers: List[int]  # 后区投注号码
    back_count: int  # 后区号码数量
    bet_amount: float  # 投注金额
    multiple: int = 1  # 投注倍数
    is_winning: bool = False  # 是否中奖
    winning_level: Optional[str] = None  # 中奖等级
    winning_amount: float = 0.0  # 中奖金额
    strategy_type: Optional[str] = None  # 投注策略类型
    confidence_level: Optional[int] = None  # 投注时置信度
    analysis_notes: Optional[str] = None  # 投注分析笔记

@dataclass
class RewardPenaltyRecord:
    """奖罚分明记录实体类"""
    id: int
    period_number: str  # 期号
    algorithm_version: str  # 算法版本
    recommendation_id: int  # 对应的推荐记录ID
    front_hit_count: int  # 前区命中数量
    back_hit_count: int  # 后区命中数量
    hit_score: float  # 命中得分
    reward_points: float  # 奖励积分
    penalty_points: float  # 惩罚积分
    net_points: float  # 净积分
    hit_details: Optional[Dict[str, Any]]  # 命中详情
    missed_numbers: Optional[List[int]]  # 未命中号码分析
    performance_rating: Optional[int] = None  # 表现评级(1-5星)
    accuracy_deviation: Optional[float] = None  # 准确度偏差
    improvement_suggestions: Optional[str] = None  # 改进建议

@dataclass
class ABTestConfig:
    """A/B测试配置实体类"""
    id: int
    test_name: str  # 测试名称
    test_description: Optional[str]  # 测试描述
    algorithm_a: str  # 算法A版本
    algorithm_b: str  # 算法B版本
    split_ratio: float = 0.5  # 流量分配比例
    test_parameters: Optional[Dict[str, Any]] = None  # 测试参数
    success_metrics: Dict[str, Any]  # 成功指标定义
    test_status: str = "draft"  # 测试状态
    start_date: Optional[datetime.date] = None  # 开始日期
    end_date: Optional[datetime.date] = None  # 结束日期
    min_sample_size: int = 100  # 最小样本量
    current_sample_size: int = 0  # 当前样本量
    algorithm_a_performance: Optional[Dict[str, Any]] = None  # 算法A表现
    algorithm_b_performance: Optional[Dict[str, Any]] = None  # 算法B表现
    statistical_significance: Optional[float] = None  # 统计显著性
