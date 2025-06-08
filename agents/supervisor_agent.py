from .base_agent import ReActAgent, GameState


class SupervisorAgent(ReActAgent):
    """Manages game flow and stats using ReAct pattern"""

    def __init__(self):
        super().__init__("SupervisorAgent")

    def display_menu(self, state: GameState) -> GameState:
        # THINK: Analyze current session state
        games_played = state.get("number_games_played", 0) + state.get(
            "word_games_played", 0
        )
        total_wins = state.get("number_wins", 0) + state.get("word_wins", 0)

        thought = self.think(
            state,
            f"Session status: {games_played} games played, {total_wins} total wins. Need to present menu options.",
        )

        # ACT: Display current session stats and menu
        action = self.act(state, "Displaying current session stats and game menu")

        # Show current session stats if any games have been played
        if games_played > 0:
            print(f"\nCurrent Session Stats:")
            print(f"Word Game Wins: {state.get('word_wins', 0)}")
            print(f"Number Game Wins: {state.get('number_wins', 0)}")

        print("\nChoose a game:")
        print("1. Number Game")
        print("2. Word Game")
        print("(Leave blank to exit)")

        choice = input().strip()

        # OBSERVE: Record user's choice and decide next action
        if not choice:
            observation = self.observe(
                state, "User chose to exit - preparing session summary"
            )
            state["action"] = "exit"
        elif choice == "1":
            observation = self.observe(
                state, "User selected Number Game - initializing number game session"
            )
            state["action"] = "number_game"
            state["number_games_played"] = state.get("number_games_played", 0) + 1
        elif choice == "2":
            observation = self.observe(
                state, "User selected Word Game - initializing word game session"
            )
            state["action"] = "word_game"
            state["word_games_played"] = state.get("word_games_played", 0) + 1
        else:
            observation = self.observe(
                state, "Invalid input detected - returning to menu"
            )
            print("Invalid selection. Please choose 1 or 2, or leave blank to exit.")
            state["action"] = "menu"

        return state

    def show_summary(self, state: GameState) -> GameState:
        # THINK: Analyze final session statistics
        thought = self.think(
            state, "Session ending - need to compile and present final statistics"
        )

        # ACT: Calculate and display summary
        action = self.act(state, "Generating session summary report")
        print(f"\nSession Summary:")
        print(
            f"Word Games Played: {state.get('word_games_played', 0)} | Wins: {state.get('word_wins', 0)}"
        )
        print(
            f"Number Games Played: {state.get('number_games_played', 0)} | Wins: {state.get('number_wins', 0)}"
        )

        # OBSERVE: Session completed
        observation = self.observe(state, "Session summary displayed - ending session")
        state["action"] = "end"
        return state
