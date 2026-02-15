from __future__ import annotations
import pandas as pd
import numpy as np

class MatchingEngine:
    """
    AI Property Matching Engine (Phase 3)
    Matches user profile to available properties using semantic logic.
    """
    
    def __init__(self, property_data_path="mlops/data/properties.csv"):
        try:
            self.properties = pd.read_csv(property_data_path)
            # Ensure index if needed
        except FileNotFoundError:
            print(f"Properties file not found at {property_data_path}, using empty dataframe.")
            self.properties = pd.DataFrame()
            
    def match_user_request(self, user_profile: dict, top_k=5) -> pd.DataFrame:
        """
        Rank properties for a user based on profile.
        
        Args:
            user_profile: {
                "budget_max": 350000,
                "preferred_area": ["대치동", "도곡동"],
                "min_size_py": 30,
                "school_priority_weight": 0.8, # 0.0 ~ 1.0
                "investment_focus": True
            }
        """
        if self.properties.empty:
            return pd.DataFrame()
            
        df = self.properties.copy()
        
        # 1. Hard Filters (Budget, Area, Size)
        # Budget
        budget_limit = user_profile.get("budget_max", 10000000)
        df = df[df['market_price'] <= budget_limit]
        
        # Area
        areas = user_profile.get("preferred_area", [])
        if areas:
            df = df[df['dong'].isin(areas)]
            
        # Size (py)
        # Assuming we have numeric size or parse 'size_type'
        # Simple string comparison for now if '30py' format
        min_size = user_profile.get("min_size_py", 0)
        # "30py" -> 30
        df['size_num'] = df['size_type'].astype(str).str.extract(r'(\d+)').astype(float)
        df = df[df['size_num'] >= min_size]
        
        if df.empty:
            return pd.DataFrame()
        
        # 2. Scoring (Soft Matching)
        # Base Score = (Budget proximity) * 0.3 + (School Score * Priority) * 0.4 + (Undervalued Score * Investment Weight) * 0.3
        
        # Normalize budget efficiency: Closer to budget is better? Or lower is better? 
        # Usually for buyers, lower is better, but closer to max budget often means better quality.
        # Let's say: Value for Money logic on 'undervalued_score' handles price efficiency.
        
        # Investment Weight
        inv_weight = 0.5 if user_profile.get("investment_focus", False) else 0.2
        school_weight = user_profile.get("school_priority_weight", 0.5)
        
        # Calculate Match Score
        # Undervalued Score is 0-100
        # School Score is 1-5 -> Normalize to 0-100 (x20)
        
        df['norm_school'] = df['school_score'] * 20
        
        # Weighted Sum
        df['match_score'] = (
            (df['undervalued_score'] * inv_weight) + 
            (df['norm_school'] * school_weight)
        )
        
        # Sort desc
        results = df.sort_values(by='match_score', ascending=False).head(top_k)
        
        return results[['property_id', 'dong', 'market_price', 'undervalued_score', 'match_score']]

if __name__ == "__main__":
    # Test Matching
    engine = MatchingEngine("mlops/data/properties.csv") # Assuming generated
    profile = {
        "budget_max": 400000, # 40억
        "preferred_area": ["대치동"],
        "min_size_py": 30,
        "school_priority_weight": 0.9,
        "investment_focus": True
    }
    
    print("User Profile:", profile)
    matches = engine.match_user_request(profile)
    print("\nTop Matches:\n", matches)
