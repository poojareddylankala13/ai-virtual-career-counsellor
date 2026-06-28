import sys
import os
import pytest

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.recommender import CareerRecommender


def test_recommendation_logic():
    recommender = CareerRecommender()
    
    # Check that careers loaded successfully
    assert len(recommender.careers) > 0
    
    # Mock user profile
    mock_profile = {
        "preferred_domain": "Technology",
        "skills": "Python, Deep Learning, Git, SQL",
        "interests": "Coding, AI, Neural networks",
        "highest_qualification": "Bachelor's",
        "current_degree": "B.Tech in Computer Science",
        "career_goal": "Become an AI Researcher"
    }
    
    recs = recommender.recommend(mock_profile)
    
    # Recommendations should be found
    assert len(recs) > 0
    
    # The top recommended career should be related to Technology
    top_career = recs[0]
    assert top_career["domain"] == "Technology"
    assert "AI Engineer" in [r["name"] for r in recs[:3]] or "Machine Learning Engineer" in [r["name"] for r in recs[:3]]
    
    # Scores should be sorted in descending order
    percentages = [r["match_percentage"] for r in recs]
    assert percentages == sorted(percentages, reverse=True)
