from typing import TypedDict, Optional, Any, Dict


class GameState(TypedDict):
    session_id: str
    action: str
    number_games_played: int
    word_games_played: int
    number_wins: int
    word_wins: int
    interrupted: Optional[bool]
    current_game: Optional[str]
    checkpoint_data: Optional[Dict[str, Any]]
    last_checkpoint: Optional[str]
    user_input: Optional[str]
    resumable: Optional[bool]


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

    def create_checkpoint(
        self, state: GameState, checkpoint_name: str = None
    ) -> GameState:
        """Create a checkpoint of current state"""
        import time

        checkpoint_name = checkpoint_name or f"checkpoint_{int(time.time())}"

        # Store current state as checkpoint data
        checkpoint_data = {
            "session_id": state.get("session_id"),
            "number_games_played": state.get("number_games_played", 0),
            "word_games_played": state.get("word_games_played", 0),
            "number_wins": state.get("number_wins", 0),
            "word_wins": state.get("word_wins", 0),
            "current_game": state.get("current_game"),
            "timestamp": time.time(),
        }

        state["checkpoint_data"] = checkpoint_data
        state["last_checkpoint"] = checkpoint_name
        state["resumable"] = True

        self.observe(state, f"Checkpoint '{checkpoint_name}' created")
        return state

    def can_resume(self, state: GameState) -> bool:
        """Check if current state can be resumed"""
        return (
            state.get("resumable", False) and state.get("checkpoint_data") is not None
        )
