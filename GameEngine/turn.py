import deck
import player
import agent_path
import NEAT_agent as ne
from numpy.random import randint


class AbstractTurn:
    """Dette er superklassen til PlayerTurn og AgentTurn som skal brukes. Denne klassen er ufullstendig"""

    def __init__(
        self,
        player: player.Player,
        deck: deck.Deck,
        pile: deck.Deck,
        burnt_cards: deck.Deck,
    ) -> None:
        self.player = player
        self.deck = deck
        self.pile = pile
        self.burnt_cards = burnt_cards

    def play_turn(self) -> None:
        """
        Selve turen blir spilt av en spiller. Dette er hovedfunksjonen og må bli kalt for at turen skal bli spilt
        """
        must_play = True
        playable_cards = self.get_playable_cards()
        can_play = bool(playable_cards)
        may_build = False

        if not can_play:
            self.can_not_play_actions(playable_cards, must_play)

        while (must_play or may_build) and can_play:
            self.show_player_info(playable_cards, must_play)
            player_input, chosen_card = self.get_player_input(playable_cards, must_play)

            if player_input == "n":
                break

            self.play_card(player_input)
            must_play, may_build = self.apply_side_effects(chosen_card)
            self.take_visible_table_cards()  # Funksjonen sjekker om spilleren har mulighet også
            playable_cards = self.get_playable_cards(may_build)
            can_play = bool(playable_cards)
            self.restore_hand()
        self.take_hidden_table_cards()
        self.player.check_if_finished()

    """ 
    ACTIONS
    """

    def apply_side_effects(self, played_card: deck.Card) -> tuple:
        """Sjekk om det skal skje noe spesielt på grunn kortet som ble spilt. Hvis ja, gjennomfør disse effektene. -> must_play, may_build"""
        if played_card.value == 10 or self.check_4_in_a_row():

            self.burnt_cards += self.pile
            self.pile.clear()
            return (True, False)

        elif played_card.value == 2:
            return (True, False)

        else:
            return (False, True)

    def can_not_play_actions(self, playable_cards: list) -> None:
        pass

    def play_card(self, index: int):
        self.pile.add_card(self.player.play_hand_card(index))

    def restore_hand(self) -> None:
        if len(self.player.hand) < 3 and self.deck:
            while len(self.player.hand) < 3 and self.deck:
                self.player.hand.append(self.deck.pop_top_card())

    def take_pile(self) -> None:
        self.player.hand += self.pile.cards
        self.pile.clear()

    def take_visible_table_cards(self) -> None:
        pass

    def take_hidden_table_cards(self) -> None:
        pass

    """
    GET-FUNCTIONS
    """

    def get_playable_cards(self, can_build=False) -> list:
        if not bool(self.pile):
            playable_cards = list(enumerate(self.player.hand))
            return playable_cards

        playable_cards = []
        if not can_build:
            for index, card in enumerate(self.player.hand):
                if self.check_if_playable_card(card):
                    playable_cards.append((index, card))
            return playable_cards
        else:
            for index, card in enumerate(self.player.hand):
                if self.check_if_buildable_card(card, self.pile.get_top_card()):
                    playable_cards.append((index, card))
            return playable_cards

    """
    CHECKS
    """

    def check_if_playable_card(self, card: deck.Card) -> bool:
        if not bool(self.pile):
            return True
        elif card.value == 2 or card.value == 10:
            return True
        elif card.value >= self.pile.get_top_card().value:
            return True
        return False

    def check_if_buildable_card(self, card: deck.Card, prev_card: deck.Card) -> bool:
        if card.value == 10:
            return False
        if prev_card.value == card.value:
            return True
        if prev_card.value + 1 == card.value:
            return True
        return False

    def check_if_valid_index(self, playable_cards: list, player_input: int) -> bool:
        for index, _ in playable_cards:
            if index == player_input:
                return True
        return False

    def check_4_in_a_row(self) -> bool:
        CARDS_TO_CHECK = 4
        if len(self.pile) < CARDS_TO_CHECK:
            return False
        for card in self.pile[-CARDS_TO_CHECK + 1 :]:
            if card.value != self.pile[-CARDS_TO_CHECK].value:
                return False
        return True

    def check_if_can_continue(self, playable_cards: list) -> bool:
        if not self.player.hand:
            return False
        if not bool(playable_cards):
            return False
        return True

    """
    OUTPUT
    """

    def show_player_info(self, playable_cards: list) -> None:
        pass

    """ 
    INPUT
    """

    def get_player_input(self, playable_cards: list, can_build: bool) -> int:
        pass


