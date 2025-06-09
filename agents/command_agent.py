import json
import os
from typing import Dict, Any, Optional, List
from .base_agent import ReActAgent, GameState


class CommandAgent(ReActAgent):
    """Dedicated agent for interpreting user commands and managing interrupt/resume flows"""

    def __init__(self):
        super().__init__("CommandAgent")
        self.available_commands = {
            "resume": "Resume a previous game session",
            "switch": "Switch between different game types",
            "pause": "Pause current session and save state",
            "exit": "Exit the current game",
            "help": "Show available commands",
            "status": "Show current session status",
            "clear": "Clear current session",
            "save": "Save current session with custom name",
            "load": "Load a saved session",
            "list": "List all saved sessions",
        }
        self.checkpoint_dir = "checkpoints"
        self._ensure_checkpoint_dir()

    def _ensure_checkpoint_dir(self):
        """Ensure checkpoint directory exists"""
        if not os.path.exists(self.checkpoint_dir):
            os.makedirs(self.checkpoint_dir)

    def interpret_input(self, user_input: str, state: GameState) -> GameState:
        """Main method to interpret user input and determine appropriate action"""

        # THINK: Analyze user input for commands or game choices
        thought = self.think(
            state,
            f"Analyzing user input: '{user_input}' for commands or game selections",
        )

        # Clean and parse input
        input_clean = user_input.strip().lower()

        # Check for structured commands
        if input_clean.startswith("/") or input_clean in self.available_commands:
            return self._handle_command(input_clean, state)

        # Check for interrupt signals
        if input_clean in ["quit", "q", "stop", "interrupt", "ctrl+c"]:
            return self._handle_interrupt(state)

        # Check for standard game choices
        if input_clean in ["1", "2", ""]:
            return self._handle_game_choice(input_clean, state)

        # Handle unexpected input
        return self._handle_unexpected_input(user_input, state)

    def _handle_command(self, command: str, state: GameState) -> GameState:
        """Handle structured commands"""
        # Remove leading slash if present
        cmd = command.lstrip("/")

        action = self.act(state, f"Processing command: {cmd}")

        if cmd == "resume":
            return self._resume_session(state)
        elif cmd == "switch":
            return self._switch_game(state)
        elif cmd == "pause":
            return self._pause_session(state)
        elif cmd == "help":
            return self._show_help(state)
        elif cmd == "status":
            return self._show_status(state)
        elif cmd == "clear":
            return self._clear_session(state)
        elif cmd == "save":
            return self._save_session(state)
        elif cmd == "load":
            return self._load_session(state)
        elif cmd == "list":
            return self._list_sessions(state)
        elif cmd == "exit":
            return self._handle_interrupt(state)
        else:
            observation = self.observe(state, f"Unknown command: {cmd}")
            print(f"Unknown command: {cmd}. Type 'help' for available commands.")
            return state

    def _handle_interrupt(self, state: GameState) -> GameState:
        """Handle session interruption with save option"""
        action = self.act(state, "Processing interrupt signal - offering save options")

        print("\nSession interrupted. Would you like to:")
        print("1. Save and exit")
        print("2. Exit without saving")
        print("3. Continue playing")

        choice = input("Choose (1-3): ").strip()

        if choice == "1":
            self._save_session(state, auto_name=True)
            observation = self.observe(state, "Session saved and exiting")
            state["action"] = "exit"
            state["interrupted"] = True
        elif choice == "2":
            observation = self.observe(state, "Exiting without saving")
            state["action"] = "exit"
            state["interrupted"] = True
        else:
            observation = self.observe(state, "Continuing session")
            state["action"] = "menu"

        return state

    def _handle_game_choice(self, choice: str, state: GameState) -> GameState:
        """Handle standard game menu choices"""
        action = self.act(state, f"Processing game choice: {choice}")

        if choice == "":
            state["action"] = "exit"
        elif choice == "1":
            state["action"] = "number_game"
            state["number_games_played"] = state.get("number_games_played", 0) + 1
        elif choice == "2":
            state["action"] = "word_game"
            state["word_games_played"] = state.get("word_games_played", 0) + 1

        observation = self.observe(
            state, f"Game choice processed, action set to: {state['action']}"
        )
        return state

    def _handle_unexpected_input(self, user_input: str, state: GameState) -> GameState:
        """Handle unexpected or invalid input"""
        observation = self.observe(state, f"Unexpected input received: {user_input}")
        print(
            f"Unexpected input: '{user_input}'. Type 'help' for commands or choose 1/2 for games."
        )
        state["action"] = "menu"
        return state

    def _resume_session(self, state: GameState) -> GameState:
        """Resume the most recent session"""
        try:
            checkpoint_files = [
                f for f in os.listdir(self.checkpoint_dir) if f.endswith(".json")
            ]
            if not checkpoint_files:
                print("No saved sessions found.")
                return state

            # Get most recent checkpoint
            latest_file = max(
                checkpoint_files,
                key=lambda f: os.path.getctime(os.path.join(self.checkpoint_dir, f)),
            )

            with open(os.path.join(self.checkpoint_dir, latest_file), "r") as f:
                saved_state = json.load(f)

            state.update(saved_state)
            state["action"] = "menu"

            observation = self.observe(state, f"Session resumed from {latest_file}")
            print(f"Session resumed from {latest_file}")

        except Exception as e:
            observation = self.observe(state, f"Failed to resume session: {e}")
            print(f"Failed to resume session: {e}")

        return state

    def _switch_game(self, state: GameState) -> GameState:
        """Switch to a different game type"""
        current_in_game = state.get("current_game", None)

        if current_in_game:
            print(f"Currently in {current_in_game}. Switching to menu...")
            state["action"] = "menu"
            state["current_game"] = None
        else:
            print("Not currently in a game. Returning to menu...")
            state["action"] = "menu"

        observation = self.observe(state, "Switched to game menu")
        return state

    def _pause_session(self, state: GameState) -> GameState:
        """Pause and save current session"""
        return self._save_session(state, auto_name=True)

    def _save_session(self, state: GameState, auto_name: bool = False) -> GameState:
        """Save current session state"""
        try:
            if auto_name:
                filename = f"session_{state.get('session_id', 'unknown')}.json"
            else:
                name = input("Enter save name (or press Enter for auto-name): ").strip()
                filename = (
                    f"{name}.json"
                    if name
                    else f"session_{state.get('session_id', 'unknown')}.json"
                )

            filepath = os.path.join(self.checkpoint_dir, filename)

            # Create a clean state copy for saving
            save_state = {k: v for k, v in state.items() if k != "action"}
            save_state["saved_at"] = str(state.get("session_id", "unknown"))

            print(f"Saving session to {filepath}")
            with open(filepath, "w") as f:
                json.dump(save_state, f, indent=2)

            observation = self.observe(state, f"Session saved as {filename}")
            print(f"Session saved as {filename}")

        except Exception as e:
            observation = self.observe(state, f"Failed to save session: {e}")
            print(f"Failed to save session: {e}")

        return state

    def _load_session(self, state: GameState) -> GameState:
        """Load a specific session"""
        try:
            checkpoint_files = [
                f for f in os.listdir(self.checkpoint_dir) if f.endswith(".json")
            ]
            if not checkpoint_files:
                print("No saved sessions found.")
                return state

            print("Available sessions:")
            for i, filename in enumerate(checkpoint_files, 1):
                print(f"{i}. {filename}")

            choice = input("Enter session number to load: ").strip()

            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(checkpoint_files):
                    filename = checkpoint_files[idx]
                    with open(os.path.join(self.checkpoint_dir, filename), "r") as f:
                        saved_state = json.load(f)

                    state.update(saved_state)
                    state["action"] = "menu"

                    observation = self.observe(state, f"Session loaded from {filename}")
                    print(f"Session loaded from {filename}")
                else:
                    print("Invalid session number.")
            else:
                print("Invalid input.")

        except Exception as e:
            observation = self.observe(state, f"Failed to load session: {e}")
            print(f"Failed to load session: {e}")

        return state

    def _list_sessions(self, state: GameState) -> GameState:
        """List all saved sessions"""
        try:
            checkpoint_files = [
                f for f in os.listdir(self.checkpoint_dir) if f.endswith(".json")
            ]
            if not checkpoint_files:
                print("No saved sessions found.")
            else:
                print("Saved sessions:")
                for filename in checkpoint_files:
                    filepath = os.path.join(self.checkpoint_dir, filename)
                    mod_time = os.path.getmtime(filepath)
                    print(f"  - {filename} (modified: {mod_time})")
        except Exception as e:
            print(f"Error listing sessions: {e}")

        observation = self.observe(state, "Listed saved sessions")
        return state

    def _show_help(self, state: GameState) -> GameState:
        """Show available commands"""
        print("\nAvailable commands:")
        for cmd, desc in self.available_commands.items():
            print(f"  /{cmd} - {desc}")
        print("\nYou can also use standard game choices:")
        print("  1 - Number Game")
        print("  2 - Word Game")
        print("  (blank) - Exit")

        observation = self.observe(state, "Displayed help information")
        return state

    def _show_status(self, state: GameState) -> GameState:
        """Show current session status"""
        print("\nCurrent Session Status:")
        print(f"Session ID: {state.get('session_id', 'N/A')}")
        print(f"Number Games Played: {state.get('number_games_played', 0)}")
        print(f"Word Games Played: {state.get('word_games_played', 0)}")
        print(f"Number Game Wins: {state.get('number_wins', 0)}")
        print(f"Word Game Wins: {state.get('word_wins', 0)}")
        print(f"Current Action: {state.get('action', 'Unknown')}")

        observation = self.observe(state, "Displayed session status")
        return state

    def _clear_session(self, state: GameState) -> GameState:
        """Clear current session stats"""
        confirm = (
            input("Are you sure you want to clear the current session? (y/N): ")
            .strip()
            .lower()
        )

        if confirm == "y":
            # Reset game stats but keep session_id
            session_id = state.get("session_id")
            state.clear()
            state["session_id"] = session_id
            state["action"] = "menu"
            state["number_games_played"] = 0
            state["word_games_played"] = 0
            state["number_wins"] = 0
            state["word_wins"] = 0

            observation = self.observe(state, "Session cleared")
            print("Session cleared.")
        else:
            observation = self.observe(state, "Session clear cancelled")
            print("Clear cancelled.")

        return state
