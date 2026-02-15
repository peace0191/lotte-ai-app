from undervalued_model import UndervaluedScoreModel
from data_generator import generate_sample_properties
import pandas as pd
import numpy as np

def run_experiment(n_samples=1000, max_depth=None):
    """
    Run an experiment: Train 'UndervaluedScoreModel' and check performance.
    """
    print(f"--- Running Experiment (n={n_samples}, depth={max_depth}) ---")
    
    # 1. Generate Data
    data = generate_sample_properties(n_samples)
    
    # 2. Train Model
    model = UndervaluedScoreModel()
    metrics = model.train(data)
    
    # 3. Save Artifacts
    if metrics:
        print(f"Experiment Metrics: {metrics}")
        model.save(f"mlops/metrics_{n_samples}.pkl")
    else:
        print("Training Failed")

if __name__ == "__main__":
    # Test multiple runs
    for size in [500, 1000]:
        run_experiment(n_samples=size)
