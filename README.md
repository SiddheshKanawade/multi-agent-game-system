# Multi-Agent Game System

A streamlined LangGraph-based multi-agent system implementing **ReAct (Reasoning, Acting, Observing)** design pattern for playing two interactive games.

## Features

### Command Agent

- **Structured Command Interpretation**: Dedicated agent for parsing and executing user commands
- **Intent Recognition**: Maps commands to appropriate agent behaviors
- **Extensible Command System**: Easy to add new commands and functionality

### Interrupt/Resume Logic

- **Graceful Interruption**: Handle Ctrl+C and unexpected exits cleanly
- **Session Persistence**: Automatic saving of session state
- **Resume Capability**: Continue interrupted sessions seamlessly
- **Dynamic Checkpoints**: Pause and resume flows at any point

### Session Management

- **Automatic Checkpoints**: Created before critical game actions
- **Session History**: List and manage multiple saved sessions

## 📋 Available Commands

| Command   | Description                                 |
| --------- | ------------------------------------------- |
| `/help`   | Show available commands                     |
| `/status` | Show current session status                 |
| `/save`   | Save current session with custom name       |
| `/load`   | Load a saved session                        |
| `/list`   | List all saved sessions                     |
| `/resume` | Resume the most recent session              |
| `/pause`  | Pause and save current session              |
| `/switch` | Switch between game types or return to menu |
| `/clear`  | Clear current session stats                 |
| `/exit`   | Exit with save options                      |

## Game Features

### Word Game Agent

- Strategic questioning using ReAct pattern
- Knowledge base building
- Interrupt handling during gameplay
- Checkpoint creation at key decision points

### Number Game Agent

- Binary search optimization
- Range tracking with checkpoints
- Mid-game interruption support
- Resume from exact game state

### Supervisor Agent

- Session flow management
- Statistics tracking
- Interrupt signal handling
- Graceful shutdown coordination

## Quick Start

### Starting the Game System

```bash
python game.py
```

### Example Session

```
$ python game.py
====================================================
  Welcome to the Enhanced Multi-Agent Game System!
  Features: Command handling, Interrupt/Resume, Checkpoints
====================================================

Found 2 saved session(s).
Would you like to resume a previous session? (y/N): y

Choose a game:
1. Number Game
2. Word Game
Type '/help' for commands or leave blank to exit
Choice: /status

Current Session Status:
Session ID: abc123-def456
Number Games Played: 2
Word Games Played: 1
Number Game Wins: 1
Word Game Wins: 0
Current Action: menu
```

## 🔧 Technical Implementation

### State Management

The enhanced `GameState` includes:

- `interrupted`: Flag for handling interruptions
- `current_game`: Track active game type
- `checkpoint_data`: Serializable game state
- `last_checkpoint`: Reference to last saved state
- `resumable`: Indicates if session can be resumed

### Interrupt Handling

1. **Signal Handlers**: Capture SIGINT/SIGTERM gracefully
2. **Command Detection**: Recognize quit/exit commands
3. **Checkpoint Creation**: Auto-save before interruption
4. **Recovery Options**: Offer save/resume choices

### Command Processing

1. **Input Analysis**: Parse user input for commands vs game choices
2. **Command Routing**: Direct to appropriate handler methods
3. **State Modification**: Update game state based on command
4. **Flow Control**: Route back to appropriate game state

## Error Handling

- **Graceful Degradation**: System continues operating with partial failures
- **Emergency Saves**: Auto-save on unexpected errors
- **Recovery Mechanisms**: Resume from last known good state
- **User Feedback**: Clear error messages and recovery options

## 🎯 Usage Examples

### Save and Resume

```bash
# During gameplay
Choice: /save important_session
Session saved as important_session.json

# Later
Choice: /load
Available sessions:
1. important_session.json
2. session_abc123.json
Enter session number to load: 1
Session loaded from important_session.json
```

### Interrupt Handling

```bash
# Press Ctrl+C during gameplay
^C
Session interrupted. Would you like to:
1. Save and exit
2. Exit without saving
3. Continue playing
Choose (1-3): 1
Session saved as session_abc123.json
```

### Command Usage

```bash
Choice: /help
Available commands:
  /resume    - Resume a previous game session
  /switch    - Switch between different game types
  /pause     - Pause current session and save state
  /exit      - Exit the current game
  ...
```
