# ai/prediction/lstm_predictor.py
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
from typing import Tuple, Dict, Any, Optional
import os
import logging
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error

logger = logging.getLogger(__name__)

class LSTMModel(nn.Module):
    """LSTM for time-series forecasting."""

    def __init__(self, input_size: int, hidden_size: int = 64, num_layers: int = 2, output_size: int = 1):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        out, _ = self.lstm(x)  # out: (batch, seq_len, hidden)
        out = out[:, -1, :]     # Take last output
        out = self.fc(out)
        return out

class LSTMPredictor:
    """LSTM model for time-series traffic prediction."""

    def __init__(self, model_dir: str = "../models/lstm"):
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        self.model = None
        self.scaler = MinMaxScaler()
        self.input_size = 1  # default, will be set during train
        self.hidden_size = 64
        self.num_layers = 2
        self.output_size = 1
        self.lookback = 12

    def train(
        self,
        X: np.ndarray,
        y: np.ndarray,
        epochs: int = 50,
        batch_size: int = 32,
        lr: float = 0.001,
        save: bool = True
    ) -> Dict[str, float]:
        """Train LSTM model."""
        # X: (samples, lookback, features) -> here features=1 for univariate
        # Reshape if needed
        if len(X.shape) == 2:
            X = X.reshape(X.shape[0], X.shape[1], 1)
        self.input_size = X.shape[2]
        self.lookback = X.shape[1]

        # Scale data
        X_flat = X.reshape(-1, X.shape[-1])
        X_scaled = self.scaler.fit_transform(X_flat).reshape(X.shape)
        y_scaled = self.scaler.fit_transform(y.reshape(-1, 1))

        # Split
        split = int(0.8 * len(X))
        X_train, X_test = X_scaled[:split], X_scaled[split:]
        y_train, y_test = y_scaled[:split], y_scaled[split:]

        # Create DataLoader
        train_dataset = TensorDataset(
            torch.tensor(X_train, dtype=torch.float32),
            torch.tensor(y_train, dtype=torch.float32)
        )
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

        # Model
        self.model = LSTMModel(
            input_size=self.input_size,
            hidden_size=self.hidden_size,
            num_layers=self.num_layers,
            output_size=self.output_size
        )
        criterion = nn.MSELoss()
        optimizer = optim.Adam(self.model.parameters(), lr=lr)

        # Train
        self.model.train()
        for epoch in range(epochs):
            epoch_loss = 0.0
            for batch_X, batch_y in train_loader:
                optimizer.zero_grad()
                outputs = self.model(batch_X)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()
                epoch_loss += loss.item()
            if epoch % 10 == 0:
                logger.info(f"Epoch {epoch}/{epochs}, Loss: {epoch_loss/len(train_loader):.4f}")

        # Evaluate
        self.model.eval()
        with torch.no_grad():
            X_test_tensor = torch.tensor(X_test, dtype=torch.float32)
            preds = self.model(X_test_tensor).numpy()
            # Inverse transform
            y_test_inv = self.scaler.inverse_transform(y_test)
            preds_inv = self.scaler.inverse_transform(preds)
            mae = mean_absolute_error(y_test_inv, preds_inv)
            mse = mean_squared_error(y_test_inv, preds_inv)
        logger.info(f"LSTM trained: MAE={mae:.2f}, MSE={mse:.2f}")

        if save:
            self.save()
        return {"mae": mae, "mse": mse}

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions."""
        if self.model is None:
            raise RuntimeError("Model not loaded/trained.")
        if len(X.shape) == 2:
            X = X.reshape(X.shape[0], X.shape[1], 1)
        # Scale
        X_flat = X.reshape(-1, X.shape[-1])
        X_scaled = self.scaler.transform(X_flat).reshape(X.shape)
        self.model.eval()
        with torch.no_grad():
            X_tensor = torch.tensor(X_scaled, dtype=torch.float32)
            preds = self.model(X_tensor).numpy()
        # Inverse transform
        preds_inv = self.scaler.inverse_transform(preds)
        return preds_inv.flatten()

    def save(self):
        """Save model state and scaler."""
        if self.model:
            torch.save({
                'model_state_dict': self.model.state_dict(),
                'scaler': self.scaler,
                'input_size': self.input_size,
                'hidden_size': self.hidden_size,
                'num_layers': self.num_layers,
                'output_size': self.output_size,
                'lookback': self.lookback,
            }, os.path.join(self.model_dir, "lstm_model.pt"))
            logger.info(f"LSTM model saved to {self.model_dir}")

    def load(self):
        """Load model state and scaler."""
        model_path = os.path.join(self.model_dir, "lstm_model.pt")
        if os.path.exists(model_path):
            checkpoint = torch.load(model_path, map_location=torch.device('cpu'))
            self.input_size = checkpoint['input_size']
            self.hidden_size = checkpoint['hidden_size']
            self.num_layers = checkpoint['num_layers']
            self.output_size = checkpoint['output_size']
            self.lookback = checkpoint['lookback']
            self.scaler = checkpoint['scaler']
            self.model = LSTMModel(
                input_size=self.input_size,
                hidden_size=self.hidden_size,
                num_layers=self.num_layers,
                output_size=self.output_size
            )
            self.model.load_state_dict(checkpoint['model_state_dict'])
            logger.info("LSTM model loaded.")
            return True
        logger.warning("LSTM model files not found.")
        return False