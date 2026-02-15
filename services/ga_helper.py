import streamlit as st
from services.ga4_tracking import ga_event

def track_once(event_name, params=None):
    key = f"ga_sent_{event_name}"
    if not st.session_state.get(key):
        ga_event(event_name, params or {})
        st.session_state[key] = True

def track(event_name, params=None):
    ga_event(event_name, params or {})
