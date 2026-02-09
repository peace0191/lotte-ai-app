import streamlit as st
import pandas as pd
import numpy as np
import time
import plotly.express as px
import plotly.graph_objects as go

def app():
    st.set_page_config(page_title="MLOps 관리자 대시보드", page_icon="⚙️", layout="wide")
    
    st.title("⚙️ MLOps 파이프라인 모니터링 (Admin)")
    st.markdown("학습 파이프라인 상태, 모델 성능 지표, 그리고 AI 자동화 작업 로그를 실시간으로 확인합니다.")

    # 1. Pipeline Status Overview
    st.subheader("1. Airflow Pipeline Status")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Data Ingestion DAG", value="Success ✅", delta="Last run: 2 mins ago")
    with col2:
        st.metric(label="Model Training DAG", value="Running 🏃", delta="Step: 3/5")
    with col3:
        st.metric(label="Shorts Gen DAG", value="Success ✅", delta="Created: 5 vids")
    with col4:
        st.metric(label="Active Models", value="v2.1.0", delta="Production")

    st.divider()

    # 2. Model Performance (MLflow)
    st.subheader("2. Model Performance Tracking (MLflow)")
    
    tab1, tab2 = st.tabs(["📉 Loss & Accuracy", "📊 Feature Importance"])
    
    with tab1:
        # 가상의 학습 데이터 생성
        epochs = list(range(1, 21))
        train_loss = [0.8 * (0.9 ** i) + np.random.normal(0, 0.02) for i in epochs]
        val_loss = [0.85 * (0.88 ** i) + np.random.normal(0, 0.03) for i in epochs]
        
        df_perf = pd.DataFrame({
            "Epoch": epochs,
            "Train Loss": train_loss,
            "Validation Loss": val_loss
        })
        
        fig = px.line(df_perf, x="Epoch", y=["Train Loss", "Validation Loss"], 
                      title="Training vs Validation Loss (Real-time)", markers=True)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        features = ["건물 연식", "지하철 거리", "학군 등급", "세대 수", "한강 조망", "주차 대수"]
        importance = [0.35, 0.25, 0.15, 0.10, 0.10, 0.05]
        fig_imp = px.bar(x=importance, y=features, orientation='h', 
                         title="SHAP Feature Importance (영향력 분석)", labels={'x':'Importance', 'y':'Feature'})
        st.plotly_chart(fig_imp, use_container_width=True)

    st.divider()

    # 3. AI Shorts Generation Logs
    st.subheader("3. AI Shorts Automation Logs")
    
    log_data = [
        {"Time": "10:00:01", "Job": "Shorts_Gen_Batch_01", "Status": "Success", "Detail": "대치 팰리스 45평 영상 생성 완료"},
        {"Time": "10:05:23", "Job": "Upload_Youtube", "Status": "Success", "Detail": "URL: youtube.com/shorts/xyz"},
        {"Time": "10:10:45", "Job": "Shorts_Gen_Batch_02", "Status": "Processing", "Detail": "은마아파트 이미지 분석 중..."},
        {"Time": "10:11:00", "Job": "Model_Retrain_Trigger", "Status": "Pending", "Detail": "데이터 드리프트 감지 대기중"}
    ]
    df_log = pd.DataFrame(log_data)
    
    # 상태에 따른 색상 함수
    def color_status(val):
        color = '#28a745' if val == 'Success' else '#ffc107' if val == 'Processing' else '#6c757d'
        return f'color: {color}; font-weight: bold'

    st.dataframe(df_log.style.applymap(color_status, subset=['Status']), use_container_width=True)

    # 수동 트리거 버튼 (데모용)
    c1, c2 = st.columns(2)
    if c1.button("🚀 긴급 재학습 실행 (Manual Trigger)"):
        with st.spinner("Airflow DAG 트리거 신호 전송 중..."):
            time.sleep(2)
        st.success("재학습 파이프라인이 시작되었습니다. (Run ID: manual__20260209)")

    if c2.button("🎬 선택 매물 숏츠 즉시 생성"):
        with st.spinner("이미지 분석 및 영상 렌더링 중..."):
            time.sleep(3)
        st.success("영상 생성이 완료되었습니다! (outputs/video_temp.mp4)")

if __name__ == "__main__":
    app()
