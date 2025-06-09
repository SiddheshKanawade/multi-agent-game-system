from .base_agent import ReActAgent, GameState


class NumberGameAgent(ReActAgent):
    """Number guessing game with ReAct pattern and binary search"""

    def __init__(self):
        super().__init__("NumberGameAgent")

    def _get_input_with_interrupt_check(self, prompt: str, state: GameState) -> tuple:
        """Get user input with interrupt and command handling"""
        try:
            user_input = input(prompt).strip()

            # Check for interrupt signals
            if user_input.lower() in ["quit", "q", "exit", "/exit"]:
                return user_input, True

            # Check for commands
            if user_input.startswith("/"):
                return user_input, True

            return user_input, False

        except (KeyboardInterrupt, EOFError):
            return "interrupt", True

    def play(self, state: GameState) -> GameState:
        # THINK: Initialize game strategy
        thought = self.think(
            state,
            "Starting number guessing game. Will use binary search strategy for optimal guessing.",
        )
        print("\nThink of a number between 1 and 100. I'll try to guess it!")
        print("(Type '/help' for commands or '/exit' to return to menu)")

        min_num = 1
        max_num = 100
        attempts = 0

        # Create initial checkpoint
        state = self.create_checkpoint(state, "number_game_started")

        while min_num <= max_num:
            attempts += 1

            # THINK: Calculate optimal guess
            guess = (min_num + max_num) // 2
            thought = self.think(
                state,
                f"Range is {min_num}-{max_num}. Optimal binary search guess: {guess}",
            )

            # ACT: Make guess and request feedback
            action = self.act(state, f"Guessing {guess} and requesting user feedback")

            print(f"\nIs your number {guess}?")

            response, interrupted = self._get_input_with_interrupt_check(
                "Enter 'yes', 'higher', or 'lower': ", state
            )

            if interrupted:
                # Create checkpoint before handling interrupt
                checkpoint_data = {
                    "min_num": min_num,
                    "max_num": max_num,
                    "attempts": attempts,
                    "last_guess": guess,
                }
                state["checkpoint_data"] = checkpoint_data
                state = self.create_checkpoint(
                    state, f"number_game_attempt_{attempts}_interrupted"
                )

                if response == "interrupt":
                    state["action"] = "interrupt"
                    state["interrupted"] = True
                elif response.startswith("/"):
                    state["action"] = "command"
                    state["user_input"] = response
                else:
                    state["action"] = "menu"
                return state

            response = response.lower()

            # OBSERVE: Process user feedback and adjust strategy
            if response == "yes":
                observation = self.observe(
                    state,
                    f"SUCCESS! Guessed correctly in {attempts} attempts using binary search",
                )
                print("Correct! You guessed it.")
                state["number_wins"] = state.get("number_wins", 0) + 1
                print(f"Number Game Wins: {state.get('number_wins', 0)}")
                break
            elif response == "higher":
                observation = self.observe(
                    state,
                    f"Number is higher than {guess}. Adjusting range to {guess + 1}-{max_num}",
                )
                min_num = guess + 1

                # Create checkpoint after range adjustment
                checkpoint_data = {
                    "min_num": min_num,
                    "max_num": max_num,
                    "attempts": attempts,
                    "last_guess": guess,
                    "last_response": response,
                }
                state["checkpoint_data"] = checkpoint_data

            elif response == "lower":
                observation = self.observe(
                    state,
                    f"Number is lower than {guess}. Adjusting range to {min_num}-{guess - 1}",
                )
                max_num = guess - 1

                # Create checkpoint after range adjustment
                checkpoint_data = {
                    "min_num": min_num,
                    "max_num": max_num,
                    "attempts": attempts,
                    "last_guess": guess,
                    "last_response": response,
                }
                state["checkpoint_data"] = checkpoint_data

            else:
                observation = self.observe(
                    state, "Invalid response received. Requesting clarification."
                )
                print("Please enter 'yes', 'higher', or 'lower'")
                continue

        # Clear current game state
        state["current_game"] = None
        state["action"] = "menu"
        return state
