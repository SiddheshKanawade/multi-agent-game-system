import random
from .base_agent import ReActAgent, GameState


class WordGameAgent(ReActAgent):
    """Word guessing game with ReAct pattern and strategic questioning"""

    def __init__(self):
        super().__init__("WordGameAgent")
        self.word_list = [
            "apple",
            "banana",
            "car",
            "dog",
            "elephant",
            "flower",
            "guitar",
            "house",
            "island",
            "jungle",
            "kite",
            "lion",
            "mountain",
            "notebook",
            "ocean",
            "piano",
            "queen",
            "robot",
            "sunset",
            "tree",
        ]
        self.knowledge_base = []

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
        # THINK: Initialize word guessing strategy
        thought = self.think(
            state,
            f"Starting word game with {len(self.word_list)} possible words. Will use strategic questioning.",
        )

        print(f"\nChoose a word from this list:")
        print(", ".join(self.word_list))
        print("(Type '/help' for commands or '/exit' to return to menu)")

        chosen_word, interrupted = self._get_input_with_interrupt_check(
            "Enter your chosen word: ", state
        )

        if interrupted:
            if chosen_word == "interrupt":
                state["action"] = "interrupt"
                state["interrupted"] = True
            elif chosen_word.startswith("/"):
                state["action"] = "command"
                state["user_input"] = chosen_word
            else:
                state["action"] = "menu"
            return state

        chosen_word = chosen_word.lower()

        if chosen_word not in self.word_list:
            observation = self.observe(
                state, "Invalid word selected. Requesting valid selection."
            )
            print("Please choose a word from the list.")
            state["action"] = "word_game"
            return state

        # Create checkpoint after word selection
        state = self.create_checkpoint(state, f"word_selected_{chosen_word}")

        # THINK: Plan questioning strategy
        thought = self.think(
            state,
            "Word selected. Planning strategic questions to narrow down possibilities.",
        )

        # ACT: Ask strategic questions
        questions = [
            "Is it a living thing?",
            "Is it bigger than a breadbox?",
            "Can you hold it in your hand?",
            "Is it found in nature?",
            "Does it make sound?",
        ]

        self.knowledge_base = []
        for i, question in enumerate(questions):
            if i >= 5:
                break

            # THINK: Consider what this question will reveal
            thought = self.think(
                state, f"Asking question {i+1}/5: '{question}' to gather information"
            )

            # ACT: Ask question
            action = self.act(state, f"Asking: {question}")
            print(f"\n{question}")

            answer, interrupted = self._get_input_with_interrupt_check(
                "Answer (yes/no/maybe): ", state
            )

            if interrupted:
                # Create checkpoint before handling interrupt
                state = self.create_checkpoint(state, f"word_game_q{i+1}_interrupted")

                if answer == "interrupt":
                    state["action"] = "interrupt"
                    state["interrupted"] = True
                elif answer.startswith("/"):
                    state["action"] = "command"
                    state["user_input"] = answer
                else:
                    state["action"] = "menu"
                return state

            answer = answer.lower()

            # OBSERVE: Record answer and update knowledge
            observation = self.observe(state, f"Response to '{question}': {answer}")
            self.knowledge_base.append({"question": question, "answer": answer})

        # Create checkpoint before making final guess
        state = self.create_checkpoint(state, "word_game_making_guess")

        # THINK: Analyze collected information to make educated guess
        thought = self.think(
            state,
            f"Collected {len(self.knowledge_base)} pieces of information. Analyzing to make best guess.",
        )

        # ACT: Make strategic guess based on answers (simplified logic for demo)
        living_things = ["dog", "elephant", "flower", "lion", "tree"]
        non_living = [
            "car",
            "guitar",
            "house",
            "island",
            "mountain",
            "notebook",
            "ocean",
            "piano",
            "queen",
            "robot",
            "sunset",
        ]
        small_items = ["apple", "banana", "kite"]

        # Simple reasoning based on first question
        if self.knowledge_base and self.knowledge_base[0]["answer"] == "yes":
            candidates = living_things
            reasoning = "Based on 'living thing' = yes, focusing on living candidates"
        elif self.knowledge_base and self.knowledge_base[0]["answer"] == "no":
            candidates = non_living + small_items
            reasoning = (
                "Based on 'living thing' = no, focusing on non-living candidates"
            )
        else:
            candidates = self.word_list
            reasoning = "Insufficient clear answers, making random guess"

        guess = random.choice(candidates)

        action = self.act(
            state, f"Making educated guess: {guess} (reasoning: {reasoning})"
        )
        print(f"\nI think your word is: {guess}")

        correct, interrupted = self._get_input_with_interrupt_check(
            "Was I correct? (yes/no): ", state
        )

        if interrupted:
            if correct == "interrupt":
                state["action"] = "interrupt"
                state["interrupted"] = True
            elif correct.startswith("/"):
                state["action"] = "command"
                state["user_input"] = correct
            else:
                state["action"] = "menu"
            return state

        correct = correct.lower()

        # OBSERVE: Record final result
        if correct == "yes":
            observation = self.observe(
                state,
                f"SUCCESS! Correctly guessed '{guess}' using strategic questioning",
            )
            print("Correct! I guessed your word.")
            state["word_wins"] = state.get("word_wins", 0) + 1
            print(f"Word Game Wins: {state.get('word_wins', 0)}")
        else:
            observation = self.observe(
                state,
                f"MISS. Guessed '{guess}' but was incorrect. Learning from this outcome.",
            )
            print("I was wrong. Good game!")

        # Clear current game state
        state["current_game"] = None
        state["action"] = "menu"
        return state
