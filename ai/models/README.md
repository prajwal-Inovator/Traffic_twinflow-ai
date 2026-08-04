# Model Weights Directory

This directory stores pre-trained and fine-tuned model weights for the AI modules.

## Subdirectories

- `yolov11/` – YOLOv11 detection model weights (downloaded from Ultralytics or custom)
- `xgboost/` – XGBoost model files (saved with joblib)
- `lstm/` – PyTorch LSTM model files (saved with torch.save)

## Usage

Models are loaded by the respective predictors at runtime. They can be replaced/updated without code changes.

## Notes

- Large files (>100 MB) are not committed to Git; they are downloaded on first run or via a separate model registry.