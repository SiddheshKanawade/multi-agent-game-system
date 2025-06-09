"""Enhanced Multi-Agent Game System with Command Agent and Interrupt/Resume Logic"""

import random
import uuid
import signal
import sys
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from agents import (
    GameState,
    SupervisorAgent,
    NumberGameAgent,
    WordGameAgent,
    CommandAgent,
)


def create_game_system():
    """Create the ReAct-based game system"""

    # Initialize ReAct agents
    supervisor = SupervisorAgent()
    number_agent = NumberGameAgent()
    word_agent = WordGameAgent()
    command_agent = CommandAgent()

    # Create graph
    workflow = StateGraph(GameState)

    # Define node functions
    def menu_node(state: GameState) -> GameState:
        return supervisor.display_menu(state)

    def number_game_node(state: GameState) -> GameState:
        # Create checkpoint before starting game
        state = number_agent.create_checkpoint(state, "before_number_game")
        return number_agent.play(state)

    def word_game_node(state: GameState) -> GameState:
        # Create checkpoint before starting game
        state = word_agent.create_checkpoint(state, "before_word_game")
        return word_agent.play(state)

    def command_node(state: GameState) -> GameState:
        """Handle command processing"""
        user_input = state.get("user_input", "")
        return command_agent.interpret_input(user_input, state)

    def interrupt_node(state: GameState) -> GameState:
        """Handle interrupt scenarios"""
        return supervisor.handle_interrupt(state)

    def summary_node(state: GameState) -> GameState:
        return supervisor.show_summary(state)

    # Add nodes
    workflow.add_node("menu", menu_node)
    workflow.add_node("number_game", number_game_node)
    workflow.add_node("word_game", word_game_node)
    workflow.add_node("command", command_node)
    workflow.add_node("interrupt", interrupt_node)
    workflow.add_node("summary", summary_node)

    # Define routing
    def route_from_menu(state: GameState) -> str:
        action = state.get("action", "menu")
        if action == "exit":
            return "summary"
        elif action == "number_game":
            return "number_game"
        elif action == "word_game":
            return "word_game"
        elif action == "command":
            return "command"
        elif action == "interrupt":
            return "interrupt"
        else:
            return "menu"

    def route_from_command(state: GameState) -> str:
        """Route after command processing"""
        action = state.get("action", "menu")
        if action == "exit":
            return "summary"
        elif action == "number_game":
            return "number_game"
        elif action == "word_game":
            return "word_game"
        else:
            return "menu"

    def route_from_interrupt(state: GameState) -> str:
        """Route after interrupt handling"""
        action = state.get("action", "exit")
        if action == "exit":
            return "summary"
        elif action == "command":
            return "command"
        else:
            return "menu"

    # Set up routing
    workflow.set_entry_point("menu")
    workflow.add_conditional_edges("menu", route_from_menu)
    workflow.add_conditional_edges("command", route_from_command)
    workflow.add_conditional_edges("interrupt", route_from_interrupt)
    workflow.add_edge("number_game", "menu")
    workflow.add_edge("word_game", "menu")
    workflow.add_edge("summary", END)

    # Compile with memory
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)


def setup_signal_handlers(current_state):
    """Setup signal handlers for graceful interruption"""

    def signal_handler(signum, frame):
        print(f"\n\nReceived signal {signum}. Initiating graceful shutdown...")
        current_state["action"] = "interrupt"
        current_state["interrupted"] = True
        # Don't exit immediately, let the workflow handle it

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def initialize_state_with_resume_check(command_agent: CommandAgent) -> Dict[str, Any]:
    """Initialize state and check for resumable sessions"""
    # Check for resumable sessions
    import os

    checkpoint_dir = "checkpoints"

    current_state = {
        "session_id": str(uuid.uuid4()),
        "action": "menu",
        "number_games_played": 0,
        "word_games_played": 0,
        "number_wins": 0,
        "word_wins": 0,
        "interrupted": False,
        "resumable": False,
    }

    # Check if there are any saved sessions
    if os.path.exists(checkpoint_dir):
        checkpoint_files = [
            f for f in os.listdir(checkpoint_dir) if f.endswith(".json")
        ]
        if checkpoint_files:
            print(f"\nFound {len(checkpoint_files)} saved session(s).")
            resume_choice = (
                input("Would you like to resume a previous session? (y/N): ")
                .strip()
                .lower()
            )

            if resume_choice == "y":
                temp_state = current_state.copy()
                temp_state["user_input"] = "resume"
                resumed_state = command_agent.interpret_input("resume", temp_state)
                if resumed_state.get("session_id") != current_state["session_id"]:
                    # Session was successfully resumed
                    current_state = resumed_state
                    print("Session resumed successfully!")

    return current_state


def main():
    """Enhanced main game loop with interrupt handling"""
    print("=" * 60)
    print("  Welcome to the Enhanced Multi-Agent Game System!")
    print("  Features: Command handling, Interrupt/Resume, Checkpoints")
    print("=" * 60)

    # Create agents for initialization
    command_agent = CommandAgent()

    # Initialize state with resume capability
    current_state = initialize_state_with_resume_check(command_agent)

    # Setup signal handlers. Graceful shutdown.
    setup_signal_handlers(current_state)

    # Create game system
    graph = create_game_system()

    # Run the game loop
    config = {"configurable": {"thread_id": "main_session"}}

    try:
        while True:
            # Check for interrupt flag
            if (
                current_state.get("interrupted", False)
                and current_state.get("action") != "interrupt"
            ):
                current_state["action"] = "interrupt"

            # Run one iteration of the workflow
            result = graph.invoke(current_state, config)

            # Update current state with the result
            current_state.update(result)

            # Check if we should exit
            if current_state.get("action") == "end":
                break

    except KeyboardInterrupt:
        print("\n\nKeyboard interrupt detected. Initiating graceful shutdown...")
        current_state["interrupted"] = True
        current_state["action"] = "interrupt"

        # Try to run one more time to handle the interrupt gracefully
        try:
            result = graph.invoke(current_state, config)
            current_state.update(result)
        except:
            print("Emergency exit - session state may not be saved.")

    except Exception as e:
        print(f"\nUnexpected error occurred: {e}")
        current_state["interrupted"] = True
        current_state["action"] = "interrupt"

        # Try to save state before exiting
        try:
            command_agent._save_session(current_state, auto_name=True)
            print("Session saved due to unexpected error.")
        except:
            print("Could not save session due to error.")

    print("\nThanks for playing!")


if __name__ == "__main__":
    main()
