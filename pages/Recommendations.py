# 算法推荐
# file: pages/Recommendations.py
import streamlit as st
import pandas as pd
import json
from datetime import datetime
from src.database.database_manager import DatabaseManager
from src.ui.style_utils import load_global_styles


def get_algorithm_recommendations(db_manager, period_number=None):
    """获取算法推荐"""
    try:
        if period_number:
            query = """
            SELECT ar.*, rd.recommend_type, rd.strategy_logic, 
                   rd.front_numbers, rd.back_numbers, rd.win_probability
            FROM algorithm_recommendation ar
            LEFT JOIN recommendation_details rd ON ar.id = rd.recommendation_metadata_id
            WHERE ar.period_number = %s
            ORDER BY ar.recommend_time DESC
            """
            results = db_manager.execute_query(query, (period_number,))
        else:
            query = """
            SELECT ar.*, rd.recommend_type, rd.strategy_logic, 
                   rd.front_numbers, rd.back_numbers, rd.win_probability
            FROM algorithm_recommendation ar
            LEFT JOIN recommendation_details rd ON ar.id = rd.recommendation_metadata_id
            ORDER BY ar.recommend_time DESC
            LIMIT 50
            """
            results = db_manager.execute_query(query)

        return results
    except Exception as e:
        st.error(f"获取算法推荐时出错: {e}")
        return []


def get_available_algorithms(db_manager):
    """获取可用算法"""
    try:
        query = "SELECT algorithm_name, algorithm_type, description FROM algorithm_configs WHERE is_active = 1"
        results = db_manager.execute_query(query)
        return results
    except Exception as e:
        st.error(f"获取算法列表时出错: {e}")
        return []


def generate_recommendation(db_manager, period_number, algorithm_version):
    """生成算法推荐（模拟）"""
    try:
        # 这里应该是调用实际的算法逻辑
        # 目前先模拟生成一些推荐数据

        recommendations = []

        # 模拟不同策略的推荐
        strategies = [
            {
                "type": "热号主攻",
                "logic": "基于近期热号统计分析",
                "front": "5,12,18,23,35",
                "back": "3,8",
                "probability": 0.85
            },
            {
                "type": "冷号回补",
                "logic": "关注长期遗漏的冷门号码",
                "front": "2,9,17,28,33",
                "back": "1,11",
                "probability": 0.72
            },
            {
                "type": "平衡策略",
                "logic": "奇偶、大小均衡分布",
                "front": "7,14,19,26,31",
                "back": "5,9",
                "probability": 0.78
            }
        ]

        # 插入推荐元数据
        recommendation_id = db_manager.insert_algorithm_recommendation_root(
            period_number=period_number,
            model_name=algorithm_version,
            confidence_score=0.75,
            risk_level="medium"
        )

        if recommendation_id:
            # 插入推荐详情
            for strategy in strategies:
                detail_data = {
                    'recommendation_metadata_id': recommendation_id,
                    'recommend_type': strategy['type'],
                    'strategy_logic': strategy['logic'],
                    'front_numbers': strategy['front'],
                    'back_numbers': strategy['back'],
                    'win_probability': strategy['probability']
                }

                # 这里需要调用插入推荐详情的函数
                # 暂时先添加到返回列表
                recommendations.append({
                    'period_number': period_number,
                    'algorithm_version': algorithm_version,
                    'recommend_type': strategy['type'],
                    'strategy_logic': strategy['logic'],
                    'front_numbers': strategy['front'],
                    'back_numbers': strategy['back'],
                    'win_probability': strategy['probability'],
                    'confidence_score': 0.75,
                    'risk_level': 'medium'
                })

        return recommendations

    except Exception as e:
        st.error(f"生成推荐时出错: {e}")
        return []


