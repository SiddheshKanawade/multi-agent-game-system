from .base_agent import ReActAgent, GameState


class NumberGameAgent(ReActAgent):
    """Number guessing game with ReAct pattern and binary search"""

    def __init__(self):
        super().__init__("NumberGameAgent")

    def play(self, state: GameState) -> GameState:
        # THINK: Initialize game strategy
        thought = self.think(
            state,
            "Starting number guessing game. Will use binary search strategy for optimal guessing.",
        )
        print(thought)  # Placeholder to see LLM thinking
        print("\nThink of a number between 1 and 100. I'll try to guess it!")

        min_num = 1
        max_num = 100
        attempts = 0

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
            print(action)  # Placeholder to see LLM acting

            print(f"\nIs your number {guess}?")
            response = input("Enter 'yes', 'higher', or 'lower': ").strip().lower()

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
            elif response == "lower":
                observation = self.observe(
                    state,
                    f"Number is lower than {guess}. Adjusting range to {min_num}-{guess - 1}",
                )
                max_num = guess - 1
            else:
                observation = self.observe(
                    state, "Invalid response received. Requesting clarification."
                )
                print("Please enter 'yes', 'higher', or 'lower'")
                continue

        state["action"] = "menu"
        return state
