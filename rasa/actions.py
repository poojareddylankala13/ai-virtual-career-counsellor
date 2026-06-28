import os
import sys
import json
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

# Add parent directory to path to enable imports from utils/ and config
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

try:
    from config import CAREER_DATASET_PATH
    from utils.recommender import CareerRecommender
except ImportError:
    # Backup relative paths if running direct
    CAREER_DATASET_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "careers.json")
    CareerRecommender = None


class ActionBase(Action):
    """Base Action providing utility methods to query the career dataset."""
    
    def name(self) -> Text:
        return "action_base"

    def get_career_by_name(self, name: str) -> Dict[str, Any]:
        if not name:
            return {}
        try:
            with open(CAREER_DATASET_PATH, "r", encoding="utf-8") as f:
                careers = json.load(f)
                for c in careers:
                    if c["name"].lower() == name.lower():
                        return c
        except Exception as e:
            print(f"Error reading careers in action: {e}")
        return {}

    def get_active_career(self, tracker: Tracker) -> Dict[str, Any]:
        """Resolves the career that the user is currently inquiring about."""
        selected = tracker.get_slot("selected_career")
        if selected:
            career_info = self.get_career_by_name(selected)
            if career_info:
                return career_info

        # Backup: Check user message for direct career matches
        latest_message = tracker.latest_message.get("text", "").lower()
        try:
            with open(CAREER_DATASET_PATH, "r", encoding="utf-8") as f:
                careers = json.load(f)
                for c in careers:
                    if c["name"].lower() in latest_message:
                        return c
        except Exception:
            pass
        return {}


class ActionRecommendCareer(Action):
    def name(self) -> Text:
        return "action_recommend_career"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Collect slot data
        profile = {
            "preferred_domain": tracker.get_slot("preferred_domain"),
            "skills": tracker.get_slot("skills"),
            "interests": tracker.get_slot("interests"),
            "highest_qualification": tracker.get_slot("qualification"),
            "current_degree": tracker.get_slot("degree"),
            "career_goal": tracker.get_slot("career_goal")
        }

        # Check if we have enough inputs
        has_inputs = any(profile.values())

        if not has_inputs:
            dispatcher.utter_message(
                text="To recommend matching careers, I need to know a bit about you. "
                     "Could you please share your interests, skills, or what you are studying? "
                     "Alternatively, you can fill out the form in the Streamlit Sidebar! 📋"
            )
            return []

        # Run recommender
        try:
            if CareerRecommender:
                recommender = CareerRecommender(dataset_path=CAREER_DATASET_PATH)
                recs = recommender.recommend(profile)
            else:
                recs = []
        except Exception as e:
            dispatcher.utter_message(text=f"I encountered a technical issue while evaluating matches: {str(e)}")
            return []

        if not recs:
            dispatcher.utter_message(
                text="Based on your profile, I couldn't find a direct high-confidence match. "
                     "Could you tell me more about your interests? (e.g., technology, commerce, healthcare, arts)"
            )
            return []

        # Return top matches
        top_rec = recs[0]
        top_name = top_rec["name"]
        
        reply = f"Based on your profile, my top recommendation for you is **{top_name}** ({top_rec['match_percentage']}% match) in the {top_rec['domain']} sector!\n\n"
        reply += f"**Why**: {top_rec['reason']}\n\n"
        
        if len(recs) > 1:
            other_matches = [f"{r['name']} ({r['match_percentage']}%)" for r in recs[1:4]]
            reply += f"Other good options for you are: {', '.join(other_matches)}."

        dispatcher.utter_message(text=reply)
        return [SlotSet("selected_career", top_name)]


class ActionExplainSkills(ActionBase):
    def name(self) -> Text:
        return "action_explain_skills"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        career = self.get_active_career(tracker)
        if not career:
            dispatcher.utter_message(text="Which career path are you asking about? Please tell me the name of the career.")
            return []

        skills_list = ", ".join(career.get("required_skills", []))
        dispatcher.utter_message(
            text=f"To succeed as a **{career['name']}**, you should master these core skills:\n\n👉 {skills_list}"
        )
        return [SlotSet("selected_career", career["name"])]


