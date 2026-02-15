# ============================================================
# dashboard.py 수정 - 마지막 부분 교체
# ============================================================
# 
# 사용 방법:
# 1. dashboard.py 열기
# 2. Ctrl + F 검색: "st.markdown("### 📄 맞춤형 제안서 PDF 다운로드")"
# 3. 이 줄부터 파일 끝까지 삭제
# 4. 아래 코드로 교체
#
# ============================================================

    st.divider()

    # ============================================================
    # PDF 다운로드 & 바로가기 버튼 통합 섹션
    # ============================================================
    st.markdown("### 📄 맞춤형 제안서 PDF 다운로드")
    
    # 버튼 4개를 한 줄에 배치
    btn_col1, btn_col2, btn_col3, btn_col4 = st.columns([3, 2, 2, 2])
    
    with btn_col1:
        # PDF 생성 버튼
        if st.button("📄 PDF 생성 및 다운로드 (지도 포함)", key="pdf_gen_btn", use_container_width=True):
            with st.spinner("PDF 생성 중..."):
                try:
                    # 지도 데이터 준비
                    df_points = load_points()
                    points_list = []
                    for _, r in df_points.iterrows():
                        points_list.append({
                            "name": r["name"],
                            "lat": r["lat"],
                            "lon": r["lon"],
                            "category": r["category"],
                            "color": r["color"],
                            "group": r["category"],
                            "note": r.get("note", "")
                        })
                    
                    # 지도 이미지 생성
                    map_png = build_points_map_png(points_list)
                    
                    # PDF 생성
                    pdf_path = build_lease_offer_pdf(
                        out_path="outputs/Daechi_Offer.pdf",
                        title=f"대치1동 {user_persona} 맞춤 제안서",
                        subtitle="2026년 학군 프리미엄 분석 리포트",
                        badge="SSS등급",
                        jeonse_text="16.5억 (52%)",
                        wolse_text="10억 / 280만원",
                        landlord_pitch="안정적인 전세 수요와 높은 학군 프리미엄으로 자산 가치 방어가 탁월합니다.",
                        consult_script="고객님, 이 물건은 대치초-대청중 라인의 핵심 매물로, 지금 잡으셔야 합니다.",
                        shorts_script="대치동 학군지, 지금이 기회입니다! 34평 로얄동 매물!",
                        summary_text=get_sss_side_message(user_persona).replace("<br/>", "\n"),
                        map_png_bytes=map_png
                    )
                    
                    # 다운로드 버튼
                    with open(pdf_path, "rb") as f:
                        st.download_button(
                            label="📥 다운로드",
                            data=f,
                            file_name="Daechi_Lease_Offer.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    st.success("✅ PDF 생성 완료!")
                    
                except Exception as e:
                    st.error(f"❌ PDF 생성 실패: {e}")
                    st.info("💡 outputs 폴더가 없으면 자동으로 생성됩니다.")
    
    with btn_col2:
        # 대치특성 상단 이동
        if st.button("⬆️ 대치특성 상단", key="go_top_btn", use_container_width=True):
            scroll_to_top()
            st.rerun()
    
    with btn_col3:
        # 추천매물 페이지 이동
        if st.button("🏠 추천매물", key="go_props_btn", use_container_width=True):
            st.session_state.menu_index = 1
            st.rerun()
    
    with btn_col4:
        # AI 챗봇 페이지 이동
        if st.button("💬 AI 챗봇", key="go_chat_btn", use_container_width=True):
            st.session_state["manual_nav_target"] = "💬 AI 챗봇"
            st.rerun()

    # 시연 환경 초기화 버튼 (별도 줄)
    st.markdown("---")
    st.markdown("### 🔄 시연 환경 관리")
    
    reset_col1, reset_col2, reset_col3 = st.columns([2, 4, 2])
    with reset_col2:
        if st.button("📋 시연 환경 초기화 (Reset All)", key="reset_all_btn", use_container_width=True, type="secondary"):
            # 세션 상태 초기화
            keys_to_clear = [k for k in st.session_state.keys()]
            for k in keys_to_clear:
                del st.session_state[k]
            st.success("✅ 초기화 완료!")
            st.rerun()

    # 하단 네비게이션
    render_bottom_nav("🎓 대치1동 특성")
