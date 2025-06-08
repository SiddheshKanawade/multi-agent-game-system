# Simple Multi-Agent Game System (ReAct Design)

A streamlined LangGraph-based multi-agent system implementing **ReAct (Reasoning, Acting, Observing)** design pattern for playing two interactive games.

## Features

- **ReAct Agent Design**: All agents follow Think → Act → Observe pattern
- **Number Guessing Game**: AI uses binary search with reasoning to guess your number (1-100)
- **Word Clue Game**: AI uses strategic questioning with analysis to guess your chosen word
- **Session Stats**: Tracks wins and games played per session
- **Simple CLI**: Easy-to-use command line interface with agent reasoning logs

## Requirements

- Python 3.8+
- LangGraph

## Installation

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the game:

```bash
python game.py
```

## How to Play

1. **Choose a game** (1 for Number Game, 2 for Word Game, or blank to exit)
2. **Number Game**: Think of a number 1-100, answer "yes", "higher", or "lower"
3. **Word Game**: Pick a word from the list, answer the AI's questions with "yes", "no", or "maybe"
4. **View your stats** after each game
5. **Exit** to see session summary

## ReAct Architecture

### Base ReAct Agent Pattern

Each agent follows the ReAct methodology:

- **🧠 THINKING**: Analyze current situation and plan next move
- **🎯 ACTING**: Execute the planned action
- **👁️ OBSERVING**: Record results and learn from outcomes

### Agent Implementations

- **SupervisorAgent**:

  - _Thinks_: Analyzes session stats and user choices
  - _Acts_: Displays menus and routes to appropriate games
  - _Observes_: Tracks user decisions and game outcomes

- **NumberGameAgent**:

  - _Thinks_: Calculates optimal binary search strategy
  - _Acts_: Makes educated guesses based on range analysis
  - _Observes_: Adjusts search range based on user feedback

- **WordGameAgent**:
  - _Thinks_: Plans strategic questions to narrow possibilities
  - _Acts_: Asks targeted questions and makes educated guesses
  - _Observes_: Builds knowledge base from answers for better guessing

### LangGraph Orchestration

- **State Management**: Maintains game state across agent interactions
- **Workflow Routing**: Directs flow between agents based on user choices
- **Memory**: Persists session data using LangGraph checkpointer

Simple, clean, and intelligently designed!
