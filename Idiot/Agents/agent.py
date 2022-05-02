"""
Format på input:

data = {
    hand_cards: [...],
    playable_cards: [...],
    table_cards: [...],
    pile: [...],
    played_cards: [...],
    burnt_cards: [...]
}
"""


class AbstractAgent:
    def __init__(self, name="AbstractAgent") -> None:
        self.output = None  # SKal være indeksen til kortet som skal spilles
        self.name = name
        self.wins = 0

    def process_input(self, data: dict) -> None:
        """Choose best play according to the policy"""
        pass

    def return_output(self) -> tuple:
        return self.output
