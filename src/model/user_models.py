# models/user_models.py
from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime

@dataclass
class User:
    """用户实体类"""
    id: int
    username: str  # 用户名
    email: Optional[str]  # 邮箱
    password_hash: str  # 密码哈希
    user_role: str = "user"  # 用户角色
    preferences: Optional[Dict[str, Any]] = None  # 用户偏好设置
    risk_tolerance: str = "medium"  # 风险承受能力
    total_bets: int = 0  # 总投注次数
    total_investment: float = 0.0  # 总投入金额
    total_winnings: float = 0.0  # 总中奖金额
    success_rate: float = 0.0  # 总体成功率
    is_active: bool = True  # 是否活跃
    last_login: Optional[datetime] = None  # 最后登录时间
