from typing import TypedDict


class GameState(TypedDict):
    session_id: str
    action: str
    number_games_played: int
    word_games_played: int
    number_wins: int
    word_wins: int


class ReActAgent:
    """Base ReAct agent with Think, Act, Observe pattern"""

    def __init__(self, name: str):
        self.name = name
        self.thoughts = []
        self.actions = []
        self.observations = []

    def think(self, state: GameState, context: str) -> str:
        """Reasoning step - analyze current situation"""
        thought = f"[{self.name} THINKING]: {context}"
        self.thoughts.append(thought)
        return thought

    def act(self, state: GameState, action: str) -> str:
        """Acting step - take an action"""
        action_log = f"[{self.name} ACTING]: {action}"
        self.actions.append(action_log)
        return action_log

    def observe(self, state: GameState, observation: str) -> str:
        """Observing step - record what happened"""
        obs_log = f"[{self.name} OBSERVING]: {observation}"
        self.observations.append(obs_log)
        return obs_log
