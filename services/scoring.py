import streamlit as st
import datetime
from services.ga4_tracking import ga_event

# --------------------------------------------------------------------------------
# Constants & Weights (Architecture Spec)
# --------------------------------------------------------------------------------
WEIGHTS = {
    "view_property_cnt": 2,
    "return_within_3d": 6,
    "avg_detail_time_sec_factor": 2, # (time / 30) * 2
    "lead_click": 8,
    "lead_submit": 12,
    "verification_actions": 3,
}

CUTOFF_A = 25
CUTOFF_B = 15

# --------------------------------------------------------------------------------
# Session Initialization
# --------------------------------------------------------------------------------
def init_score_session():
    defaults = {
        "score_view_property_cnt": 0,
        "score_lead_click": 0,
        "score_lead_submit": 0,
        "score_verification_actions": 0,
        "score_total_detail_time_sec": 0,
        "score_last_visit": str(datetime.date.today()),
        "score_is_returning": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    # Check 'return_within_3d' logic
    # In a real app with persistent user auth, we compare last login. 
    # Here, we simulate with a cookie or local storage if possible, but session_state resets on refresh.
    # For demo, we just use a flag or assume new users unless specified.
    pass

# --------------------------------------------------------------------------------
# Action Loggers
# --------------------------------------------------------------------------------

def log_view_property(property_id: str):
    init_score_session()
    st.session_state["score_view_property_cnt"] += 1
    # Check if duplicate or new property view? For now, simplistic count.
    ga_event("view_property", {"property_id": property_id})
    _update_score()

def log_lead_click(lead_type: str, property_id: str):
    init_score_session()
    st.session_state["score_lead_click"] += 1
    ga_event("lead_click", {"lead_type": lead_type, "property_id": property_id})
    _update_score()

def log_lead_submit(property_id: str, form_data: dict):
    init_score_session()
    st.session_state["score_lead_submit"] += 1
    ga_event("lead_submit", {"property_id": property_id, **form_data})
    _update_score()

def log_verification_action(action_name: str):
    """Logs actions like map zoom, tax calculalator use, loan inquiry."""
    init_score_session()
    st.session_state["score_verification_actions"] += 1
    ga_event("verification_action", {"action_name": action_name})
    _update_score()

def log_time_on_page(seconds: int):
    init_score_session()
    st.session_state["score_total_detail_time_sec"] += seconds
    _update_score()

# --------------------------------------------------------------------------------
# Calculation
# --------------------------------------------------------------------------------

def calculate_score():
    init_score_session()
    s = st.session_state

    # 1. Basic Counts
    score = (s["score_view_property_cnt"] * WEIGHTS["view_property_cnt"])
    score += (s["score_lead_click"] * WEIGHTS["lead_click"])
    score += (s["score_lead_submit"] * WEIGHTS["lead_submit"])
    score += (s["score_verification_actions"] * WEIGHTS["verification_actions"])

    # 2. Time Factor (avg_detail_time_sec / 30 * 2)
    # Simplified: (total_time / 30) * 2
    time_points = (s["score_total_detail_time_sec"] / 30) * WEIGHTS["avg_detail_time_sec_factor"]
    score += time_points

    # 3. Returning User (Mock)
    if s["score_is_returning"]:
        score += WEIGHTS["return_within_3d"]

    return round(score, 1)

def get_lead_grade(score):
    if score >= CUTOFF_A:
        return "A (VIP)"
    elif score >= CUTOFF_B:
        return "B (Potential)"
    else:
        return "C (General)"

def _update_score():
    current_score = calculate_score()
    grade = get_lead_grade(current_score)
    st.session_state["current_lead_score"] = current_score
    st.session_state["current_lead_grade"] = grade
    
    # Store for UI or Debug
    ga_event("score_update", {"score": float(current_score), "grade": grade})
