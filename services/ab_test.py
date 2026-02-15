import streamlit as st
import random
from services.ga4_tracking import ga_event

def get_variant(test_name: str, traffic_split: float = 0.5) -> str:
    """
    Returns 'A' or 'B' for the given test_name based on user session.
    Persists the assignment in session_state so the user sees the same variant during their session.
    """
    key = f"ab_test_{test_name}"
    
    if key not in st.session_state:
        # Assign variant
        # In a real app, you might use a hash of the user_id to ensure consistency across sessions
        if random.random() < traffic_split:
            st.session_state[key] = "A"
        else:
            st.session_state[key] = "B"
            
    return st.session_state[key]

def track_exposure(test_name: str):
    """
    Sends an 'ab_exposure' event to GA4.
    Should be called when the user actually sees the variant element.
    """
    variant = st.session_state.get(f"ab_test_{test_name}")
    if variant:
        # Check if we already tracked exposure for this test in this rerun to avoid duplicate events
        # (Streamlit reruns the whole script on interaction)
        exposure_key = f"ab_tracked_{test_name}"
        if exposure_key not in st.session_state:
            ga_event("ab_exposure", {
                "test_name": test_name,
                "variant": variant
            })
            st.session_state[exposure_key] = True
