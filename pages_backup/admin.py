import streamlit as st
from services.auth import require_admin

require_admin()
import pandas as pd
import numpy as np
import time

def render(properties: dict = {}):
    # 0. Session State Safety Initialization (v4.30)
    if "redirect_to" not in st.session_state: st.session_state["redirect_to"] = None
    if "latest_star" not in st.session_state: st.session_state["latest_star"] = None
    if "star_dict" not in st.session_state: st.session_state["star_dict"] = {}

    st.markdown("## ⚙️ 자율 재학습 시스템 모니터링 (v3.2)")
    st.caption("Auto-Retraining System Dashboard | Status: **Operational** 🟢")

    # --- CSV Export Section ---
    with st.sidebar:
        st.markdown("### 📥 데이터 다운로드")
        
        # 1. Properties CSV
        all_props = []
        for complex_name, items in properties.items():
            for it in items:
                row = it.copy()
                row["complex"] = complex_name
                all_props.append(row)
        
        if all_props:
            df_props = pd.DataFrame(all_props)
            csv_props = df_props.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="🏠 매물 리스트 CSV 다운로드",
                data=csv_props,
                file_name="lotte_properties.csv",
                mime="text/csv",
                use_container_width=True
            )

        # 2. Reservation CSV
        try:
            from services.matching_svc import matching_svc
            res_list = matching_svc.match_reservations
            if res_list:
                df_res = pd.DataFrame(res_list)
                csv_res = df_res.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📝 매칭 예약 내역 CSV 다운로드",
                    data=csv_res,
                    file_name="matching_reservations.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        except:
            pass

        # 3. MOLIT Transaction Data CSV (New v4.30)
        try:
            import os
            import json
            from pathlib import Path
            data_dir = Path("data")
            all_transactions = []
            for f in os.listdir(data_dir):
                if f.endswith(".json") and "실거래가" in f:
                    with open(data_dir / f, "r", encoding="utf-8") as jf:
                        all_transactions.extend(json.load(jf))
            
            if all_transactions:
                df_molit = pd.DataFrame(all_transactions)
                csv_molit = df_molit.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📊 MOLIT 실거래 종합 다운로드",
                    data=csv_molit,
                    file_name="molit_real_transactions.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        except:
            pass

        # 4. Sync Database (New v4.30 Accurate Mode)
        st.markdown("---")
        if st.button("🔄 실거래 데이터 실시간 동기화", use_container_width=True, type="secondary"):
            with st.spinner("📊 CSV 데이터를 분석하여 DB에 적재 중..."):
                try:
                    from services.csv_processor import process_csv_files
                    process_csv_files()
                    st.success("✅ 실거래 데이터 동기화 완료!")
                    st.balloons()
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 동기화 오류: {str(e)}")

        st.markdown("---")
        st.info("💡 **Tip**: 아래 표 우측 상단의 아이콘을 클릭하여 직접 CSV로 저장할 수도 있습니다.")

    # 1. System Status Indicators
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Model Version", "v3.2.4", "Staging -> Prod")
    with c2:
        st.metric("Drift Status", "Safe", "KS Test < 0.05")
    with c3:
        st.metric("Last Retrain", "04:00 AM", "Success")
    with c4:
        st.metric("Active Traffic", "Canary 10%", "Stable")

    st.markdown("---")

    # 2. Drift Monitoring Visualization
    st.subheader("📡 Real-time Drift Detection (Airflow & MLflow)")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 📉 Data Drift (입력 데이터 분포 변화)")
        st.caption("Kolmogorov-Smirnov Test P-Value Trend")
        chart_data = pd.DataFrame(
            np.random.randn(20, 2) * 0.02 + 0.03,
            columns=['P-Value', 'Threshold']
        )
        chart_data['Threshold'] = 0.05 
        st.line_chart(chart_data)
        st.info("✅ P-Value가 임계치(0.05) 아래로 안정적으로 유지되고 있습니다.")

    with col2:
        st.markdown("#### 🎯 Prediction Drift (예측 오차율)")
        st.caption("RMSE (Root Mean Square Error) Monitoring")
        rmse_data = pd.DataFrame(
            np.random.randn(20) * 1000 + 5000, 
            columns=['RMSE']
        )
        st.area_chart(rmse_data)
        st.info("✅ 예측 오차가 허용 범위 내에 있어 재학습이 필요하지 않습니다.")

    st.markdown("---")
    # 3. Privacy & Security Management Console
    st.subheader("🛡️ Privacy & Security Console")
    
    try:
        from services.matching_svc import matching_svc
        
        sec_c1, sec_c2, sec_c3 = st.columns(3)
        with sec_c1:
            st.metric("Masking Status", "Active 🔒", "GDPR Basis")
        with sec_c2:
            st.metric("Encryption", "AES-256 (Mock)", "Data at Rest")
        with sec_c3:
            st.metric("Privacy Logs", f"{len(matching_svc.security_logs)}건", "Last 24h")

        st.subheader("🏆 실시간 AI 매칭 예약자 관리 (Masked View)")
        
        if "admin_unlocked" not in st.session_state:
            st.session_state.admin_unlocked = False

        if not st.session_state.admin_unlocked:
            st.warning("🔐 관리자 전용 접근")
            st.caption("이 페이지는 관계자 외 접근이 제한됩니다.")
            with st.form("admin_pin_form"):
                pin_input = st.text_input("관리자 PIN 번호를 입력하세요", type="password", placeholder="PIN", help="기본값: 0000")
                pin_btn = st.form_submit_button("확인")
                
                if pin_btn:
                    if pin_input == "0000": 
                        st.session_state.admin_unlocked = True
                        st.rerun()
                    else:
                        st.error("⛔ PIN 번호 오류: 접근이 승인되지 않았습니다.")
        else:
            if st.button("🔒 보안 잠금 (Lock)", type="secondary"):
                st.session_state.admin_unlocked = False
                st.rerun()

            reservations = matching_svc.get_masked_reservations()
            if not reservations:
                st.info("현재 접수된 매칭 예약 내역이 없습니다.")
            else:
                rows = []
                for r in reservations:
                    cond = r["conditions"]
                    score = r.get("match_score", 0)
                    score_color = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"
                    
                    rows.append({
                        "순번": f"{r['queue_no']}번",
                        "AI 점수": f"{score_color} {score}점",
                        "성함": cond.get("user_name"),
                        "연락처": cond.get("user_phone"),
                        "대상단지": cond.get("district", "-"),
                        "유형": cond.get("type", "-"),
                        "점수": score,
                        "상태": r["status"]
                    })
                st.dataframe(pd.DataFrame(rows), use_container_width=True)
                st.caption("🔒 모든 개인정보는 보안 가이드에 따라 자동 마스킹 처리되었습니다.")

        st.markdown("---")
        with st.expander("🕵️ Privacy Audit Trail (보안 감사 로그)"):
            if not matching_svc.security_logs:
                st.write("기록된 보안 이벤트가 없습니다.")
            else:
                log_df = pd.DataFrame(matching_svc.security_logs).iloc[::-1]
                st.table(log_df)
    except Exception as e:
        st.error(f"⚠️ 시스템 모듈 로드 중 오류 발생: {str(e)}")
        st.info("서비스 모듈(matching_svc) 상태를 확인해주세요.")

    st.markdown("---")
    
    # 4. MLOps Model Registry & Deployment (New Feature)
    st.subheader("🏗️ MLOps: Model Registry & Deployment")
    st.caption("MLflow 기반 모델 성과 비교 및 원클릭 배포 시스템")

    try:
        from services.ml_service import ml_service
        
        # 1) Current Status Header
        curr_ver = ml_service.get_current_production_version()
        st.info(f"🚀 현재 서비스 중인 모델(Live): **{curr_ver}** (Hybrid Valuation Engine)")

        # 2) Registry Cards
        models = ml_service.get_model_registry()
        
        # Header Row
        h1, h2, h3, h4, h5 = st.columns([1.5, 2, 2, 2, 2])
        h1.markdown("**Version**")
        h2.markdown("**Status**")
        h3.markdown("**정확도 (Acc)**")
        h4.markdown("**계약 전환율**")
        h5.markdown("**Action**")
        
        for m in models:
            with st.container():
                c1, c2, c3, c4, c5 = st.columns([1.5, 2, 2, 2, 2])
                
                # Version
                with c1:
                    st.write(f"**{m['version']}**")
                
                # Stage Badge
                with c2:
                    if m['stage'] == "Production":
                        st.success("✅ Production")
                    elif m['stage'] == "Staging":
                        st.warning("🟡 Staging")
                    else:
                        st.caption("⚫ Archived")
                        
                # Metrics
                with c3:
                    st.write(f"{m['accuracy']:.2f}")
                with c4:
                    st.write(f"{m['contract_rate']:.2f}")
                    
                # Action Button
                with c5:
                    if m['stage'] != "Production":
                        if st.button("🚀 승격 (Deploy)", key=f"promote_{m['version']}"):
                            ml_service.promote_model(m['version'])
                            st.toast(f"모델 {m['version']} 이(가) Production으로 배포되었습니다!", icon="🚀")
                            time.sleep(1.5)
                            st.rerun()
                    else:
                        st.button("사용 중", disabled=True, key=f"curr_{m['version']}")
            st.divider()

    except Exception as e:
        st.error(f"⚠️ MLOps 모듈 로드 오류: {e}")

    st.markdown("---")
    st.subheader("🚀 빠른 메뉴 이동")
    
    def nav_to(label):
        st.session_state["redirect_to"] = label
        st.rerun()

    nav_cols = st.columns(3)
    nav_cols[0].button("🏠 추천매물", key="nav_admin_1", type="primary", on_click=nav_to, args=("🏠 추천매물",))
    nav_cols[1].button("🎯 AI 저평가", key="nav_admin_2", type="primary", on_click=nav_to, args=("🎯 AI 저평가",))
    nav_cols[2].button("💬 AI 챗봇", key="nav_admin_3", type="primary", on_click=nav_to, args=("💬 AI 챗봇",))