class ActionExplainCourses(ActionBase):
    def name(self) -> Text:
        return "action_explain_courses"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        career = self.get_active_career(tracker)
        if not career:
            dispatcher.utter_message(text="Which career path are you inquiring about? Let me know the career name to find courses.")
            return []

        courses = career.get("courses", [])
        if not courses:
            dispatcher.utter_message(text=f"I don't have online course data catalogued for {career['name']} at this moment.")
            return []

        reply = f"Here are the recommended courses for **{career['name']}**:\n\n"
        for course in courses:
            reply += f"📚 {course}\n"
        dispatcher.utter_message(text=reply)
        return [SlotSet("selected_career", career["name"])]


class ActionExplainSalary(ActionBase):
    def name(self) -> Text:
        return "action_explain_salary"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        career = self.get_active_career(tracker)
        if not career:
            dispatcher.utter_message(text="Please specify the career you're asking about so I can share salary estimates.")
            return []

        salaries = career.get("salary_range", {})
        reply = f"Here is the approximate annual salary range for a **{career['name']}**:\n\n"
        reply += f"💼 **Entry Level**: {salaries.get('entry', 'N/A')}\n"
        reply += f"📈 **Mid Level**: {salaries.get('mid', 'N/A')}\n"
        reply += f"👑 **Senior Level**: {salaries.get('senior', 'N/A')}\n\n"
        reply += "*Note: Salary ranges vary based on location, organization, and actual expertise.*"
        
        dispatcher.utter_message(text=reply)
        return [SlotSet("selected_career", career["name"])]


class ActionExplainScope(ActionBase):
    def name(self) -> Text:
        return "action_explain_scope"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        career = self.get_active_career(tracker)
        if not career:
            dispatcher.utter_message(text="Which career path's future scope and growth would you like to review?")
            return []

        growth = career.get("growth", "High demand.")
        scope = career.get("future_scope", "Expanding market.")
        
        reply = f"🔍 **Future Scope & Growth for {career['name']}**:\n\n"
        reply += f"📈 **Growth Track**: {growth}\n\n"
        reply += f"🚀 **Future Outlook**: {scope}"
        
        dispatcher.utter_message(text=reply)
        return [SlotSet("selected_career", career["name"])]


class ActionExplainRoadmap(ActionBase):
    def name(self) -> Text:
        return "action_explain_roadmap"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        career = self.get_active_career(tracker)
        if not career:
            dispatcher.utter_message(text="Which career roadmap should I show you?")
            return []

        roadmap = career.get("learning_roadmap", [])
        if not roadmap:
            dispatcher.utter_message(text=f"Roadmap details are not available for {career['name']}.")
            return []

        reply = f"🗺️ **Learning Roadmap to become a {career['name']}**:\n\n"
        for i, step in enumerate(roadmap, start=1):
            reply += f"{i}. {step}\n"
            
        dispatcher.utter_message(text=reply)
        return [SlotSet("selected_career", career["name"])]


class ActionExplainCertifications(ActionBase):
    def name(self) -> Text:
        return "action_explain_certifications"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        career = self.get_active_career(tracker)
        if not career:
            dispatcher.utter_message(text="Which career path's certifications are you interested in?")
            return []

        certs = career.get("certifications", [])
        if not certs:
            dispatcher.utter_message(text=f"I don't have certification listings for {career['name']} yet.")
            return []

        reply = f"🏅 **Key Certifications for {career['name']}**:\n\n"
        for cert in certs:
            reply += f"✓ {cert}\n"
            
        dispatcher.utter_message(text=reply)
        return [SlotSet("selected_career", career["name"])]


class ActionExplainProjects(ActionBase):
    def name(self) -> Text:
        return "action_explain_projects"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        career = self.get_active_career(tracker)
        if not career:
            dispatcher.utter_message(text="Please name the career you'd like to build projects in.")
            return []

        projects = career.get("projects", [])
        if not projects:
            dispatcher.utter_message(text=f"No portfolio projects are listed for {career['name']} yet.")
            return []

        reply = f"🛠️ **Suggested Portfolio Projects for {career['name']}**:\n\n"
        for proj in projects:
            reply += f"⚡ {proj}\n"
            
        dispatcher.utter_message(text=reply)
        return [SlotSet("selected_career", career["name"])]


class ActionDefaultFallback(Action):
    def name(self) -> Text:
        return "action_default_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(
            text="I'm sorry, I couldn't quite follow that. As your Career Counsellor, "
                 "you can ask me things like 'what are the certifications for an AI engineer?', "
                 "'how much does a CA earn?', 'give me a roadmap for UI/UX designer', or 'recommend a career for me'!"
        )
        return []
