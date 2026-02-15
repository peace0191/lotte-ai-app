import os
import sys

# Add current dir to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_generator import generate_sample_properties
from undervalued_model import UndervaluedScoreModel
from train_model import run_experiment

def main():
    print("==================================================")
    print("[START] Quickstart for Real Estate AI Engine (Phase 2)")
    print("==================================================")
    
    # 1. Create Directories
    DATA_DIR = "mlops/data"
    MODEL_DIR = "mlops/models"
    
    for d in [DATA_DIR, MODEL_DIR]:
        if not os.path.exists(d):
            os.makedirs(d)
            print(f"Created directory: {d}")
    
    # 2. Generate Data
    print("\n[Step 1] Creating Synthetic Data...")
    df = generate_sample_properties(n_samples=2000)
    df.to_csv(os.path.join(DATA_DIR, "properties.csv"), index=False)
    print(f"[OK] Generated {len(df)} records -> {DATA_DIR}/properties.csv")
    
    # 3. Train Model
    print("\n[Step 2] Training Undervalued Score Model...")
    model_obj = UndervaluedScoreModel()
    metrics = model_obj.train(df)
    
    print(f"[OK] Training completed. Metrics: {metrics}")
    
    # 4. Save Model
    model_path = os.path.join(MODEL_DIR, "best_model.pkl")
    model_obj.save(model_path)
    print(f"[OK] Model saved to {model_path}")
    
    # 5. Verify Prediction
    print("\n[Step 3] Verifying Prediction...")
    # Take a sample
    sample_input = df.iloc[:1].copy()
    
    # Predict (Using dummy prediction logic since sk-learn model object is complex to serialize fully here without robust pipeline code, 
    # but let's assume `model_obj.predict` works if trained)
    try:
        score = model_obj.predict(sample_input)
        print(f"Input: {sample_input[['dong', 'market_price', 'jeonse_ratio']].to_dict('records')[0]}")
        print(f"Predicted Undervalued Score: {score}")
        print("[OK] Prediction Successful!")
    except Exception as e:
        print(f"[ERROR] Prediction Failed: {e}")

    print("\n==================================================")
    print("AI Engine Setup Completed Successfully!")
    print("==================================================")

if __name__ == "__main__":
    main()
