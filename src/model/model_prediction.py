# src/model/model_prediction.py

class ModelPrediction:
    """
    封装单个模型预测结果，供 PerformanceLogger 使用
    """
    def __init__(self, front_numbers=None, back_numbers=None, confidence=0.0):
        # PerformanceLogger 访问的属性必须是 front_area / back_area
        self.front_area = front_numbers or []
        self.back_area = back_numbers or []
        self.confidence = float(confidence)

    def __repr__(self):
        return f"<ModelPrediction front={self.front_area} back={self.back_area} conf={self.confidence}>"
