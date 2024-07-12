from multiprocessing import Pool, current_process

from pokerface import *
from itertools import combinations

from src.utils import Stream, flatten, split_into_chunks

class PokleSolver:
    def __init__(self, hands = None, order = None, game_string = None) -> None:
        self.evaluator = StandardEvaluator()

        if game_string:
            self.config = self.convert_gamestring_to_config(game_string)
        elif hands and order:
            self.config = self.create_config(hands, order)
        else:
            self.config = None
        self.solutions = []
    
    def write_solutions_to_file(self, filename):
        # convert to strings if any of them is a tuple
        if any ( [ isinstance ( solution, tuple ) for solution in self.solutions ] ):
            self.solutions = [ "".join ( flatten(solution) ) for solution in self.solutions ]

        with Stream ( filename, "w" ) as stream:
            stream.write ( "\n".join ( self.solutions ) )

    def read_solutions_from_file(self, filename):
        with Stream ( filename, "r" ) as stream:
            lines = [ l.strip() for l in stream.readlines() ]

        # split each line into 2-character chunks
        self.solutions = [ [ l[i:i+2] for i in range(0, len(l), 2) ] for l in lines ]

        # group solution by level
        self.solutions = [ ([sol[0], sol[1], sol[2]], [sol[3]], [sol[4]]) for sol in self.solutions ]

        print ( f"[+] read {len(self.solutions)} solutions from {filename}" )

    def convert_gamestring_to_config(self, gameString):
        #                                              MANDATORY          MANDATORY
        #                            <  solution  > <  input hands  > <   results     > <        combos        >
        # example full gamestring = "2s 7c 5s 4s 6d|as 7s 5d 2h 3s 3c|2 1 3 1 2 3 1 3 2|P 2P P Fl 2P P Fl 2P St"
        # gs =                      "              |9c 4d Kd 9d 8s Js|1 3 2 2 3 1 1 3 2|                       "

        solution, _input, _order, hands = gameString.replace('10', 'T').split("|")

        return self.create_config ( _input, _order )

    def create_config(self, player_hands_str, player_order_str):
        player_inputs = player_hands_str.split(" ")
        player_order = player_order_str.split(" ")

        # in player inputs, replace first letter as capital
        for idx, player_input in enumerate ( player_inputs ):
            player_inputs[idx] = player_input[0].upper() + player_input[1:]

        config = {
            "Pam": "".join ( player_inputs[0:2] ),
            "Sam": "".join ( player_inputs[2:4] ),
            "Lam": "".join ( player_inputs[4:6] ),
            "flop": {},
            "turn": {},
            "river": {}
        }

        players = ["Pam", "Sam", "Lam"]
        conversion = {
            '1': "first",
            '2': "second",
            '3': "third"
        }
        for level_idx, level in enumerate ( ["flop", "turn", "river"] ):
            for position_idx, position in enumerate ( ["first", "second", "third"] ):
                config [ level ] [ conversion [ player_order[level_idx*3 + position_idx] ] ] = players[position_idx]

        return config

    def prepare_deck(self):
        deck = StandardDeck()
        for player in ["Sam", "Pam", "Lam"]:
            deck.draw( parse_cards( self.config[player] ) )

        return deck

    def check_winner(self, board, level ):
        winner, second, loser = [ 
            self.evaluator.evaluate_hand( parse_cards ( self.config[self.config[level][position]] ), parse_cards( board ) ) 
            for position in ["first", "second", "third"] 
        ]

        return winner > second and winner > loser and second > loser

    def check_board(self, list_of_boards_and_level):
        # unpacking arg
        list_of_boards, level = list_of_boards_and_level
        after_level, deck = [], self.prepare_deck()

        print ( f"[+] [{current_process().pid}] started checking {len(list_of_boards)} boards for {level}")

        for idx, board in enumerate(list_of_boards):
            # print ( f"[+] [{level}] processing {idx} / {len(list_of_boards)}: {board}", end='\r')

            # remove the board cards from the deck
            deck.draw( parse_cards( board ) )

            # check for new card only if the current board is not flop
            if level != "flop":
                # iterate over remaining cards in the deck
                for card in deck:
                    str_card = str ( card )
                    new_board = board + str_card

                    if self.check_winner(new_board, level):
                        after_level.append ( new_board )

            else:
                if self.check_winner(board, level):
                    after_level.append ( board )
            
            # return board cards to the deck
            deck += parse_cards( board )
        
        # print ()
        print ( f"[+] [{current_process().pid}] ...... done ")
        return after_level

    def solve(self, cores = 1):
        assert self.config

        # flop --> 3 cards
        deck = self.prepare_deck()
        self.solutions = [ "".join ( [ str(c) for c in card]) for card in  combinations (deck, 3 ) ]
        
        for level in ["flop", "turn", "river"]:
            print ( f"[+] preparing check: {level} with {cores} cores")
            # we are splitting before each level, so that all threads have the same amount of work
            chunks = [ (data, level) for data in split_into_chunks ( self.solutions, len ( self.solutions) // cores ) ]

            pool = Pool(cores)
            self.solutions = flatten ( [ solution for solution in pool.map( self.check_board, chunks ) ] )

        print ( f"[+] current Pokle has {len(self.solutions)} solutions! " )
    
    def narrow (self, level_str, cards):
        if not cards or cards == "":
            return 
        
        if isinstance ( cards, str ):
            cards = cards.split()

        original_size = len ( self.solutions )

        # convert the card nominal to uppercase 
        for char in ['t', 'j', 'q', 'k', 'a']:
            cards = [card.replace ( char, char.upper() ) for card in cards]
        
        # and ofc, make sure the '10' will be replaced by 'T'
        cards = [ card.replace ( '10', 'T') for card in cards ]

        # split cards into two groups
        included = [ c for c in cards if not c.startswith('!') and not c.startswith('?') ]
        excluded, possible = [ c[1:] for c in cards if c.startswith('!') ], [ c[1:] for c in cards if c.startswith('?') ]

        level_decode = {
            "flop": 0,
            "turn": 1,
            "river": 2
        }

        level = level_decode[level_str]
        
        # first, filter for exact card 
        self.solutions = [ solution for solution in self.solutions if all ( [c in solution[level] for c in included] ) ]

        # now filter for cards that are not in the solution
        self.solutions = [ sol for sol in self.solutions if all ( [ all ( [ s[0] != c[0] and s[1] != c[1] for s in sol[level] if s not in included ] ) for c in excluded ] ) ]

        # possible cards: for now just filter solution which do not contain any of the possible cards
        # TODO: implement a more sophisticated filter
        self.solutions = [ solution for solution in self.solutions if all ( [ c not in solution[level] for c in possible ] ) ]

        # temporary: filter turn and river for questionable cards
        if level_str in ["turn", "river"] and possible:
            self.solutions = [ solution for solution in self.solutions if all ( [ solution[level][0][0] == c[0] or solution[level][0][1] == c[1] for c in possible ] ) ]

        print ( f"[-->] [{level_str}] narrowed from {original_size} down to {len(self.solutions)} solutions (-{original_size - len(self.solutions)})" )
    
    def filter(self, inFile, flop = None, turn = None, river = None):
        # read solutions from file
        if inFile:
            self.read_solutions_from_file(inFile)

        for level, cards in [("flop", flop), ("turn", turn), ("river", river)]:
            cards = cards if cards else input ( f"[+] enter cards for {level} (separated by space): " )
            self.narrow(level, cards)
