import unittest
import pandas as pd
import numpy as np
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from undervalued_model import UndervaluedScoreModel
from matching_model import MatchingEngine
from data_generator import generate_sample_properties

class TestAIModels(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Generate data once
        cls.data = generate_sample_properties(100)
        
    def test_01_data_generation(self):
        self.assertEqual(len(self.data), 100)
        self.assertTrue('undervalued_score' in self.data.columns)
        
    def test_02_model_training(self):
        model = UndervaluedScoreModel()
        metrics = model.train(self.data)
        self.assertTrue('mae' in metrics)
        self.assertGreater(metrics['r2'], 0.5) # Should pass simple linear relation
        
        # Test Prediction
        sample = self.data.iloc[:5].copy()
        pred = model.predict(sample)
        self.assertEqual(len(pred), 5)
        
    def test_03_ai_matching(self):
        # Mock properties since file might not exist yet in test env
        import os
        if not os.path.exists("mlops/data/properties.csv"):
            self.data.to_csv("mlops/data/properties.csv", index=False)
            
        matcher = MatchingEngine("mlops/data/properties.csv")
        profile = {
            "budget_max": 250000, # 25억
            "preferred_area": ["대치동"],
            "min_size_py": 20
        }
        
        results = matcher.match_user_request(profile)
        # Should return dataframe
        self.assertIsInstance(results, pd.DataFrame)
        if not results.empty:
            self.assertTrue('match_score' in results.columns)
            self.assertTrue((results['market_price'] <= 250000).all())

if __name__ == "__main__":
    unittest.main()
