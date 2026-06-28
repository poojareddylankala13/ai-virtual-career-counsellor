import json
import os
from typing import Dict, List, Any
from config import CAREER_DATASET_PATH
from utils.nltk_preprocessor import NLTKPreprocessor


class CareerRecommender:
    """
    Evaluates user profiles against the career dataset to compute scores,
    match percentages, existing/missing skills, and custom recommendation reasons.
    """

    def __init__(self, dataset_path: str = CAREER_DATASET_PATH):
        self.dataset_path = dataset_path
        self.preprocessor = NLTKPreprocessor()
        self.careers = self._load_dataset()

    def _load_dataset(self) -> List[Dict[str, Any]]:
        """Loads the career list from the JSON dataset."""
        if not os.path.exists(self.dataset_path):
            # Fallback empty list if dataset doesn't exist
            return []
        try:
            with open(self.dataset_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading career dataset: {e}")
            return []

    def get_all_domains(self) -> List[str]:
        """Returns a sorted list of unique domains available in the dataset."""
        return sorted(list(set(c["domain"] for c in self.careers)))

    def get_all_skills(self) -> List[str]:
        """Gathers a flat list of all unique skills across all careers."""
        skills = set()
        for c in self.careers:
            skills.update(c.get("required_skills", []))
        return sorted(list(skills))

    def recommend(self, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Calculates recommendation scores for all career options.
        Profile keys expected:
          - preferred_domain: str
          - skills: List[str] or str
          - interests: List[str] or str
          - highest_qualification: str
          - current_degree: str
          - career_goal: str
        """
        if not self.careers:
            return []

        # Clean/Normalize profile fields
        user_domain = str(profile.get("preferred_domain", "")).strip()
        user_skills = profile.get("skills", [])
        if isinstance(user_skills, str):
            user_skills = [s.strip() for s in user_skills.replace(",", " ").split() if s.strip()]
        
        user_interests = profile.get("interests", [])
        if isinstance(user_interests, str):
            user_interests = [i.strip() for i in user_interests.replace(",", " ").split() if i.strip()]

        user_degree = str(profile.get("current_degree", "")).strip().lower()
        user_qualification = str(profile.get("highest_qualification", "")).strip().lower()

        # Clean user skills and interests using NLTK preprocessor for accurate matching
        clean_user_skills = set(self.preprocessor.preprocess(" ".join(user_skills)))
        clean_user_interests = set(self.preprocessor.preprocess(" ".join(user_interests)))

        recommendations = []

        for career in self.careers:
            score = 0
            max_possible_score = 100

            career_name = career["name"]
            career_domain = career["domain"]
            career_skills = career.get("required_skills", [])
            career_academic = [p.lower() for p in career.get("academic_path", [])]

            # 1. Domain Match (Max: 40 points)
            domain_matched = False
            if user_domain.lower() == career_domain.lower():
                score += 40
                domain_matched = True
            else:
                # If preferred domain is blank or different, check if user's interests match the domain
                clean_career_domain = self.preprocessor.preprocess(career_domain)
                if any(ci in clean_career_domain for ci in clean_user_interests):
                    score += 25
                    domain_matched = True

            # 2. Skills Match (Max: 40 points)
            matching_skills = []
            missing_skills = []

            for s in career_skills:
                # Lemmatize career skill
                clean_c_skill = " ".join(self.preprocessor.preprocess(s))
                
                # Check overlap
                is_match = False
                for us in clean_user_skills:
                    if us in clean_c_skill or clean_c_skill in us:
                        is_match = True
                        break
                
                if is_match:
                    matching_skills.append(s)
                else:
                    missing_skills.append(s)

            if career_skills:
                overlap_ratio = len(matching_skills) / len(career_skills)
                score += int(overlap_ratio * 40)

            # 3. Academic Pathway Fit (Max: 20 points)
            academic_matched = False
            for path in career_academic:
                if (user_degree and user_degree in path) or (user_qualification and user_qualification in path):
                    score += 20
                    academic_matched = True
                    break

            if not academic_matched and (user_degree or user_qualification):
                # Mild score increase if there are common words (e.g. Science, Commerce, Arts)
                user_ac_tokens = self.preprocessor.preprocess(f"{user_degree} {user_qualification}")
                career_ac_tokens = self.preprocessor.preprocess(" ".join(career_academic))
                if any(token in career_ac_tokens for token in user_ac_tokens):
                    score += 10

            # Match Percentage
            match_percentage = min(100, int((score / max_possible_score) * 100))

            # Don't recommend careers with negligible score (unless no qualifications/skills are set)
            if match_percentage < 15 and (clean_user_skills or clean_user_interests):
                continue

            # Create personalized recommendation reason
            reason_parts = []
            if domain_matched and user_domain:
                reason_parts.append(f"It aligns perfectly with your preferred domain of '{career_domain}'")
            elif domain_matched:
                reason_parts.append(f"Your stated interests align well with the {career_domain} sector")

            if matching_skills:
                # Limit list of matched skills to 3 to keep reason concise
                matched_sample = ", ".join(matching_skills[:3])
                reason_parts.append(f"you already have foundation skills in {matched_sample}")

            if academic_matched:
                reason_parts.append("your academic background meets the standard qualification path")

            if not reason_parts:
                reason_parts.append("it matches general career avenues based on your profile inputs")

            recommendation_reason = "This career is recommended because " + "; ".join(reason_parts) + "."

            # Prepare output object
            rec_detail = {
                "name": career_name,
                "domain": career_domain,
                "description": career.get("description", ""),
                "match_percentage": match_percentage,
                "reason": recommendation_reason,
                "required_skills": career_skills,
                "user_existing_skills": matching_skills,
                "skills_to_improve": missing_skills,
                "learning_roadmap": career.get("learning_roadmap", []),
                "recommended_certifications": career.get("recommended_certifications", []),
                "recommended_courses": career.get("recommended_courses", []),
                "suggested_projects": career.get("suggested_projects", []),
                "growth": career.get("growth", ""),
                "future_scope": career.get("future_scope", ""),
                "salary_range": career.get("salary_range", {"entry": "N/A", "mid": "N/A", "senior": "N/A"})
            }
            recommendations.append(rec_detail)

        # Sort recommendations by match percentage desc
        recommendations.sort(key=lambda x: x["match_percentage"], reverse=True)
        return recommendations
