class CheckAndBumpStep:
    """Tracks the current game step and handles step changes."""

    def __init__(self) -> None:
        """Starts the game in Step 1."""
        self.step: int = 1

    def get_step(self) -> int:
        """Returns the current game step (1, 2, or 3)."""
        return self.step

    def _start_step_2(self) -> None:
        """Starts Step 2 and applies its game rule changes."""
        raise NotImplementedError

    def _start_step_3(self) -> None:
        """Starts Step 3 and applies its game rule changes."""
        raise NotImplementedError

    def check_and_bump_to_step_2(self) -> None:
        """Starts Step 2 at the beginning of Bureaucracy when the city threshold is met.

        The threshold is 7 connected cities for 2-5 players, or 6 for 6 players.
        """
        raise NotImplementedError

    def check_and_bump_to_step_3(self) -> None:
        """Starts Step 3 at the next phase after the Step 3 card is drawn."""
        raise NotImplementedError
    