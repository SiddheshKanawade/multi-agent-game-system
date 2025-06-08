"""Simple Multi-Agent Game System with LangGraph - ReAct Design"""

import random
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from agents import GameState, SupervisorAgent, NumberGameAgent, WordGameAgent


def create_game_system():
    """Create the ReAct-based game system"""

    # Initialize ReAct agents
    supervisor = SupervisorAgent()
    number_agent = NumberGameAgent()
    word_agent = WordGameAgent()

    # Create graph
    workflow = StateGraph(GameState)

    # Define node functions
    def menu_node(state: GameState) -> GameState:
        return supervisor.display_menu(state)

    def number_game_node(state: GameState) -> GameState:
        return number_agent.play(state)

    def word_game_node(state: GameState) -> GameState:
        return word_agent.play(state)

    def summary_node(state: GameState) -> GameState:
        return supervisor.show_summary(state)

    # Add nodes
    workflow.add_node("menu", menu_node)
    workflow.add_node("number_game", number_game_node)
    workflow.add_node("word_game", word_game_node)
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
        else:
            return "menu"

    # Set up routing
    workflow.set_entry_point("menu")
    workflow.add_conditional_edges("menu", route_from_menu)
    workflow.add_edge("number_game", "menu")
    workflow.add_edge("word_game", "menu")
    workflow.add_edge("summary", END)

    # Compile with memory
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)


def main():
    """Main game loop"""
    print("=" * 50)
    print("  Welcome to the Multi-Agent Game System!")
    print("=" * 50)

    # Create game system
    graph = create_game_system()

    # Initialize state
    current_state = {
        "action": "menu",
        "number_games_played": 0,
        "word_games_played": 0,
        "number_wins": 0,
        "word_wins": 0,
    }

    # Run the game loop
    config = {"configurable": {"thread_id": "main_session"}}

    try:
        while True:
            # Run one iteration of the workflow
            result = graph.invoke(current_state, config)

            # Update current state with the result
            current_state.update(result)

            # Check if we should exit
            if current_state.get("action") == "end":
                break

    except KeyboardInterrupt:
        print("\nGame interrupted. Thanks for playing!")

    print("\nThanks for playing!")


if __name__ == "__main__":
    main()