def recommendations_page():
    """算法推荐页面"""
    # 检查登录状态
    if not st.session_state.get("logged_in", False):
        st.warning("请先登录系统")
        st.switch_page("pages/Login.py")
        return

    load_global_styles()

    # 页面标题
    st.markdown("""
    <div class="card">
        <h1>🤖 智能算法推荐</h1>
        <p style="color: #7f8c8d;">基于多算法融合的智能选号推荐</p>
    </div>
    """, unsafe_allow_html=True)

    # 数据库连接
    try:
        db_manager = DatabaseManager(
            host='localhost', user='root', password='123456789',
            database='lottery_analysis_system', port=3309
        )
        if not db_manager.connect():
            st.error("数据库连接失败")
            return
    except Exception as e:
        st.error(f"数据库连接错误: {e}")
        return

    try:
        # 侧边栏控制
        st.sidebar.header("推荐设置")

        # 期号选择
        latest_period_query = "SELECT period_number FROM lottery_history ORDER BY draw_date DESC LIMIT 1"
        latest_period_result = db_manager.execute_query(latest_period_query)
        default_period = latest_period_result[0]['period_number'] if latest_period_result else "2025001"

        selected_period = st.sidebar.text_input("推荐期号", value=default_period)

        # 算法选择
        algorithms = get_available_algorithms(db_manager)
        algorithm_options = [f"{alg['algorithm_name']} ({alg['algorithm_type']})" for alg in algorithms]

        selected_algorithm = st.sidebar.selectbox(
            "选择算法",
            algorithm_options if algorithm_options else ["v1.0-statistical (statistical)"]
        )

        # 主内容区
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("### 🎯 生成推荐")

            if st.button("🚀 生成智能推荐", type="primary", use_container_width=True):
                with st.spinner("正在运行算法生成推荐..."):
                    # 提取算法版本
                    algorithm_version = selected_algorithm.split(' ')[0]

                    # 生成推荐
                    recommendations = generate_recommendation(db_manager, selected_period, algorithm_version)

                    if recommendations:
                        st.success(f"✅ 成功生成 {len(recommendations)} 条推荐")

                        # 显示推荐结果
                        for i, rec in enumerate(recommendations, 1):
                            with st.expander(
                                    f"推荐方案 {i}: {rec['recommend_type']} (置信度: {rec['confidence_score'] * 100}%)",
                                    expanded=True):
                                col_a, col_b, col_c = st.columns(3)

                                with col_a:
                                    st.markdown("**前区号码**")
                                    front_nums = rec['front_numbers'].split(',')
                                    front_html = " ".join([
                                        f'<span style="display: inline-block; width: 35px; height: 35px; background: #ff4757; color: white; border-radius: 50%; text-align: center; line-height: 35px; margin: 2px; font-weight: bold;">{num}</span>'
                                        for num in front_nums
                                    ])
                                    st.markdown(f'<div style="margin-bottom: 10px;">{front_html}</div>',
                                                unsafe_allow_html=True)

                                with col_b:
                                    st.markdown("**后区号码**")
                                    back_nums = rec['back_numbers'].split(',')
                                    back_html = " ".join([
                                        f'<span style="display: inline-block; width: 35px; height: 35px; background: #3742fa; color: white; border-radius: 50%; text-align: center; line-height: 35px; margin: 2px; font-weight: bold;">{num}</span>'
                                        for num in back_nums
                                    ])
                                    st.markdown(f'<div>{back_html}</div>', unsafe_allow_html=True)

                                with col_c:
                                    st.metric("预计中奖概率", f"{rec['win_probability'] * 100:.1f}%")
                                    st.metric("风险等级", rec['risk_level'])

                                st.markdown(f"**策略逻辑:** {rec['strategy_logic']}")

                                # 快速投注按钮
                                if st.button(f"💸 使用此推荐投注", key=f"bet_{i}", use_container_width=True):
                                    st.session_state.recommendation_for_betting = rec
                                    st.switch_page("pages/Betting.py")

            st.markdown("### 📈 历史推荐")

            # 获取历史推荐
            historical_recommendations = get_algorithm_recommendations(db_manager, selected_period)

            if historical_recommendations:
                # 转换为表格显示
                rec_data = []
                for rec in historical_recommendations:
                    rec_data.append({
                        "算法版本": rec['algorithm_version'],
                        "推荐类型": rec['recommend_type'],
                        "前区": rec['front_numbers'],
                        "后区": rec['back_numbers'],
                        "中奖概率": f"{rec['win_probability'] * 100:.1f}%",
                        "置信度": f"{rec['confidence_score'] * 100:.1f}%",
                        "风险等级": rec['risk_level'],
                        "生成时间": rec['recommend_time'].strftime("%Y-%m-%d %H:%M") if rec.get(
                            'recommend_time') else "N/A"
                    })

                df = pd.DataFrame(rec_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("暂无历史推荐记录")

        with col2:
            st.markdown("### 🔧 算法信息")

            if algorithms:
                for alg in algorithms:
                    with st.expander(f"{alg['algorithm_name']} ({alg['algorithm_type']})"):
                        st.write(alg['description'])
                        st.info(f"类型: {alg['algorithm_type']}")
            else:
                st.info("暂无算法配置信息")

            st.markdown("### 📊 性能指标")

            # 获取算法性能
            performance_query = "SELECT * FROM algorithm_performance"
            performance_results = db_manager.execute_query(performance_query)

            if performance_results:
                for perf in performance_results:
                    with st.expander(perf['algorithm_version']):
                        col_p1, col_p2 = st.columns(2)
                        with col_p1:
                            st.metric("前区命中率", f"{perf['avg_front_hit_rate'] * 100:.1f}%")
                            st.metric("稳定性", f"{perf['stability_score'] * 100:.1f}%")
                        with col_p2:
                            st.metric("后区命中率", f"{perf['avg_back_hit_rate'] * 100:.1f}%")
                            st.metric("性能趋势", perf['performance_trend'])
            else:
                st.info("暂无性能数据")

        # 快速导航
        st.markdown("---")
        st.markdown("### 🚀 快速导航")
        col_nav1, col_nav2, col_nav3 = st.columns(3)
        with col_nav1:
            if st.button("🏠 返回首页", use_container_width=True):
                st.switch_page("pages/Home.py")
        with col_nav2:
            if st.button("🔍 智能分析", use_container_width=True):
                st.switch_page("pages/Analysis.py")
        with col_nav3:
            if st.button("💸 我要投注", use_container_width=True):
                st.switch_page("pages/Betting.py")

    except Exception as e:
        st.error(f"页面加载出错: {e}")
    finally:
        db_manager.disconnect()


if __name__ == "__main__":
    recommendations_page()
else:
    recommendations_page()