import os
import streamlit as st

def load_config():
    """
    Load configuration from streamlit secrets into environment variables
    for compatibility with existing service code.
    """
    
    # Define mapping from secrets structure to environment variables
    # Format: ("ENV_VAR_NAME", access_function)
    mappings = {
        "SOLAPI_API_KEY": lambda s: s.get("solapi", {}).get("api_key", ""),
        "SOLAPI_API_SECRET": lambda s: s.get("solapi", {}).get("api_secret", ""),
        "SOLAPI_SENDER": lambda s: s.get("solapi", {}).get("sender_phone", ""),
        
        "KAKAO_JS_KEY": lambda s: s.get("kakao", {}).get("js_key", ""),
        
        "OTP_PEPPER": lambda s: s.get("auth", {}).get("otp_pepper", "DEV_DEFAULT_PEPPER"),
        "ADMIN_PHONES": lambda s: s.get("auth", {}).get("admin_phones", ""),
        
        "APP_BASE_URL": lambda s: s.get("app", {}).get("base_url", ""),
        "APP_DETAIL_PATH_PREFIX": lambda s: s.get("app", {}).get("detail_path_prefix", "/p"),

        "KAKAO_BIZMSG_BASE_URL": lambda s: s.get("kakao_bizmsg", {}).get("base_url", "bizmsg-web.kakaoenterprise.com"),
        "KAKAO_BIZMSG_CLIENT_ID": lambda s: s.get("kakao_bizmsg", {}).get("client_id", ""),
        "KAKAO_BIZMSG_CLIENT_SECRET": lambda s: s.get("kakao_bizmsg", {}).get("client_secret", ""),
        "KAKAO_BIZMSG_SENDER_KEY": lambda s: s.get("kakao_bizmsg", {}).get("sender_key", ""),
        "KAKAO_BIZMSG_SENDER_NO": lambda s: s.get("kakao_bizmsg", {}).get("sender_no", ""),
        "KAKAO_BIZMSG_TEMPLATE_REVIEW": lambda s: s.get("kakao_bizmsg", {}).get("template_review", ""),
    }
    for env_key, getter in mappings.items():
        # Only set if not already set in OS environment (OS env takes precedence for securities)
        if not os.environ.get(env_key):
            try:
                val = getter(st.secrets)
                if val:
                    os.environ[env_key] = str(val)
            except Exception:
                pass # Secrets might be missing or different structure

def get_config() -> dict:
    """
    Returns a unified configuration dictionary (env vars + secrets as fallback).
    This function mimics dictionary access (e.g. cfg.get('key'))
    but actually prioritizing os.environ.
    But for deeper keys like 'app.base_url', we just return a flat dict or use st.secrets structure.
    For simplicity here, we return a dict that allows dot notation access via get().
    Actually, let's keep it simple: return st.secrets but patched with env vars if needed.
    Wait, the cleanest way for this project is just to rely on st.secrets as source of truth
    for structure, but we promoted keys to env vars.
    
    Let's return a simple wrapper around st.secrets for now.
    """
    # For now, just return st.secrets wrapper that might be safer
    try:
        return st.secrets
    except:
        return {}

# Run on import
load_config()
