src = open("app.py","r",encoding="utf-8").read()
func = """
def _render_customer_management_panel():
    import pandas as _pd, random as _rnd
    from datetime import datetime as _dt, timedelta as _td
    _kc = st.columns(5)
    for _i,(_num,_label,_color) in enumerate([
        ("4,218","전체 고객","#60a5fa"),("1,847","매수 희망","#34d399"),
        ("1,203","임차 희망","#c084fc"),("891","매도/임대","#fbbf24"),("277","계약 완료","#f87171"),
    ]):
        _kc[_i].markdown(f'<div style="background:rgba(30,41,59,0.9);border:1px solid rgba(255,255,255,0.15);border-radius:8px;padding:12px;text-align:center;"><div style="font-size:1.4rem;font-weight:700;color:{_color};">{_num}</div><div style="font-size:0.72rem;color:#94a3b8;">{_label}</div></div>',unsafe_allow_html=True)
    st.markdown("<div style='height:8px'></div>",unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns([2,2,3,1.5])
    _ct = c1.selectbox("고객유형",["전체","매수희망","임차희망","매도/임대","계약완료"],key="cm_type")
    _cd = c2.selectbox("거래유형",["전체","매매","전세","월세"],key="cm_deal")
    _kw = c3.text_input("검색어",placeholder="이름, 연락처, 단지명...",key="cm_kw")
    c4.markdown("<div style='height:27px'></div>",unsafe_allow_html=True)
    c4.button("검색",use_container_width=True,type="primary",key="cm_search")
    _rnd.seed(7); _base=_dt(2026,1,1)
    _nm=["이상수","김민준","박서연","최도윤","정유진","강민지","윤하은","장현우","김은경","이지은","박준혁","최수아"]
    _dl=["매수희망","임차희망","매도/임대","계약완료"]
    _cx=["래미안대치팰리스","대치SK뷰","대치아이파크","은마아파트","시그니엘레지던스"]
    _rows=[]
    for _i in range(40):
        _tp=_rnd.choice(_dl); _b=_rnd.randint(8,65)
        _rows.append({"등록일":(_base+_td(days=_rnd.randint(0,60))).strftime("%Y-%m-%d"),
            "이름":_rnd.choice(_nm),"연락처":f"010-{_rnd.randint(1000,9999)}-{_rnd.randint(1000,9999)}",
            "고객유형":_tp,"희망단지":_rnd.choice(_cx),"거래유형":_rnd.choice(["매매","전세","월세"]),
            "희망예산(억)":f"{_b}~{_b+5}","입주희망일":(_base+_td(days=_rnd.randint(30,180))).strftime("%Y-%m-%d"),
            "AI매칭점수":f"{_rnd.randint(72,99)}%","상태":_rnd.choice(["대기중","상담완료","매칭완료","계약진행","완료"]),
            "메모":_rnd.choice(["학군 중요","즉시입주","주차필수","대출활용","급함"])})
    _df=_pd.DataFrame(_rows)
    if _kw: _df=_df[_df["이름"].str.contains(_kw,na=False)|_df["희망단지"].str.contains(_kw,na=False)]
    if _ct!="전체": _df=_df[_df["고객유형"]==_ct]
    if _cd!="전체": _df=_df[_df["거래유형"]==_cd]
    ab1,ab2=st.columns([2,6])
    with ab1:
        if st.button("고객 등록",use_container_width=True,key="cm_add"):
            st.session_state["cm_show_form"]=True
    _csv=_df.to_csv(index=False,encoding="utf-8-sig").encode("utf-8-sig")
    ab2.download_button("엑셀저장",data=_csv,file_name="고객목록.csv",mime="text/csv",key="cm_dl")
    def _sc(v):
        m={"대기중":"background:rgba(59,130,246,0.25);color:#93c5fd;font-weight:bold;",
           "상담완료":"background:rgba(16,185,129,0.25);color:#6ee7b7;font-weight:bold;",
           "매칭완료":"background:rgba(250,204,21,0.25);color:#fde68a;font-weight:bold;",
           "계약진행":"background:rgba(245,158,11,0.25);color:#fcd34d;font-weight:bold;",
           "완료":"background:rgba(100,116,139,0.2);color:#94a3b8;"}
        return m.get(v,"")
    st.dataframe(_df.style.applymap(_sc,subset=["상태"]),use_container_width=True,height=400)
    if st.session_state.get("cm_show_form"):
        st.markdown("---"); st.markdown("#### 신규 고객 등록")
        with st.form("cm_form"):
            r1,r2,r3=st.columns(3)
            _fn=r1.text_input("이름"); r2.text_input("연락처",placeholder="010-0000-0000")
            r3.selectbox("고객유형",["매수희망","임차희망","매도/임대"])
            r4,r5,r6=st.columns(3)
            r4.text_input("희망단지"); r5.selectbox("거래유형",["매매","전세","월세"])
            r6.text_input("희망예산(억)",placeholder="30~35"); st.text_area("메모",height=70)
            if st.form_submit_button("저장",type="primary",use_container_width=True):
                st.success(f"고객 등록 완료!"); st.session_state["cm_show_form"]=False

"""
if "_render_customer_management_panel" not in src:
    src = src.replace("def _render_property_management_panel():", func + "def _render_property_management_panel():", 1)
    print("함수 추가 완료!")
else:
    print("이미 존재함")
open("app.py","w",encoding="utf-8").write(src)
print("저장 완료!")
