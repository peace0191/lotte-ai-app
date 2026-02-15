import streamlit as st
import requests
import uuid
import time
import hmac

# Initialize session state for client_id if not exists
def get_client_id():
    if "client_id" not in st.session_state:
        st.session_state["client_id"] = str(uuid.uuid4())
    return st.session_state["client_id"]

def ga_event(name: str, params: dict):
    """
    Sends a GA4 event via Measurement Protocol.
    Requirements:
    - st.secrets["GA_MEASUREMENT_ID"]
    - st.secrets["GA_API_SECRET"]
    """
    # Check if secrets exist
    if "GA_MEASUREMENT_ID" not in st.secrets or "GA_API_SECRET" not in st.secrets:
        # Fail silently or log warning
        print("GA4 Secrets not found. Event not sent.")
        return 400

    ga_measurement_id = st.secrets["GA_MEASUREMENT_ID"]
    ga_api_secret = st.secrets["GA_API_SECRET"]

    # Merge with global user properties if available
    base_params = {
        "session_id": st.session_state.get("session_id", str(uuid.uuid4())),
        "engagement_time_msec": "100", # Default placebo
    }
    
    # Add common context from session state (architecture req)
    for k in ["property_type", "price_band", "region", "source_intent", "agent_id"]:
        if k in st.session_state:
            base_params[k] = st.session_state[k]
            
    # Merge passed params (override base)
    final_params = {**base_params, **params}

    url = "https://www.google-analytics.com/mp/collect"
    payload = {
        "client_id": get_client_id(),
        "events": [{"name": name, "params": final_params}],
    }
    
    try:
        r = requests.post(
            url,
            params={"measurement_id": ga_measurement_id, "api_secret": ga_api_secret},
            json=payload,
            timeout=2,
        )
        return r.status_code
    except Exception as e:
        # print(f"GA4 Event Send Error: {e}")
        return 500

def inject_ga():
    """
    Injects the generic GA4 pageview script into the Streamlit app.
    """
    if "GA_MEASUREMENT_ID" in st.secrets:
        ga_measurement_id = st.secrets["GA_MEASUREMENT_ID"]
        components_html = f"""
        <!-- Google tag (gtag.js) -->
        <script async src="https://www.googletagmanager.com/gtag/js?id={ga_measurement_id}"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){{dataLayer.push(arguments);}}
          gtag('js', new Date());
          gtag('config', '{ga_measurement_id}', {{ 'send_page_view': true }});
        </script>
        """
        st.components.v1.html(components_html, height=0)
