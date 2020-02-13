import json, random


class PlayNode:
    """
    Node of play possibility.
    """

    def __init__(self, score, agent_turn):
        self.agent_turn = agent_turn
        self.score = score
        self.branch = {}


class TicTacToeAgent:
    """
    Tic tac toe playing AI Agent.
    """

    PRINT_AVAILABLE_PLAYS_SCORE = False                  # :bool: Enables play evaluation on screen printing.
    PRINT_POSSIBILITY_TREE = False                       # :bool: Enables possibility tree on screen printing.
    RANDOM_INITIAL_MOVES = False                         # :bool: First move of agent is random despite playing order.
    VICTORY_CONDITIONS = [                               # :list: Board formations indicating victory.
        ('1', '2', '3'), ('1', '4', '7'),
        ('1', '5', '9'), ('2', '5', '8'),
        ('3', '5', '7'), ('3', '6', '9'),
        ('4', '5', '6'), ('7', '8', '9')
    ]

    def __init__(self, board: dict, agent_symbol: str):
        """
        Agent constructor, stores given board situation and player symbols.
        :param board: Given board situation.
        :param agent_symbol: Symbol to be assigned to agent.
        """

        self.board = dict(board)                                 # :dict: Given board situation.
        self.agent_symbol = agent_symbol                         # :str: Agent symbol on board.
        self.opponent_symbol = self.__get_opponent_symbol()      # :str: Opponent symbol on board.

    def get_move(self) -> str:
        """
        Triggers movement selection logic and returns result.
        :return: Integer denoting result.
        """

        # If enabled, first move of agent is random, being the first or second to play.
        if self.RANDOM_INITIAL_MOVES:
            initial_move = self.get_initial_moves()

            # If initial move has been detected, updates internal board, log and returns move.
            if initial_move:
                if self.PRINT_AVAILABLE_PLAYS_SCORE:
                    print(f'0 -> Special initial move: {initial_move}')
                self.board[initial_move] = self.agent_symbol
                return initial_move

        # Random initial moves is disabled, agent plays randomly only if it's the first to play.
        else:
            if self.is_board_empty():
                initial_move = self.get_initial_move()
                if self.PRINT_AVAILABLE_PLAYS_SCORE:
                    print(f'0 -> Special initial move: {initial_move}')
                # Update internal board with chosen move end return value.
                self.board[initial_move] = self.agent_symbol
                return initial_move

        # Recursively calculates complete possibility tree and logs result if required.
        possibility_tree = self.__get_possibility_tree(board=self.board)
        if self.PRINT_POSSIBILITY_TREE:
            print(json.dumps(possibility_tree, indent=4, sort_keys=False))

        # Evaluates each position's branch score.
        next_moves = []
        for move, node in possibility_tree.items():
            branch_score = self.__evaluate_moves({move: node})
            next_moves.append({
                'move': move,
                'branch_score': round(branch_score, 7)
            })

        # Sorts by best score and displays results if required.
        next_moves = sorted(next_moves, key=lambda k: k['branch_score'], reverse=True)
        if self.PRINT_AVAILABLE_PLAYS_SCORE:
            for i, x in enumerate(next_moves):
                print(f"{i} -> Move: {x.get('move')} | Branch score: {x.get('branch_score')}")

        # Randomizes chosen move amongst best equally scored moves.
        best_move_score = next_moves[0].get('branch_score')
        chosen_move = random.choice([x.get('move') for x in next_moves if x.get('branch_score') == best_move_score])
        if self.PRINT_AVAILABLE_PLAYS_SCORE:
            print(f"Chosen move: {chosen_move}")

        # Updates internal board with new position.
        self.board[chosen_move] = self.agent_symbol

        # Returns movement choice or None if board has no available position.
        return chosen_move

    def __get_possibility_tree(self, board: dict, possibility_tree: dict = None, agent_turn: bool = True,
                               branch_level: int = 0) -> dict:
        """
        Recursively builds the position possibilities tree.
        :param board: Dictionary containing current board situation.
        :param possibility_tree: Possibility tree under construction.
        :param agent_turn: Boolean stating if it's the agent's turn or not.
        :param branch_level: Current score multiplier.
        :return: Dictionary containing possibility tree.
        """

        # Initializes possibility tree if none was provided.
        if not possibility_tree: possibility_tree = {}

        # Gets available board positions for this branch.
        available_plays = [k for k, v in board.items() if not v.strip()]

        # If no positions are left, returns empty branch.
        if len(available_plays) == 0: return {}

        # Updates current branch level value.
        branch_level += 1
        # print(branch_level, str(available_plays))

        # Iterates on available board positions.
        for play in available_plays:

            # Updates board with current iteration's position.
            updated_board = dict(board)
            updated_board[play] = self.agent_symbol if agent_turn else self.opponent_symbol

            # Evaluates current move score.
            victory, score = self.__check_victory(updated_board)
            if victory and branch_level > 1:
                score /= 10**(branch_level-1) if victory == self.agent_symbol else -(10**(branch_level-1))

            # If there's a victory or loss on first move, prioritize attack.
            elif victory:
                score = score if victory == self.agent_symbol else -score*0.9

            # Creates node for currently analyzed position.
            possibility_tree[str(play)] = PlayNode(score, agent_turn).__dict__

            # Populates current branch and adds new node to the sub-branch if victory hasn't been achieved.
            if not victory:
                possibility_tree[str(play)]['branch'] = \
                    self.__get_possibility_tree(
                        board=updated_board,
                        possibility_tree=possibility_tree[str(play)]['branch'],
                        agent_turn=not agent_turn,
                        branch_level=branch_level
                    )
            else:
                possibility_tree[str(play)]['branch'] = {}

        return possibility_tree

    @classmethod
    def __evaluate_moves(cls, moves: dict, branch_score: float = 0) -> float:
        """
        Recursively evaluates current branch score.
        :param moves: Dictionary containing current position and associated node.
        :param branch_score: Current position score.
        :return:
        """

        for k, v in moves.items():
            branch_score += v.get('score')
            if v.get('branch'):
                branch_score = cls.__evaluate_moves(
                    moves=v.get('branch'),
                    branch_score=branch_score
                )

        return branch_score

    @classmethod
    def __check_victory(cls, board: dict) -> (str, int):
        """
        Checks victory conditions.
        :param board: Dictionary containing board to be analyzed.
        :return: Symbol of winner or None case no winners.
        """

        for a, b, c in cls.VICTORY_CONDITIONS:
            if board[a] == board[b] == board[c] != ' ':
                return board[a], 10

        return None, 0

    @staticmethod
    def get_initial_move() -> str:
        """
        Randomizes initial move according to given positions.
        :return: String denoting move.
        """

        return str(random.choice(range(1, 10)))

    def get_initial_moves(self) -> str:
        """
        Randomizes initial move according to given positions.
        :return: String denoting move.
        """

        no_of_moves = ''.join([v for k, v in self.board.items()]).replace(self.agent_symbol, '*')\
            .replace(self.opponent_symbol, '*').count('*')
        available_positions = [k for k, v in self.board.items() if not v.strip()]
        if no_of_moves < 2:
            choice = random.choice(available_positions)
            return choice
        else:
            return None

    def is_board_empty(self) -> bool:
        """
        Checks if internal board is empty denoting first play.
        :return: Boolean denoting if internal board is empty or not.
        """

        return len({v for k, v in self.board.items()}) == 1

    def print_board(self):
        """
        Prints current internal board.
        :return: void.
        """

        b = self.board
        print(f"{b['7']}|{b['8']}|{b['9']}")
        print("-+-+-")
        print(f"{b['4']}|{b['5']}|{b['6']}")
        print("-+-+-")
        print(f"{b['1']}|{b['2']}|{b['3']}")

    def get_board(self) -> dict:
        """
        Exposes current internal board.
        :return: Dictionary containing current internal board.
        """

        return self.board

    def __get_opponent_symbol(self) -> str:
        """
        Deduces opponent symbol.
        :return: String containing opponent symbol.
        """

        if self.agent_symbol == 'X': return 'O'
        else: return 'X'


if __name__ == "__main__":

    current_board = {'7': 'O', '8': 'X', '9': ' ',
                     '4': 'X', '5': 'O', '6': 'O',
                     '1': ' ', '2': ' ', '3': 'X'}

    TicTacToeAgent.PRINT_POSSIBILITY_TREE = True
    TicTacToeAgent.PRINT_AVAILABLE_PLAYS_SCORE = True
    agent_symbol = 'X'

    agent = TicTacToeAgent(current_board, agent_symbol)
    this_move = agent.get_move()

    print(f"Agent symbol: {agent_symbol}")
    print(f'Chosen move: {this_move}')
    print('Final test board:')
    agent.print_board()
