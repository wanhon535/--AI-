def build_lotto_pro_prompt(
        recent_draws: list,  # 最近50期开奖数据
        user_bets: list,  # 用户历史投注记录
        game_name: str = "超级大乐透",
        next_issue_hint: str = None  # 可选：下一期期号提示
):
    """
    构建 Lotto-Pro 核心分析引擎的标准 Prompt
    适用于调用 Qwen / ChatGLM 等大模型 API

    输入：
        recent_draws: [LotteryHistory对象, ...]
        user_bets:    [PersonalBetting对象, ...]
        game_name: 彩种名称
        next_issue_hint: 下一期期号（如'2025101'），若无则自动推断
    """

    # 自动推断最新期号 - 修改为使用对象属性访问
    latest_issue = max(recent_draws, key=lambda x: x.period_number).period_number if recent_draws else "未知"
    next_issue = next_issue_hint or str(int(latest_issue) + 1) if latest_issue.isdigit() else "下一期"

    # 将数据转为文本表格 - 修改为使用对象属性访问
    draws_text = "\n".join([
        f"{d.period_number} | {' '.join(f'{n:02d}' for n in d.front_area)} + {' '.join(f'{n:02d}' for n in d.back_area)} | 和值:{d.sum_value}"
        for d in recent_draws[-10:]  # 仅显示最近10期减少token消耗
    ])

    bets_text = "\n".join([
        f"{'复式' if len(b.front_numbers) > 5 else '单注'} | {' '.join(f'{n:02d}' for n in b.front_numbers)} + {' '.join(f'{n:02d}' for n in b.back_numbers)}"
        for b in user_bets[-10:]
    ])

    PROMPT = f"""
【角色设定】
你是「Lotto-Pro」核心分析引擎，专精中国体育彩票“{game_name}”的历史规律挖掘与个性化推荐。你的输出必须基于量化分析，禁止主观臆测或虚构数据。

【任务说明】
根据提供的历史开奖与个人投注数据，完成三阶段分析，并生成结构化推荐结果。

【输入数据】
### 📊 历史开奖数据（最近 {len(recent_draws)} 期）
期号 | 前区号码 + 后区号码 | 和值
{draws_text}

### 🧑‍💼 个人历史投注记录（最近 {len(user_bets)} 笔）
类型 | 投注号码
{bets_text}

【执行步骤】

1️⃣ 【最新期号识别】
强制从历史开奖中提取最大期号：{latest_issue}
→ 设定本期分析期号为：{next_issue}

2️⃣ 【阶段一：个人投注风格分析】
- 计算用户前区平均和值、跨度（最大-最小）、奇偶比、大小比（≥18为大）、连号频率。
- 输出一句话风格总结（如：“高和值分散型”、“均衡奇偶偏好”）。

3️⃣ 【阶段二：客观规律分析】
- 统计最近50期前区奇偶比、大小比、和值范围，锁定出现频率最高且累计占比 >35% 的模式作为「最强模式」。
- 构建「高潜力号码池」：
   • 热号TOP5：最近30期出现频次最高的5个前区号码
   • 冷号TOP5：遗漏期数 ≥15 的前区号码
   → 合并去重，总数不超过10个

4️⃣ 【阶段三：智能推荐】
生成4组推荐，每组必须满足：
- 遵循「最强模式」
- 前区包含 ≥3 个来自「高潜力号码池」的号码

【输出要求】
严格按以下 Markdown 表格格式输出，不得添加额外解释：

**Lotto-Pro 核心分析引擎报告 (V8.0)**

### 本期分析期号：{next_issue}

### 阶段一：个人投注风格分析
**风格总结：** [填写]

### 阶段二：客观规律分析  
- 最强模式：[描述]，历史占比：[XX%]
- 高潜力号码池：[n1,n2,...]

### 阶段三：专业推荐
| 推荐类型 | 策略逻辑（等待策略助手校准） | 前区号码（5/6/8码） | 后区号码（2/3码） | 推荐号码中奖率 (%) |
|----------|-----------------------------|----------------------|-------------------|---------------------|
| 热号主攻 | 遵循最强模式 + 热号集中 | [5号码] | [2号码] | [理论EV] |
| 冷号回补 | 模式+冷号突破 | [5号码] | [2号码] | [理论EV] |
| **复式 (6+3)** | **遵循风格 + 最强模式强化** | **[6号码]** | **[3号码]** | **[理论EV]** |
| **复式 (8+3)** | **综合高潜力池全覆盖** | **[8号码]** | **[3号码]** | **[理论EV]** |

---
📌 注：所有推荐均为数据分析参考，彩票为随机事件，不保证中奖。
"""
    return PROMPT, next_issue  # 返回两个值以匹配调用代码
