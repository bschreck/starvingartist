from typing import List, Dict, Optional

class GoalManager:
    def __init__(self):
        self.current_goal: Optional[str] = None
        self.long_term_goals: List[str] = []
        self.completed_goals: List[str] = []

    def set_current_goal(self, goal: str):
        self.current_goal = goal

    def add_long_term_goal(self, goal: str):
        self.long_term_goals.append(goal)

    def complete_current_goal(self):
        if self.current_goal:
            self.completed_goals.append(self.current_goal)
            self.current_goal = None

    def get_goals_context(self) -> str:
        context = "Goals:\n"
        if self.current_goal:
            context += f"- Current: {self.current_goal}\n"
        if self.long_term_goals:
            context += "- Long-term:\n"
            for goal in self.long_term_goals:
                context += f"  - {goal}\n"
        return context
