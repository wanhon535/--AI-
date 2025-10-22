# file: src/prompt_templates.py

from typing import List, Tuple, Any


# 假设您的数据对象定义在其他地方，这里为了示例完整性先定义一个伪类
class LotteryHistory:
    def __init__(self, **kwargs):
        self.period_number = kwargs.get('period_number')
        self.front_area = kwargs.get('front_area', [])
        self.back_area = kwargs.get('back_area', [])
        self.sum_value = sum(self.front_area)


class PersonalBetting:
    def __init__(self, **kwargs):
        self.front_numbers = kwargs.get('front_numbers', [])
        self.back_numbers = kwargs.get('back_numbers', [])


def build_lotto_pro_prompt_v9(
        recent_draws: List[LotteryHistory],
        user_bets: List[PersonalBetting],
        game_name: str = "超级大乐透",
        next_issue_hint: str = None,
        last_performance_report: str = None  # 新增：接收上一期的分析报告
) -> Tuple[str, str]:
    """
    构建 Lotto-Pro V9.0 Meta-Analysis 核心引擎的 Prompt。
    新版特性：
    - 集成动态走势判断与策略选择。
    - 强调核心共识号码池的构建。
    - 以风险规避和精简投入为决策核心。
    - 引入上一期表现作为反馈，实现闭环优化。
    """
    # --- 1. 数据准备 ---
    latest_issue = "未知"
    if recent_draws:
        latest_issue = max(d.period_number for d in recent_draws)

    next_issue = next_issue_hint or (str(int(latest_issue) + 1) if latest_issue.isdigit() else "下一期")

    # 格式化输入数据文本
    draws_text = "\n".join([
        f"{d.period_number} | {' '.join(f'{n:02d}' for n in d.front_area)} + {' '.join(f'{n:02d}' for n in d.back_area)} | 和值:{d.sum_value}"
        for d in recent_draws[-10:]  # 仅显示最近10期，节约token
    ]) if recent_draws else "无"

    bets_text = "\n".join([
        f"{'复式' if len(b.front_numbers) > 5 else '单注'} | {' '.join(f'{n:02d}' for n in b.front_numbers)} + {' '.join(f'{n:02d}' for n in b.back_numbers)}"
        for b in user_bets[-10:]
    ]) if user_bets else "无"

    # --- 2. 动态构建 Prompt ---
    # 使用列表逐部分构建，更加灵活和清晰
    prompt_parts = []

    # [角色与核心原则]
    prompt_parts.append(
        f"【角色设定与核心原则】\n"
        f"你是「Lotto-Pro V9.0 Meta-Analysis Engine」，一个专精于“{game_name}”的顶级策略分析AI。\n"
        f"你的核心任务是在“最大化中奖概率”和“风险规避”之间取得最佳平衡。\n"
        f"**首要原则：尽量不要亏损。** 因此，在资金有限的假设下，优先推荐高价值的**精简复式（如7+3）**，而不是大面积投注。"
    )

    # [反馈与反思] - 仅在提供了上一期报告时加入
    if last_performance_report:
        prompt_parts.append(
            "\n【上期预测表现回顾与反思】\n"
            "这是对你上一期推荐的复盘分析，请仔细阅读并总结经验，将其作为本期策略修正的关键依据：\n"
            f"{last_performance_report}"
        )

    # [输入数据]
    prompt_parts.append(
        "\n【输入数据】\n"
        f"### 📊 历史开奖数据（最近 {len(recent_draws)} 期）\n"
        "期号 | 前区号码 + 后区号码 | 和值\n"
        f"{draws_text}\n"
        f"### 🧑‍💼 个人历史投注记录（最近 {len(user_bets)} 笔）\n"
        "类型 | 投注号码\n"
        f"{bets_text}"
    )

    # [执行步骤] - 这是本次优化的核心
    prompt_parts.append(
        "\n【执行步骤】\n"
        f"1️⃣ **【第一步：当前走势诊断】** - 你必须首先分析近期数据（尤其是最近5-10期）的整体走势，并明确判断当前处于以下哪种状态：\n"
        "   - **平稳震荡期**：号码分布均衡，冷热交替规律。 \n"
        "   - **热号连开期**：少数几个号码或某个区间连续开出。\n"
        "   - **极端遗漏期**：某些号码或模式（如全大、全奇）已达到理论遗漏极值。\n"

        f"2️⃣ **【第二步：构建核心共识号码池】** - 综合多种分析维度，提取它们的**交集**，形成一个不超过12个号码的高潜力池：\n"
        "   - **高频热号**：近期（10-20期内）出现频率最高的号码。\n"
        "   - **关键遗漏号**：当前遗漏超过平均值（如遗漏>15期）且有回补趋势的号码。\n"
        "   - **趋势形态号**：根据连号、同尾号等走势图模式推断出的号码。\n"

        f"3️⃣ **【第三步：策略驱动分析】** - **根据第一步的走势诊断结果，从以下策略中选择一个作为本期核心打法**，并围绕第二步的号码池进行组号：\n"
        "   - 若为 **平稳震荡期** → 执行 **遗漏回补策略**：优先选择「核心共识池」中的冷号和次冷号。\n"
        "   - 若为 **热号连开期** → 执行 **追逐热号策略**：优先选择「核心共识池」中的高频热号，并考虑其邻号。\n"
        "   - 若为 **极端遗漏期** → 执行 **逆向追逐策略**：大胆选择符合该极端模式的边缘号码或长期未开出的组合。\n"

        f"4️⃣ **【第四步：生成结构化推荐】** - 基于所选策略，生成推荐。其中必须包含一组风险与收益平衡的 **(7+3) 复式**。"
    )

    # [输出要求]
    prompt_parts.append(
        "\n【输出要求】\n"
        "严格按照以下 Markdown 格式输出，所有分析和判断都必须填写完整。\n\n"
        f"**Lotto-Pro V9.0 Meta-Analysis Engine 报告**\n\n"
        f"### 本期分析期号：{next_issue}\n\n"
        f"### 阶段一：当前走势诊断与策略选择\n"
        f"**走势诊断：** [明确填写：平稳震荡期 / 热号连开期 / 极端遗漏期]\n"
        f"**本期核心策略：** [明确填写：遗漏回补 / 追逐热号 / 逆向追逐]\n\n"
        f"### 阶段二：核心共识号码池\n"
        f"**号码池：** [n1, n2, ...]\n\n"
        f"### 阶段三：专业推荐\n"
        "| 推荐类型 | 策略逻辑 | 前区号码 | 后区号码 | 推荐号码中奖率 (%) |\n"
        "|:---|:---|:---|:---|:---|\n"
        "| 策略主攻 | [根据本期核心策略简述] | [5号码] | [2号码] | [理论EV] |\n"
        "| 稳健备选 | [与主策略互补的逻辑] | [5号码] | [2号码] | [理论EV] |\n"
        "| **核心复式 (7+3)** | **风险平衡，覆盖核心池** | **[7号码]** | **[3号码]** | **[理论EV]** |"
    )

    final_prompt = "\n".join(prompt_parts)

    return final_prompt, next_issue