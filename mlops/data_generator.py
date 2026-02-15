import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

def generate_sample_properties(n_samples=1000):
    """
    Generate sample real estate property data for Daechi-dong area.
    """
    districts = ["강남구", "서초구", "송파구"]
    dong_list = ["대치동", "도곡동", "개포동", "반포동", "잠실동"]
    
    data = []
    
    base_prices = {
        "20py": 230000, # 23억
        "30py": 320000, # 32억
        "40py": 480000  # 48억
    }
    
    for i in range(n_samples):
        district = random.choice(districts)
        dong = random.choice(dong_list)
        
        # Py (Size) - 20, 30, 40
        size_type = random.choice(["20py", "30py", "40py"])
        area_sqm = {
            "20py": random.uniform(59, 65),
            "30py": random.uniform(84, 85),
            "40py": random.uniform(110, 120)
        }[size_type]
        
        # Price base + random variation
        base = base_prices[size_type]
        price_variation = random.uniform(-0.15, 0.15) # +/- 15%
        market_price = base * (1 + price_variation)
        
        # Jeonse ratio (50% ~ 60%)
        jeonse_ratio = random.uniform(0.50, 0.60)
        jeonse_price = market_price * jeonse_ratio
        
        # School score (1~5)
        school_score = random.randint(3, 5) if dong == "대치동" else random.randint(1, 4)
        
        # Subway distance (m)
        subway_dist = random.randint(100, 1500)
        
        # Floor
        floor = random.randint(1, 35)
        
        # Generate ID
        prop_id = f"PROP_{i:04d}"
        
        data.append({
            "property_id": prop_id,
            "district": district,
            "dong": dong,
            "size_type": size_type,
            "area_sqm": round(area_sqm, 2),
            "floor": floor,
            "market_price": round(market_price, 0), # 만원 단위
            "jeonse_price": round(jeonse_price, 0),
            "jeonse_ratio": round(jeonse_ratio, 2),
            "school_score": school_score,
            "subway_distance_m": subway_dist,
            "contract_date": (datetime.now() - timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d")
        })
        
    df = pd.DataFrame(data)
    
    # Calculate 'Undervalued Score' (Synthetic Target)
    # Logic: Higher Score = More Undervalued (High jeonse ratio, low price relative to avg, high school score)
    # This is a dummy logic for training
    df['avg_price_by_size'] = df.groupby('size_type')['market_price'].transform('mean')
    df['price_diff_percent'] = (df['avg_price_by_size'] - df['market_price']) / df['avg_price_by_size']
    
    # Score = (Price Diff %) * 50 + (School Score) * 10 + (Jeonse Ratio) * 20
    # Normalize to 0-100
    uuid_score = (df['price_diff_percent'] * 100 * 0.5) + (df['school_score'] * 10) + (df['jeonse_ratio'] * 100 * 0.2)
    # Add noise
    uuid_score += np.random.normal(0, 5, n_samples)
    
    # Clip 0-100
    df['undervalued_score'] = uuid_score.clip(0, 100).round(1)
    
    return df

if __name__ == "__main__":
    df = generate_sample_properties(1000)
    print(f"Generated {len(df)} sample properties.")
    print(df.head())
    
    # Save to CSV
    import os
    if not os.path.exists("mlops/data"):
        os.makedirs("mlops/data")
    df.to_csv("mlops/data/sample_properties.csv", index=False)
    print("Saved to mlops/data/sample_properties.csv")