class PlayerTurn(AbstractTurn):
    def __init__(
        self,
        player: player.Player,
        deck: deck.Deck,
        pile: deck.Deck,
        burnt_cards: deck.Deck,
    ):
        super().__init__(player, deck, pile, burnt_cards)

    """ 
    ACTIONS
    """

    def can_not_play_actions(self, playable_cards: list, must_play) -> None:
        self.show_player_info(playable_cards, must_play)
        msg = f"{self.player.name}: Du må trekke inn kortene; vennligst bekreft ved å trykke enter"
        input(msg)
        print("\n" * 2)
        self.take_pile()

    def take_visible_table_cards(self) -> None:
        if not (self.deck or self.player.hand) and self.player.table_visible:
            input("Taking visible table cards; press enter")
            self.player.hand += self.player.table_visible
            self.player.table_visible.clear()
        self.player.check_if_finished()

    def take_hidden_table_cards(self) -> None:
        if (
            not (self.deck or self.player.hand or self.player.table_visible)
            and self.player.table_hidden
        ):
            input("Taking random face-down card; press enter")
            self.player.hand.append(self.player.table_hidden.pop())
        self.player.check_if_finished()

    """
    OUTPUT
    """

    def show_player_info(self, playable_cards: list, must_play) -> None:
        self.show_player_hand()
        self.show_playable_cards(playable_cards)
        self.show_top_pile_card()

    def show_top_pile_card(self) -> None:
        if bool(self.pile):
            self.pile.get_top_card().show_card()
        else:
            print("Empty deck")

    def show_player_hand(self) -> None:
        self.player.show_hand()

    def show_playable_cards(self, playable_cards: list) -> None:
        print("Playable cards:")
        print("-" * 20)
        for index, card in playable_cards:
            print(f"Index: {index}", end="\n    ")
            card.show_card()
        print("-" * 20)

    """ 
    INPUT
    """

    def get_player_input(self, playable_cards: list, can_build: bool) -> int:
        valid_input = False
        chosen_card = None

        while not valid_input:
            if can_build:
                print("Du kan velge å ikke spille; (N)")

            player_input = input("Hvilken indeks? ")
            valid_input = False

            if player_input.isdigit():
                player_input = int(player_input)
                valid_input = self.check_if_valid_index(playable_cards, player_input)
            elif player_input.capitalize() == "N" and can_build:
                player_input = "n"
                valid_input = True

            if not valid_input:
                print("Ikke gyldig input")
        if player_input != "n":
            chosen_card = self.player.get_hand_card(player_input)

        print("\n" * 2)
        return player_input, chosen_card


class AgentTurn(AbstractTurn):
    def __init__(
        self,
        player: player.AgentPlayer,
        deck: deck.Deck,
        pile: deck.Deck,
        burnt_cards: deck.Deck,
        log_turn=False,
        turn_number=0,
    ):
        super().__init__(player, deck, pile, burnt_cards)
        self.log_turn = log_turn
        self.turn_number = turn_number

    def play_turn(self) -> None:
        """
        Selve turen blir spilt av en spiller. Dette er hovedfunksjonen og må bli kalt for at turen skal bli spilt
        """
        must_play = True
        playable_cards = self.get_playable_cards()
        can_play = bool(playable_cards)
        may_build = False

        if not can_play:
            self.can_not_play_actions()

        while (must_play or may_build) and can_play:
            self.show_player_info(playable_cards, must_play)
            player_input, chosen_card = self.get_player_input()

            if player_input == None:
                break

            if self.log_turn:
                top_pile_card = 0
                if self.pile:
                    top_pile_card = self.pile.get_top_card()
                self.log_play(chosen_card, playable_cards, must_play, top_pile_card)

            self.play_card(player_input)
            must_play, may_build = self.apply_side_effects(chosen_card)
            self.take_visible_table_cards()  # Funksjonen sjekker om spilleren har mulighet også
            playable_cards = self.get_playable_cards(may_build)
            can_play = bool(playable_cards)
            self.restore_hand()
        self.take_hidden_table_cards()
        self.player.check_if_finished()

    """
    ACTIONS
    """

    def can_not_play_actions(self) -> None:
        self.take_pile()

    def take_visible_table_cards(self) -> None:
        if not (self.deck or self.player.hand) and self.player.table_visible:
            self.player.hand += self.player.table_visible
            self.player.table_visible.clear()
        self.player.check_if_finished()

    def take_hidden_table_cards(self) -> None:
        if (
            not (self.deck or self.player.hand or self.player.table_visible)
            and self.player.table_hidden
        ):
            self.player.hand.append(self.player.table_hidden.pop())
        self.player.check_if_finished()

    def log_play(
        self,
        chosen_card: deck.Card,
        playable_cards: list,
        must_play: bool,
        top_pile_card: deck.Card,
    ):
        if not type(self.player.policy) == ne.NEAT_Agent3:
            return

        playable_cards_values = [card.value for _, card in playable_cards]
        if top_pile_card == 0:
            top_pile_card_value = 0
        else:
            top_pile_card_value = top_pile_card.value
        save_data = [
            self.turn_number,
            chosen_card.value,
            playable_cards_values,
            must_play,
            top_pile_card_value,
        ]
        with open(r".\Log\log_turns.txt", "a") as f:
            f.write(str(save_data))
            f.write("\n")

    """
    GET-FUNCTIONS
    """

    def find_card(self, value: int, playable_cards: list) -> tuple:
        for index, card in playable_cards:
            if value == card.value:
                return index, card, True
        return None, None, False

    """
    
    OUTPUT
    """

    def show_player_info(self, playable_cards: list, must_play: bool) -> None:
        """Gir info som spillet til spilleren. Det er denne som er kalt i run_game()"""
        input_data = {
            "hand_cards": self.player.hand,
            "playable_cards": playable_cards,
            "table_cards": self.player.table_visible,
            "pile": self.pile,
            "burnt_cards": self.burnt_cards,
            "must_play": must_play,
        }
        self.player.policy.process_input(input_data)

    """ 
    INPUT
    """

    def get_player_input(self) -> tuple:
        """return_output format = (output, index, safe?)"""
        chosen_card = None
        chosen_index = None
        chosen_index, chosen_card = self.player.policy.return_output()

        if chosen_index == None:
            return chosen_index, chosen_card

        if chosen_index != None and chosen_card != None:
            return chosen_index, chosen_card
        else:
            raise Exception("Ikke gyldig output")
