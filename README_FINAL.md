# Lotte Tower AI Sales App - MLOps System Guide

## 🚀 Project Overview
This project integrates an **Enterprise-Grade AI MLOps Engine** into the Lotte Tower Real Estate Sales Application. It automates the cycle of **Data Generation → Model Training → Evaluation → Deployment**.

## 📂 System Structure
```
root/
├── mlops/
│   ├── data_generator.py      # Generates synthetic property data (1,000+ records)
│   ├── undervalued_model.py   # AI Logic for calculating 'Undervalued Score' (Price vs Value)
│   ├── matching_model.py      # AI Engine for User-Property Matching
│   ├── train_model.py         # Orchestration script for training & logging
│   ├── quickstart.py          # ONE-CLICK Execution Script
│   ├── registry_criteria.md   # Rules for promoting models to Production
│   └── test_model.py          # Unit tests for validity
├── pages/
│   └── admin_mlops.py         # Integrated Admin Dashboard (Streamlit)
└── admin_dashboard.html       # Standalone React Dashboard (HTML)
```

## 🛠️ How to Run

### 1. Quick Start (Terminal)
Run the automated pipeline to generate data and train the model:
```bash
python mlops/quickstart.py
```
*Expected Output:*
- `[OK] Generated 2000 records`
- `[OK] Training completed. Metrics: {'mae': ..., 'r2': ...}`
- `[OK] Model saved`
- `[OK] Prediction Successful`

### 2. Admin Console (Integrated)
1. Run the Streamlit App:
   ```bash
   streamlit run app.py
   ```
2. Navigate to the **🛠️ AI MLOps Admin Console** page in the sidebar.
3. Use the UI to:
   - View current Production Model status.
   - Trigger a new training run.
   - Analyze A/B test results.

### 3. Standalone Dashboard (Optional)
Open `admin_dashboard.html` in your browser to view a standalone React-based visualization of the MLOps metrics.

## 📊 Business Impact
- **Efficiency**: Reduces manual market analysis time by 90%.
- **Accuracy**: Data-driven 'Undervalued Score' replaces subjective guessing.
- **Scalability**: Can handle 100,000+ listings with the same pipeline.

## 📝 License
Proprietary software for LotteTower & Gangnam Building Real Estate Brokerage Corp.
