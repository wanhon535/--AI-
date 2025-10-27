# src/algorithms/advanced_algorithms/neural_lottery_predictor.py
from src.algorithms.base_algorithm import BaseAlgorithm
from src.algorithms.advanced_algorithms.feature_engineer import FeatureEngineer
from src.model.lottery_models import LotteryHistory
from typing import List, Dict, Any, Optional
import numpy as np

try:
    import torch
    import torch.nn as nn
    from torch.utils.data import Dataset, DataLoader
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


if TORCH_AVAILABLE:
    class _LSTMDataset(Dataset):
        def __init__(self, X, y):
            self.X = torch.tensor(X.values, dtype=torch.float32)
            self.y = torch.tensor(y.values, dtype=torch.float32)

        def __len__(self):
            return len(self.X)

        def __getitem__(self, idx):
            return self.X[idx], self.y[idx]

    class _LSTMModel(nn.Module):
        def __init__(self, input_size: int, hidden_size: int = 64):
            super().__init__()
            self.lstm = nn.LSTM(input_size, hidden_size, batch_first=True)
            self.fc = nn.Linear(hidden_size, 1)

        def forward(self, x):
            x = x.unsqueeze(1)
            out, _ = self.lstm(x)
            return self.fc(out[:, -1, :])

    class NeuralLotteryPredictor(BaseAlgorithm):
        """基于LSTM的神经网络预测器"""

        def __init__(self):
            super().__init__("neural_lottery_predictor", "1.0")
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
            self.model = None

        def train(self, history_data: List[LotteryHistory]) -> bool:
            X, y = FeatureEngineer.build_features(history_data)
            if X.empty:
                return False

            dataset = _LSTMDataset(X, y)
            loader = DataLoader(dataset, batch_size=32, shuffle=True)
            self.model = _LSTMModel(input_size=X.shape[1]).to(self.device)
            opt = torch.optim.Adam(self.model.parameters(), lr=1e-3)
            loss_fn = nn.MSELoss()

            for epoch in range(10):
                for xb, yb in loader:
                    xb, yb = xb.to(self.device), yb.to(self.device)
                    opt.zero_grad()
                    out = self.model(xb)
                    loss = loss_fn(out, yb)
                    loss.backward()
                    opt.step()
            self.is_trained = True
            return True

        def predict(self, history_data: List[LotteryHistory]) -> Dict[str, Any]:
            if not self.is_trained:
                return {'error': '模型未训练'}

            X, y = FeatureEngineer.build_features(history_data)
            x_input = torch.tensor(X.values[-1:], dtype=torch.float32).to(self.device)
            with torch.no_grad():
                pred = self.model(x_input).cpu().numpy()[0][0]
            return {
                'algorithm': self.name,
                'version': self.version,
                'recommendations': [{'predicted_sum': float(pred)}],
                'analysis': {'features': list(X.columns[:10])}
            }
else:
    class NeuralLotteryPredictor(BaseAlgorithm):
        def __init__(self):
            super().__init__("neural_lottery_predictor", "1.0")
        def train(self, *_):
            raise RuntimeError("PyTorch 未安装")
        def predict(self, *_):
            return {'error': 'PyTorch 未安装'}
