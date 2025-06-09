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

        # Show resume option if resumable
        if state.get("resumable", False):
            print(
                f"\n[Session is resumable from: {state.get('last_checkpoint', 'unknown')}]"
            )

        print("\nChoose a game:")
        print("1. Number Game")
        print("2. Word Game")
        print("Type '/help' for commands or leave blank to exit")

        try:
            choice = input("Choice: ").strip()
        except (KeyboardInterrupt, EOFError):
            # Handle Ctrl+C or EOF gracefully
            print("\n\nInterrupt detected...")
            state["action"] = "interrupt"
            state["interrupted"] = True
            return state

        # Create a checkpoint before processing choice
        state = self.create_checkpoint(state, f"menu_choice_{choice or 'exit'}")

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
            state["current_game"] = "number_game"
            state["number_games_played"] = state.get("number_games_played", 0) + 1
        elif choice == "2":
            observation = self.observe(
                state, "User selected Word Game - initializing word game session"
            )
            state["action"] = "word_game"
            state["current_game"] = "word_game"
            state["word_games_played"] = state.get("word_games_played", 0) + 1
        elif choice.startswith("/") or choice.lower() in [
            "help",
            "status",
            "save",
            "load",
            "pause",
            "resume",
            "switch",
            "clear",
            "list",
        ]:
            # Command detected - let CommandAgent handle it
            observation = self.observe(
                state, f"Command detected: {choice} - routing to CommandAgent"
            )
            state["action"] = "command"
            state["user_input"] = choice
        else:
            observation = self.observe(
                state, "Invalid input detected - returning to menu"
            )
            print(
                "Invalid selection. Type '/help' for commands or choose 1/2 for games."
            )
            state["action"] = "menu"

        return state

    def show_summary(self, state: GameState) -> GameState:
        # THINK: Analyze final session statistics
        thought = self.think(
            state, "Session ending - need to compile and present final statistics"
        )

        # ACT: Calculate and display summary
        action = self.act(state, "Generating session summary report")

        # Check if session was interrupted
        if state.get("interrupted", False):
            print(f"\nSession ended due to interruption.")

        print(f"\nSession Summary (Should be saved in DB for persistence):")
        print(f"Session ID: {state.get('session_id', 'N/A')}")
        print(
            f"Word Games Played: {state.get('word_games_played', 0)} | Wins: {state.get('word_wins', 0)}"
        )
        print(
            f"Number Games Played: {state.get('number_games_played', 0)} | Wins: {state.get('number_wins', 0)}"
        )

        # Show checkpoint info if available
        if state.get("resumable", False):
            print(f"Last Checkpoint: {state.get('last_checkpoint', 'N/A')}")
            print("This session can be resumed later using '/resume' or '/load'")

        # OBSERVE: Session completed
        observation = self.observe(state, "Session summary displayed - ending session")
        state["action"] = "end"
        return state

    def handle_interrupt(self, state: GameState) -> GameState:
        """Handle interruption scenarios"""
        thought = self.think(
            state, "Processing interrupt signal - creating emergency checkpoint"
        )

        # Create emergency checkpoint
        state = self.create_checkpoint(
            state, f"interrupt_{state.get('session_id', 'unknown')}"
        )

        action = self.act(
            state, "Created interrupt checkpoint - routing to exit with save option"
        )

        # Set interrupted flag and route to command handling
        state["interrupted"] = True
        state["action"] = "command"
        state["user_input"] = "interrupt"

        observation = self.observe(
            state, "Interrupt processed - prepared for graceful exit"
        )
        return state
