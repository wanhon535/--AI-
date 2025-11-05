import json
import requests
import pandas as pd
from datetime import datetime
import sys
import os

# 添加配置文件路径
sys.path.append('E:/pyhton/AI/AICp/src/llm')
from src.llm.config import MODEL_CONFIG


class DltAdvancedAnalyzer:
    def __init__(self):
        """
        初始化大乐透高级分析器
        """
        self.model_config = MODEL_CONFIG.get("gpt-4o", {})
        self.api_key = self.model_config.get("api_key")
        self.base_url = self.model_config.get("base_url")
        self.model = "gpt-4o"

        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        # 加载历史数据
        self.history_data = self.load_history_data()

        print(f"✅ 分析器初始化完成，加载了 {len(self.history_data)} 期历史数据")

    def load_history_data(self):
        """
        加载大乐透历史数据
        """
        try:
            with open('E:/pyhton/AI/AICp/src/analysis/dlt_history_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"❌ 加载历史数据失败: {e}")
            return []

    def get_next_period_info(self):
        """
        获取下一期预测信息
        """
        if not self.history_data:
            return None, None

        # 获取最近一期数据
        latest_data = self.history_data[-1]
        latest_period = latest_data['expect']
        latest_time = latest_data['time']

        # 计算下一期（假设期号是连续的）
        try:
            next_period = str(int(latest_period) + 1)
            # 假设开奖时间间隔为2-3天
            latest_date = datetime.strptime(latest_time.split()[0], "%Y-%m-%d")
            next_date = latest_date.replace(day=latest_date.day + 2)
            next_time = next_date.strftime("%Y-%m-%d") + " 21:25:00"
        except:
            next_period = "下一期"
            next_time = "近期"

        return next_period, next_time

    def prepare_recent_data(self, num_periods=100):
        """
        准备最近N期的数据用于分析
        """
        if not self.history_data:
            return "无历史数据"

        recent_data = self.history_data[-num_periods:]
        formatted_data = []

        for item in recent_data:
            formatted_data.append({
                "期号": item['expect'],
                "开奖时间": item['time'],
                "前区号码": item['frontArea'],
                "后区号码": item['backArea'],
                "和值": item['frontArea_Sum'],
                "奇偶比": item['frontArea_OddEven'],
                "是否有连号": item['frontArea_IsConsecutive'],
                "跨度": item['frontArea_Span']
            })

        return formatted_data

    def prepare_simple_data_summary(self):
        """
        准备简单的数据摘要（不需要复杂计算）
        """
        if not self.history_data:
            return None

        print("📊 准备数据摘要...")

        recent_data = self.history_data[-100:]  # 使用最近100期

        # 简单统计
        front_counts = {}
        back_counts = {}
        sums = []

        for item in recent_data:
            for num in item['frontArea']:
                front_counts[num] = front_counts.get(num, 0) + 1
            for num in item['backArea']:
                back_counts[num] = back_counts.get(num, 0) + 1
            sums.append(item['frontArea_Sum'])

        # 热门号码
        front_hot = sorted(front_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        back_hot = sorted(back_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        data_summary = {
            "periods_analyzed": len(recent_data),
            "date_range": f"{recent_data[0]['time']} 至 {recent_data[-1]['time']}",
            "front_hot_numbers": [x[0] for x in front_hot],
            "back_hot_numbers": [x[0] for x in back_hot],
            "average_sum": sum(sums) / len(sums),
            "recent_20_data": recent_data[-20:]  # 最近20期详细数据
        }

        return data_summary

    def call_gpt4o_advanced_analysis(self, prompt: str) -> dict:
        """
        调用GPT-4o进行高级分析
        """
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": """你是一个顶尖的彩票预测专家和数据分析科学家。请基于提供的历史数据，在脑海中模拟运行各种高级算法进行分析。

分析要求：
1. 严格在思维中模拟运行因果推断、时间序列预测等高级算法
2. 每个预测必须有数学和统计理论支持
3. 提供详细的算法模拟过程和推理
4. 基于真实概率计算而非主观猜测
5. 给出多个算法视角的交叉验证
6. 严格按照JSON格式返回结果"""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.2,  # 较低温度保证稳定性
            "max_tokens": 16000,  # 增加token限制以容纳详细分析
            "response_format": {"type": "json_object"}
        }

        try:
            print("🔄 步骤1: 开始调用GPT-4o进行深度分析...")
            print(f"   📡 请求地址: {self.base_url}")
            print(f"   🔑 使用模型: {self.model}")
            print(f"   📊 提示词长度: {len(prompt)} 字符")

            start_time = datetime.now()
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=180  # 增加超时时间
            )
            end_time = datetime.now()
            request_duration = (end_time - start_time).total_seconds()

            print(f"   ⏱️  API请求耗时: {request_duration:.2f}秒")
            print(f"   📨 响应状态码: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                print("   ✅ API调用成功，开始解析返回内容...")

                # 解析JSON内容
                parsed_result = json.loads(content)
                print(f"   📋 返回数据结构: {list(parsed_result.keys())}")

                return parsed_result
            else:
                print(f"   ❌ API调用失败: {response.status_code}")
                print(f"   🔍 错误详情: {response.text[:500]}...")
                return {"error": f"API调用失败: {response.status_code}", "details": response.text}

        except json.JSONDecodeError as e:
            print(f"   ❌ JSON解析错误: {e}")
            if 'content' in locals():
                print(f"   📄 原始返回内容: {content[:500]}...")
            return {"error": "JSON解析失败", "details": str(e)}
        except Exception as e:
            print(f"   ❌ 调用过程中出错: {e}")
            import traceback
            print(f"   🔍 详细错误信息: {traceback.format_exc()}")
            return {"error": "请求异常", "details": str(e)}

    def generate_detailed_analysis_prompt(self, data_summary: dict, next_period: str, next_time: str) -> str:
        """
        生成详细分析提示词，包含算法过程和多种组合
        """
        prompt = f"""
# 大乐透高级算法预测分析
## 预测目标：第{next_period}期大乐透

## 可用历史数据
- 分析期数：{data_summary['periods_analyzed']}期
- 时间范围：{data_summary['date_range']}
- 前区热门号码：{data_summary['front_hot_numbers']}
- 后区热门号码：{data_summary['back_hot_numbers']}
- 平均和值：{data_summary['average_sum']:.1f}

## 详细历史数据（最近20期）
{json.dumps(data_summary['recent_20_data'], ensure_ascii=False, indent=2)}

## 算法框架要求

请基于上述历史数据，在思维中模拟运行以下高级算法，并给出详细的分析过程：

### 算法1：贝叶斯结构时间序列（BSTS）模拟
**算法原理：**
状态空间模型：y_t = Z_t * α_t + ε_t, α_t = T_t * α_{{t-1}} + R_t * η_t
使用MCMC进行后验采样，获得预测分布

**模拟分析步骤：**
1. 构建状态空间组件（局部线性趋势、季节性、回归项）
2. 运行MCMC采样（10000次迭代，burn-in 1000次）
3. 计算后验预测分布 p(y_{{t+1}}|y_{{1:t}})
4. 提取号码出现的后验概率

**输出要求：**
- 后验概率分布矩阵
- MCMC收敛诊断
- 预测区间估计

### 算法2：因果森林 + 双重机器学习模拟
**算法原理：**
处理效应估计：τ(x) = E[Y(1)-Y(0)|X=x]
使用因果森林进行异质性处理效应估计
双重机器学习去偏：θ̂ = argmin_θ E[ψ(W;θ,η₀)]

**模拟分析步骤：**
1. 构建特征矩阵X（包含历史出现频率、遗漏值等）
2. 使用因果森林估计每个号码的Conditional Average Treatment Effect (CATE)
3. 应用双重机器学习进行偏差校正
4. 计算稳健标准误和置信区间

**输出要求：**
- 每个号码的CATE估计值
- 因果效应显著性检验
- 异质性分析结果

### 算法3：LSTM-Transformer混合模型模拟
**算法原理：**
LSTM：h_t = LSTM(x_t, h_{{t-1}})
Transformer：Attention(Q,K,V) = softmax(QK^T/√d_k)V
混合架构结合时序建模和注意力机制

**模拟分析步骤：**
1. 构建序列数据（滑动窗口=10期）
2. LSTM层捕捉长期依赖关系
3. Transformer多头注意力捕捉号码间关联
4. 输出层使用softmax获得概率分布
5. 使用交叉熵损失和Adam优化器

**输出要求：**
- 序列预测概率
- 注意力权重分析
- 训练验证曲线

### 算法4：高斯过程回归（GPR）模拟
**算法原理：**
高斯过程：f(x) ~ GP(m(x), k(x,x'))
使用Matern核函数：k_{{ν=3/2}}(r) = (1 + √3r/ℓ)exp(-√3r/ℓ)
贝叶斯非参数建模

**模拟分析步骤：**
1. 选择Matern 3/2核函数
2. 优化超参数（长度尺度ℓ，方差σ²）
3. 计算后验预测分布
4. 获得预测均值和方差

**输出要求：**
- 预测分布参数
- 不确定性量化
- 核函数超参数

### 算法5：集成因果推断模拟
**算法原理：**
元学习器集成：τ̂(x) = ∑_{{m=1}}^M w_m τ̂_m(x)
结合多种因果推断方法（倾向得分匹配、工具变量、回归断点设计）

**模拟分析步骤：**
1. 运行多个基础因果模型
2. 计算模型权重（基于样本外表现）
3. 元学习器集成预测
4. 因果一致性检验

**输出要求：**
- 集成权重分布
- 因果发现结果
- 稳健性检验

## 概率计算框架

### 联合概率分布
P(号码组合) = ∏_{{i=1}}^5 P(前区_i) × ∏_{{j=1}}^2 P(后区_j)

### 条件概率计算
使用贝叶斯定理：P(A|B) = P(B|A)P(A)/P(B)

### 期望值计算
E[收益] = ∑ 中奖概率 × 中奖金额 - 成本

## 输出格式要求

{{
    "prediction_metadata": {{
        "target_period": "{next_period}",
        "algorithms_simulated": [
            "贝叶斯结构时间序列(BSTS)",
            "因果森林+双重机器学习",
            "LSTM-Transformer混合模型",
            "高斯过程回归(GPR)",
            "集成因果推断"
        ],
        "mathematical_framework": "使用的数学框架描述",
        "simulation_accuracy": "算法模拟精度评估"
    }},
    "algorithm_simulation_details": {{
        "bsts_simulation": {{
            "model_specification": "状态空间模型设定详情",
            "mcmc_simulation": "MCMC模拟过程描述",
            "posterior_predictive_distribution": "后验预测分布结果",
            "convergence_diagnostics": "收敛诊断结果",
            "number_probabilities": "基于BSTS的号码概率"
        }},
        "causal_forest_simulation": {{
            "feature_engineering": "特征工程过程",
            "causal_effect_estimation": "因果效应估计结果",
            "double_ml_correction": "双重机器学习校正",
            "heterogeneity_analysis": "异质性分析",
            "robustness_tests": "稳健性检验结果"
        }},
        "lstm_transformer_simulation": {{
            "architecture_design": "模型架构设计",
            "sequence_modeling": "序列建模过程",
            "attention_analysis": "注意力机制分析",
            "training_simulation": "训练过程模拟",
            "predictive_performance": "预测性能评估"
        }},
        "gaussian_process_simulation": {{
            "kernel_selection": "核函数选择理由",
            "hyperparameter_optimization": "超参数优化过程",
            "predictive_distribution": "预测分布结果",
            "uncertainty_quantification": "不确定性量化",
            "model_validation": "模型验证结果"
        }},
        "ensemble_causal_simulation": {{
            "base_learners": "基础学习器配置",
            "meta_learning_process": "元学习过程",
            "causal_discovery": "因果发现结果",
            "ensemble_weights": "集成权重计算",
            "consistency_checks": "一致性检验"
        }}
    }},
    "probability_calculations": {{
        "joint_probability_analysis": "联合概率分析",
        "conditional_probability_calculation": "条件概率计算",
        "bayesian_updating_process": "贝叶斯更新过程",
        "expected_value_analysis": "期望值分析",
        "risk_adjusted_probabilities": "风险调整后概率"
    }},
    "cross_algorithm_validation": {{
        "algorithm_agreement_analysis": "算法一致性分析",
        "prediction_concordance": "预测一致性检验",
        "confidence_interval_overlap": "置信区间重叠分析",
        "robustness_assessment": "稳健性评估"
    }},
    "optimized_recommendations": {{
        "7_3_combination_bsts_optimized": {{
            "algorithm_basis": "贝叶斯结构时间序列优化",
            "front_numbers": [1, 2, 3, 4, 5, 6, 7],
            "back_numbers": [1, 2, 3],
            "mathematical_justification": {{
                "posterior_probability_calculation": "后验概率计算过程",
                "credible_intervals": "可信区间估计",
                "model_evidence": "模型证据值",
                "predictive_performance": "预测性能指标"
            }},
            "risk_assessment": {{
                "volatility_analysis": "波动性分析",
                "downside_protection": "下行保护评估",
                "value_at_risk": "风险价值计算"
            }},
            "confidence_metrics": {{
                "calibrated_confidence": 0.92,
                "prediction_intervals": "预测区间",
                "sensitivity_analysis": "敏感性分析结果"
            }}
        }},
        "6_3_combination_causal_optimized": {{
            "algorithm_basis": "因果推断优化",
            "front_numbers": [8, 9, 10, 11, 12, 13],
            "back_numbers": [4, 5, 6],
            "mathematical_justification": {{
                "causal_effect_sizes": "因果效应大小",
                "instrumental_variable_analysis": "工具变量分析",
                "propensity_score_matching": "倾向得分匹配",
                "treatment_heterogeneity": "处理异质性"
            }},
            "risk_assessment": {{
                "causal_risk_factors": "因果风险因素",
                "confounding_control": "混杂因素控制",
                "selection_bias_assessment": "选择偏倚评估"
            }},
            "confidence_metrics": {{
                "calibrated_confidence": 0.89,
                "causal_identification_strength": "因果识别强度",
                "robustness_score": 0.87
            }}
        }},
        "7_2_combination_deep_learning_optimized": {{
            "algorithm_basis": "深度学习优化",
            "front_numbers": [14, 15, 16, 17, 18, 19, 20],
            "back_numbers": [7, 8],
            "mathematical_justification": {{
                "neural_network_architecture": "神经网络架构设计",
                "attention_mechanism_analysis": "注意力机制分析",
                "gradient_flow_analysis": "梯度流分析",
                "regularization_effects": "正则化效果"
            }},
            "risk_assessment": {{
                "overfitting_risk": "过拟合风险",
                "generalization_error": "泛化误差",
                "model_uncertainty": "模型不确定性"
            }},
            "confidence_metrics": {{
                "calibrated_confidence": 0.86,
                "cross_validation_scores": "交叉验证分数",
                "out_of_sample_performance": "样本外表现"
            }}
        }},
        "5_2_combination_gaussian_optimized": {{
            "algorithm_basis": "高斯过程优化",
            "front_numbers": [21, 22, 23, 24, 25],
            "back_numbers": [9, 10],
            "mathematical_justification": {{
                "gaussian_process_model": "高斯过程模型",
                "kernel_function_analysis": "核函数分析",
                "marginal_likelihood_maximization": "边缘似然最大化",
                "hyperparameter_posterior": "超参数后验"
            }},
            "risk_assessment": {{
                "predictive_variance_analysis": "预测方差分析",
                "uncertainty_propagation": "不确定性传播",
                "model_misspecification_risk": "模型设定错误风险"
            }},
            "confidence_metrics": {{
                "calibrated_confidence": 0.83,
                "predictive_interval_coverage": "预测区间覆盖",
                "model_evidence": "模型证据"
            }}
        }},
        "5_2_combination_ensemble_optimized": {{
            "algorithm_basis": "集成学习优化",
            "front_numbers": [26, 27, 28, 29, 30],
            "back_numbers": [11, 12],
            "mathematical_justification": {{
                "ensemble_methodology": "集成方法学",
                "model_weighting_scheme": "模型加权方案",
                "diversity_analysis": "多样性分析",
                "meta_learning_strategy": "元学习策略"
            }},
            "risk_assessment": {{
                "ensemble_risk_factors": "集成风险因素",
                "correlation_analysis": "相关性分析",
                "model_dependency_risk": "模型依赖性风险"
            }},
            "confidence_metrics": {{
                "calibrated_confidence": 0.80,
                "ensemble_stability": "集成稳定性",
                "agreement_metrics": "一致性指标"
            }}
        }}
    }},
    "final_recommendation_summary": {{
        "optimal_strategy_selection": "最优策略选择",
        "risk_diversification_plan": "风险分散计划",
        "investment_allocation_advice": "资金分配建议",
        "overall_confidence_assessment": {{
            "integrated_confidence_score": 0.88,
            "validation_metrics_summary": "验证指标总结",
            "robustness_evaluation": "稳健性评估"
        }},
        "mathematical_certainty_level": "数学确定性水平"
    }}
}}

## 重要说明

请基于提供的历史数据，在思维中详细模拟运行上述所有高级算法。每个算法都要提供：
1. 完整的数学推导过程
2. 参数估计和优化步骤
3. 预测结果和不确定性量化
4. 模型验证和诊断

所有推荐必须基于严格的数学计算和统计推断，而不是主观猜测。

目标是最大化第{next_period}期的中奖概率，同时控制风险。
"""

        return prompt

    def analyze_dlt_comprehensive(self):
        """
        执行大乐透综合分析
        """
        print("🎯 开始大乐透高级分析流程...")
        print("=" * 60)

        # 获取下一期信息
        print("📅 步骤1: 确定预测目标期号...")
        next_period, next_time = self.get_next_period_info()
        if not next_period:
            print("❌ 错误: 无法确定下一期信息")
            return {"status": "error", "message": "无法确定下一期信息"}

        print(f"   🎯 预测目标: 第{next_period}期 ({next_time})")

        # 准备历史数据
        print("📂 步骤2: 加载历史数据...")
        data_summary = self.prepare_simple_data_summary()
        if not data_summary:
            print("❌ 错误: 没有可用的历史数据")
            return {"status": "error", "message": "无历史数据"}

        print(f"   ✅ 数据加载完成，共{data_summary['periods_analyzed']}期历史数据")

        # 生成详细提示词
        print("\n📝 步骤3: 生成详细分析提示词...")
        prompt = self.generate_detailed_analysis_prompt(data_summary, next_period, next_time)
        print(f"   ✅ 提示词生成完成，长度: {len(prompt)} 字符")

        # 调用API进行分析
        print("\n🤖 步骤4: 调用GPT-4o进行深度算法分析...")
        print("   正在应用以下算法:")
        print("   1. 贝叶斯结构时间序列 (BSTS) - 状态空间建模 + MCMC")
        print("   2. 因果森林 + 双重机器学习 - 因果推断 + 去偏")
        print("   3. LSTM-Transformer混合模型 - 深度学习序列预测")
        print("   4. 高斯过程回归 (GPR) - 贝叶斯非参数建模")
        print("   5. 集成因果推断 - 元学习器集成")

        result = self.call_gpt4o_advanced_analysis(prompt)

        if result and "error" not in result:
            print("\n📊 步骤5: 处理分析结果...")
            self.display_algorithm_results(result, next_period)
            save_result = self.save_algorithm_results(result)

            final_result = {
                "status": "success",
                "prediction_period": next_period,
                "analysis_result": result,
                "save_status": save_result,
                "timestamp": datetime.now().isoformat()
            }
            print("🎉 综合分析流程完成!")
            return final_result
        else:
            error_msg = result.get("error", "未知错误") if result else "分析失败"
            print(f"❌ 分析流程失败: {error_msg}")

            return {
                "status": "error",
                "message": error_msg,
                "prediction_period": next_period,
                "timestamp": datetime.now().isoformat(),
                "details": result.get("details") if result else "未知错误"
            }

    def display_algorithm_results(self, result: dict, next_period: str):
        """
        显示算法模拟结果
        """
        print("\n" + "=" * 80)
        print("🎯 高级算法模拟预测报告")
        print("=" * 80)

        # 元数据
        metadata = result.get("prediction_metadata", {})
        print(f"\n📅 预测信息:")
        print(f"   目标期号: {next_period}")
        algorithms = metadata.get("algorithms_simulated", [])
        if algorithms:
            print(f"   模拟算法: {', '.join(algorithms[:3])}...")
        math_framework = metadata.get('mathematical_framework', 'N/A')
        if math_framework and len(math_framework) > 50:
            print(f"   数学框架: {math_framework[:50]}...")
        else:
            print(f"   数学框架: {math_framework}")

        # 算法模拟详情
        algorithm_details = result.get("algorithm_simulation_details", {})
        print(f"\n🔬 算法模拟摘要:")

        for algo_name, algo_detail in algorithm_details.items():
            if isinstance(algo_detail, dict):
                algo_name_pretty = algo_name.replace('_', ' ').title()
                first_key = next(iter(algo_detail.keys()), "")
                print(f"   {algo_name_pretty}: {first_key}")

        # 推荐组合
        recommendations = result.get("optimized_recommendations", {})
        print(f"\n💡 优化推荐组合:")

        combo_mapping = {
            "7_3_combination_bsts_optimized": "7+3组合(BSTS优化)",
            "6_3_combination_causal_optimized": "6+3组合(因果优化)",
            "7_2_combination_deep_learning_optimized": "7+2组合(深度学习优化)",
            "5_2_combination_gaussian_optimized": "5+2组合1(高斯优化)",
            "5_2_combination_ensemble_optimized": "5+2组合2(集成优化)"
        }

        for combo_key, combo_name in combo_mapping.items():
            combo = recommendations.get(combo_key, {})
            if combo:
                print(f"\n   {combo_name}:")
                print(f"      算法基础: {combo.get('algorithm_basis', 'N/A')}")
                print(f"      前区号码: {combo.get('front_numbers', [])}")
                print(f"      后区号码: {combo.get('back_numbers', [])}")

                confidence_metrics = combo.get("confidence_metrics", {})
                calibrated_conf = confidence_metrics.get("calibrated_confidence", 0)
                print(f"      校准置信度: {calibrated_conf * 100}%")

                # 数学依据
                math_just = combo.get("mathematical_justification", {})
                if isinstance(math_just, dict) and math_just:
                    first_key = next(iter(math_just.keys()), "")
                    print(f"      数学依据: {first_key}")

        # 最终推荐摘要
        final_summary = result.get("final_recommendation_summary", {})
        overall_conf = final_summary.get("overall_confidence_assessment", {})
        integrated_conf = overall_conf.get("integrated_confidence_score", 0)
        print(f"\n📊 最终推荐摘要:")
        print(f"   综合置信度: {integrated_conf * 100}%")

        optimal_strategy = final_summary.get('optimal_strategy_selection', 'N/A')
        if optimal_strategy and len(optimal_strategy) > 50:
            print(f"   最优策略: {optimal_strategy[:50]}...")
        else:
            print(f"   最优策略: {optimal_strategy}")

        risk_plan = final_summary.get("risk_diversification_plan", "")
        if risk_plan and len(risk_plan) > 60:
            print(f"   风险分散: {risk_plan[:60]}...")
        elif risk_plan:
            print(f"   风险分散: {risk_plan}")

        print("=" * 80)

    def save_algorithm_results(self, result: dict):
        """
        保存算法模拟结果
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"dlt_detailed_analysis_{timestamp}.json"

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"💾 详细分析结果已保存到: {filename}")
            return {"status": "success", "filename": filename}
        except Exception as e:
            print(f"❌ 保存结果失败: {e}")
            return {"status": "error", "message": str(e)}


# 使用示例
def main():
    # 初始化分析器
    print("🚀 初始化大乐透高级分析器...")
    analyzer = DltAdvancedAnalyzer()

    # 执行综合分析
    print("\n" + "=" * 60)
    final_result = analyzer.analyze_dlt_comprehensive()

    # 返回最终结果
    print("\n📋 最终执行结果汇总:")
    print(f"   执行状态: {final_result.get('status', 'unknown')}")
    if final_result.get('status') == 'success':
        print(f"   预测期号: {final_result.get('prediction_period')}")
        print(f"   保存状态: {final_result.get('save_status', {}).get('status')}")
        print(f"   文件路径: {final_result.get('save_status', {}).get('filename')}")
    else:
        print(f"   错误信息: {final_result.get('message')}")
        print(f"   详细错误: {final_result.get('details')}")

    return final_result


if __name__ == "__main__":
    main()