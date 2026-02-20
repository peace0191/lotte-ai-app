import streamlit as st
import pandas as pd
import os
import sys
import time

# Add root directory to path to import mlops modules
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from mlops.undervalued_model import UndervaluedScoreModel
from mlops.data_generator import generate_sample_properties

st.set_page_config(page_title="Admin MLOps Console", layout="wide")

st.title("🛠️ AI MLOps Admin Console")
st.markdown("Monitor, train, and deploy AI models for Lotte Tower AI Real Estate.")

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Model Registry", "🚀 Training & Experiments", "📈 A/B Testing"])

# --- Tab 1: Registry ---
with tab1:
    st.header("🏆 Current Production Model")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Model Version", "v2.3.0", "+0.1")
    with col2:
        st.metric("Status", "Production", "Active")
    with col3:
        st.metric("Accuracy (R²)", "0.83", "+0.02")
    with col4:
        st.metric("Last Deployed", "2026-02-15")
        
    st.divider()
    
    st.subheader("📜 Model History")
    # Mock data for registry
    history_data = [
        {"Version": "v2.3.0", "Stage": "Production", "R2": 0.83, "MAE": "320만원", "Date": "2026-02-15"},
        {"Version": "v2.2.1", "Stage": "Staging", "R2": 0.81, "MAE": "345만원", "Date": "2026-02-10"},
        {"Version": "v2.1.0", "Stage": "Archived", "R2": 0.76, "MAE": "410만원", "Date": "2026-01-20"},
    ]
    st.dataframe(pd.DataFrame(history_data), use_container_width=True)
    
    st.info("💡 'Staging' model v2.2.1 is currently under A/B testing.")

# --- Tab 2: Training ---
with tab2:
    st.header("🧪 Experiment & Training")
    
    c_t1, c_t2 = st.columns([1, 2])
    
    with c_t1:
        st.markdown("### Configuration")
        n_samples = st.slider("Sample Data Size", 500, 5000, 1000)
        epochs = st.number_input("Epochs (Simulated)", 1, 100, 10)
        
        if st.button("🚀 Start Training Pipeline", type="primary", use_container_width=True):
            with st.status("Running MLOps Pipeline...", expanded=True) as status:
                st.write("1. Generating synthetic data...")
                data = generate_sample_properties(n_samples)
                time.sleep(1)
                st.write(f"   - Generated {len(data)} records.")
                
                st.write("2. Training Undervalued Score Model...")
                model = UndervaluedScoreModel()
                metrics = model.train(data)
                time.sleep(2)
                
                st.write("3. Evaluating performance...")
                st.write(f"   - MAE: {metrics.get('mae', 0):.2f}")
                st.write(f"   - R2: {metrics.get('r2', 0):.2f}")
                
                if metrics.get('r2', 0) > 0.8:
                    st.write("4. Registration: Success! (Promoted to Staging)")
                    status.update(label="Training Complete! ✅", state="complete")
                    st.success("New model successfully trained and registered.")
                else:
                    st.write("4. Registration: Skipped (Performance below threshold)")
                    status.update(label="Training Finished (Low Performance) ⚠️", state="complete")
                    st.warning("Model performance did not meet the requirement for staging.")

    with c_t2:
        st.markdown("### Real-time Training Logs (MLflow)")
        st.code("""
[INFO] Starting run: exp-20260215-001
[INFO] Params: n_estimators=100, max_depth=10
[INFO] Metric mae: 320.5
[INFO] Metric r2: 0.831
[INFO] Model saved to artifacts/model
[INFO] Run finished.
        """, language="bash")
        
# --- Tab 3: A/B Testing ---
with tab3:
    st.header("🆚 A/B Test Results (v2.3.0 vs v2.2.1)")
    
    c_a1, c_a2 = st.columns(2)
    
    with c_a1:
        st.subheader("Group A (Existing Model)")
        st.metric("Contract Rate", "15.2%", "Baseline")
        st.metric("Avg Click Rate", "8.4%", "Baseline")
        
    with c_a2:
        st.subheader("Group B (New Model)")
        st.metric("Contract Rate", "18.5%", "+3.3%")
        st.metric("Avg Click Rate", "9.2%", "+0.8%")
        
    st.success("✨ **Conclusion:** New model v2.3.0 shows statistically significant improvement in contract rate (p < 0.05). Recommended for full rollout.")
    
    if st.button("🚀 Promote v2.3.0 to Production (100% Rollout)"):
        with st.spinner("Deploying..."):
            time.sleep(2)
        st.balloons()
        st.success("Deployment Complete! v2.3.0 is now live.")
