import os
import random
import datetime
from decimal import Decimal

# Try to import mlflow, handle if missing
try:
    import mlflow
    from mlflow.tracking import MlflowClient
    HAS_MLFLOW = True
except ImportError:
    HAS_MLFLOW = False

class MLService:
    def __init__(self):
        self.experiment_name = "real_estate_undervalue"
        self.tracking_uri = "file:./mlruns"  # Local file based
        
        # Mock storage for demo if MLflow is not installed
        self.mock_registry = [
            {"version": "v2.1", "stage": "Archived", "accuracy": 0.82, "contract_rate": 0.45, "created": "2025-12-10"},
            {"version": "v2.2", "stage": "Staging", "accuracy": 0.88, "contract_rate": 0.62, "created": "2026-01-15"},
            {"version": "v2.3", "stage": "Production", "accuracy": 0.85, "contract_rate": 0.58, "created": "2026-01-05"},
        ]
        
        if HAS_MLFLOW:
            try:
                mlflow.set_tracking_uri(self.tracking_uri)
                mlflow.set_experiment(self.experiment_name)
                self.client = MlflowClient()
            except:
                # Fallback if initialization fails
                self.client = None

    def log_valuation_experiment(self, input_data: dict, output_metrics: dict, tags: dict = None):
        """
        Logs a single valuation run as an MLflow experiment.
        """
        if not HAS_MLFLOW:
            return  # Fail silently or log to console

        try:
            with mlflow.start_run(run_name=f"valuation_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"):
                # Log Parameters (Inputs)
                for k, v in input_data.items():
                    mlflow.log_param(k, v)
                
                # Log Metrics (Outputs)
                for k, v in output_metrics.items():
                    mlflow.log_metric(k, float(v) if v is not None else 0.0)
                
                # Log Tags
                if tags:
                    mlflow.set_tags(tags)
                
                # Auto-log system tags
                mlflow.set_tag("model_type", "rule_based_undervalue_v4_3")
                mlflow.set_tag("user_os", "windows")
                
        except Exception as e:
            print(f"[MLService] Logging failed: {e}")

    def get_model_registry(self):
        """
        Returns a list of models in the registry with their performance metrics.
        In a real scenario, this queries the MLflow Model Registry.
        For this demo, it returns a mix of mock data and real implementation hooks.
        """
        # If we had real MLflow models, we would query them here.
        # For the demo requirement ("Model Comparison"), we will manage a simulated registry.
        return sorted(self.mock_registry, key=lambda x: x['accuracy'], reverse=True)

    def promote_model(self, version, target_stage="Production"):
        """
        Promotes a specific model version to the target stage.
        Simulates the 'Click to Deploy' functionality.
        """
        # 1. Update Mock Registry
        for model in self.mock_registry:
            if model["version"] == version:
                model["stage"] = target_stage
            elif model["stage"] == target_stage:
                # Demote current production/staging to None or Archived
                model["stage"] = "Archived"
        
        # 2. (Optional) Log this deployment event
        if HAS_MLFLOW:
            with mlflow.start_run(run_name=f"deploy_{version}_{target_stage}"):
                mlflow.log_param("deployed_version", version)
                mlflow.log_param("target_stage", target_stage)
                mlflow.set_tag("event", "deployment")

        return True

    def get_current_production_version(self):
        for model in self.mock_registry:
            if model["stage"] == "Production":
                return model["version"]
        return "Unknown"

# Singleton
ml_service = MLService()
