from __future__ import annotations
import os
import json
import logging
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Metric, Dimension, FilterExpression, Filter
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Import secrets/config
# Note: In Streamlit production, use st.secrets.
# For local script execution, you might need a local .env or direct JSON key file.

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_ga4_client():
    """
    Initialize GA4 client.
    Requires GOOGLE_APPLICATION_CREDENTIALS environment variable or explicit credentials.
    In Streamlit Cloud, you would use st.secrets["gcp_service_account"].
    """
    try:
        # Check if running in Streamlit Cloud environment to use secrets
        if "gcp_service_account" in st.secrets:
            # Construct credentials object from secrets
            from google.oauth2 import service_account
            creds = service_account.Credentials.from_service_account_info(
                st.secrets["gcp_service_account"]
            )
            return BetaAnalyticsDataClient(credentials=creds)
        else:
            # Local fallback (needs JSON key file path in env)
            return BetaAnalyticsDataClient()
    except Exception as e:
        logger.error(f"Failed to initialize GA4 client: {e}")
        return None

def fetch_funnel_report(property_id: str):
    """
    Fetches the funnel report for a specific property (or overall).
    """
    client = get_ga4_client()
    if not client:
        return None

    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date="28daysAgo", end_date="yesterday")],
        dimensions=[Dimension(name="eventName")],
        metrics=[Metric(name="eventCount"), Metric(name="totalUsers")],
        dimension_filter=FilterExpression(
            filter=Filter(
                field_name="eventName",
                in_list_filter=Filter.InListFilter(
                    values=["session_start", "view_property", "lead_click", "lead_submit", "visit_booked", "contract"],
                    case_sensitive=False
                )
            )
        )
    )

    try:
        response = client.run_report(request)
        data = []
        for row in response.rows:
            data.append({
                "Event Name": row.dimension_values[0].value,
                "Event Count": int(row.metric_values[0].value),
                "Users": int(row.metric_values[1].value)
            })
        return pd.DataFrame(data)
    except Exception as e:
        logger.error(f"Error fetching report: {e}")
        return None

def generate_weekly_insight(df: pd.DataFrame):
    """
    Generates a simple text insight based on the funnel dataframe.
    """
    if df is None or df.empty:
        return "데이터가 부족하여 분석할 수 없습니다."

    # Sort/Order by funnel steps logic if needed, but for now simple summary
    total_sessions = df[df["Event Name"] == "session_start"]["Event Count"].sum()
    leads = df[df["Event Name"] == "lead_submit"]["Event Count"].sum()
    
    conversion_rate = 0
    if total_sessions > 0:
        conversion_rate = (leads / total_sessions) * 100

    insight = f"""
    [주간 퍼널 요약]
    - 총 세션: {total_sessions}
    - 리드 제출: {leads}
    - 전환율: {conversion_rate:.2f}%
    
    [제언]
    전환율이 1% 미만일 경우 상세 페이지의 CTA 문구를 변경하거나 
    A/B 테스트('trust_badges_v1')의 B안(신뢰 뱃지) 도입을 적극 검토하십시오.
    """
    return insight

if __name__ == "__main__":
    # Example usage (requires property ID setup)
    PROPERTY_ID = os.getenv("GA4_PROPERTY_ID", "YOUR_PROPERTY_ID")
    if PROPERTY_ID == "YOUR_PROPERTY_ID":
        print("Please set GA4_PROPERTY_ID environment variable.")
    else:
        df = fetch_funnel_report(PROPERTY_ID)
        if df is not None:
            print(df)
            print("-" * 30)
            print(generate_weekly_insight(df))
