# algorithm_api.py
from flask import Flask, request, jsonify
from src.algorithms.algorithm_recommendation_service import AlgorithmRecommendationService
import logging

app = Flask(__name__)
service = AlgorithmRecommendationService()


@app.route('/api/generate_recommendations', methods=['POST'])
def generate_recommendations():
    """生成算法推荐 - 前端调用接口"""
    try:
        data = request.get_json()

        target_period = data.get('target_period')
        algorithms = data.get('algorithms', ['bayesian'])  # 默认使用贝叶斯算法
        history_limit = data.get('history_limit', 100)

        if not target_period:
            return jsonify({'error': '缺少目标期号'}), 400

        # 生成推荐
        result = service.generate_recommendations(
            target_period=target_period,
            algorithm_names=algorithms,
            history_limit=history_limit
        )

        return jsonify({
            'success': True,
            'data': result
        })

    except Exception as e:
        logging.error(f"API调用失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/recommendations/latest', methods=['GET'])
def get_latest_recommendations():
    """获取最新的推荐结果"""
    try:
        algorithm = request.args.get('algorithm')
        limit = int(request.args.get('limit', 5))

        recommendations = service.get_latest_recommendations(
            algorithm_name=algorithm,
            limit=limit
        )

        return jsonify({
            'success': True,
            'data': recommendations
        })

    except Exception as e:
        logging.error(f"获取推荐失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/algorithms/available', methods=['GET'])
def get_available_algorithms():
    """获取可用的算法列表"""
    algorithms = [
        {
            'name': 'bayesian',
            'display_name': '贝叶斯概率模型',
            'description': '基于历史号码出现频率的贝叶斯概率预测',
            'version': '2.0'
        }
        # 未来可以添加更多算法
    ]

    return jsonify({
        'success': True,
        'data': algorithms
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

# // 前端调用示例
# async function
# generateRecommendations()
# {
# try {
# const response = await fetch('/api/generate_recommendations', {
# method: 'POST',
# headers: {
#     'Content-Type': 'application/json',
# },
# body: JSON.stringify({
#     target_period: '2025070',
#     algorithms: ['bayesian'],
#     history_limit: 100
# })
# });
#
# const
# result = await response.json();
#
# if (result.success)
# {
#     console.log('推荐生成成功:', result.data);
# // 更新UI显示推荐结果
# displayRecommendations(result.data);
# } else {
#     console.error('推荐生成失败:', result.error);
# }
# } catch(error)
# {
#     console.error('API调用错误:', error);
# }
# }
#
# async function
# getLatestRecommendations()
# {
# try {
# const response = await fetch('/api/recommendations/latest?limit=5');
# const result = await response.json();
#
# if (result.success) {
# console.log('最新推荐:', result.data);
# return result.data;
# }
# } catch(error)
# {
#     console.error('获取推荐失败:', error);
# }
# }