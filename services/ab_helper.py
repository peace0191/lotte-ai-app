import streamlit as st
from services.ga4_tracking import ga_event
import random

def get_variant(test_name, variants=("A", "B")):
    key = f"ab_variant_{test_name}"
    if key not in st.session_state:
        st.session_state[key] = random.choice(variants)
        ga_event("ab_exposure", {
            "test_name": test_name,
            "variant": st.session_state[key]
        })
    return st.session_state[key]
