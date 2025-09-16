# score/tests.py
from django.test import TestCase
from .scoring import calculate_rule_score

class RuleScoringTestCase(TestCase):
    
    def setUp(self):
        """Set up a standard offer for all test cases."""
        self.offer = {
            "name": "AI Outreach Automation",
            "value_props": ["24/7 outreach", "6x more meetings"],
            "ideal_use_cases": ["B2B SaaS mid-market", "sales teams"]
        }

    def test_perfect_lead_max_score(self):
        """
        Test a lead that meets all criteria and should receive the maximum rule score (50).
        - Decision Maker (+20)
        - Exact Industry Match (+20)
        - Complete Data (+10)
        """
        perfect_lead = {
            "name": "Ava Patel",
            "role": "Head of Growth",
            "company": "FlowMetrics",
            "industry": "B2B SaaS",
            "location": "San Francisco",
            "linkedin_bio": "Leading growth strategies."
        }
        
        expected_score = 50 # 20 (role) + 20 (industry) + 10 (complete)
        actual_score = calculate_rule_score(perfect_lead, self.offer)
        
        self.assertEqual(actual_score, expected_score)
        print("\n✅ test_perfect_lead_max_score: Passed")

    def test_influencer_adjacent_industry(self):
        """
        Test a lead who is an influencer in an adjacent industry.
        - Influencer (+10)
        - Adjacent Industry (+10)
        - Complete Data (+10)
        """
        influencer_lead = {
            "name": "Liam Chen",
            "role": "Senior Software Engineer",
            "company": "DataWeave Inc.",
            "industry": "General SaaS", # Contains "SaaS", an adjacent keyword
            "location": "New York",
            "linkedin_bio": "Building scalable data pipelines."
        }
        
        expected_score = 30 # 10 (role) + 10 (industry) + 10 (complete)
        actual_score = calculate_rule_score(influencer_lead, self.offer)
        
        self.assertEqual(actual_score, expected_score)
        print("✅ test_influencer_adjacent_industry: Passed")

    def test_incomplete_data(self):
        """
        Test a lead with incomplete data, who should not get the completeness bonus.
        - Decision Maker (+20)
        - Exact Industry Match (+20)
        - Incomplete Data (+0)
        """
        incomplete_lead = {
            "name": "Sophia Rodriguez",
            "role": "Marketing Manager",
            "company": "Innovate Corp",
            "industry": "sales teams",
            "location": "London",
            "linkedin_bio": "" # Bio is empty, so data is incomplete
        }
        
        expected_score = 40 # 20 (role) + 20 (industry) + 0 (incomplete)
        actual_score = calculate_rule_score(incomplete_lead, self.offer)
        
        self.assertEqual(actual_score, expected_score)
        print("✅ test_incomplete_data: Passed")

    def test_no_match_lead(self):
        """
        Test a lead who matches no criteria and should score 0.
        - Irrelevant Role (+0)
        - Irrelevant Industry (+0)
        - Complete Data (+10) -> Let's test for 0 score with irrelevant role/industry
        """
        no_match_lead = {
            "name": "John Doe",
            "role": "Student",
            "company": "University",
            "industry": "Education",
            "location": "Anytown",
            "linkedin_bio": "Learning new things."
        }
        
        # This lead should only get points for data completeness if we were testing for 10.
        # But for a true "no match", let's assume we are testing for 0 points from role and industry.
        # The function gives 10 for complete data, so we test that this lead gets ONLY 10.
        expected_score = 10 # 0 (role) + 0 (industry) + 10 (complete)
        actual_score = calculate_rule_score(no_match_lead, self.offer)
        
        self.assertEqual(actual_score, expected_score)
        print("✅ test_no_match_lead: Passed")