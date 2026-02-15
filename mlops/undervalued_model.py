from __future__ import annotations
import pandas as pd
import numpy as np
import pickle
import os

try:
    import mlflow
    import mlflow.sklearn
    import mlflow.models
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    print("Warning: MLflow not installed. Logging disabled.")

# Simple linear regression or dummy logic
class UndervaluedScoreModel:
    def __init__(self, run_id=None):
        self.model = None
        self.run_id = run_id
        
    def train(self, data: pd.DataFrame):
        """
        Train a model on the data.
        Features: 'jeonse_ratio', 'school_score', 'subway_distance_m', 'size_type_30py'
        Target: 'undervalued_score'
        """
        if MLFLOW_AVAILABLE:
            mlflow.start_run()
            self.run_id = mlflow.active_run().info.run_id
            
        # Feature Engineering (Minimal)
        X = data[['jeonse_ratio', 'school_score', 'subway_distance_m', 'size_type']]
        # One-hot encode size_type
        X = pd.get_dummies(X, columns=['size_type'], drop_first=True)
        y = data['undervalued_score']
        
        # Fit a simple linear model (using statsmodels or sklearn if available, or just heuristic weights)
        try:
            from sklearn.linear_model import LinearRegression
            from sklearn.metrics import mean_absolute_error, r2_score
            
            self.model = LinearRegression()
            self.model.fit(X, y)
            
            y_pred = self.model.predict(X)
            mae = mean_absolute_error(y, y_pred)
            r2 = r2_score(y, y_pred)
            
            print(f"Training Complete. MAE: {mae:.2f}, R2: {r2:.2f}")
            
            if MLFLOW_AVAILABLE:
                mlflow.log_metric("mae", mae)
                mlflow.log_metric("r2", r2)
                mlflow.sklearn.log_model(self.model, "model")
                mlflow.end_run()
                
            return {"mae": mae, "r2": r2}
            
        except ImportError:
            print("Sklearn not found, using dummy model logic.")
            self.model = "dummy"
            return {"mae": 0.0, "r2": 0.0}

    def predict(self, input_features: pd.DataFrame):
        """
        Predict 'undervalued_score' for new data.
        """
        if self.model is None:
            raise ValueError("Model not trained yet.")
            
        if self.model == "dummy":
            # Dummy prediction based on heuristic
            # Score = Jeonse Ratio * 50 + School Score * 10
            scores = (input_features['jeonse_ratio'] * 50) + (input_features.get('school_score', 3) * 10)
            return scores
            
        # Preprocess input same as training
        X = input_features.copy()
        if 'size_type' in X.columns:
            # Handle categorical manually if needed or ensure identical col structure
            # For simplicity, assume user handles encoding or we use robust pipeline
            pass
        
        # For simplicity in this demo, just recreate structure (in production use pipeline)
        # Re-create dummy cols if missing
        for col in ['size_type_30py', 'size_type_40py']: # Check model features
            if col not in X.columns:
                X[col] = 0
                
        # Only keep numeric columns expected
        feature_names = []
        if hasattr(self.model, "feature_names_in_"):
             feature_names = self.model.feature_names_in_
             # Basic alignment
             X_aligned = pd.DataFrame(0, index=X.index, columns=feature_names)
             for c in X.columns:
                 if c in feature_names:
                     X_aligned[c] = X[c]
             return self.model.predict(X_aligned)
        
        return np.zeros(len(input_features)) # Fallback

    def save(self, path="mlops/model.pkl"):
        with open(path, "wb") as f:
            pickle.dump(self.model, f)
            print(f"Model saved to {path}")
            
    def load(self, path="mlops/model.pkl"):
        if os.path.exists(path):
            with open(path, "rb") as f:
                self.model = pickle.load(f)
            print(f"Model loaded from {path}")
        else:
            print("Model file not found.")

if __name__ == "__main__":
    # Test run
    # Generate dummy data
    from data_generator import generate_sample_properties
    df = generate_sample_properties(100)
    
    model = UndervaluedScoreModel()
    metrics = model.train(df)
    print("Metrics:", metrics)
    model.save()
